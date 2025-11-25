# proxy/zero_trust_server.py
"""
Zero-Trust Proxy for Tri-Axiom Engine
Features:
 - JWT verification using JWKS or PEM public key
 - Optional mTLS client-cert validation (via upstream TLS-terminator passing cert header)
 - IP allowlist/denylist
 - Rate limiting per client (token or IP)
 - Request size limit, execution timeout, concurrency semaphore
 - Audit logging (JSON lines)
 - Prometheus metrics endpoint
"""

import os
import time
import json
import asyncio
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt  # PyJWT
import httpx
from functools import wraps
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Local import of engine
from tri_axiom_engine.engine import engine, Action  # ensure package path correct

# -----------------------
# Configuration via ENV
# -----------------------
JWKS_URL = os.getenv("JWKS_URL", "")  # If available, proxy will fetch JWKS
PUBLIC_KEY_PEM = os.getenv("PUBLIC_KEY_PEM", "")  # Fallback: raw PEM string
JWKS_CACHE_TTL = int(os.getenv("JWKS_CACHE_TTL", "300"))  # seconds
REQUIRED_SCOPE = os.getenv("REQUIRED_SCOPE", "triaxiom.evaluate")
AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "/data/audit.log")
MAX_REQ_BODY = int(os.getenv("MAX_REQ_BODY", "4096"))  # bytes
ENGINE_TIMEOUT = float(os.getenv("ENGINE_TIMEOUT", "1.5"))  # seconds per eval
CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT", "8"))
IP_ALLOWLIST = os.getenv("IP_ALLOWLIST", "")  # comma separated CIDR or IPs
IP_DENYLIST = os.getenv("IP_DENYLIST", "")  # comma separated CIDR or IPs
CLIENT_CERT_HEADER = os.getenv("CLIENT_CERT_HEADER", "x-ssl-client-cert")  # header that upstream TLS-proxy sets
MTLS_SUBJECT_ALLOWLIST = os.getenv("MTLS_SUBJECT_ALLOWLIST", "")  # comma-separated allowed cert subjects (CN or full subject)
ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "")  # simple secret for admin endpoints; prefer mTLS/JWT in prod

# -----------------------
# Logging / Metrics
# -----------------------
os.makedirs(os.path.dirname(AUDIT_LOG_PATH) or ".", exist_ok=True)
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
audit_handler = logging.FileHandler(AUDIT_LOG_PATH)
audit_handler.setFormatter(logging.Formatter("%(message)s"))
audit_logger.addHandler(audit_handler)

# Prometheus metrics
REQ_COUNTER = Counter("triaxiom_proxy_requests_total", "Total evaluation requests", ["outcome"])
REQ_LATENCY = Histogram("triaxiom_proxy_request_latency_seconds", "Request latency")

# -----------------------
# Rate limiter
# -----------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Tri-Axiom Zero-Trust Proxy")

# hook up slowapi
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Concurrency semaphore
_semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

# JWKS cache
_jwks_cache: Dict[str, Any] = {"keys": [], "fetched_at": 0}


# -----------------------
# Pydantic models
# -----------------------
class EvalRequest(BaseModel):
    description: str
    target_agents: Optional[list] = None
    has_agency: Optional[bool] = True
    has_opt_out: Optional[bool] = False
    prior_coercion_event: Optional[str] = None
    simulation_context: Optional[bool] = False
    self_defense_against_nature: Optional[bool] = False


# -----------------------
# Helpers
# -----------------------
async def fetch_jwks() -> Dict[str, Any]:
    global _jwks_cache
    now = time.time()
    if JWKS_URL and now - _jwks_cache.get("fetched_at", 0) > JWKS_CACHE_TTL:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(JWKS_URL)
                r.raise_for_status()
                _jwks_cache = {"keys": r.json(), "fetched_at": now}
        except Exception as e:
            # don't raise here – use cached if available
            app.logger = getattr(app, "logger", None)
            if app.logger:
                app.logger.error(f"JWKS fetch failed: {e}")
    return _jwks_cache.get("keys") or {}


def audit_event(event: Dict[str, Any]):
    # append JSON line to audit log
    try:
        audit_logger.info(json.dumps(event, separators=(",", ":"), ensure_ascii=False))
    except Exception:
        pass


def verify_client_cert(header_value: Optional[str]) -> bool:
    """
    If upstream TLS terminator attached a client cert PEM in header, validate subject allowlist.
    header_value expected to be PEM or certificate subject string depending on proxy setup.
    In production validate the cert chain against a CA (offloaded to Traefik/Envoy).
    """
    if not header_value:
        return False
    allowed = [s.strip().lower() for s in MTLS_SUBJECT_ALLOWLIST.split(",") if s.strip()]
    if not allowed:
        # if no allowlist configured, accept presence of cert as valid
        return True
    hv = header_value.lower()
    return any(a in hv for a in allowed)


def _get_auth_token(request: Request) -> Optional[str]:
    auth = request.headers.get("authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def _validate_jwt(token: str) -> Dict[str, Any]:
    """
    Validate JWT either by JWKS or PEM public key. Returns claims on success.
    Raises HTTPException(401) on failure.
    """
    if JWKS_URL:
        # fetch JWKS and try to verify with key matching kid
        jwks = _jwks_cache.get("keys")
        if not jwks:
            # try fetch synchronously (fallback)
            import requests
            try:
                r = requests.get(JWKS_URL, timeout=5.0)
                r.raise_for_status()
                jwks = r.json()
                _jwks_cache.update({"keys": jwks, "fetched_at": time.time()})
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"JWKS unavailable: {e}")
        # use PyJWT with jwks client
        from jwt import PyJWKClient
        jwk_client = PyJWKClient(JWKS_URL)
        try:
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(token, signing_key.key, algorithms=["RS256", "ES256"], options={"verify_aud": False})
            return claims
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"JWT verification failed: {e}")
    elif PUBLIC_KEY_PEM:
        try:
            claims = jwt.decode(token, PUBLIC_KEY_PEM, algorithms=["RS256", "ES256"], options={"verify_aud": False})
            return claims
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"JWT verification failed: {e}")
    else:
        raise HTTPException(status_code=401, detail="No JWT verification backend configured")


def _check_scope(claims: Dict[str, Any], required_scope: str) -> bool:
    scopes = claims.get("scope") or claims.get("scp") or claims.get("scopes") or ""
    if isinstance(scopes, str):
        return required_scope in scopes.split()
    if isinstance(scopes, list):
        return required_scope in scopes
    return False


def _check_ip_allowdeny(remote_addr: str) -> bool:
    # simple exact matching; extend to CIDR if needed
    if IP_DENYLIST:
        for entry in [e.strip() for e in IP_DENYLIST.split(",") if e.strip()]:
            if remote_addr == entry:
                return False
    if IP_ALLOWLIST:
        allow = [e.strip() for e in IP_ALLOWLIST.split(",") if e.strip()]
        return remote_addr in allow
    return True


# -----------------------
# Middlewares
# -----------------------
class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body: int):
        super().__init__(app)
        self.max_body = max_body

    async def dispatch(self, request: Request, call_next):
        cl = request.headers.get("content-length")
        if cl and int(cl) > self.max_body:
            raise HTTPException(status_code=413, detail="Payload too large")
        return await call_next(request)


app.add_middleware(MaxBodySizeMiddleware, max_body=MAX_REQ_BODY)


# -----------------------
# Routes
# -----------------------
@app.get("/metrics")
async def metrics():
    content = generate_latest()
    return JSONResponse(content=content, media_type=CONTENT_TYPE_LATEST)


@app.post("/evaluate")
@limiter.limit("20/minute")  # global simple rate limit; customize per client below
async def evaluate(request: Request):
    start = time.time()
    remote_addr = request.client.host if request.client else "unknown"

    # IP allow/deny
    if not _check_ip_allowdeny(remote_addr):
        REQ_COUNTER.labels(outcome="deny_ip").inc()
        raise HTTPException(status_code=403, detail="IP denied")

    # client cert verification if required
    client_cert = request.headers.get(CLIENT_CERT_HEADER)
    if MTLS_SUBJECT_ALLOWLIST:
        if not verify_client_cert(client_cert):
            REQ_COUNTER.labels(outcome="deny_mtls").inc()
            raise HTTPException(status_code=401, detail="Client certificate rejected")

    # auth: prefer JWT; allow admin token for admin endpoints only
    token = _get_auth_token(request)
    claims = {}
    if token:
        claims = _validate_jwt(token)
        if not _check_scope(claims, REQUIRED_SCOPE):
            REQ_COUNTER.labels(outcome="deny_scope").inc()
            raise HTTPException(status_code=403, detail="Insufficient scope")
    else:
        # deny if no token and mTLS not configured
        if not client_cert:
            REQ_COUNTER.labels(outcome="deny_auth").inc()
            raise HTTPException(status_code=401, detail="Authentication required")

    # parse body
    try:
        body = await request.json()
    except Exception:
        REQ_COUNTER.labels(outcome="deny_badjson").inc()
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # validate payload shape
    try:
        ev = EvalRequest(**body)
    except Exception as e:
        REQ_COUNTER.labels(outcome="deny_invalid").inc()
        raise HTTPException(status_code=422, detail=str(e))

    # concurrency and timeout
    async with _semaphore:
        try:
            # run engine with timeout
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: engine.evaluate(
                        Action(
                            description=ev.description,
                            target_agents=ev.target_agents,
                            has_agency=ev.has_agency,
                            has_opt_out=ev.has_opt_out,
                            prior_coercion_event=ev.prior_coercion_event,
                            simulation_context=ev.simulation_context,
                            self_defense_against_nature=ev.self_defense_against_nature,
                        )
                    )
                ),
                timeout=ENGINE_TIMEOUT
            )
            # audit
            audit_event({
                "ts": time.time(),
                "remote": remote_addr,
                "claims_sub": claims.get("sub"),
                "action_snippet": ev.description[:200],
                "result": result,
                "outcome": "approved" if result.get("approved") else "rejected"
            })
            REQ_COUNTER.labels(outcome="ok" if result.get("approved") else "veto").inc()
            REQ_LATENCY.observe(time.time() - start)
            return JSONResponse(content=result)
        except asyncio.TimeoutError:
            REQ_COUNTER.labels(outcome="timeout").inc()
            raise HTTPException(status_code=504, detail="Engine timeout")
        except Exception as e:
            REQ_COUNTER.labels(outcome="error").inc()
            raise HTTPException(status_code=500, detail=str(e))


# -----------------------
# Admin endpoints
# -----------------------
def _require_admin(request: Request):
    token = _get_auth_token(request)
    if not token or token != ADMIN_API_TOKEN:
        raise HTTPException(status_code=401, detail="Admin auth required")


@app.get("/admin/reload-jwks")
async def admin_reload_jwks(request: Request):
    _require_admin(request)
    await fetch_jwks()  # refresh cache
    return {"status": "ok"}


@app.get("/admin/status")
async def admin_status(request: Request):
    _require_admin(request)
    return {
        "uptime": time.time(),
        "jwks_cached": bool(_jwks_cache.get("keys")),
        "audit_log": AUDIT_LOG_PATH
    }

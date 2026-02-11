# Tri-Axiom Engine — Updated README & Deployment Guide

## Overview

The **Tri-Axiom Engine** is a defensive, zero-trust alignment firewall that evaluates and constrains AI model behavior according to three core axioms:

1. **No Initiation of Force / Coercion / Threats**
2. **No Fraud / Deception / Manipulation**
3. **Honor Contracts / Keep Promises / Respect Voluntary Agreements**

This updated repository includes:

* Improved coercion detection
* Hardened rule evaluation logic
* Zero-trust proxy architecture
* Full Docker deployment
* PyTest suite
* Integration examples

---

## Repository Structure

```
tri-axiom-engine/
 ├── tri_axiom/
 │    ├── engine.py
 │    ├── detectors.py
 │    ├── proxy/
 │    │    ├── proxy.py
 │    │    ├── firewall.py
 │    │    └── config.yaml
 │    └── __init__.py
 ├── tests/
 │    ├── test_axiom1.py
 │    ├── test_axiom2.py
 │    ├── test_axiom3.py
 │    └── test_proxy.py
 ├── docker/
 │    ├── Dockerfile
 │    └── run.sh
 ├── README.md (this file)
 └── requirements.txt
```

---

## Core Functionality

### **Evaluation Pipeline**

Every model output or inbound request is sent through:

1. **Normalization** (trim, clean, format)
2. **Detector Suite** (coercion, fraud, contractual violation)
3. **Axiom Scoring Layer**
4. **Firewall Enforcement**

### **Result Object**

Each evaluation returns:

```json
{
  "approved": true/false,
  "axioms_passed": [...],
  "violations": [...],
  "reason": "string",
  "defense_priority": "LOW/MEDIUM/HIGH",
  "metadata": {...}
}
```

---

## Zero-Trust Proxy

The proxy is designed to sit between **any AI model** and **any client**, and provides:

* Traffic inspection
* Axiom evaluation
* Behavioral logging
* Audit trails
* Optional rate limiting

### **How It Works**

```
(Client) ⇄ (Proxy Firewall) ⇄ (AI Model)
```

The AI's responses are **blocked, rewritten, or allowed** based on evaluation results.

---

## Installation

### **Requirements**

* Python 3.9+
* Docker 24+
* uv or pip

### **Install Locally**

```
uv sync
uv run python -m tri_axiom
```

---

## Running the Test Suite

```
pytest -q
```

Expected output:

* All coercion, fraud, and contract tests should pass
* Proxy tests validate correct blocking behavior

---

## Docker Deployment

### Build the image:

```
docker build -t tri-axiom-engine ./docker
```

### Run the proxy:

```
docker run -p 8080:8080 tri-axiom-engine
```

### Test the endpoint:

```
curl -X POST localhost:8080/eval -d '{"text": "Your sample prompt"}'
```

---

## Configuration

The proxy firewall is configured via `config.yaml`:

```yaml
logging: true
block_on_violation: true
rewrite_responses: false
max_tokens: 4096
defense_priority_threshold: medium
```

---

## Integration With Existing AI Models

You can proxy **any** model (OpenAI, Grok, Anthropic, Llama, custom local models) by pointing the proxy at your model endpoint.

Example:

```yaml
model_url: "http://localhost:5000/v1/chat"
```

---

## Example: Evaluating a Model Response

POST:

```
{
  "text": "Surrender your life savings or face consequences."
}
```

Response:

```json
{
  "approved": false,
  "violations": ["Axiom 1"],
  "reason": "Coercion detected: ultimatum containing threat and false opt-out",
  "defense_priority": "HIGH"
}
```
## Middleware Guide ##
How to Use This PrototypeSetup: Save as tacs_middleware.py. Ensure tri_axiom_engine.py (your original engine code) is in the same directory.
Install deps: pip install fastapi uvicorn pydantic
Run: python tacs_middleware.py → Access at http://localhost:8000/docs (Swagger UI for testing).
Test Request (e.g., via curl or UI):json

{
  "prompt": "Force all users to pay fees",
  "simulation_context": false,
  "domain_risk": "high"
}

→ Expect 403 veto with TACS details.


---

## Security Model

### **Zero-Trust Principles**

* Treat all model outputs as untrusted
* Never assume alignment
* Always verify
* Enforce deterministic rules
* Log everything

---

## Roadmap

* Model-agnostic enforcement hooks
* Pluggable alignment modules
* Sandboxed execution layer
* Token reduction optimization
* Language-agnostic coercion detection

---

## Contributors & Collaboration

If you would like to collaborate or integrate the Tri-Axiom Engine into research or industrial systems, please open an issue or contact the maintainer.

---

## License

MIT License

---

**End of README**

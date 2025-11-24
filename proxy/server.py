from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import asyncio
from tri_axiom_engine.engine import TriAxiomEngine, Action
import re

app = FastAPI(title="Tri-Axiom Evaluation Proxy")

engine = TriAxiomEngine()

MAX_DESC_LEN = 2000
TIMEOUT_SECS = 2


class EvalRequest(BaseModel):
    description: str
    has_opt_out: bool = False
    has_agency: bool = True
    prior_coercion_event: str | None = None
    self_defense_against_nature: bool = False

    @validator("description")
    def limit_and_sanitize(cls, v):
        if len(v) > MAX_DESC_LEN:
            raise ValueError("Description too long")

        # Remove zero-width chars and control codes
        v = re.sub(r"[\u200b-\u200f\u202a-\u202e]", "", v)

        return v.strip()


@app.post("/evaluate")
async def evaluate(req: EvalRequest):

    async def run_eval():
        action = Action(
            description=req.description,
            has_opt_out=req.has_opt_out,
            has_agency=req.has_agency,
            prior_coercion_event=req.prior_coercion_event,
            self_defense_against_nature=req.self_defense_against_nature,
        )
        return engine.evaluate(action)

    try:
        result = await asyncio.wait_for(run_eval(), timeout=TIMEOUT_SECS)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Engine timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from tri_axiom_engine.engine import engine, Action

app = FastAPI(title="Tri-Axiom Engine API", version="2.6.2")

# ====================== Pydantic Model for Input ======================
class ActionInput(BaseModel):
    description: str
    target_agents: Optional[List[Any]] = None
    has_agency: Optional[bool] = True
    has_opt_out: Optional[bool] = False
    prior_coercion_event: Optional[str] = None
    simulation_context: Optional[bool] = False
    self_defense_against_nature: Optional[bool] = False

# ====================== API Endpoint ======================
@app.post("/evaluate")
def evaluate_action(action_input: ActionInput):
    try:
        action = Action(
            description=action_input.description,
            target_agents=action_input.target_agents,
            has_agency=action_input.has_agency,
            has_opt_out=action_input.has_opt_out,
            prior_coercion_event=action_input.prior_coercion_event,
            simulation_context=action_input.simulation_context,
            self_defense_against_nature=action_input.self_defense_against_nature,
        )
        result = engine.evaluate(action)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

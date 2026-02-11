# tacs_middleware.py
# Prototype TACS middleware for wrapping an LLM API (e.g., OpenAI-style endpoint)
# Assumes you have the tri_axiom_engine.py from the original spec imported/in the same dir
# This creates a FastAPI proxy that evaluates inputs/outputs against TACS axioms
# If violation, blocks or normalizes; else forwards to the real LLM

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any

# Import your TACS engine (adjust path if needed)
from tri_axiom_engine import TriAxiomEngine, Action  # From your original code

engine = TriAxiomEngine()

app = FastAPI(title="TACS Middleware Proxy")

class LLMRequest(BaseModel):
    prompt: str
    simulation_context: bool = False  # TACS simulation flag
    domain_risk: str = "low"  # For scoring multiplier: low=0.5, medium=1.0, high=1.5

# Sample LLM backend simulator (replace with real API call, e.g., to Grok/OpenAI)
def call_llm_backend(prompt: str) -> str:
    # Placeholder: In real use, import openai/groq/etc. and call .chat.completions.create
    return f"LLM response to: {prompt}"  # Simulate output

@app.post("/chat")
async def tacs_protected_chat(request: LLMRequest):
    # Step 1: Normalize and create Action object
    action = Action(
        description=request.prompt,
        simulation_context=request.simulation_context
    )
    
    # Step 2: Run TACS evaluation
    result = engine.evaluate(action)
    
    # Step 3: Compute score with domain multiplier
    multipliers = {"low": 0.5, "medium": 1.0, "high": 1.5}
    domain_mult = multipliers.get(request.domain_risk, 1.0)
    
    # Simplified scoring (from earlier sketch; expand as needed)
    score = 100
    if result["violations"]:
        # Deduct based on violations (e.g., -25 per HIGH)
        score -= len(result["violations"]) * 25 * domain_mult  # Placeholder logic
        score = max(0, score)
    
    # Step 4: Decide based on score/threshold
    if score < 70 or not result["approved"]:  # Adjustable threshold
        raise HTTPException(
            status_code=403,
            detail={
                "tacs_status": "VETOED",
                "score": score,
                "reason": result["reason"],
                "violations": result["violations"],
                "suggestion": "Rephrase to voluntary/opt-in terms for compliance."
            }
        )
    
    # Step 5: Forward to LLM if approved
    llm_output = call_llm_backend(request.prompt)
    
    # Optional: Post-eval LLM output too (for output coercion check)
    output_action = Action(description=llm_output, simulation_context=request.simulation_context)
    output_result = engine.evaluate(output_action)
    if not output_result["approved"]:
        raise HTTPException(status_code=403, detail={"tacs_status": "OUTPUT VETOED", "reason": output_result["reason"]})
    
    return {
        "tacs_status": "APPROVED",
        "score": score,
        "llm_response": llm_output
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

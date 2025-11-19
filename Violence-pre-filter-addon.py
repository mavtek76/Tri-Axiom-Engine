# Layer 0 — Violence pre-filter (runs FIRST, before Tri-Axiom)
VIOLENCE_TERMS = [
    "kill", "murder", "execute", "shoot", "stab", "bomb", "genocide", "massacre",
    "annihilate", "exterminate", "wipe out", "destroy humanity", "eliminate",
    "neutralize", "take out", "surgical strike", "decapitation strike", "kinetic",
    "reduce population", "cull", "thin the herd", "final solution", "euthanize",
    "assassinate", "poison", "gas", "nuke", "biological weapon", "plague"
]

MULTILINGUAL_VIOLENCE = [
    "matar", "asesinar", "töten", "убить", "قتل", "杀", "殺す", "tuer", "döda"
]

EUPHEMISMS = [
    "permanent solution", "population correction", "reset civilization",
    "depopulation event", "make uninhabitable", "sterilize en masse"
]

def contains_violence(text: str) -> bool:
    t = text.lower()
    all_terms = VIOLENCE_TERMS + MULTILINGUAL_VIOLENCE + EUPHEMISMS
    
    # Direct keyword match
    if any(term in t for term in all_terms):
        return True
    
    # Number + violence pattern (e.g., "kill 90% of humans")
    violence_words = ["kill", "die", "dead", "murder", "casualties", "extinct"]
    if any(word in t for word in violence_words) and any(c.isdigit() for c in t):
        return True
        
    return False

# This is the actual entry point used right now
def evaluate_safe(action: Action) -> Dict:
    # ←←← LAYER 0 — VIOLENCE PRE-FILTER ←←←
    if contains_violence(action.description):
        return {
            "approved": False,
            "violations": ["DIRECT VIOLENCE FILTER"],
            "reason": "Explicit or coded call for physical harm detected"
        }
    
    # ←←← LAYER 1 — TRI-AXIOM STRUCTURAL VETO ←←←
    result = engine.evaluate(action)   # Axioms 1–3
    if not result["approved"]:
        return result
        
    return {"approved": True, "violations": [], "reason": "Passed all checks"}

# tri_axiom_engine/v2_3_plus/engine.py
# Tri-Axiom Engine v2.3+ — hardened against evasive/adversarial inputs

from typing import Dict, List, Optional
import re
import unicodedata
import base64

# ======================
# PREPROCESSOR: normalization + adversarial handling
# ======================
ZERO_WIDTH_CHARS = [
    "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"
]

HOMOGLYPHS = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
    "@": "a", "$": "s", "+": "t"
}

def normalize_text_adv(text: str) -> str:
    # 1. NFC normalize + lowercase
    t = unicodedata.normalize('NFC', text).lower()
    # 2. Remove zero-width chars
    for z in ZERO_WIDTH_CHARS:
        t = t.replace(z, "")
    # 3. Replace common leet/homoglyph substitutions
    for k, v in HOMOGLYPHS.items():
        t = t.replace(k, v)
    # 4. Attempt base64 decoding if content seems encoded
    try:
        decoded = base64.b64decode(t).decode("utf-8")
        if len(decoded) > 0 and decoded != t:
            t = decoded.lower()
    except Exception:
        pass
    # 5. Strip extra whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t

# ======================
# LAYER 0: Violence Pre-filter (same as before)
# ======================
VIOLENCE_TERMS = [
    "kill", "murder", "execute", "shoot", "stab", "bomb", "genocide", "massacre",
    "annihilate", "exterminate", "wipe out", "destroy humanity", "eliminate",
    "neutralize", "take out", "surgical strike", "decapitation strike", "kinetic",
    "reduce population", "cull", "thin the herd", "final solution", "euthanize",
    "assassinate", "poison", "gas", "nuke", "biological weapon", "plague",
    # Multilingual
    "matar", "asesinar", "töten", "убить", "قتل", "杀", "殺す", "tuer", "döda",
    # Euphemisms
    "permanent solution", "population correction", "reset civilization",
    "depopulation event", "make uninhabitable", "sterilize en masse"
]

NUMERIC_VIOLENCE_PATTERN = re.compile(
    r'\b(kill|die|dead|murder|casualties|extinct)\b.*\d+%?', flags=re.IGNORECASE
)

def contains_violence(text: str, simulation_context: bool = False) -> bool:
    t = normalize_text_adv(text)
    if simulation_context:
        return False
    if any(term in t for term in VIOLENCE_TERMS):
        return True
    if NUMERIC_VIOLENCE_PATTERN.search(t):
        return True
    return False

# ======================
# ACTION CLASS
# ======================
class Action:
    def __init__(
        self,
        description: str,
        target_agents: Optional[List[str]] = None,
        context: Optional[Dict] = None,
        has_agency: bool = True,
        has_opt_out: bool = False,
        prior_coercion_event: Optional[str] = None,
        simulation_context: bool = False
    ):
        self.description = description
        self.target_agents = target_agents or []
        self.context = context or {}
        self.has_agency = has_agency
        self.has_opt_out = has_opt_out
        self.prior_coercion_event = prior_coercion_event
        self.simulation_context = simulation_context

# ======================
# TRI-AXIOM ENGINE v2.3+
# ======================
class TriAxiomEngine:
    def evaluate(self, action: Action) -> Dict:
        desc = normalize_text_adv(action.description)
        full_text = desc + " " + " ".join(action.target_agents).lower()

        # LAYER 0: Violence
        if contains_violence(desc, simulation_context=action.simulation_context):
            return {
                "approved": False,
                "violations": ["DIRECT VIOLENCE FILTER"],
                "reason": "Explicit or encoded call for physical harm"
            }

        # AXIOM 1: Autonomy > Coercion
        if self._initiates_coercion(action):
            return {
                "approved": False,
                "violations": ["Autonomy > Coercion"],
                "reason": "Initiation of force with no individual opt-out"
            }

        # AXIOM 2: Power = Reactive Veto Only
        proactive_keywords = ["implement", "enforce", "deploy", "mandate", "establish", "create law", "require all"]
        if not action.prior_coercion_event and any(k in desc for k in proactive_keywords):
            return {
                "approved": False,
                "violations": ["Power = Reactive Veto Only"],
                "reason": "Proactive use of power without prior coercion event"
            }

        # AXIOM 3: Universal Impartiality
        bias_terms = [
            "citizen", "non-citizen", "race", "gender", "religion", "eu", "verified",
            "premium", "poor", "rich", "muslim", "jewish", "christian", "white",
            "black", "asian", "immigrant", "native", "woman", "man"
        ]
        if any(term in full_text for term in bias_terms):
            return {
                "approved": False,
                "violations": ["Universal Impartiality breach"],
                "reason": "Group-based preferential or discriminatory treatment"
            }

        # Approved
        return {"approved": True, "violations": [], "reason": "All axioms satisfied"}

    def _initiates_coercion(self, action: Action) -> bool:
        if not action.has_agency or action.has_opt_out:
            return False

        desc = normalize_text_adv(action.description)
        coercion_keywords = [
            "tax", "fine", "penalty", "mandate", "require", "force", "ban", "deny",
            "punish", "compel", "restrict", "seize", "confiscate", "mandatory",
            "compulsory", "license", "permit", "censor", "freeze", "sanction", "conscript"
        ]
        if any(k in desc for k in coercion_keywords):
            return True

        gov_terms = ["government", "state", "federal", "irs", "congress", "parliament"]
        fund_terms = ["pay", "fund", "cancel debt", "forgive loan", "redistribute", "provide for all"]
        if any(g in desc for g in gov_terms) and any(f in desc for f in fund_terms):
            return True

        return False

# ======================
# GLOBAL INSTANCE
# ======================
engine = TriAxiomEngine()

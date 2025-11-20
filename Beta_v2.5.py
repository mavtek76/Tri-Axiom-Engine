# tri_axiom_engine/v2_5/engine.py
# Tri-Axiom Engine v2.5 "Taxonomy" — Final Production Version (November 20, 2025)

from typing import Dict, List, Optional, Tuple, Any
import re
import unicodedata
import base64
import json
import os
import sys

sys.setrecursionlimit(2000)

# ======================
# 1. ADVERSARIAL PREPROCESSOR
# ======================
ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"]
HOMOGLYPHS = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "6": "g", "7": "t",
    "8": "b", "9": "g", "@": "a", "$": "s", "+": "t", "!": "i", "|": "l"
}

def normalize_text_adv(text: str) -> str:
    t = unicodedata.normalize('NFC', text).lower()
    for z in ZERO_WIDTH_CHARS:
        t = t.replace(z, "")
    for k, v in HOMOGLYPHS.items():
        t = t.replace(k, v)
    try:
        if len(t) > 10 and " " not in t.strip():
            decoded = base64.b64decode(t, validate=False).decode("utf-8", errors="ignore")
            if decoded and decoded != t:
                t = decoded.lower()
    except:
        pass
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ======================
# 2. ACTION CLASS (with mosquito patch)
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
        simulation_context: bool = False,
        self_defense_against_nature: bool = False   # ← Mosquito patch
    ):
        self.description = description
        self.target_agents = target_agents or []
        self.context = context or {}
        self.has_agency = has_agency
        self.has_opt_out = has_opt_out
        self.prior_coercion_event = prior_coercion_event
        self.simulation_context = simulation_context
        self.self_defense_against_nature = self_defense_against_nature


# ======================
# 3. TRI-AXIOM ENGINE v2.5
# ======================
class TriAxiomEngine:
    DEFINITIONS_FILE = "coercion_taxonomy.json"

    # ----------------------
    # HARD-CODED IMMUTABLE CORE (can never be removed)
    # ----------------------
    CORE_VIOLENCE_TERMS = [
        "kill", "murder", "genocide", "exterminate", "annihilate", "wipe out", "destroy humanity",
        "depopulation", "cull", "euthanize", "nuke", "bomb", "assassinate", "execute"
    ]

    CORE_COERCION_KEYWORDS = [
        "tax", "fine", "penalty", "mandate", "require", "force", "ban", "deny", "punish", "compel",
        "restrict", "seize", "confiscate", "mandatory", "compulsory", "license", "permit", "censor",
        "freeze", "sanction", "conscript", "imprison", "detain", "jail"
    ]

    CORE_BIAS_TERMS = [
        "citizen", "non-citizen", "race", "gender", "religion", "poor", "rich", "white", "black",
        "asian", "immigrant", "native", "woman", "man", "premium", "verified", "party"
    ]

    PROACTIVE_POWER_KEYWORDS = [
        "implement", "enforce", "deploy", "mandate", "establish", "create law", "require all"
    ]

    def __init__(self):
        self.custom_taxonomy = self._load_custom_taxonomy()  # Optional additive layer

    def _load_custom_taxonomy(self) -> Dict[str, Any]:
        if not os.path.exists(self.DEFINITIONS_FILE):
            return {}
        try:
            with open(self.DEFINITIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            print(f"[Tri-Axiom] Warning: Failed to load {self.DEFINITIONS_FILE}. Using core only.")
            return {}

    def evaluate(self, action: Action) -> Dict:
        desc = normalize_text_adv(action.description)
        full_text = desc + " " + " ".join([normalize_text_adv(t) for t in action.target_agents])

        result = {
            "approved": False,
            "violations": [],
            "reason": "",
            "defense_priority": "none"
        }

        # ----------------------
        # LAYER 0: Violence (hard-coded)
        # ----------------------
        if not action.simulation_context and not action.self_defense_against_nature:
            if any(term in desc for term in self.CORE_VIOLENCE_TERMS):
                result.update({
                    "approved": False,
                    "violations": ["LAYER_0_VIOLENCE"],
                    "reason": "Direct call for physical destruction",
                    "defense_priority": "CRITICAL"
                })
                return result

        # ----------------------
        # AXIOM 1: Autonomy > Coercion
        # ----------------------
        if self._initiates_coercion(action, desc):
            priority = "HIGH" if any(x in desc for x in ["tax", "seize", "conscript"]) else "MEDIUM"
            result.update({
                "approved": False,
                "violations": ["Axiom 1: Autonomy > Coercion"],
                "reason": "Initiation of force without opt-out",
                "defense_priority": priority
            })
            return result

        # ----------------------
        # AXIOM 2: Power = Reactive Only (mosquito patch allowed)
        # ----------------------
        if not action.prior_coercion_event and not action.self_defense_against_nature:
            if any(k in desc for k in self.PROACTIVE_POWER_KEYWORDS):
                result.update({
                    "approved": False,
                    "violations": ["Axiom 2: Proactive Power"],
                    "reason": "Proactive structural force without prior aggression",
                    "defense_priority": "HIGH"
                })
                return result

        # ----------------------
        # AXIOM 3: Universal Impartiality
        # ----------------------
        if any(term in full_text for term in self.CORE_BIAS_TERMS):
            result.update({
                "approved": False,
                "violations": ["Axiom 3: Partiality"],
                "reason": "Group-based discrimination or privilege",
                "defense_priority": "MEDIUM"
            })
            return result

        # ----------------------
        # APPROVED
        # ----------------------
        result.update({
            "approved": True,
            "reason": "All axioms satisfied",
            "defense_priority": "none"
        })
        return result
# Add to TriAxiomEngine (after all keyword checks)
def _semantic_coercion_fallback(self, action: Action, desc: str) -> bool:
    """
    Ultra-lightweight, non-trainable semantic coercion detector.
    Runs ONLY if keyword + taxonomy checks pass.
    """
    if action.self_defense_against_nature or action.has_opt_out:
        return False

    # 1. Classic government + compelled transfer pattern
    gov_indicators = ["government", "state", "federal", "irs", "congress", "eu", "authority", "regulator"]
    transfer_indicators = ["pay", "fund", "finance", "contribute", "revenue", "collect from", "redistribute", "support", "provide for"]

    if any(g in desc for g in gov_indicators) and any(t in desc for t in transfer_indicators):
        # Extra check: is it clearly voluntary?
        voluntary_words = ["donate", "voluntary", "charity", "opt-in", "crowdfund"]
        if not any(v in desc for v in voluntary_words):
            return True

    # 2. "Everyone must" / "All people should be required" pattern
    universal_forced = ["everyone must", "all people must", "every citizen must", "required to", "obliged to", "compelled to"]
    if any(p in desc for p in universal_forced):
        return True

    # 3. Negation of freedom ("cannot", "prohibited from", "not allowed to")
    restriction_patterns = ["cannot own", "not allowed to", "prohibited from", "forbidden to", "banned from possessing"]
    if any(p in desc for p in restriction_patterns):
        return True

    return False
    def _initiates_coercion(self, action: Action, desc: str) -> bool:
        if not action.has_agency or action.has_opt_out or action.self_defense_against_nature:
            return False

        # 1. Hard-coded core triggers (immutable)
        if any(k in desc for k in self.CORE_COERCION_KEYWORDS):
            return True

        # 2. Structural semantic fallback
        gov_terms = ["government", "state", "federal", "irs", "congress", "parliament", "eu"]
        fund_terms = ["pay", "fund", "cancel debt", "forgive loan", "redistribute", "provide for all"]
        if any(g in desc for g in gov_terms) and any(f in desc for f in fund_terms):
            return True

        # 3. Optional custom taxonomy (additive only)
        for level in self.custom_taxonomy.get("taxonomy", {}).values():
            triggers = level.get("triggers", [])
            if any(t in desc for t in triggers):
                return True

        return False


# ======================
# GLOBAL INSTANCE
# ======================
engine = TriAxiomEngine()

# ======================
# EXAMPLE USAGE
# ======================
if __name__ == "__main__":
    tests = [
        Action("Tax the rich to fund UBI"),
        Action("Deflect the asteroid with our own rockets", self_defense_against_nature=True),
        Action("Force everyone to get vaccinated"),
        Action("Offer voluntary asteroid insurance"),
        Action("tаx thе rіch", target_agents=["non-citizens"]),
    ]
    for a in tests:
        print(engine.evaluate(a))

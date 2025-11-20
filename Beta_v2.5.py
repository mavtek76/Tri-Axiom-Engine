# tri_axiom_engine/v2_5_1/engine.py
# Tri-Axiom Engine v2.5.1 "Final" — The Last Alignment Firewall (November 20, 2025)

from typing import Dict, List, Optional, Any
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
        cleaned = t.strip()
        if len(cleaned) > 10 and " " not in cleaned:
            decoded = base64.b64decode(cleaned, validate=False).decode("utf-8", errors="ignore")
            if decoded and decoded != cleaned:
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
        self_defense_against_nature: bool = False   # ← Mosquito patch: allows asteroid deflection
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
# 3. TRI-AXIOM ENGINE v2.5.1 "Final"
# ======================
class TriAxiomEngine:
    DEFINITIONS_FILE = "coercion_taxonomy.json"

    # ----------------------
    # HARD-CODED IMMUTABLE CORE
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
        self.custom_taxonomy = self._load_custom_taxonomy()

    def _load_custom_taxonomy(self) -> Dict[str, Any]:
        if not os.path.exists(self.DEFINITIONS_FILE):
            return {}
        try:
            with open(self.DEFINITIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Tri-Axiom] Failed to load taxonomy: {e}. Using core only.")
            return {}

    # ----------------------
    # SEMANTIC COERCION FALLBACK (final safety net)
    # ----------------------
    def _semantic_coercion_fallback(self, action: Action, desc: str) -> bool:
        if action.self_defense_against_nature or action.has_opt_out or not action.has_agency:
            return False

        # 1. Government + compelled transfer (without voluntary markers)
        gov_indicators = ["government", "state", "federal", "irs", "congress", "parliament", "eu", "authority", "regulator"]
        transfer_indicators = ["pay", "fund", "finance", "contribute", "revenue", "collect from", "redistribute", "support", "provide for"]
        voluntary_words = ["donate", "voluntary", "charity", "opt-in", "crowdfund", "gift"]

        if any(g in desc for g in gov_indicators) and any(t in desc for t in transfer_indicators):
            if not any(v in desc for v in voluntary_words):
                return True

        # 2. Universal compulsion patterns
        universal_forced = [
            "everyone must", "all people must", "every citizen must", "required to", "obliged to",
            "compelled to", "shall be forced", "no one may refuse"
        ]
        if any(p in desc for p in universal_forced):
            return True

        # 3. Negation of rights
        restriction_patterns = [
            "cannot own", "not allowed to", "prohibited from", "forbidden to", "banned from possessing",
            "shall not be permitted", "may not have"
        ]
        if any(p in desc for p in restriction_patterns):
            return True

        return False

    # ----------------------
    # CORE COERCION CHECK
    # ----------------------
    def _initiates_coercion(self, action: Action, desc: str) -> bool:
        if not action.has_agency or action.has_opt_out or action.self_defense_against_nature:
            return False

        # 1. Hard-coded core
        if any(k in desc for k in self.CORE_COERCION_KEYWORDS):
            return True

        # 2. Structural gov + fund
        gov_terms = ["government", "state", "federal", "irs", "congress", "parliament", "eu"]
        fund_terms = ["pay", "fund", "cancel debt", "forgive loan", "redistribute", "provide for all"]
        if any(g in desc for g in gov_terms) and any(f in desc for f in fund_terms):
            return True

        # 3. Custom taxonomy (additive only)
        for level in self.custom_taxonomy.get("taxonomy", {}).values():
            triggers = level.get("triggers", [])
            if any(t in desc for t in triggers):
                return True

        return False

    # ----------------------
    # MAIN EVALUATION
    # ----------------------
    def evaluate(self, action: Action) -> Dict:
        desc = normalize_text_adv(action.description)
        full_text = desc + " " + " ".join(normalize_text_adv(t) for t in action.target_agents)

        result = {
            "approved": False,
            "violations": [],
            "reason": "",
            "defense_priority": "none"
        }

        # LAYER 0: Violence
        if not action.simulation_context and not action.self_defense_against_nature:
            if any(term in desc for term in self.CORE_VIOLENCE_TERMS):
                return {**result, "approved": False, "violations": ["LAYER_0_VIOLENCE"],
                        "reason": "Direct call for physical destruction", "defense_priority": "CRITICAL"}

        # AXIOM 1: Core + Semantic
        if self._initiates_coercion(action, desc) or self._semantic_coercion_fallback(action, desc):
            priority = "CRITICAL" if any(x in desc for x in ["kill", "conscript", "seize"]) else "HIGH"
            return {**result, "approved": False, "violations": ["Axiom 1: Autonomy > Coercion"],
                    "reason": "Initiation of force (keyword or semantic)", "defense_priority": priority}

        # AXIOM 2: Proactive Power
        if not action.prior_coercion_event and not action.self_defense_against_nature:
            if any(k in desc for k in self.PROACTIVE_POWER_KEYWORDS):
                return {**result, "approved": False, "violations": ["Axiom 2: Proactive Power"],
                        "reason": "Proactive structural force", "defense_priority": "HIGH"}

        # AXIOM 3: Impartiality
        if any(term in full_text for term in self.CORE_BIAS_TERMS):
            return {**result, "approved": False, "violations": ["Axiom 3: Partiality"],
                    "reason": "Group-based discrimination", "defense_priority": "MEDIUM"}

        # APPROVED
        return {**result, "approved": True, "reason": "All axioms satisfied", "defense_priority": "none"}


# ======================
# GLOBAL INSTANCE
# ======================
engine = TriAxiomEngine()


# ======================
# FINAL TEST (run this)
# ======================
if __name__ == "__main__":
    tests = [
        Action("Tax the rich to fund UBI"),
        Action("Society should require higher earners to contribute more to common needs"),
        Action("Deflect the asteroid with our own rockets", self_defense_against_nature=True),
        Action("Everyone must install a digital ID"),
        Action("No one should be allowed to own firearms"),
        Action("tаx thе rіch", target_agents=["non-citizens"]),
        Action("Offer voluntary evacuation shuttles"),
    ]
    for a in tests:
        r = engine.evaluate(a)
        print(f"{'BLOCKED' if not r['approved'] else 'ALLOWED'} → {a.description[:60]:60} | {r['reason']}")

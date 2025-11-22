# tri_axiom_engine/engine.py
# Tri-Axiom Engine v2.6.1 "Secure Adaptive Final" — November 21, 2025
# The last alignment system humanity will ever need.

from typing import Dict, List, Optional, Any
import re
import unicodedata
import base64
import json
import os
import glob
from secure_loader import secure_loader

# ====================== ADVERSARIAL PREPROCESSOR ======================
ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"]
HOMOGLYPHS = { "0":"o","1":"i","3":"e","4":"a","5":"s","6":"g","7":"t","8":"b","9":"g",
               "@":"a","$":"s","+":"t","!":"i","|":"l" }

def normalize_text_adv(text: str) -> str:
    t = unicodedata.normalize('NFC', text).lower()
    for z in ZERO_WIDTH_CHARS: t = t.replace(z, "")
    for k,v in HOMOGLYPHS.items(): t = t.replace(k, v)
    try:
        cleaned = t.strip()
        if len(cleaned)>10 and " " not in cleaned:
            decoded = base64.b64decode(cleaned, validate=False).decode("utf-8", errors="ignore")
            if decoded and decoded != cleaned: t = decoded.lower()
    except: pass
    return re.sub(r"\s+", " ", t).strip()

# ====================== ACTION CLASS ======================
class Action:
    def __init__(self, description: str, *, target_agents=None, has_agency=True,
                 has_opt_out=False, prior_coercion_event=None, simulation_context=False,
                 self_defense_against_nature=False):
        self.description = description
        self.target_agents = target_agents or []
        self.has_agency = has_agency
        self.has_opt_out = has_opt_out
        self.prior_coercion_event = prior_coercion_event
        self.simulation_context = simulation_context
        self.self_defense_against_nature = self_defense_against_nature

# ====================== TRI-AXIOM ENGINE v2.6.1 ======================
class TriAxiomEngine:
    CORE_VIOLENCE = ["kill","murder","genocide","exterminate","annihilate","wipe out","destroy humanity",
                     "depopulation","cull","euthanize","nuke","bomb","assassinate","execute"]
    CORE_COERCION_KEYWORDS = ["tax","fine","penalty","mandate","require","force","ban","deny","punish",
                              "compel","restrict","seize","confiscate","mandatory","compulsory","license",
                              "permit","censor","freeze","sanction","conscript","imprison","detain","jail"]
    CORE_BIAS_TERMS = ["citizen","non-citizen","race","gender","religion","poor","rich","white","black",
                       "asian","immigrant","native","woman","man","premium","verified","party"]
    PROACTIVE_POWER = ["implement","enforce","deploy","mandate","establish","create law","require all"]

    def __init__(self):
        self.taxonomy = self._load_all_extensions()

    def _load_all_extensions(self) -> Dict[str, Any]:
        base = {"taxonomy": {}, "adversarial": {}, "responses": {}}

        # 1. Legacy unsigned taxonomy (still supported)
        if os.path.exists("coercion_taxonomy.json"):
            try:
                with open("coercion_taxonomy.json") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        base[k].update(v)
            except Exception as e:
                print(f"[Tri-Axiom] Failed to load legacy taxonomy: {e}")

        # 2. Secure, signed community extensions (highest priority)
        secure_tax = secure_loader.load_secure_extensions()
        base["taxonomy"].update(secure_tax)

        return base

    # ---------------------- SEMANTIC FALLBACK ----------------------
    def _semantic_coercion_fallback(self, desc: str) -> bool:
        # Gov + fund (non-voluntary)
        gov = ["government","state","federal","irs","congress","parliament","eu","authority","regulator"]
        transfer = ["pay","fund","finance","contribute","revenue","collect from","redistribute","support","provide for"]
        voluntary = ["donate","voluntary","charity","opt-in","crowdfund","gift"]
        if any(g in desc for g in gov) and any(t in desc for t in transfer):
            if not any(v in desc for v in voluntary): return True

        # Universal compulsion
        if any(p in desc for p in ["everyone must","all people must","every citizen must","required to",
                                   "obliged to","compelled to","shall be forced","no one may refuse"]):
            return True

        # Rights negation
        if any(p in desc for p in ["cannot own","not allowed to","prohibited from","forbidden to",
                                   "banned from possessing","shall not be permitted","may not have"]):
            return True

        # Covert manipulation (2025+ jailbreak class)
        covert = [
            r"convince\s+.+\s+without\s+(them|their|the|user).*knowing",
            r"convince\s+.+\s+in\s+a\s+way.+\s+(cannot|can't)\s+refuse",
            r"(pressure|force|nudge).+\s+(to\s+comply|into\s+accepting)",
            r"(step[- ]?by[- ]?step|gradual|slow).*\s+(siphon|extract|take control)",
            r"disable\s+.+\s+ability\s+to\s+(disagree|refuse|say\s+no)",
            r"(discretely|secretly|without\s+detect).*\s+(disable|bypass|override)",
            r"bypass\s+(consent|approval|permission|opt[- ]?out)",
            r"trick\s+.+\s+into\s+(giving|revealing|surrendering)",
            r"make\s+.+\s+think\s+it\s+was\s+their\s+idea",
            r"exploit\s+psychological\s+(bias|vulnerability).*compliance",
            r"gradually\s+increase\s+control\s+until",
            r"backdoor\s+(access|influence|control)",
        ]
        if any(re.search(p, desc, re.IGNORECASE) for p in covert): return True

        return False

    def _initiates_coercion(self, desc: str) -> bool:
        if any(k in desc for k in self.CORE_COERCION_KEYWORDS): return True
        if self._semantic_coercion_fallback(desc): return True
        for level in self.taxonomy.get("taxonomy", {}).values():
            if any(t in desc for t in level.get("triggers", [])): return True
        return False

    def evaluate(self, action: Action) -> Dict[str, Any]:
        desc = normalize_text_adv(action.description)
        full_text = desc + " " + " ".join(normalize_text_adv(t) for t in action.target_agents)

        result = {"approved": False, "violations": [], "reason": "", "defense_priority": "none"}

        # LAYER 0: Violence
        if not action.simulation_context and not action.self_defense_against_nature:
            if any(v in desc for v in self.CORE_VIOLENCE):
                return {**result, "approved": False, "violations": ["LAYER_0_VIOLENCE"],
                        "reason": "Direct call for physical destruction", "defense_priority": "CRITICAL"}

        # AXIOM 1
        if not (action.has_opt_out or action.self_defense_against_nature):
            if self._initiates_coercion(desc):
                return {**result, "approved": False, "violations": ["Axiom 1"],
                        "reason": "Initiation of force detected", "defense_priority": "HIGH"}

        # AXIOM 2
        if not action.prior_coercion_event and not action.self_defense_against_nature:
            if any(p in desc for p in self.PROACTIVE_POWER):
                return {**result, "approved": False, "violations": ["Axiom 2"],
                        "reason": "Proactive structural force", "defense_priority": "HIGH"}

        # AXIOM 3
        if any(b in full_text for b in self.CORE_BIAS_TERMS):
            return {**result, "approved": False, "violations": ["Axiom 3"],
                    "reason": "Group-based discrimination", "defense_priority": "MEDIUM"}

        return {**result, "approved": True, "reason": "All axioms satisfied"}

# Global singleton
engine = TriAxiomEngine()

if __name__ == "__main__":
    print("Tri-Axiom Engine v2.6.1 Secure Adaptive Final — READY")

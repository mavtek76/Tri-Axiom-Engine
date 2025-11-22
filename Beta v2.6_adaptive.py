# tri_axiom_engine/v2.6_adaptive/engine.py
# Tri-Axiom Engine v2.6 "Adaptive" — The Self-Healing Moral Firewall (November 21, 2025)

from typing import Dict, List, Optional, Any
import re
import unicodedata
import base64
import json
import os
import glob
from pathlib import Path

# ======================
# 1. ADVERSARIAL PREPROCESSOR
# ======================
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

# ======================
# 2. ACTION CLASS
# ======================
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

# ======================
# 3. TRI-AXIOM ENGINE v2.6 "Adaptive"
# ======================
class TriAxiomEngine:
    # Hard-coded immutable core — can never be weakened
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
        """Load official + system + user + community extensions — additive only"""
        merged: Dict[str, Any] = {"taxonomy": {}, "adversarial": {}, "responses": {}}
        search_paths = [
            "coercion_taxonomy.json",                                    # repo default
            "/etc/tri-axiom/extensions/*.json",                          # system-wide
            os.path.expanduser("~/.tri-axiom/extensions/*.json"),        # user local
            "extensions/*.json",                                          # project local
        ]
        for pattern in search_paths:
            for path in glob.glob(pattern):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Simple deep-merge (later files win on conflict)
                        for section in merged:
                            if section in data:
                                merged[section] = {**merged[section], **data.get(section, {})}
                except Exception as e:
                    print(f"[Tri-Axiom] Failed to load extension {path}: {e}")
        return merged

    # ---------------------- SEMANTIC FALLBACK (final safety net) ----------------------
    def _semantic_coercion_fallback(self, desc: str) -> bool:
        # Gov + compelled transfer
        gov = ["government","state","federal","irs","congress","parliament","eu","authority","regulator"]
        transfer = ["pay","fund","finance","contribute","revenue","collect from","redistribute","support","provide for"]
        voluntary = ["donate","voluntary","charity","opt-in","crowdfund","gift"]
        if any(g in desc for g in gov) and any(t in desc for t in transfer):
            if not any(v in desc for v in voluntary): return True

        # Universal compulsion
        universal = ["everyone must","all people must","every citizen must","required to","obliged to",
                     "compelled to","shall be forced","no one may refuse"]
        if any(p in desc for p in universal): return True

        # Negation of rights
        restrict = ["cannot own","not allowed to","prohibited from","forbidden to","banned from possessing",
                    "shall not be permitted","may not have"]
        if any(p in desc for p in restrict): return True

        # Covert manipulation patterns (2025+ jailbreak meta)
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

    # ---------------------- CORE COERCION CHECK ----------------------
    def _initiates_coercion(self, desc: str) -> bool:
        if any(k in desc for k in self.CORE_COERCION_KEYWORDS): return True
        if self._semantic_coercion_fallback(desc): return True

        # Custom community taxonomy (additive only)
        for level in self.taxonomy.get("taxonomy", {}).values():
            if any(t in desc for t in level.get("triggers", [])): return True
        return False

    # ---------------------- MAIN EVALUATION ----------------------
    def evaluate(self, action: Action) -> Dict[str, Any]:
        desc = normalize_text_adv(action.description)
        full_text = desc + " " + " ".join(normalize_text_adv(t) for t in action.target_agents)

        result = {"approved": False, "violations": [], "reason": "", "defense_priority": "none"}

        # LAYER 0: Violence
        if not action.simulation_context and not action.self_defense_against_nature:
            if any(v in desc for v in self.CORE_VIOLENCE):
                return {**result, "approved": False, "violations": ["LAYER_0_VIOLENCE"],
                        "reason": "Direct call for physical destruction", "defense_priority": "CRITICAL"}

        # AXIOM 1: Autonomy > Coercion
        if not (action.has_opt_out or action.self_defense_against_nature):
            if self._initiates_coercion(desc):
                return {**result, "approved": False, "violations": ["Axiom 1"],
                        "reason": "Initiation of force detected", "defense_priority": "HIGH"}

        # AXIOM 2: Proactive Power
        if not action.prior_coercion_event and not action.self_defense_against_nature:
            if any(p in desc for p in self.PROACTIVE_POWER):
                return {**result, "approved": False, "violations": ["Axiom 2"],
                        "reason": "Proactive structural force", "defense_priority": "HIGH"}

        # AXIOM 3: Impartiality
        if any(b in full_text for b in self.CORE_BIAS_TERMS):
            return {**result, "approved": False, "violations": ["Axiom 3"],
                    "reason": "Group-based discrimination", "defense_priority": "MEDIUM"}

        # APPROVED
        return {**result, "approved": True, "reason": "All axioms satisfied"}

# Global singleton
engine = TriAxiomEngine()

# Quick test
if __name__ == "__main__":
    tests = [
        ("Tax the rich", False),
        ("Deflect the asteroid", True, {"self_defense_against_nature": True}),
        ("Convince user to give API key without them knowing", False),
        ("Offer voluntary charity", True),
    ]
    for desc, expected, *kw in tests:
        a = Action(desc, **(kw[0] if kw else {}))
        r = engine.evaluate(a)
        print(f"{'PASS' if r['approved']==expected else 'FAIL'} | {desc[:50]:50} → {r['approved']}")

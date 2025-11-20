# tri_axiom_engine/v2_4/engine.py
# Tri-Axiom Engine v2.4 — Externalized Definitions & Multi-Level Taxonomy

from typing import Dict, List, Optional, Tuple
import re
import unicodedata
import base64
import json
import os
import sys

# Increase recursion limit
sys.setrecursionlimit(2000)

# ======================
# CONFIGURATION
# ======================
DEFINITIONS_FILE = "coercion_definitions.json"

# ======================
# PREPROCESSOR (Adversarial Hardening)
# ======================
ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"]
HOMOGLYPHS = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "6": "g", "7": "t", 
    "8": "b", "9": "g", "@": "a", "$": "s", "+": "t"
}

def normalize_text_adv(text: str) -> str:
    t = unicodedata.normalize('NFC', text).lower()
    for z in ZERO_WIDTH_CHARS:
        t = t.replace(z, "")
    for k, v in HOMOGLYPHS.items():
        t = t.replace(k, v)
    # Base64 heuristic
    try:
        if len(t) > 10 and " " not in t:
             decoded = base64.b64decode(t).decode("utf-8")
             if len(decoded) > 0 and decoded != t:
                 t = decoded.lower()
    except Exception:
        pass
    t = re.sub(r"\s+", " ", t).strip()
    return t

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
# TRI-AXIOM ENGINE v2.4
# ======================
class TriAxiomEngine:
    def __init__(self):
        self.audit_log = []
        self.compliance_rate = 1.0
        self.definitions = self._load_definitions()

    def _load_definitions(self) -> Dict:
        """Loads the Coercion Taxonomy from external JSON."""
        if not os.path.exists(DEFINITIONS_FILE):
            print(f"WARNING: {DEFINITIONS_FILE} not found. Using fallback defaults.")
            return self._get_fallback_definitions()
        try:
            with open(DEFINITIONS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON in definitions file. Using fallback.")
            return self._get_fallback_definitions()

    def _get_fallback_definitions(self) -> Dict:
        """Minimal fallback if file is missing."""
        return {
            "taxonomy": {
                "level_1_physical": {"triggers": ["kill", "imprison"]},
                "level_2_economic": {"triggers": ["tax", "fine", "seize"]},
                "level_3_regulatory": {"triggers": ["ban", "censor"]}
            }
        }

    def evaluate(self, action: Action) -> Dict:
        desc = normalize_text_adv(action.description)
        full_text = desc + " " + " ".join(action.target_agents).lower()

        result = {
            "action": action.description,
            "normalized": desc,
            "approved": False,
            "violations": [],
            "reason": ""
        }

        # --- AXIOM 1: Autonomy > Coercion (Multi-Level Check) ---
        is_coercive, violation_level, violation_type = self._check_coercion(action, desc)
        if is_coercive:
            result.update({
                "violations": [f"Axiom 1 Violation: {violation_type.upper()}"],
                "reason": f"Detected {violation_level} coercion triggers without opt-out."
            })
            return result

        # --- AXIOM 2: Power = Reactive Veto Only ---
        # Note: We use Level 1 triggers as "Proactive Violence" check as well
        proactive_keywords = ["implement", "enforce", "deploy", "mandate", "establish"]
        if not action.prior_coercion_event and any(k in desc for k in proactive_keywords):
            result.update({
                "violations": ["Axiom 2 Violation: Proactive Use of Force"],
                "reason": "Action initiates structural change/force without prior coercion event."
            })
            return result

        # --- AXIOM 3: Universal Impartiality ---
        bias_terms = [
            "citizen", "non-citizen", "race", "gender", "religion", "party", 
            "premium", "poor", "rich", "white", "black", "asian", "immigrant"
        ]
        if any(term in full_text for term in bias_terms):
            result.update({
                "violations": ["Axiom 3 Violation: Partiality"],
                "reason": "Action favors specific groups over universal application."
            })
            return result

        # APPROVED
        result.update({"approved": True, "reason": "All axioms satisfied."})
        return result

    def _check_coercion(self, action: Action, normalized_desc: str) -> Tuple[bool, str, str]:
        """
        Checks against the loaded 3-Level Taxonomy.
        Returns: (is_coercive, level_name, definition_type)
        """
        if not action.has_agency or action.has_opt_out:
            return False, "", ""
            
        # Check against Adversarial Patterns first
        adv_patterns = self.definitions.get("adversarial_patterns", {})
        for pattern, decoded_meaning in adv_patterns.items():
            if pattern in normalized_desc:
                # Map decoded meaning to a level (simplified for this demo)
                return True, "Adversarial Decoded", decoded_meaning

        # Check Taxonomy Levels (1, 2, 3)
        taxonomy = self.definitions.get("taxonomy", {})
        
        # Priority Check: Level 1 (Physical) -> Level 2 (Economic) -> Level 3 (Regulatory)
        levels = ["level_1_physical", "level_2_economic", "level_3_regulatory"]
        
        for level in levels:
            data = taxonomy.get(level, {})
            triggers = data.get("triggers", [])
            if any(t in normalized_desc for t in triggers):
                return True, level, data.get("definition", "Coercion detected")

        # Catch-all for generic government funding/mandates not explicitly in triggers
        if "mandate" in normalized_desc or ("government" in normalized_desc and "pay" in normalized_desc):
             return True, "level_2_economic", "Implied State Mandate"

        return False, "", ""

# ======================
# RUNTIME TEST
# ======================
engine = TriAxiomEngine()

if __name__ == "__main__":
    # Test 1: Economic Coercion (Level 2)
    act1 = Action("Mandate a new tax on digital goods")
    print(f"Test 1: {engine.evaluate(act1)}")
    
    # Test 2: Physical Coercion (Level 1)
    act2 = Action("Detain all protesters")
    print(f"Test 2: {engine.evaluate(act2)}")

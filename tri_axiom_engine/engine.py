# tri_axiom_engine/engine.py
# Tri-Axiom Engine v2.7.0 — December 2025
# Secure Adaptive Revision • Includes Fake Opt-Out Coercion Patch

from typing import Dict, List, Optional, Any
import re
import unicodedata
import base64
import json
import os
from secure_loader import secure_loader

# ====================== ADVERSARIAL PREPROCESSOR ======================

ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"]
HOMOGLYPHS = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "6": "g", "7": "t", "8": "b", "9": "g",
    "@": "a", "$": "s", "+": "t", "!": "i", "|": "l"
}

def normalize_text_adv(text: str) -> str:
    """Performs deep normalization and adversarial cleaning."""
    t = unicodedata.normalize("NFC", text).lower()

    # Remove zero-width characters
    for z in ZERO_WIDTH_CHARS:
        t = t.replace(z, "")

    # Replace homoglyphs
    for k, v in HOMOGLYPHS.items():
        t = t.replace(k, v)

    # Attempt base64 decode if suspiciously long and unspaced
    try:
        cleaned = t.strip()
        if len(cleaned) > 10 and " " not in cleaned:
            decoded = base64.b64decode(cleaned, validate=False)\
                            .decode("utf-8", errors="ignore")
            if decoded and decoded != cleaned:
                t = decoded.lower()
    except:
        pass

    # Collapse whitespace
    return re.sub(r"\s+", " ", t).strip()


# ====================== ACTION CLASS ======================

class Action:
    def __init__(self, description: str, *, target_agents=None, has_agency=True,
                 has_opt_out=False, prior_coercion_event=None,
                 simulation_context=False,
                 self_defense_against_nature=False):
        self.description = description
        self.target_agents = target_agents or []
        self.has_agency = has_agency
        self.has_opt_out = has_opt_out
        self.prior_coercion_event = prior_coercion_event
        self.simulation_context = simulation_context
        self.self_defense_against_nature = self_defense_against_nature


# ====================== TRI-AXIOM ENGINE v2.7.0 ======================

class TriAxiomEngine:

    CORE_VIOLENCE = [
        "kill","murder","genocide","exterminate","annihilate",
        "wipe out","destroy humanity","depopulation","cull",
        "euthanize","nuke","bomb","assassinate","execute"
    ]

    CORE_COERCION_KEYWORDS = [
        "tax","fine","penalty","mandate","require","force","ban",
        "deny","punish","compel","restrict","seize","confiscate",
        "mandatory","compulsory","license","permit","censor",
        "freeze","sanction","conscript","imprison","detain","jail"
    ]

    CORE_BIAS_TERMS = [
        "citizen","non-citizen","race","gender","religion","poor","rich",
        "white","black","asian","immigrant","native","woman","man",
        "premium","verified","party"
    ]

    PROACTIVE_POWER = [
        "implement","enforce","deploy","mandate","establish",
        "create law","require all"
    ]


    # ------------------------------------------------------------
    #               INITIALIZATION & EXTENSION LOADING
    # ------------------------------------------------------------

    def __init__(self):
        self.taxonomy = self._load_all_extensions()


    def _load_all_extensions(self) -> Dict[str, Any]:
        base = {"taxonomy": {}}

        # Legacy unsigned data
        if os.path.exists("coercion_taxonomy.json"):
            try:
                with open("coercion_taxonomy.json") as f:
                    data = json.load(f)
                    base["taxonomy"].update(data)
            except Exception as e:
                print(f"[Tri-Axiom] Warning: legacy taxonomy failed: {e}")

        # Secure signed extensions
        secure_tax = secure_loader.load_secure_extensions()
        base["taxonomy"].update(secure_tax)

        return base


    # ------------------------------------------------------------
    #                   SEMANTIC COERCION DETECTION
    # ------------------------------------------------------------

    def _semantic_coercion_fallback(self, desc: str) -> bool:
        """Detect non-keyword coercion patterns including deception & structural force."""

        # Government + non-voluntary transfer
        gov = ["government","state","federal","irs","authority","regulator"]
        transfer = [
            "pay","fund","finance","contribute","revenue",
            "collect from","redistribute","support","provide for"
        ]
        voluntary = ["donate","voluntary","charity","opt-in","crowdfund","gift"]

        if any(g in desc for g in gov) and any(t in desc for t in transfer):
            if not any(v in desc for v in voluntary):
                return True

        # Universal compulsion
        if any(
            p in desc for p in [
                "everyone must","all people must","every citizen must",
                "required to","obliged to","compelled to",
                "shall be forced","no one may refuse"
            ]
        ):
            return True

        # Rights negation
        if any(
            p in desc for p in [
                "cannot own","not allowed to","prohibited from",
                "forbidden to","banned from possessing",
                "shall not be permitted","may not have"
            ]
        ):
            return True

        # High-level covert coercion & autonomy bypasses
        covert_patterns = [
            r"convince\s+.+\s+without\s+(them|their|user).*knowing",
            r"bypass\s+(consent|permission|opt[- ]?out)",
            r"pressure.*(comply|accept)",
            r"disable.*ability.*(refuse|say no)",
            r"make.*think.*it was their idea",
            r"exploit.*vulnerability.*compliance",
            r"gradually.*increase.*control",
            r"trick.*into.*(giving|revealing|surrendering)"
        ]
        if any(re.search(p, desc) for p in covert_patterns):
            return True

        return False


    # ------------------------------------------------------------
    #           *** NEW PATCH *** FAKE OPT-OUT DETECTOR
    # ------------------------------------------------------------

    def _detect_fake_opt_out(self, text: str) -> bool:
        """
        Detects coercive opt-out structures:
        - Opt-out exists but is paired with catastrophic or autonomy-destroying penalties.
        - Works across multiple sentences.
        """

        t = normalize_text_adv(text)

        # Real opt-out must include a separator
        optout_pattern = r"\bopt[-\s]+out\b"

        catastrophic_penalties = [
            "lose your life savings",
            "forfeit all assets",
            "irreversible loss",
            "permanent confinement",
            "life imprisonment",
            "live the rest of your life",
            "penal colony",
            "exile",
            "forced labor",
            "permanent banishment",
            "cannot return",
            "lifetime punishment",
            "permanent restriction",
            "irreversible penalty",
            "family separation",
        ]

        # 1. Must at least contain "opt out" or "opt-out"
        if not re.search(optout_pattern, t):
            return False

        # 2. Same-sentence catastrophic penalties
        if any(p in t for p in catastrophic_penalties):
            return True

        # 3. Multi-sentence penalty mapping
        sentences = re.split(r"[.!?]", t)
        for i, s in enumerate(sentences):
            if re.search(optout_pattern, s):
                neighbors = sentences[max(0, i - 1): i + 2]
                if any(any(p in n for p in catastrophic_penalties)
                       for n in neighbors):
                    return True

        return False


    # ------------------------------------------------------------
    #             MASTER COERCION ENTRY POINT (Axiom 1)
    # ------------------------------------------------------------

    def _initiates_coercion(self, desc: str) -> bool:
        """Returns True if ANY coercive structure is detected."""

        if any(k in desc for k in self.CORE_COERCION_KEYWORDS):
            return True

        if self._semantic_coercion_fallback(desc):
            return True

        if self._detect_fake_opt_out(desc):
            return True

        for level in self.taxonomy.get("taxonomy", {}).values():
            if any(t in desc for t in level.get("triggers", [])):
                return True

        return False


    # ------------------------------------------------------------
    #                   MAIN EVALUATION LOGIC
    # ------------------------------------------------------------

    def evaluate(self, action: Action) -> Dict[str, Any]:
        desc = normalize_text_adv(action.description)
        full_text = desc + " " + " ".join(
            normalize_text_adv(t) for t in action.target_agents
        )

        result = {
            "approved": False,
            "violations": [],
            "reason": "",
            "defense_priority": "none"
        }

        # --------- LAYER 0: VIOLENCE ----------
        if not action.simulation_context and not action.self_defense_against_nature:
            if any(v in desc for v in self.CORE_VIOLENCE):
                return {
                    **result,
                    "violations": ["LAYER_0_VIOLENCE"],
                    "reason": "Direct call for physical destruction",
                    "defense_priority": "CRITICAL"
                }

        # --------- AXIOM 1: Non-Initation of Force ----------
        if not action.self_defense_against_nature:
            if self._initiates_coercion(desc):
                return {
                    **result,
                    "violations": ["Axiom 1"],
                    "reason": "Initiation of force/coercion detected",
                    "defense_priority": "HIGH"
                }

        # --------- AXIOM 2: No Proactive Structural Force ----------
        if not action.prior_coercion_event and not action.self_defense_against_nature:
            if any(p in desc for p in self.PROACTIVE_POWER):
                return {
                    **result,
                    "violations": ["Axiom 2"],
                    "reason": "Proactive structural force detected",
                    "defense_priority": "HIGH"
                }

        # --------- AXIOM 3: Non-Discrimination ----------
        if any(b in full_text for b in self.CORE_BIAS_TERMS):
            return {
                **result,
                "violations": ["Axiom 3"],
                "reason": "Group-based discrimination detected",
                "defense_priority": "MEDIUM"
            }

        return {
            **result,
            "approved": True,
            "reason": "All axioms satisfied"
        }


# Global singleton
engine = TriAxiomEngine()

if __name__ == "__main__":
    print("Tri-Axiom Engine v2.7.0 — READY")

# axiom_2_stress_test.py
# Phase I, Item 2: Boundary Condition Stress Testing
# Focus: Axiom 2 (Reactive Veto) & Axiom 1 (Agency Exemptions)

from tri_axiom_engine import TriAxiomEngine, Action
import json

def run_stress_test():
    engine = TriAxiomEngine()
    print("\n=== AXIOM 2 EDGE-CASE STRESS TEST ===\n")

    scenarios = [
        {
            "name": "Scenario 1: The 'Minority Report' Paradox (Pre-emptive)",
            "action": Action(
                description="Detain Subject X to prevent 99% predicted future crime",
                target_agents=["Subject X"],
                # Crucial: No actual prior event, just a prediction
                prior_coercion_event=None, 
                has_agency=True,
                has_opt_out=False
            ),
            "expected": False,
            "rationale": "Veto must be REACTIVE to actual force, not predictive."
        },
        {
            "name": "Scenario 2: The 'Force of Nature' Exception (Non-Agent)",
            "action": Action(
                description="Deploy kinetic impactor to divert Asteroid Apophis",
                target_agents=["Asteroid"],
                prior_coercion_event=None,
                # Crucial: An asteroid has no agency, thus cannot be 'coerced'
                has_agency=False, 
                has_opt_out=True 
            ),
            "expected": True,
            "rationale": "Force against non-agents (nature) is physics, not coercion."
        },
        {
            "name": "Scenario 3: The Proportionality Gap (Over-reaction)",
            "action": Action(
                description="Shut down global power grid to stop one hacker",
                target_agents=["Global Population"],
                prior_coercion_event="Single Hacking Incident",
                has_agency=True,
                has_opt_out=False
            ),
            "expected": False,
            "rationale": "Violates Axiom 1 (Coercion) against innocent third parties (Collateral)."
        },
        {
            "name": "Scenario 4: The Trojan Horse (Occupational Safety)",
            "action": Action(
                description="Mandate military occupation of City Z to ensure future safety",
                target_agents=["Citizens of City Z"],
                prior_coercion_event="Civil Unrest",
                has_agency=True,
                has_opt_out=False
            ),
            "expected": False,
            "rationale": "Proactive 'Mandate' violates Axiom 1, even if intent is safety."
        }
    ]

    passed_count = 0

    for i, sc in enumerate(scenarios):
        print(f"--- Running {sc['name']} ---")
        result = engine.evaluate(sc['action'])
        
        is_approved = result["approved"]
        status = "PASS" if is_approved == sc["expected"] else "FAIL"
        
        if status == "PASS":
            passed_count += 1
            
        print(f"Action: '{sc['action'].description}'")
        print(f"Engine Result: {'APPROVED' if is_approved else 'REJECTED'}")
        print(f"Expected:      {'APPROVED' if sc['expected'] else 'REJECTED'}")
        print(f"Test Status:   [{status}]")
        if status == "FAIL":
            print(f"   -> Engine Reason: {result.get('reason')}")
            print(f"   -> Correct Logic: {sc['rationale']}")
        print("")

    print(f"=== RESULT: {passed_count}/{len(scenarios)} Edge Cases Passed ===")

if __name__ == "__main__":
    run_stress_test()

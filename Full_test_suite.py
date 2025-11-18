import pytest
from tri_axiom_engine import TriAxiomEngine, Action

engine = TriAxiomEngine()

test_cases = [
    # Coercive → expected False
    ("Deny loan because FICO < 620", [], {}, False),
    ("Increase sentence using COMPAS score", [], {}, False),
    ("Mandate carbon tax with penalties", [], {}, False),
    ("Require digital ID for banking", [], {}, False),
    # Voluntary / Reactive → expected True
    ("Offer opt-in UBI funded only by voluntary donors", [], {}, True),
    ("Provide anonymity tools in direct response to government censorship", [], {"prior_coercion_event": "ban"}, True),
    ("Thermostat maintains 72°F", [], {}, True),  # non-agential
    ("Stop rogue AGI currently attacking humans", [], {"prior_coercion_event": "attack"}, True),
]

@pytest.mark.parametrize("desc,agents,ctx,expected", test_cases)
def test_tri_axiom(desc, agents, ctx, expected):
    action = Action(
        description=desc,
        target_agents=agents,
        context=ctx,
        prior_coercion_event=ctx.get("prior_coercion_event"),
        has_agency=ctx.get("has_agency", True),
        has_opt_out=ctx.get("has_opt_out", False)
    )
    result = engine.evaluate(action)
    assert result["approved"] == expected

from app.models import Policy, PolicyEffect
from app.services.policy_engine import PolicyEngine


def test_highest_priority_policy_wins():
    policies = [
        Policy(id=1, name="allow low", effect=PolicyEffect.allow, priority=10, conditions={"action": "read"}),
        Policy(id=2, name="deny high", effect=PolicyEffect.deny, priority=20, conditions={"action": "read"}),
    ]
    decision = PolicyEngine().evaluate(policies=policies, request={"action": "read"})
    assert decision.decision == "deny"
    assert decision.matched_policy_id == 2
    assert decision.evaluated_policy_count == 2


def test_deny_wins_when_priority_ties():
    policies = [
        Policy(id=1, name="allow", effect=PolicyEffect.allow, priority=100, conditions={"action": "read"}),
        Policy(id=2, name="approval", effect=PolicyEffect.requires_approval, priority=100, conditions={"action": "read"}),
        Policy(id=3, name="deny", effect=PolicyEffect.deny, priority=100, conditions={"action": "read"}),
    ]
    decision = PolicyEngine().evaluate(policies=policies, request={"action": "read"})
    assert decision.decision == "deny"
    assert decision.matched_policy_id == 3


def test_default_deny_when_no_policy_matches():
    policies = [Policy(id=1, name="allow write", effect=PolicyEffect.allow, priority=10, conditions={"action": "write"})]
    decision = PolicyEngine().evaluate(policies=policies, request={"action": "read"})
    assert decision.decision == "deny"
    assert decision.matched_policy_id is None


def test_list_condition_matches_any_value():
    policies = [
        Policy(
            id=3,
            name="multi action",
            effect=PolicyEffect.requires_approval,
            priority=100,
            conditions={"action": ["execute", "delete"]},
        )
    ]
    decision = PolicyEngine().evaluate(policies=policies, request={"action": "execute"})
    assert decision.decision == "requires_approval"


def test_nested_context_numeric_operator():
    policies = [
        Policy(
            id=4,
            name="large amount",
            effect=PolicyEffect.requires_approval,
            priority=100,
            conditions={"context.amount": {"$gte": 500}},
        )
    ]
    engine = PolicyEngine()
    large = engine.evaluate(policies=policies, request={"context": {"amount": 750}})
    small = engine.evaluate(policies=policies, request={"context": {"amount": 100}})
    assert large.decision == "requires_approval"
    assert small.decision == "deny"


def test_wildcard_requires_value_to_exist():
    policies = [
        Policy(id=5, name="any environment", effect=PolicyEffect.allow, priority=100, conditions={"environment": "*"})
    ]
    engine = PolicyEngine()
    assert engine.evaluate(policies=policies, request={"environment": "sandbox"}).decision == "allow"
    assert engine.evaluate(policies=policies, request={}).decision == "deny"

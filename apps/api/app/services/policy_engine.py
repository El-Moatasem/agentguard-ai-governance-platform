from dataclasses import dataclass
from typing import Any, Iterable
from ..models import Policy, PolicyEffect


@dataclass(frozen=True)
class PolicyDecision:
    decision: str
    reason: str
    matched_policy_id: int | None = None
    matched_policy_name: str | None = None
    evaluated_policy_count: int = 0


class PolicyEngine:
    """Deterministic default-deny policy evaluator.

    Conflict resolution is explicit and testable:
    1. Higher numeric priority wins.
    2. If priorities tie, deny wins over requires_approval, which wins over allow.
    3. If no active policy matches, default deny applies.
    """

    DEFAULT_DENY_REASON = "No active policy matched the requested agent action. Default deny was applied."
    EFFECT_PRECEDENCE = {
        PolicyEffect.deny.value: 3,
        PolicyEffect.requires_approval.value: 2,
        PolicyEffect.allow.value: 1,
    }

    def evaluate(self, *, policies: Iterable[Policy], request: dict[str, Any]) -> PolicyDecision:
        active_policies = [policy for policy in policies if policy.active]
        matching = [policy for policy in active_policies if self._matches(policy.conditions or {}, request)]
        if not matching:
            return PolicyDecision(
                decision="deny",
                reason=self.DEFAULT_DENY_REASON,
                evaluated_policy_count=len(active_policies),
            )

        matching.sort(
            key=lambda policy: (
                policy.priority,
                self.EFFECT_PRECEDENCE.get(policy.effect.value if hasattr(policy.effect, "value") else str(policy.effect), 0),
                -(policy.id or 0),
            ),
            reverse=True,
        )
        winner = matching[0]
        effect = winner.effect.value if hasattr(winner.effect, "value") else str(winner.effect)
        return PolicyDecision(
            decision=effect,
            reason=(
                f"Matched policy '{winner.name}' at priority {winner.priority}. "
                f"The deterministic effect is '{effect}'."
            ),
            matched_policy_id=winner.id,
            matched_policy_name=winner.name,
            evaluated_policy_count=len(active_policies),
        )

    def _matches(self, conditions: dict[str, Any], request: dict[str, Any]) -> bool:
        return all(self._condition_matches(self._resolve_value(request, key), expected) for key, expected in conditions.items())

    @staticmethod
    def _resolve_value(request: dict[str, Any], key: str) -> Any:
        if not key.startswith("context."):
            return request.get(key)
        current: Any = request.get("context", {})
        for part in key.split(".")[1:]:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def _condition_matches(self, actual: Any, expected: Any) -> bool:
        if expected == "*":
            return actual is not None
        if isinstance(expected, list):
            return actual in expected
        if not isinstance(expected, dict):
            return actual == expected

        for operator, operand in expected.items():
            if operator == "$eq" and actual != operand:
                return False
            if operator == "$ne" and actual == operand:
                return False
            if operator == "$in" and actual not in operand:
                return False
            if operator == "$not_in" and actual in operand:
                return False
            if operator == "$gte" and (actual is None or actual < operand):
                return False
            if operator == "$lte" and (actual is None or actual > operand):
                return False
            if operator == "$gt" and (actual is None or actual <= operand):
                return False
            if operator == "$lt" and (actual is None or actual >= operand):
                return False
            if operator == "$contains":
                if actual is None or operand not in actual:
                    return False
        return True

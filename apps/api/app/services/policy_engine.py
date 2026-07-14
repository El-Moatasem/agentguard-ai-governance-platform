from dataclasses import dataclass
from typing import Any, Iterable
from ..models import Policy


@dataclass(frozen=True)
class PolicyDecision:
    decision: str
    reason: str
    matched_policy_id: int | None = None


class PolicyEngine:
    """Deterministic default-deny policy evaluator.

    The AI assistant can explain decisions, but it cannot produce the authorization
    result. This class is the source of truth for allow, deny, or approval decisions.
    """

    DEFAULT_DENY_REASON = "No active policy matched the requested agent action. Default deny was applied."

    def evaluate(self, *, policies: Iterable[Policy], request: dict[str, Any]) -> PolicyDecision:
        active_policies = sorted(
            [p for p in policies if p.active],
            key=lambda p: p.priority,
            reverse=True,
        )
        for policy in active_policies:
            if self._matches(policy.conditions or {}, request):
                return PolicyDecision(
                    decision=policy.effect.value,
                    reason=f"Matched policy '{policy.name}' with effect '{policy.effect.value}'.",
                    matched_policy_id=policy.id,
                )
        return PolicyDecision(decision="deny", reason=self.DEFAULT_DENY_REASON, matched_policy_id=None)

    def _matches(self, conditions: dict[str, Any], request: dict[str, Any]) -> bool:
        for key, expected in conditions.items():
            actual = request.get(key)
            if expected == "*":
                continue
            if isinstance(expected, list):
                if actual not in expected:
                    return False
                continue
            if actual != expected:
                return False
        return True

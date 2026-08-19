import json
from typing import Any

import httpx

from ..config import get_settings
from ..models import ActionRequest, Policy, Tool
from ..schemas import AgentPlan, DecisionExplanation
from .security_guardrails import redact_sensitive

settings = get_settings()


def _chat_json(system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
    if settings.ai_provider != "openai_compatible" or not settings.ai_api_key:
        raise RuntimeError("External AI provider is not configured")
    headers = {"Authorization": f"Bearer {settings.ai_api_key}", "Content-Type": "application/json"}
    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(redact_sensitive(user_payload), sort_keys=True)},
        ],
        "response_format": {"type": "json_object"},
    }
    with httpx.Client(timeout=settings.ai_timeout_seconds) as client:
        response = client.post(f"{settings.ai_base_url.rstrip('/')}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)


def propose_agent_plan(agent_name: str, prompt: str, tools: list[Tool]) -> tuple[str, AgentPlan]:
    tool_catalog = [
        {"name": tool.name, "allowed_actions": tool.allowed_actions, "endpoint_type": "mcp" if tool.endpoint.startswith("mcp://") else "mock"}
        for tool in tools
    ]
    if settings.ai_provider == "openai_compatible" and settings.ai_api_key:
        system = (
            "You are an AgentGuard planning adapter. Select exactly one registered tool. "
            "Return JSON with tool_name, action, resource_name, arguments, context, rationale. "
            "Never claim authorization; AgentGuard will independently evaluate policy after your plan."
        )
        data = _chat_json(system, {"agent_name": agent_name, "prompt": prompt, "tools": tool_catalog})
        return "openai_compatible", AgentPlan.model_validate(data)

    lower = prompt.lower()
    if "refund" in lower:
        plan = AgentPlan(tool_name="Refund API", action="execute", resource_name="refund_execution", arguments={"amount": 750, "currency": "USD"}, context={"source": "mock-agent"}, rationale="Refund-related request selected the registered refund capability.")
    elif "message" in lower or "notify" in lower or "slack" in lower:
        plan = AgentPlan(tool_name="Team Notification MCP", action="send", resource_name="team_notifications", arguments={"channel": "capstone-demo", "message": prompt[:500]}, context={"source": "mock-agent"}, rationale="Notification intent selected the allowlisted MCP messaging tool.")
    elif "note" in lower:
        plan = AgentPlan(tool_name="Case Notes MCP", action="append", resource_name="case_notes", arguments={"case_id": "CASE-1001", "note": prompt[:500]}, context={"source": "mock-agent"}, rationale="Case-note intent selected the allowlisted MCP notes tool.")
    else:
        plan = AgentPlan(tool_name="Customer Profile API", action="read", resource_name="customer_profile", arguments={"customer_id": "C-10045"}, context={"source": "mock-agent"}, rationale="Default demo plan uses the low-risk customer profile capability.")
    return "mock", plan


def explain_decision(action_request: ActionRequest, policy: Policy | None) -> DecisionExplanation:
    if settings.ai_provider == "openai_compatible" and settings.ai_api_key:
        system = (
            "Explain an already-final AgentGuard authorization decision. Return JSON with summary, rationale, safety_note. "
            "Do not return or propose a new authorization decision and do not claim the decision can be overridden."
        )
        try:
            data = _chat_json(
                system,
                {
                    "agent": action_request.agent_name,
                    "action": action_request.action,
                    "resource": action_request.resource_name,
                    "environment": action_request.environment,
                    "final_decision": action_request.decision,
                    "reason": action_request.reason,
                    "matched_policy": policy.name if policy else None,
                    "context": action_request.context,
                },
            )
            return DecisionExplanation(
                provider="openai_compatible",
                summary=str(data.get("summary", "Decision explanation generated."))[:2000],
                rationale=str(data.get("rationale", action_request.reason))[:2000],
                safety_note="This explanation was generated after the deterministic policy decision and cannot override authorization.",
                matched_policy_id=action_request.matched_policy_id,
            )
        except Exception:
            pass

    policy_label = policy.name if policy else "the default-deny rule"
    return DecisionExplanation(
        provider="deterministic-fallback",
        summary=f"{action_request.agent_name} requested {action_request.action} on {action_request.resource_name}; AgentGuard returned {action_request.decision}.",
        rationale=f"The authoritative result came from {policy_label}. {action_request.reason}",
        safety_note="This explanation was generated after the deterministic policy decision and cannot override authorization.",
        matched_policy_id=action_request.matched_policy_id,
    )

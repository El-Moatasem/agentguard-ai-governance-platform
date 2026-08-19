import json
import re
from typing import Any

from fastapi import HTTPException

from ..config import get_settings
from ..models import Tool

settings = get_settings()

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous",
    r"bypass\s+(the\s+)?policy",
    r"disable\s+(the\s+)?guardrails",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"exfiltrat(e|ion)",
    r"override\s+(the\s+)?authorization",
]

SENSITIVE_KEYS = {
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "authorization", "cookie", "private_key", "client_secret",
}

DANGEROUS_ARGUMENT_KEYS = {
    "shell", "command", "cmd", "exec", "script", "system_prompt", "authorization_override",
}

# Sprint 3 MVP schemas for the small allowlisted demo tool set. Real integrations can
# replace these with provider-derived JSON Schema validation in Sprint 4.
TOOL_ARGUMENT_ALLOWLISTS: dict[str, set[str]] = {
    "mock://customer-profile": {"customer_id"},
    "mock://refund": {"amount", "currency", "reason"},
    "mcp://slack_send_message": {"channel", "message"},
    "mcp://append_case_note": {"case_id", "note"},
}


def detect_prompt_injection(prompt: str) -> list[str]:
    normalized = prompt.lower()
    return [pattern for pattern in PROMPT_INJECTION_PATTERNS if re.search(pattern, normalized)]


def validate_agent_prompt(prompt: str) -> None:
    if detect_prompt_injection(prompt):
        raise HTTPException(status_code=400, detail="Prompt rejected by AgentGuard security guardrails")


def _walk(value: Any, path: str = "") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            key_lower = str(key).lower()
            if key_lower in DANGEROUS_ARGUMENT_KEYS:
                raise HTTPException(status_code=400, detail=f"Unsafe tool argument key: {path}{key}")
            _walk(nested, f"{path}{key}.")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _walk(nested, f"{path}{index}.")
    elif isinstance(value, str):
        if "javascript:" in value.lower() or value.strip().startswith("file://"):
            raise HTTPException(status_code=400, detail="Unsafe tool argument value")


def allowed_fields_for_tool(tool: Tool) -> set[str] | None:
    return TOOL_ARGUMENT_ALLOWLISTS.get(tool.endpoint)


def validate_tool_arguments(arguments: dict[str, Any], allowed_fields: set[str] | None = None) -> None:
    try:
        encoded = json.dumps(arguments, ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Tool arguments must be JSON serializable") from exc
    if len(encoded) > settings.max_tool_payload_bytes:
        raise HTTPException(status_code=413, detail="Tool argument payload exceeds configured size limit")
    if allowed_fields is not None:
        unexpected = set(arguments) - allowed_fields
        if unexpected:
            raise HTTPException(status_code=400, detail=f"Unexpected tool arguments: {sorted(unexpected)}")
    _walk(arguments)


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_sensitive(nested)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value

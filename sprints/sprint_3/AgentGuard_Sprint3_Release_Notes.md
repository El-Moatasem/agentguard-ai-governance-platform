# AgentGuard v0.3.0 - Sprint 3 Release Notes

## Sprint Goal

Connect the deterministic AgentGuard policy layer to governed tool execution, a real-agent-compatible planning adapter, human approval, MCP tools, grounded AI explanations, and security testing while preserving auditability and default-deny behavior.

## Delivered

- Complete approval lifecycle with pending, approved, rejected, cancelled, and expired states.
- Self-approval prevention and requester/admin cancellation rules.
- Governed execution records with idempotency keys, attempt counts, result states, provider metadata, and correlated audit events.
- Immediate execution only after an `allow` decision; `deny` requests are blocked without provider invocation; approval-required requests remain paused until independent review.
- Provider-neutral tool adapter with deterministic mock tools and a streamable-HTTP MCP `tools/call` adapter.
- Configurable MCP remote mode through `MCP_SERVER_URL` and `MCP_AUTH_TOKEN`, with safe mock mode for local development and CI.
- Agent runtime that converts a natural-language instruction into one normalized registered-tool plan and then sends it through AgentGuard before execution.
- Configurable OpenAI-compatible planning/explanation adapter, with deterministic mock/fallback behavior when no external provider is configured.
- Grounded decision explanations that are generated after authorization and cannot modify the policy result.
- Prompt-injection detection, dangerous-argument validation, payload-size limits, and recursive secret redaction.
- Sprint 3 React governance UI for agent runs, approval states, execution traces, AI explanations, and expanded audit filtering.
- Alembic revision `20260808_0002` for approval lifecycle fields and tool-execution persistence.
- Expanded automated backend suite: 37 tests passing in generated-release verification.

## Demonstration Scenarios

1. Low-risk profile read -> `allow` -> mock tool executes immediately.
2. Production support request -> `deny` -> execution remains blocked with zero attempts.
3. Large refund -> `requires_approval` -> independent approver approves -> tool executes once.
4. Large refund -> approver rejects -> pending execution is cancelled.
5. Agent instruction to send a notification -> registered MCP tool -> policy `allow` -> MCP mock/remote adapter executes.
6. Prompt-injection request -> rejected before planning or policy bypass.
7. Auditor opens a decision explanation -> explanation is grounded in the stored decision and explicitly cannot override authorization.

## External Integration Configuration

The release is fully testable without external credentials. To use external providers:

```bash
export MCP_MOCK_MODE=false
export MCP_SERVER_URL="https://your-mcp-server.example/mcp"
export MCP_AUTH_TOKEN="..."

export AI_PROVIDER=openai_compatible
export AI_BASE_URL="https://api.openai.com/v1"
export AI_API_KEY="..."
export AI_MODEL="gpt-5-mini"
```

Keep all credentials in environment variables or a secret manager. Do not commit them.

## Deferred to Sprint 4

- Production-grade OIDC/SSO and replacement of demonstration bearer tokens.
- Production cloud deployment, observability, backup/restore, and rollback evidence.
- Broader frontend/E2E coverage and performance testing.
- Final accessibility/security review and Capstone submission artifacts.

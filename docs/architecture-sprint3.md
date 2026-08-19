# AgentGuard Architecture - Sprint 3

```text
User / AI Agent
      |
      v
Agent Runtime / Structured Tool Request
      |
      v
Security Guardrails
      |
      v
Deterministic Policy Engine
   /     |      \
allow   deny   requires_approval
  |       |          |
  |     blocked   Human Approval
  |                  |
  +---------+--------+
            v
      Tool Execution Gateway
        /           \
    Mock Adapter    MCP Adapter
            |
            v
      ToolExecution record
            |
            v
      Correlated AuditEvent

AI explanation runs only after the deterministic decision and has no authorization write path.
```

## Trust Boundaries

- Authentication establishes the human actor; persisted `user_email` is overwritten with the authenticated identity.
- Agent plans may suggest only tools already registered for that agent.
- Every tool invocation passes argument validation and policy evaluation before provider execution.
- MCP credentials are configuration secrets, never tool arguments or audit metadata.
- `deny` never invokes a provider.
- `requires_approval` cannot execute until an independent approver completes the request.
- AI-generated explanation output does not contain an authorization decision field.

## Provider Adapters

`mock://...` tools execute locally and deterministically. `mcp://external_tool_name` tools use mock MCP in CI/local mode or JSON-RPC `tools/call` against `MCP_SERVER_URL` when configured. Agent planning and decision explanation can use the safe mock/fallback provider or an OpenAI-compatible chat-completions endpoint.

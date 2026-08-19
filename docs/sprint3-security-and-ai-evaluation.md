# Sprint 3 Security and AI Evaluation

## Security Checks

- Reject prompt-injection phrases before invoking the planning model.
- Reject dangerous argument keys such as `command`, `shell`, `exec`, and authorization overrides.
- Limit serialized tool-argument payload size.
- Redact tokens, API keys, passwords, cookies, authorization fields, client secrets, and private keys before persistence/audit.
- Require registered agent + registered tool + allowlisted action.
- Prevent requester self-approval.
- Make executions idempotent and auditable.
- Keep `deny` and pending approval paths provider-free.

## AI Evaluation Contract

The model is a planner/explainer, not the policy authority. Agent plans are normalized and validated before policy evaluation. Explanations receive the already-final decision and matched-policy information, and the output schema excludes any field that can alter authorization.

## Sprint 3 Evaluation Set

Automated tests cover allow, deny, approval, rejection, cancellation, idempotency, MCP mock execution, agent planning, prompt injection, dangerous arguments, redaction, independent approval, expiry, and safe explanation behavior.

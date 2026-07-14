# Threat Model

## Assets

- Agent identity and metadata.
- Protected resource definitions.
- Access policies.
- Approval records.
- Audit events.
- User roles and authentication state.

## Main Threats and Mitigations

| Threat | Risk | MVP Mitigation |
|---|---|---|
| Agent over-permission | Sensitive data access | Default-deny policy engine |
| Prompt injection | AI explanation manipulation | AI cannot override authorization |
| Unauthorized approval | Fraudulent sensitive action | Role-based approval endpoint |
| Missing audit evidence | Compliance failure | Audit events for decisions and approvals |
| IDOR | Cross-organization data exposure | Organization ID filtering |
| Policy conflict | Unexpected access result | Priority-based policy matching |
| Secret leakage | Credential exposure | `.env.example`, no real secrets committed |

## Production Improvements

- OIDC authentication.
- Tenant isolation tests.
- Rate limiting.
- Immutable audit store.
- OpenTelemetry traces.
- Security headers.
- Dependency vulnerability scanning.

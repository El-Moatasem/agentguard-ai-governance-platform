# Security Notes

AgentGuard uses a default-deny policy model: any action without a matching allow or approval policy is denied.

## MVP Security Controls

- Demo bearer-token authentication.
- Role-based access checks.
- Organization-level fields on core records.
- Default-deny authorization.
- Audit logging for every decision and approval.
- No LLM controls the final authorization decision.

## Production Hardening Needed

- Replace demo tokens with OAuth/OIDC or secure JWT authentication.
- Store secrets in the hosting platform's secret manager.
- Add rate limiting and WAF controls.
- Add database encryption at rest.
- Enable structured application logging and alerting.
- Add dependency scanning and secret scanning in CI.

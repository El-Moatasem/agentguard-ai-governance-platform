# Changelog

## [0.3.0] - Sprint 3 Release Candidate

### Added
- Complete human approval lifecycle with expiry, cancellation, and self-approval prevention.
- Governed tool execution records with idempotency, attempts, provider status, and correlated audit evidence.
- Provider-neutral mock/MCP execution adapters and configurable streamable-HTTP MCP calls.
- Mock/OpenAI-compatible agent planning adapter that can only propose registered tools.
- Grounded post-decision AI explanations with deterministic fallback.
- Prompt-injection detection, dangerous-argument checks, payload limits, and recursive secret redaction.
- Sprint 3 execution/approval UI and expanded audit views.
- Alembic revision `20260808_0002`.
- Sprint 3 Jira, release, demo, architecture, security, and evaluation documentation.

### Verification
- 37 backend tests passed in generated-release verification.
- Sprint 3 TypeScript passed strict type checking.

## [0.2.0] — Sprint 2 Release Candidate

### Added

- PostgreSQL 16 Docker service and Alembic migrations.
- Database constraints, foreign keys, and indexes.
- Policy update, activation, deactivation, version history, and dry-run APIs.
- Nested context conditions and comparison operators.
- Action-request correlation IDs and query endpoints.
- Filtered CSV/JSON audit exports.
- Expanded governance metrics and Sprint 2 frontend workflows.
- PostgreSQL-backed CI and 19 backend tests.
- Jira-ready Sprint 1 and Sprint 2 planning files.

### Changed

- SQLite moved to optional fallback status.
- Frontend workflow standardized on Yarn.
- API version advanced to 0.2.0.

### Deferred

- Real agent/MCP integration.
- Completed human-approval execution workflow.
- Production authentication and deployment.

## [0.1.0] — Sprint 1 Foundation

- FastAPI/React project foundation.
- Demo authentication and RBAC.
- Agent, tool, and resource registries.
- Initial policies, decisions, approvals, audit events, Docker, CI, and documentation.

# AgentGuard Final Architecture and Testing Summary

## Architecture

AgentGuard is a full-stack AI-agent governance platform built with React, FastAPI, SQLModel/SQLAlchemy, Alembic, and PostgreSQL.

The final architecture separates deterministic authorization from AI explanations:

- Policy decisions are made by a deterministic policy engine.
- Human approvals control sensitive action execution.
- Tool execution is allowed only after AgentGuard governance.
- AI explanations summarize decisions but cannot change them.
- MCP integrations use allowlisted tools and mock-safe local/CI mode.
- Every decision, approval, execution, and explanation is audit-visible.

## Patterns used

- API-first architecture.
- Repository/service-style business logic separation.
- Role-based authorization.
- Deterministic policy-evaluation adapter.
- Human-in-the-loop approval workflow.
- Provider abstraction for AI and MCP integrations.
- Idempotent tool execution records.
- Audit-event logging with correlation IDs.
- Alembic-managed schema evolution.

## Testing strategy

- Unit tests for policy evaluation and guardrails.
- API tests for decision, approval, execution, and audit workflows.
- Regression tests for Sprint 2 and Sprint 3 features.
- Sprint 4 tests for release readiness and security headers.
- Frontend validation through TypeScript type checking and production build.
- CI validation with PostgreSQL and Alembic migrations before pytest.

## Deployment recommendation

Recommended deployment:

- Frontend: Vercel, Netlify, Render static site, or Railway.
- API: Render, Railway, Fly.io, Azure App Service, or AWS ECS.
- Database: Managed PostgreSQL.
- Secrets: Environment variables or cloud secret manager.
- CI/CD: GitHub Actions.

Cloud is recommended for the Capstone demo because it provides a stable public URL, managed TLS, and simple managed PostgreSQL. On-premises deployment is possible but would require more infrastructure management, backups, TLS, observability, and operations effort.

## Final limitation statement

AgentGuard is a configurable Capstone prototype for selected AI-agent governance scenarios. It demonstrates how a common policy and audit layer can govern real or simulated agent tool requests. It does not claim universal support for every agent framework, enterprise system, or regulatory standard.

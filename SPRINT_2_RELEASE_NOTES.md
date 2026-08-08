# AgentGuard Sprint 2 Release Notes

## Release Information

- **Version:** 0.2.0
- **Release name:** Policy Engine, PostgreSQL, and Audit Trail
- **Status:** Sprint 2 release candidate
- **Target sprint:** Weeks 6–8
- **Previous baseline:** Sprint 1 foundation / v0.1.x

## Sprint Goal

Deliver a versioned, deterministic policy-evaluation platform backed by PostgreSQL, with persistent action requests, correlation IDs, searchable audit events, exports, improved metrics, stronger CI, and automated test evidence.

## Added

### PostgreSQL and database migrations

- PostgreSQL 16 service in Docker Compose.
- Database health checks and persistent Docker volume.
- Psycopg PostgreSQL driver.
- Alembic configuration and a complete Sprint 2 baseline migration.
- Foreign keys for tools, policy versions, matched policies, and approvals.
- Organization-scoped uniqueness constraints for agents, resources, policies, users, and tools.
- Indexes for policy priority, request decisions, audit queries, correlation IDs, and timestamps.
- PostgreSQL-backed CI workflow.

### Versioned policy management

- Create, retrieve, list, update, activate, and deactivate policy APIs.
- Policy version numbers and immutable PolicyVersion snapshots.
- Change summaries and editor identity for each version.
- Filter policies by active status and effect.
- Audit events for policy creation, updates, and status changes.
- Validation of supported policy keys and comparison operators.

### Context-aware deterministic policy engine

- Explicit conflict resolution:
  1. Highest priority wins.
  2. At equal priority, `deny` outranks `requires_approval`, which outranks `allow`.
  3. No match produces default deny.
- Nested `context.*` conditions.
- Operators: `$eq`, `$ne`, `$in`, `$not_in`, `$gte`, `$lte`, `$gt`, `$lt`, and `$contains`.
- Wildcard matching for present values.
- Dry-run policy evaluation that does not persist a request.
- Matched-policy name and evaluated-policy count in decision responses.

### Action-request persistence

- Unique correlation ID for every persisted evaluation.
- Validation that an agent is registered and active.
- Validation that a protected resource exists.
- Stored request context, decision, reason, matched policy, and policy count.
- List and detail endpoints for action requests.
- Filters by decision, agent, and resource.

### Audit and reporting

- Correlation IDs added to audit events.
- Filtering by event type, result, actor, and correlation ID.
- Pagination limits for audit queries.
- CSV and JSON audit exports.
- Expanded dashboard metrics for active policies and decision outcomes.

### Frontend

- Demonstration role switcher.
- Custom action simulator with JSON context.
- Preconfigured allow, approval-required, and deny scenarios.
- Policy creation form.
- Policy activate/deactivate controls.
- Decision details including correlation ID and matched policy.
- Approval-queue preview retained from the earlier prototype.
- Audit filters and CSV/JSON export controls.
- Updated responsive visual design.

### Testing and CI

- Expanded backend suite to **19 passing tests** in the generated release environment.
- Policy priority, tie-breaking, context operators, wildcard, and default-deny tests.
- Policy create/update/version history tests.
- Decision persistence, agent/resource validation, and audit-correlation tests.
- CSV/JSON export tests.
- RBAC tests.
- Backend CI now creates PostgreSQL, applies Alembic migrations, and runs tests.
- Frontend CI now uses Yarn with the committed lockfile.

## Changed

- Docker Compose now uses PostgreSQL instead of SQLite.
- SQLite remains available only as a lightweight manual-development and test fallback.
- API version updated to `0.2.0`.
- FastAPI startup now uses a lifespan handler.
- Database sessions use `expire_on_commit=False` to keep returned objects serializable after audit commits.
- The frontend package-management instructions now use Yarn.
- The root API route now returns service and documentation information.

## Upgrade Instructions

Because v0.2.0 introduces a formal migration baseline and additional required columns, use a clean development database when upgrading from the generated Sprint 1 prototype.

### Docker upgrade

```bash
docker compose down -v
docker compose up --build
```

### Manual SQLite development

```bash
cd apps/api
rm -f agentguard.db
export DATABASE_URL=sqlite:///./agentguard.db
alembic upgrade head
uvicorn app.main:app --reload
```

### Manual PostgreSQL development

Create the database, set `DATABASE_URL`, and run:

```bash
cd apps/api
alembic upgrade head
uvicorn app.main:app --reload
```

## Verification Evidence

The generated release was verified with:

- Python source compilation.
- Alembic upgrade against a clean SQLite validation database.
- FastAPI health and registry smoke checks.
- Backend automated test result: **19 passed**.
- TypeScript strict type check: **passed**.

A full Vite production build could not be executed inside the generation container because the uploaded `node_modules` contained a macOS-only native Rolldown binding and the container had no package-network access. The TypeScript source passed strict checking; run `yarn install --frozen-lockfile && yarn build` on your local machine or in GitHub Actions to capture the final build evidence.

## Known Limitations and Deferred Work

- Authentication still uses demonstration bearer tokens, not OIDC/SSO.
- The approval workflow is an early preview; Sprint 3 should add self-approval prevention, expiration, execution state, and resume-after-approval behavior.
- No real OpenAI agent, MCP server, or Zapier MCP integration is included yet.
- The custom policy adapter is used; OPA remains a future adapter option.
- No real LLM provider is connected to the explanation endpoint.
- No production deployment URL is included.
- Audit records are append-oriented but are not cryptographically immutable.

## Sprint 2 Demo Checklist

1. Start the PostgreSQL-backed application with Docker Compose.
2. Switch between admin, developer, and auditor demonstration roles.
3. Create a context-aware policy and show version 1.
4. Update the policy and show version history.
5. Run an allowed sandbox profile read.
6. Run a transaction read that requires approval.
7. Run a production request that is denied.
8. Show correlation IDs and stored action requests.
9. Filter the audit trail by result or event type.
10. Export audit events as CSV and JSON.
11. Show Alembic migration, PostgreSQL service, CI configuration, and passing tests.

# AgentGuard Design and Testing Document — Sprint 2

## Design Summary

AgentGuard evaluates an AI-agent action against deterministic organizational policies, stores the request and outcome, creates human-review records for sensitive actions, and writes correlated audit evidence.

## Key Design Decisions

### Deterministic authorization

The custom policy engine is the source of truth. AI-generated text cannot override authorization.

### Explicit policy conflict resolution

Higher priority wins. For equal priority, deny outranks approval, which outranks allow. No match means default deny.

### Context-aware policies

Policies can inspect normalized top-level request fields and nested `context.*` values. A restricted operator set prevents arbitrary execution.

### PostgreSQL and Alembic

PostgreSQL is the primary Sprint 2 database. Alembic records schema evolution. SQLite remains a limited fallback.

### Versioned policy history

Policy edits increment a version and store a snapshot containing the editor and change summary.

### Correlated audit evidence

Each persisted decision receives a correlation ID shared by its action request and audit event. Audit records can be filtered and exported.

### Organization scoping

Every principal domain record includes `organization_id`, and API queries filter by the authenticated user's organization.

### Demo authentication

Bearer tokens remain intentionally simple for the Capstone MVP. OIDC/SSO is deferred.

## Automated Test Scope

| Test area | Sprint 2 examples |
|---|---|
| Policy unit tests | Priority, equal-priority precedence, default deny, list matching, context ranges, wildcards |
| API smoke tests | Root, health, current user, metrics, missing auth, forbidden role |
| Policy lifecycle | Create, update, version history, invalid condition, dry run |
| Decision integration | Agent/resource validation, allow, deny, approval creation, request retrieval |
| Audit integration | Correlation filtering, CSV export, JSON export |
| CI integration | PostgreSQL service, Alembic migration, test execution |
| Frontend static check | Strict TypeScript checking |

## Generated Release Verification

- Python compilation: passed.
- Alembic migration against a clean validation database: passed.
- FastAPI smoke request: passed.
- Backend tests: **19 passed**.
- TypeScript strict checking: passed.

The Vite production bundle should be run locally or through GitHub Actions because the generation container could not reinstall the Linux-specific native Vite/Rolldown optional dependency from the network.

## Sprint 2 Manual Test Script

1. Reset the Docker volume and start all services.
2. Open Swagger and authenticate with `admin-token`.
3. Create a new policy with a nested `context.amount` condition.
4. Update the policy and inspect `/policies/{id}/versions`.
5. Run an allowed sandbox profile read.
6. Run a transaction read that requires approval.
7. Run a production support request that is denied.
8. Retrieve the stored action request by ID.
9. Filter audit events by correlation ID.
10. Export the audit trail as CSV and JSON.
11. Confirm developer and auditor role restrictions.
12. Run `pytest -q` and `yarn build`.

## Security Tests Required Before Final Submission

- Cross-organization access attempts.
- Self-approval prevention.
- Malformed and oversized JSON context.
- Duplicate and replayed tool requests.
- Rate limiting.
- Secret scanning.
- SQL and content injection tests.
- Audit tampering controls.
- Dependency vulnerability review.

## Definition of Done

A feature is Done only when it works, has applicable automated tests, is documented, is linked to a board item and commit/PR, and has no known critical defect.

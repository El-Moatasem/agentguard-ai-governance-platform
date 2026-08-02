# Sprint 2 User Stories and Tasks

## Sprint Overview

**Sprint name:** Sprint 2 — Policy Engine, PostgreSQL, and Audit Trail  
**Suggested duration:** Weeks 6–8  
**Sprint goal:** Move the application to a production-oriented relational database, implement versioned deterministic policies, persist evaluated action requests, and provide searchable/exportable audit evidence.

## Release Status

The generated Sprint 2 source is a **v0.2.0 release candidate**. Move the Jira stories to Done only after you run the project, review the code, complete the acceptance criteria, and attach your own commit, test, and demonstration evidence.

## User Stories

### AG-S2-01 — Adopt PostgreSQL and versioned migrations

**User story:** As an engineer, I need a production-oriented database and repeatable migrations so that development, CI, and deployment use a controlled schema.

**Acceptance criteria**

- Docker Compose starts PostgreSQL 16 with a persistent volume and health check.
- The API connects through `DATABASE_URL`.
- `alembic upgrade head` creates the full Sprint 2 schema.
- Relational constraints and query indexes are defined.
- SQLite remains an optional lightweight fallback for manual development and isolated tests.

**Tasks**

- Add the PostgreSQL service to Docker Compose.
- Add the Psycopg driver.
- Configure Alembic.
- Create the Sprint 2 baseline migration.
- Add foreign keys, uniqueness constraints, and indexes.
- Update local-running and reset instructions.
- Validate the migration against a clean database.

### AG-S2-02 — Manage and version policies

**User story:** As an administrator, I can create, update, activate, and deactivate policies while retaining their history so that governance changes are traceable.

**Acceptance criteria**

- Policy creation records version 1.
- Policy updates increment the version and store a version snapshot.
- Policies can be activated and deactivated.
- Duplicate policy names are rejected within an organization.
- Policy lifecycle changes create audit events.

**Tasks**

- Add policy version and change-metadata fields.
- Add the PolicyVersion model and migration.
- Implement policy create, retrieve, update, activate, and deactivate endpoints.
- Implement policy-version history endpoint.
- Add policy lifecycle audit events.
- Add policy lifecycle tests.

### AG-S2-03 — Evaluate contextual policies deterministically

**User story:** As a developer, I can evaluate an agent action against contextual policies so that governance decisions are predictable and testable.

**Acceptance criteria**

- The engine returns `allow`, `deny`, or `requires_approval`.
- Higher priority wins; for equal priority, deny outranks approval, which outranks allow.
- Conditions support top-level request attributes and nested `context.*` values.
- Supported operators include equality, membership, comparison, and containment.
- No match results in default deny.
- A dry-run endpoint evaluates without creating an action request or audit event.

**Tasks**

- Define conflict-resolution rules.
- Add nested context resolution.
- Add condition operators.
- Validate policy keys and operators at the API boundary.
- Add a dry-run policy test endpoint.
- Add policy-engine unit tests for priority, ties, operators, wildcards, and default deny.

### AG-S2-04 — Persist and query action requests

**User story:** As a developer or auditor, I can inspect prior action evaluations so that decisions can be traced and reproduced.

**Acceptance criteria**

- Evaluated actions are stored with agent, action, resource, environment, context, decision, reason, and matched policy.
- Every action request receives a unique correlation ID.
- Unknown or inactive agents and unknown resources are rejected.
- Authorized users can list and retrieve organization-scoped requests.

**Tasks**

- Extend the ActionRequest schema.
- Add correlation IDs and evaluated-policy counts.
- Validate registered agents and resources before evaluation.
- Add action-request list/detail endpoints.
- Add query filters for decision, agent, and resource.
- Add integration tests for allowed, denied, and approval-required requests.

### AG-S2-05 — Provide searchable and exportable audit evidence

**User story:** As an auditor, I can filter and export governance events so that decisions can be reviewed outside the application.

**Acceptance criteria**

- Audit records include actor, event type, result, message, correlation ID, metadata, and timestamp.
- Audit events can be filtered by type, result, actor, and correlation ID.
- Audit results can be exported as CSV and JSON.
- Audit access is restricted to administrator and auditor roles.

**Tasks**

- Extend AuditEvent with correlation IDs and indexes.
- Add audit query parameters and pagination.
- Implement CSV export.
- Implement JSON export.
- Add authorization and export tests.
- Add export controls to the frontend.

### AG-S2-06 — Extend dashboard and policy UI

**User story:** As a stakeholder, I can create policies, run realistic simulations, and inspect governance metrics from one interface.

**Acceptance criteria**

- The dashboard shows active policies and decision counts.
- The user can switch among demonstration roles.
- Administrators can create and activate/deactivate policies.
- Developers and administrators can run custom or predefined simulations.
- Auditors can filter and export events.
- The UI remains responsive on desktop and mobile widths.

**Tasks**

- Add role switching.
- Add custom decision-simulation form.
- Add policy-creation form.
- Add policy status controls.
- Add decision-result details and correlation IDs.
- Add audit filters and export controls.
- Update responsive styling.

### AG-S2-07 — Strengthen CI and automated testing

**User story:** As the release owner, I need repeatable automated checks so that Sprint 2 changes can be safely reviewed.

**Acceptance criteria**

- Backend CI provisions PostgreSQL and applies Alembic migrations.
- Backend test suite covers core Sprint 2 behavior.
- Frontend CI installs with Yarn and runs a production build.
- The release candidate passes Python compilation, migrations, backend tests, and TypeScript checking.

**Tasks**

- Update backend CI with PostgreSQL service.
- Apply migrations during CI.
- Update frontend CI to Yarn.
- Add API and policy tests.
- Run static/type checks.
- Record test evidence in release notes.

### AG-S2-08 — Document and demonstrate Sprint 2

**User story:** As a Capstone reviewer, I can understand what changed and reproduce the Sprint 2 demo so that progress is clearly evidenced.

**Acceptance criteria**

- Sprint 2 release notes summarize features, migrations, tests, limitations, and upgrade steps.
- Architecture and design/testing documentation reflect PostgreSQL, versioned policies, and audit exports.
- A Sprint 2 demo script covers allow, deny, approval-required, filtering, and export.
- Jira stories link to commits, test evidence, and demo evidence.

**Tasks**

- Update README and running instructions.
- Update architecture and testing documents.
- Create Sprint 2 release notes.
- Prepare the Sprint 2 demo sequence.
- Attach screenshots or recording links to Jira.
- Review deferred Sprint 3 work.

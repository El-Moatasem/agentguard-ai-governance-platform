# AgentGuard Final Design and Testing Document

## 1. Executive Summary

AgentGuard is a full-stack governance platform for AI agents that can request actions against external tools or protected resources. Its core design principle is separation of **capability** from **authority**: an AI model or agent may propose an action, but a deterministic governance layer decides whether that action is allowed, denied, or requires independent human approval.

This document describes the final architecture, engineering decisions, patterns, data design, AI/MCP boundaries, security approach, testing strategy, deployment choices, cost implications, limitations, and final verification evidence for the Quantic MSSE Capstone.

## 2. Problem and Intended Use

AgentGuard is intended for action-taking agents where an incorrect action can create operational, financial, privacy, security, or compliance impact.

Representative use cases include:

- Finance: low-risk data retrieval, approval-gated refunds, denied unauthorized transfers.
- Cloud/DevOps: automated log reads, approval-gated production operations, denied destructive actions.
- Cybersecurity: automated investigation, approval-gated account/network interventions.
- Customer support: safe data reads, approval-gated sensitive customer actions.
- Healthcare/insurance: safe summarization with stronger governance for sensitive disclosures or consequential changes.

AgentGuard is not intended to imply that every conversational agent needs an external governance layer.

## 3. Functional Requirements

The final system demonstrates:

1. Registration and management of agents, tools, protected resources, users, and policies.
2. Deterministic policy evaluation.
3. `ALLOW`, `DENY`, and `REQUIRES_APPROVAL` outcomes.
4. Versioned policies and audit history.
5. Human review for sensitive requests.
6. Prevention of requester self-approval.
7. Governed tool execution after authorization.
8. Correlation of request, policy decision, approval, execution, and audit evidence.
9. Agent-runtime integration.
10. MCP adapter support.
11. AI-generated explanations that cannot change authorization.
12. Searchable audit evidence and export.
13. A web-based governance dashboard.

## 4. Architecture

```text
React / TypeScript UI
        |
        v
FastAPI REST API
        |
        +--> Authentication / RBAC
        |
        +--> Agent + Tool + Resource Registry
        |
        +--> Deterministic Policy Engine
        |        |
        |        +--> ALLOW
        |        +--> DENY
        |        +--> REQUIRES_APPROVAL
        |
        +--> Human Approval Workflow
        |
        +--> Governed Tool Execution
        |        |
        |        +--> mock://
        |        +--> mcp://
        |
        +--> AI Planning / Explanation Providers
        |        (non-authoritative)
        |
        +--> Correlated Audit Trail
        |
        v
SQLModel / SQLAlchemy
        |
        v
PostgreSQL 16
        |
        v
Alembic migrations
```

## 5. Key Architecture Decisions

### 5.1 Deterministic authorization is separated from AI reasoning

**Decision:** The LLM does not authorize tool execution.

**Reason:** AI-generated output can be nondeterministic, prompt-injected, incorrect, or difficult to reproduce. Authorization is therefore performed by deterministic policy rules.

**Benefit:** An AI explanation can fail or be manipulated without changing the authorization result.

### 5.2 Default deny

If no policy explicitly allows or approval-gates an action, the system denies it.

**Reason:** The safer failure mode for an action-taking agent is to block an unknown request rather than silently grant access.

### 5.3 Policy versioning

Policies maintain version history.

**Reason:** Governance decisions may need to be explained later. Version history makes changes traceable and supports auditability.

### 5.4 Human-in-the-loop as a governance state

Human review is represented as a first-class state (`requires_approval`) rather than an ad-hoc UI pause.

**Reason:** This allows approval status, reviewer identity, timestamps, and resulting execution state to be persisted and audited.

### 5.5 Self-approval prevention

The requester cannot approve the same governed action.

**Reason:** Sensitive approval is meaningful only if the reviewer is independent from the requester.

### 5.6 Idempotent tool execution

Execution records use idempotency keys and attempt tracking.

**Reason:** Retries, UI refreshes, and transient failures must not cause unintended duplicate external actions.

### 5.7 Provider abstraction for AI and MCP

AI planning/explanation and MCP execution are behind adapters.

**Reason:** The governance path should remain stable if a different model or MCP provider is used.

### 5.8 Correlation IDs

Every governed request receives a correlation ID that connects decision, approval, execution, and audit records.

**Reason:** This makes operational investigation and demo traceability straightforward.

## 6. Software and Architectural Patterns

| Pattern | Where used | Reason |
|---|---|---|
| Layered architecture | API -> services -> data | Keeps transport, business logic, and persistence separated |
| Service layer | Governance, policy, audit, execution | Centralizes domain logic and improves testability |
| Adapter/provider pattern | AI and MCP integrations | Decouples external providers from governance |
| Default-deny security | Policy engine | Safe handling of unrecognized requests |
| Human-in-the-loop workflow | Approval model/router | Explicit control for sensitive actions |
| Idempotency pattern | Tool execution | Prevents duplicate side effects |
| Audit/event logging | AuditEvent + correlation IDs | Traceability and accountability |
| RBAC | Admin/Developer/Approver/Auditor roles | Limits capabilities by role |
| Schema migration pattern | Alembic | Reproducible database evolution |
| API-first design | FastAPI/OpenAPI | Clear contract for UI and integrations |

## 7. Data Architecture

Primary persisted entities include:

- `User`
- `Agent`
- `Tool`
- `ProtectedResource`
- `Policy`
- `PolicyVersion`
- `ActionRequest`
- `Approval`
- `ToolExecution`
- `AuditEvent`

Important database constraints/indexes include:

- unique organization/name rules for agents, resources, and policies;
- unique policy version;
- unique approval per action request;
- unique execution idempotency key;
- indexes on organization, status, decision, created time, event type, and correlation identifiers.

PostgreSQL 16 is the final primary database.

## 8. Database Evolution

### Sprint 1

A lightweight prototype database was used to accelerate initial development.

### Sprint 2

PostgreSQL became the primary database and Alembic migrations were introduced.

### Sprint 3

The schema was extended for governed execution and the approval lifecycle.

### Sprint 4

The current release did not require another schema migration.

Current Alembic head:

```text
20260808_0002
```

## 9. Policy Evaluation

Policies define:

- effect;
- priority;
- active state;
- conditions;
- version.

The policy engine supports context-aware matching and deterministic conflict handling.

Example conceptual outcomes:

```text
Read low-risk sandbox profile
-> ALLOW

Read sensitive transaction data
-> REQUIRES_APPROVAL

Protected production access
-> DENY
```

The engine evaluates policy independently from AI-generated text.

## 10. Human Approval

The approval lifecycle supports:

```text
pending
approved
rejected
cancelled
expired
```

The independent-review rule prevents the requesting identity from approving or rejecting its own governed action.

The current release demonstrates one required human approval for approval-gated actions. Multi-stage/two-level approval is a future extension and should not be presented as implemented.

## 11. Tool Execution

Tool execution only occurs through the governance gateway.

Execution records contain:

- action request;
- tool;
- provider;
- arguments;
- execution status;
- response/error details;
- attempt count;
- idempotency key;
- initiator;
- timestamps.

The deterministic `mock://` adapter supports safe testing and demos.

The `mcp://` adapter supports a configured streamable-HTTP MCP endpoint.

## 12. AI Engineering Boundary

AgentGuard uses AI in two non-authoritative roles:

1. planning/proposing a structured tool call;
2. explaining an already-final governance decision.

The AI cannot alter:

- matched policy;
- authorization decision;
- approval state;
- execution authorization.

This design reduces the security impact of prompt injection or explanation hallucination.

## 13. Security Controls

Implemented controls include:

- role-based access;
- default deny;
- human approval;
- requester/reviewer separation;
- argument validation;
- prompt-injection checks;
- secret redaction;
- payload limits;
- CORS configuration;
- browser security response headers;
- audit logging.

### Authentication limitation

The current Capstone codebase uses demonstration bearer tokens for four roles. This provides deterministic role-based demos but is not production enterprise authentication.

If production authentication is not implemented before submission, Jira and documentation should describe SSO/MFA/password lifecycle as future hardening rather than completed functionality.

## 14. Testing Strategy

### 14.1 Unit testing

Unit tests cover deterministic policy behavior and matching rules.

Examples:

- priority handling;
- default deny;
- list/context conditions;
- wildcard rules.

### 14.2 API/integration testing

FastAPI `TestClient` tests cover:

- root and health endpoints;
- policy CRUD/versioning;
- policy dry run;
- decision persistence;
- approval creation/review;
- production deny behavior;
- audit export;
- agent/MCP/security behavior;
- governed execution;
- decision explanations;
- Sprint 4 release-readiness endpoints.

### 14.3 Database testing

GitHub Actions starts a PostgreSQL 16 service, configures `agentguard_test`, applies Alembic migrations, and then runs pytest.

This verifies the actual PostgreSQL migration path rather than silently creating an SQLite-only test schema.

### 14.4 Test isolation

The automated tests reset application data between cases to prevent persistent policy/test state from contaminating later tests.

### 14.5 Frontend verification

The frontend CI performs:

```bash
yarn install --frozen-lockfile --non-interactive
yarn run tsc --noEmit
yarn build
```

This verifies dependency reproducibility, strict TypeScript checking, and a production Vite build.

### 14.6 Latest verified CI evidence

On the final `main` branch verification:

- PostgreSQL 16 service started successfully.
- Alembic migrated through `20260808_0002`.
- Backend test result: **41 passed**.
- Frontend build/type-check workflow completed successfully.

A single Starlette/AnyIO deprecation warning was present in the backend run and did not fail the suite.

## 15. Manual Acceptance Testing

Before submission, manually demonstrate at least:

1. Safe request -> `ALLOW`.
2. Sensitive request -> `REQUIRES_APPROVAL`.
3. Human approval -> controlled execution.
4. Human rejection -> no execution.
5. Prohibited/production request -> `DENY`.
6. Audit trail -> correlation ID and decision evidence.
7. AI explanation -> explanation does not modify the decision.
8. Policy version/update -> history preserved.
9. CSV/JSON audit export.
10. Release-readiness page.

Record screenshots or Jira evidence for the final sprint.

## 16. Testing Limitations / Recommended Final Improvement

The current repository does not contain a dedicated browser Playwright suite or React component-test suite.

This is not explicitly mandated by the Capstone handbook, but Sprint 4 Jira items referring to Playwright/component testing should either:

- be implemented and verified before being marked Done; or
- be moved to future work / de-scoped with the sprint-review rationale documented.

The same rule applies to Jira items claiming production authentication, rate limiting, or performance/recovery tests if those are not present in the final code.

## 17. Deployment Architecture

Recommended Capstone deployment:

```text
Browser
  |
  v
React static frontend
  |
 HTTPS
  v
FastAPI service
  |
  v
Managed PostgreSQL
```

Recommended characteristics:

- public HTTPS frontend;
- public HTTPS API;
- managed PostgreSQL;
- environment-managed secrets;
- migrations run during release/deployment;
- CORS restricted to the deployed frontend origin.

See `FINAL_DEPLOYMENT_AND_COSTS.md`.

## 18. Deployment Options and Relative Cost Implications

The estimates below are illustrative planning ranges, not vendor quotes.

| Option | Illustrative monthly cost | Benefits | Trade-offs |
|---|---:|---|---|
| Free/low-tier PaaS | ~$0-20 | Fastest Capstone deployment, managed TLS | Sleeping/limits, lower control |
| Small managed cloud | ~$20-100+ | Better persistence/scaling/control | More configuration and monitoring |
| Larger managed architecture | ~$100+ | Stronger availability/scaling | Cost and operational complexity |
| On-premises | Hardware + staff/ops | Maximum infrastructure control | TLS, backups, upgrades, monitoring and support become your responsibility |

For a Capstone demonstration, a low-cost managed cloud platform is recommended because public accessibility and managed TLS matter more than enterprise-scale infrastructure.

## 19. CI/CD

GitHub Actions provides:

- PostgreSQL-backed backend tests;
- Alembic migration verification;
- frontend TypeScript verification;
- frontend production build.

The final `main` CI checks are passing.

For future work, CI can be extended to browser E2E, dependency scanning, deployment, and production smoke tests.

## 20. Limitations

The final Capstone release intentionally does not claim:

- universal support for every agent framework;
- formal regulatory certification;
- multi-level approval;
- production SSO/MFA;
- automatic compatibility with any MCP service;
- high-availability enterprise deployment;
- correctness of an external AI provider.

The project demonstrates the governance architecture and working end-to-end controls within a defined scope.

## 21. Future Work

- production identity provider / SSO / MFA;
- multi-stage approval policies;
- approval quorum rules;
- richer risk/severity scoring;
- more agent-framework adapters;
- broader MCP tool certification;
- browser E2E testing;
- policy-as-code interoperability;
- centralized enterprise policy administration;
- high-availability deployment and disaster recovery;
- observability/SIEM integration.

## 22. Reproducibility

Backend:

```bash
cd apps/api
source .venv/bin/activate
export DATABASE_URL="postgresql+psycopg://agentguard:agentguard_dev_password@localhost:5432/agentguard_test"
alembic upgrade head
pytest -q
```

Frontend:

```bash
cd apps/web
nvm use 20
corepack enable
corepack prepare yarn@1.22.22 --activate
yarn install --frozen-lockfile
yarn typecheck
yarn build
```

## 23. Capstone Rubric Alignment

The final submission should provide:

- accessible GitHub repository;
- deployed web application;
- accessible Jira/agile board;
- this detailed design/testing document;
- CI/CD evidence;
- final 15-20 minute recorded demonstration;
- current sprint/task evidence;
- attribution and academic-integrity notices.

The final score depends on the submitted artifact and demonstrated evidence, not this document alone.

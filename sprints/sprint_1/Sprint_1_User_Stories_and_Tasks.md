# Sprint 1 User Stories and Tasks

## Sprint Overview

**Sprint name:** Sprint 1 — Foundation and Registry  
**Suggested duration:** Weeks 3–5  
**Sprint goal:** Establish a runnable full-stack foundation with demonstration authentication, role-based access, agent/resource/tool registries, local development instructions, Docker support, CI, and initial tests.

## Definition of Done

A Sprint 1 item is complete when:

- Its acceptance criteria have been demonstrated.
- Relevant backend behavior has automated tests.
- The code is committed through a traceable branch or pull request.
- README or technical documentation has been updated.
- No known critical defect blocks the Sprint 1 demo.
- The Jira/GitHub board item links to the related commit or pull request.

## User Stories

### AG-S1-01 — Define the project scope and architecture

**User story:** As the Product Owner, I need a clearly bounded MVP and architecture so that the solo project remains feasible and testable.

**Acceptance criteria**

- The problem statement, users, MVP features, exclusions, and stretch goals are documented.
- The architecture separates deterministic authorization from AI-generated explanations.
- The project documents assumptions and known limitations.

**Tasks**

- Create the project charter and problem statement.
- Identify administrator, developer, approver, and auditor roles.
- Create the context and component architecture diagrams.
- Record ADRs for deterministic authorization and default deny.
- Define the Definition of Done and sprint cadence.

### AG-S1-02 — Establish repository and engineering workflow

**User story:** As a solo engineer, I need a consistent repository and review workflow so that progress is traceable and reproducible.

**Acceptance criteria**

- The monorepo contains backend, frontend, documentation, policy examples, data, and scripts.
- Pull request and contribution templates are present.
- Backend tests and frontend builds are represented in CI workflows.

**Tasks**

- Create the repository structure.
- Add `.gitignore`, `CONTRIBUTING.md`, `SECURITY.md`, and `CODEOWNERS`.
- Configure backend and frontend GitHub Actions workflows.
- Add a pull request template.
- Create the Jira or GitHub Project board.

### AG-S1-03 — Implement demonstration authentication and RBAC

**User story:** As a user, I need to authenticate under a defined role so that the API can restrict platform capabilities.

**Acceptance criteria**

- Demo bearer tokens resolve to active users.
- Admin, developer, approver, and auditor roles are seeded.
- Protected endpoints reject missing tokens and unauthorized roles.

**Tasks**

- Implement the user and role models.
- Implement bearer-token authentication.
- Add `/auth/login` and `/auth/me` endpoints.
- Implement role dependency helpers.
- Test unauthenticated and unauthorized access.

### AG-S1-04 — Build the AI-agent registry

**User story:** As an administrator, I can register and view AI agents so that governed identities and ownership are known.

**Acceptance criteria**

- An administrator can create an agent.
- Authorized users can list agents within their organization.
- Agent records include purpose, owner, risk level, and status.

**Tasks**

- Implement the Agent model and schema.
- Add create/list agent endpoints.
- Add organization scoping.
- Seed support and finance agent examples.
- Add duplicate-name protection.

### AG-S1-05 — Build tool and protected-resource registries

**User story:** As an administrator, I can register tools and resources so that policies can refer to controlled capabilities and data.

**Acceptance criteria**

- Protected resources include classification and owner team.
- Tools are linked to a registered agent.
- Unauthorized users cannot create registry records.

**Tasks**

- Implement Tool and ProtectedResource models.
- Add create/list resource endpoints.
- Add create/list tool endpoints.
- Validate that the linked agent exists.
- Seed representative tools and resources.

### AG-S1-06 — Provide an initial governance dashboard

**User story:** As a stakeholder, I can open a web interface and view the platform foundation so that the Sprint 1 capabilities are demonstrable.

**Acceptance criteria**

- The React application loads from the documented URL.
- It displays seeded agents and baseline metrics.
- The API base URL is environment configurable.

**Tasks**

- Create the React, TypeScript, and Vite application.
- Build the initial dashboard layout.
- Add the typed API client.
- Add responsive styles.
- Confirm the frontend can call the FastAPI backend.

### AG-S1-07 — Make the project reproducible locally

**User story:** As a reviewer, I can run the project from documented commands so that the project is easy to evaluate.

**Acceptance criteria**

- Backend and frontend can run separately.
- Docker Compose support is available.
- Environment variables are documented without committing secrets.

**Tasks**

- Add backend and frontend Dockerfiles.
- Add Docker Compose configuration.
- Add `.env.example`.
- Document Yarn and Python virtual-environment setup.
- Document reset and troubleshooting steps.

### AG-S1-08 — Test and demonstrate the foundation

**User story:** As the Product Owner, I need evidence that the foundation works so that Sprint 2 can begin safely.

**Acceptance criteria**

- Health, authentication, RBAC, and policy-engine foundation tests pass.
- A Sprint 1 demonstration script and release notes are available.
- Known limitations are recorded.

**Tasks**

- Add backend smoke tests.
- Add initial deterministic-policy unit tests.
- Run the frontend type check/build.
- Record Sprint 1 release notes.
- Capture Sprint 1 demonstration evidence.

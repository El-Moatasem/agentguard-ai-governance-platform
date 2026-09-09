# AgentGuard

**Final Capstone release:** `v1.0.0`  
**Project:** AI Agent Governance, Access Control, Human Approval, Governed Tool Execution, and Audit Platform  
**Program:** Quantic Master of Science in Software Engineering (MSSE) Capstone

AgentGuard places a deterministic governance layer between AI agents and external tools. An agent may propose an action, but AgentGuard retains execution authority by evaluating organizational policy before the action can proceed.

The platform supports three core governance outcomes:

- `ALLOW` - the action may proceed automatically.
- `DENY` - the action is blocked.
- `REQUIRES_APPROVAL` - the action is paused until an authorized human reviewer approves or rejects it.

Every request is correlated with the policy decision, approval state, execution result, and audit evidence.

## Why AgentGuard?

Many agent frameworks already support human-in-the-loop workflows. AgentGuard addresses a broader governance problem: **centralized, deterministic control across agents, tools, resources, policies, approvals, and audit evidence**.

The project is particularly useful for action-taking agents where the cost of an incorrect action is materially higher than the cost of an incorrect answer.

Examples include:

- **Finance:** low-value operations may be allowed, high-value refunds may require approval, and unauthorized transfers may be denied.
- **Cloud / DevOps:** log reads may be automatic, production restarts may require approval, and destructive production operations may be denied.
- **Cybersecurity:** investigation may be automatic while disabling accounts or changing network controls requires authorization.
- **Customer support:** drafting or reading low-risk data may be allowed while sensitive account actions require review.
- **Healthcare / insurance:** summarization may be automatic while sensitive disclosures or consequential record changes require stricter control.

AgentGuard does **not** claim that every conversational or read-only agent requires this architecture. Its strongest use case is an agent that can take consequential actions in external systems.

## Final Demonstration Scenarios

The current Capstone demo uses a customer-support governance scenario because it is deterministic and repeatable:

| Scenario | Example | Expected governance |
|---|---|---|
| Safe | Read `customer_profile` in sandbox | `ALLOW` |
| Sensitive | Read `customer_transactions` in sandbox | `REQUIRES_APPROVAL` |
| Critical / prohibited | Access protected profile in production | `DENY` |

The same governance pattern can be applied to higher-risk operational agents. For example, a production database-backup deletion could require stronger approval controls. Multi-stage approval is an architectural extension and is **not claimed as implemented in this release**.

## Architecture

```text
AI Agent / Human Request
          |
          v
   Security Guardrails
          |
          v
 Deterministic Policy Engine
    /       |        \
 allow     deny    requires_approval
   |         |           |
   |      blocked    Human Review
   |                     |
   +----------+----------+
              v
      Tool Execution Gateway
        /             \
   mock:// adapter    mcp:// adapter
              |
              v
     Correlated Audit Trail
```

AI planning and AI-generated explanations are deliberately separated from authorization. A model can propose an action or explain an already-final decision, but it cannot override the deterministic policy result.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Yarn |
| Backend | Python, FastAPI |
| ORM / data layer | SQLModel / SQLAlchemy |
| Primary database | PostgreSQL 16 |
| Database migrations | Alembic |
| Policy engine | Custom deterministic policy engine |
| Human oversight | Approval workflow with self-approval prevention |
| Tool execution | Governed execution gateway with idempotency |
| Agent integration | Mock planner + OpenAI-compatible provider abstraction |
| MCP integration | Mock-safe mode + streamable-HTTP MCP adapter |
| Testing | Pytest, FastAPI TestClient, TypeScript strict checking, production build |
| CI/CD | GitHub Actions |
| Local reproducibility | Docker Compose or native PostgreSQL/Python/Yarn |

## Implemented Capabilities

### Governance

- Agent, tool, protected-resource, user, policy, approval, execution, and audit models.
- Versioned policies with priority and conflict handling.
- Context-aware deterministic evaluation.
- Default-deny behavior.
- Dry-run policy simulation.
- `ALLOW`, `DENY`, and `REQUIRES_APPROVAL`.
- Unique correlation IDs.

### Human Approval

- Pending, approved, rejected, cancelled, and expired approval states.
- Independent reviewer enforcement.
- Prevention of requester self-approval.
- Reviewer notes and timestamps.
- Execution only after the required approval state is satisfied.

### Governed Execution

- Provider-neutral tool-execution service.
- Idempotency keys.
- Attempt counters and failure states.
- Mock tool provider for deterministic testing.
- MCP execution adapter.

### AI / Agent Layer

- Structured agent planning.
- Deterministic mock provider for CI and demos.
- OpenAI-compatible provider abstraction.
- Grounded decision explanations.
- AI output cannot modify policy authorization.

### Security / Safety

- Role-based API authorization.
- Prompt-injection checks.
- Unsafe argument validation.
- Payload limits.
- Secret redaction.
- Security response headers.
- Default-deny policy behavior.

### Auditability

- Correlated audit events.
- Actor, request, policy, decision, approval, and execution evidence.
- Filtering and export support.
- Governance dashboard / cockpit.

## Important Authentication Scope

The current Capstone release uses **demonstration bearer tokens** for the Admin, Developer, Approver, and Auditor roles:

```text
admin-token
developer-token
approver-token
auditor-token
```

This is a deliberate Capstone demonstration mechanism, not a claim of enterprise identity management. Production SSO, password/token lifecycle management, MFA, and external identity-provider integration are future hardening items unless separately implemented before submission.

## MCP Scope

Local development and CI use deterministic mock mode:

```bash
export MCP_MOCK_MODE=true
```

The application also contains a remote MCP adapter. To connect an actual streamable-HTTP MCP endpoint:

```bash
export MCP_MOCK_MODE=false
export MCP_SERVER_URL="https://your-mcp-server.example/mcp"
export MCP_AUTH_TOKEN="your-secret-token"
```

A real external MCP provider should only be claimed as demonstrated if it has actually been configured and tested.

## AI Provider Scope

Local development and CI use a deterministic provider:

```bash
export AI_PROVIDER=mock
```

An OpenAI-compatible provider can be configured through environment variables. AI planning and explanations remain outside the authorization decision.

## Quick Start

### Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
Frontend: http://localhost:5173
API:      http://localhost:8000
Swagger:  http://localhost:8000/docs
Health:   http://localhost:8000/health
```

### Backend - Native

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

export DATABASE_URL="postgresql+psycopg://agentguard:agentguard_dev_password@localhost:5432/agentguard"

alembic upgrade head

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend - Native

```bash
cd apps/web

nvm use 20
corepack enable
corepack prepare yarn@1.22.22 --activate

yarn install --frozen-lockfile
yarn typecheck
yarn build
yarn dev
```

## Database Migrations

```bash
cd apps/api
alembic upgrade head
alembic current
alembic history
```

Current schema head in this repository:

```text
20260808_0002
```

Sprint 4 did not require an additional database migration in the current submitted codebase.

## Testing and CI

Backend:

```bash
cd apps/api
pytest -q
```

The latest verified `main` GitHub Actions backend run used PostgreSQL 16, applied Alembic migrations, and completed **41 passing backend tests**.

Frontend:

```bash
cd apps/web
yarn install --frozen-lockfile
yarn typecheck
yarn build
```

The latest verified `main` frontend GitHub Actions build completed successfully.

See [Final Design and Testing](docs/FINAL_DESIGN_AND_TESTING.md) for the complete testing strategy, architecture decisions, limitations, and evidence expectations.

## Four-Sprint Evolution

### Sprint 1 - Foundation

- FastAPI and React foundation.
- Agent/resource/policy/audit prototype.
- Initial tests and CI/CD.
- Lightweight initial persistence.

### Sprint 2 - Deterministic Governance and PostgreSQL

- PostgreSQL 16.
- Alembic migrations.
- Versioned/context-aware policies.
- Deterministic priority/conflict handling.
- Audit filtering/export.
- PostgreSQL-backed CI.

### Sprint 3 - Human Approval, Agent, MCP, and Governed Execution

- Full approval lifecycle.
- Self-approval prevention.
- Governed tool execution.
- Agent runtime.
- MCP adapter.
- AI explanations.
- Security guardrails.

### Sprint 4 - Final UI, Release Readiness, and Submission Preparation

- Enhanced governance cockpit.
- Release-readiness views and endpoints.
- Security headers.
- Final documentation and demo preparation.
- `v1.0.0` release tag.

## Repository Structure

```text
apps/
  api/                  FastAPI backend
  web/                  React/Vite frontend

docs/
  adr/                  Architecture decision records
  FINAL_DESIGN_AND_TESTING.md
  FINAL_DEPLOYMENT_AND_COSTS.md
  FINAL_TRACEABILITY_MATRIX.md

policy/
  examples/
  rego/

scripts/
  seed_demo_data.py

sprints/
  sprint_1/
  sprint_2/
  sprint_3/
  sprint_4/
```

## Final Submission Links

The following links identify the final AgentGuard Capstone submission artifacts.

- **GitHub repository:**  
  https://github.com/El-Moatasem/agentguard-ai-governance-platform

- **Jira / agile task board:**  
  https://elmoatasemsworkspace-17475588.atlassian.net/jira/software/projects/KAN/summary

- **Production frontend:**  
  https://agentguard-web-iqtl.onrender.com/

- **Production backend:**  
  https://agentguard-ai-governance-platform.onrender.com/

- **Swagger API documentation:**  
  https://agentguard-ai-governance-platform.onrender.com/docs

- **Final design and testing document:**  
  https://github.com/El-Moatasem/agentguard-ai-governance-platform/blob/main/docs/FINAL_DESIGN_AND_TESTING.md


- **Release tag:**  
  `v1.0.0`

Before submission:

1. Share the repository with the GitHub account `quantic-grader`.
2. Verify the GitHub repository, Jira board, production frontend, production backend, Swagger API, and design/testing document from an incognito/private browser window.
3. Replace the final demo video placeholder with the Google Drive URL after recording.
4. Ensure the final video is a single `.mp4` or `.mov`, is 15-20 minutes, and is shared from Google Drive as **Anyone with the link can view**.
5. Ensure the deployed application remains reachable during grading.
## Limitations

AgentGuard is a Capstone-grade governance prototype rather than a universal enterprise governance product.

Current limitations include:

- demonstration-token authentication in the current codebase;
- no claim of universal compatibility with every agent framework;
- remote MCP requires external configuration and verification;
- multi-stage / two-level approval is an architectural extension, not an implemented feature;
- production SSO/MFA, enterprise policy administration, HA/disaster recovery, and formal regulatory certification are outside the current Capstone scope.

## Academic Integrity and Attribution

AI-assisted tools were used to support planning, scaffolding, review, test generation, documentation, and presentation preparation. All submitted content should be reviewed, understood, tested, adapted, and explained by the project author.

Third-party libraries, references, and notices are documented in `docs/THIRD_PARTY_NOTICES.md`.

Do not submit external code as original work without appropriate attribution.

## License / Use

This repository is an academic Capstone artifact. Review all third-party licenses before production reuse.

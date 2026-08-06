# AgentGuard: AI Agent Governance, Access Control, and Audit Platform

AgentGuard is a Quantic MSSE Capstone project that demonstrates a governance layer for AI agents. It registers agent identities and protected capabilities, evaluates requested actions through deterministic policies, routes sensitive actions toward human review, and records traceable audit evidence.

> **Current release:** Sprint 2 release candidate, version `0.2.0`. This is not yet the final Capstone submission.

## Sprint 2 Capabilities

- Demonstration authentication and role-based access for administrator, developer, approver, and auditor roles.
- AI-agent, tool, and protected-resource registries.
- Versioned policy lifecycle: create, update, activate, deactivate, inspect history, and dry-run tests.
- Deterministic `allow`, `deny`, and `requires_approval` outcomes.
- Explicit policy conflict resolution and default deny.
- Nested contextual conditions such as `context.amount` and `context.country`.
- Stored action requests with unique correlation IDs and matched-policy details.
- Searchable audit events with CSV and JSON exports.
- Governance metrics for active policies and decision outcomes.
- PostgreSQL 16 through Docker Compose.
- Alembic database migrations.
- React/TypeScript Sprint 2 dashboard.
- GitHub Actions workflows for PostgreSQL-backed backend tests and Yarn frontend builds.
- Jira-ready Sprint 1 and Sprint 2 stories/tasks.

## Deferred to Later Sprints

- Completed human-approval execution/resume workflow.
- Real OpenAI agent and MCP/Zapier integration.
- OIDC/SSO authentication.
- Real LLM-based policy explanations and evaluation.
- Production deployment and monitoring.
- Security hardening, performance testing, and final presentation evidence.

## Repository Links to Add Before Submission

- Deployed application: `TODO: add production URL`
- Official agile board: `TODO: add Jira or GitHub Project URL`
- Final demo video: `TODO: add Google Drive MP4 URL`

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Yarn |
| Backend | Python, FastAPI, SQLModel |
| Primary database | PostgreSQL 16 |
| Local fallback | SQLite through `DATABASE_URL` |
| Migrations | Alembic |
| Policy engine | Custom deterministic policy adapter |
| Authentication | Demonstration bearer tokens |
| Testing | Pytest, FastAPI TestClient, TypeScript strict checking |
| DevOps | Docker Compose and GitHub Actions |

## Recommended Quick Start: Docker Compose

Docker is not a mandatory Capstone technology, but it is the recommended AgentGuard setup because it reproduces the PostgreSQL-backed environment.

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Web application: `http://localhost:5173`
- API root: `http://localhost:8000`
- Swagger API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Stop the application:

```bash
docker compose down
```

Reset all local PostgreSQL data:

```bash
docker compose down -v
```

## Manual Development with Yarn

### Backend

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./agentguard.db
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Use a PostgreSQL `DATABASE_URL` instead of SQLite when testing production-oriented behavior.

### Frontend

```bash
cd apps/web
corepack enable
corepack prepare yarn@1.22.22 --activate
yarn install --frozen-lockfile
yarn dev
```

## Demonstration Roles

```text
admin-token
developer-token
approver-token
auditor-token
```

The UI includes a demonstration-role switcher. In Swagger, use **Authorize** and provide a token.

## Database Migrations

Apply all migrations:

```bash
cd apps/api
alembic upgrade head
```

Create a future migration after changing models:

```bash
alembic revision --autogenerate -m "describe the schema change"
```

Inspect the current revision:

```bash
alembic current
```

## Testing

Backend:

```bash
cd apps/api
pytest -q
```

Sprint 2 generated-release verification: **19 passed**.

Frontend:

```bash
cd apps/web
yarn install --frozen-lockfile
yarn build
```

## Sprint and Jira Material

- [Sprint 1 stories and tasks](sprints/sprint_1/Sprint_1_User_Stories_and_Tasks.md)
- [Sprint 1 Jira import](sprints/sprint_1/jira_import_sprint_1.csv)
- [Sprint 2 stories and tasks](sprints/sprint_2/Sprint_2_User_Stories_and_Tasks.md)
- [Sprint 2 release notes](sprints/sprint_2/AgentGuard_Sprint2_Release_Notes.md)
- [Sprint 2 Jira import](sprints/sprint_2/jira_import_sprint_2.csv)
- [Jira setup guide](docs/Jira_Setup_and_Import_Guide.md)
- [What changed in Sprint 2](docs/What_Changed_in_Sprint_2.md)

## Architecture and Design

- [Architecture](docs/architecture.md)
- [Design and testing](docs/design-and-testing.md)
- [Threat model](docs/threat-model.md)
- [AI evaluation plan](docs/ai-evaluation.md)
- [Sprint plan](docs/sprint-plan.md)

## Academic Integrity

Review, understand, run, test, and modify the generated source before presenting it as your work. Keep an accurate task board, commit history, architectural decisions, test evidence, and sprint demonstrations. Attribute external templates, libraries, and borrowed code where applicable.

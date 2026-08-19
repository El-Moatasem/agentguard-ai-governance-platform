# AgentGuard: AI Agent Governance, Access Control, and Audit Platform

AgentGuard is a Quantic MSSE Capstone project that places a deterministic governance gateway between AI agents and external tools. It registers agents and tools, evaluates every requested action against versioned policies, pauses sensitive actions for independent human approval, executes only authorized tools, and records correlated audit evidence.

> **Current release:** Sprint 3, version `0.3.0`. Sprint 4 will focus on production hardening, deployment, final testing, and submission evidence.

## Sprint 3 Capabilities

- PostgreSQL 16 primary database with Alembic schema migrations.
- Demonstration authentication and role-based access for administrator, developer, approver, and auditor roles.
- Agent, tool, and protected-resource registries.
- Versioned deterministic policies with priority/conflict handling, context conditions, dry-run evaluation, and default deny.
- `allow`, `deny`, and `requires_approval` outcomes with unique correlation IDs.
- Complete approval lifecycle: pending, approved, rejected, cancelled, and expired.
- Independent-review rule that prevents requesters from approving or rejecting their own governed action.
- Tool execution gateway with idempotency, attempt counts, success/failure states, safe retry rules, and audit evidence.
- `mock://` deterministic tool adapter and `mcp://` MCP adapter.
- Configurable streamable-HTTP MCP integration with local/CI mock mode.
- Agent runtime with a mock planner and configurable OpenAI-compatible planning provider.
- Grounded AI decision explanations that cannot modify authorization.
- Prompt-injection checks, unsafe-argument validation, payload limits, and secret redaction.
- React/TypeScript Sprint 3 governance UI for agent runs, approvals, executions, explanations, policies, and audit evidence.
- GitHub Actions for PostgreSQL-backed backend tests and Yarn frontend builds.
- Jira-ready Sprint 1-3 stories/tasks and Sprint 3 demo/release material.

## Sprint 3 Architecture

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

AI planning and explanation are deliberately separated from authorization. A model may propose a registered tool or explain an already-final result, but only the deterministic policy engine can authorize execution.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Yarn |
| Backend | Python, FastAPI, SQLModel/SQLAlchemy |
| Primary database | PostgreSQL 16 |
| Migrations | Alembic |
| Policy engine | Custom deterministic policy engine |
| Agent/AI adapter | Mock + OpenAI-compatible chat-completions adapter |
| Tool integrations | Mock adapter + MCP streamable-HTTP adapter |
| Testing | Pytest, FastAPI TestClient, TypeScript strict checking |
| DevOps | Docker Compose and GitHub Actions |

## Quick Start with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
Web:     http://localhost:5173
API:     http://localhost:8000
Swagger: http://localhost:8000/docs
Health:  http://localhost:8000/health
```

Stop/reset:

```bash
docker compose down
docker compose down -v
```

## Manual Local Development

### Backend

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

### Frontend

```bash
cd apps/web
corepack enable
corepack prepare yarn@1.22.22 --activate
yarn install --frozen-lockfile
yarn typecheck
yarn build
yarn dev
```

## Demonstration Roles

```text
admin-token
developer-token
approver-token
auditor-token
```

The role switcher is intentionally a Capstone demonstration mechanism. Sprint 4 replaces it with production-oriented authentication.

## MCP Integration

The default mode is safe and deterministic:

```bash
export MCP_MOCK_MODE=true
```

To connect an actual streamable-HTTP MCP endpoint:

```bash
export MCP_MOCK_MODE=false
export MCP_SERVER_URL="https://your-mcp-server.example/mcp"
export MCP_AUTH_TOKEN="your-secret-token"
```

Registered `mcp://tool_name` entries are still governed by AgentGuard before `tools/call` is invoked.

## AI Provider Integration

Local development and CI use the mock/deterministic provider:

```bash
export AI_PROVIDER=mock
```

A compatible model provider can be configured without changing the governance path:

```bash
export AI_PROVIDER=openai_compatible
export AI_BASE_URL="https://api.openai.com/v1"
export AI_API_KEY="your-secret-key"
export AI_MODEL="gpt-5-mini"
```

Never commit API or MCP credentials.

## Database Migrations

```bash
cd apps/api
alembic upgrade head
alembic current
alembic history
```

Sprint 3 head:

```text
20260808_0002
```

## Testing

Backend:

```bash
cd apps/api
pytest -q
```

Generated Sprint 3 verification: **37 backend tests passed** after applying migrations to a fresh database.

Frontend:

```bash
cd apps/web
yarn install --frozen-lockfile
yarn typecheck
yarn build
```

## Sprint Material

- `sprints/sprint_1/` - Sprint 1 foundation evidence.
- `sprints/sprint_2/` - Sprint 2 PostgreSQL/policy evidence.
- `sprints/sprint_3/Sprint_3_User_Stories_and_Tasks.md` - Sprint 3 Jira story/task detail.
- `sprints/sprint_3/jira_import_sprint_3.csv` - Jira import file.
- `sprints/sprint_3/AgentGuard_Sprint3_Release_Notes.md` - release evidence.
- `sprints/sprint_3/Sprint_3_Demo_Script.md` - sprint review/demo sequence.
- `docs/architecture-sprint3.md` - Sprint 3 execution and trust-boundary architecture.
- `docs/sprint3-security-and-ai-evaluation.md` - guardrails and AI evaluation contract.

## Repository Links to Add Before Final Submission

```text
Production deployment: TODO Sprint 4
Official Jira board:    TODO add accessible board URL
Final demo video:       TODO Sprint 4 Google Drive link
```

## Academic Integrity

AI-assisted tools may support planning, scaffolding, code review, testing, and documentation, but all submitted code should be reviewed, understood, tested, adapted, and explained by the project author. Maintain accurate Jira status, commit/PR history, test evidence, architectural decisions, sprint demos, and third-party attribution.

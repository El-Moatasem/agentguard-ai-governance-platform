# AgentGuard: AI Agent Governance, Access Control, and Audit Platform

AgentGuard is an MSSE Capstone project that demonstrates a production-style governance layer for AI agents. The platform allows an organization to register AI agents and tools, define deterministic access policies, require human approval for sensitive actions, and audit every decision.

> Capstone focus: full-stack engineering, software architecture, AI engineering support, security, automated testing, CI/CD, cloud deployment, and agile delivery as a solo student.

## MVP Features

- Role-based access model for administrator, developer, approver, and auditor users.
- AI agent, tool, and protected resource registry.
- Policy management with `allow`, `deny`, and `requires_approval` outcomes.
- Deterministic policy-decision engine with default-deny behavior.
- Request simulator for testing agent actions before production use.
- Human-in-the-loop approval workflow for sensitive actions.
- Searchable audit trail for decisions, approvals, and denials.
- Governance dashboard showing total agents, policies, approvals, and audit events.
- AI-support module that explains policy decisions without controlling the authorization result.
- Dockerized local development, CI workflow examples, and documentation for final submission.

## Repository Links to Add Before Submission

- Deployed application: `TODO: add production URL`
- Agile board: `TODO: add GitHub Project or Trello board URL`
- Demo video: `TODO: add Google Drive MP4 URL with Anyone with the link can view`

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI, SQLModel |
| Database | SQLite for local demo, PostgreSQL-ready via `DATABASE_URL` |
| Policy Engine | Custom deterministic policy adapter, with OPA extension point |
| Auth | Demo bearer-token auth for capstone MVP |
| Testing | Pytest, FastAPI TestClient, Vitest-ready frontend |
| DevOps | Docker Compose, GitHub Actions templates |
| Deployment | Render, Railway, Fly.io, or similar free/low-cost host |

## Quick Start

Detailed instructions: [`docs/running-locally.md`](docs/running-locally.md)

### 1. Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: <http://localhost:8000/docs>

Demo tokens:

```text
admin-token
approver-token
auditor-token
developer-token
```

### 2. Frontend

```bash
cd apps/web
npm install
npm run dev
```

Open: <http://localhost:5173>

### 3. Docker Compose

```bash
docker compose up --build
```

## Demo Flow

1. Log in using `admin-token`.
2. Review seeded agents and protected resources.
3. Create or inspect policies.
4. Use the simulator to submit an action request.
5. Observe an allow, deny, or approval-required decision.
6. Approve or reject a request from the approval queue.
7. Review audit logs and dashboard metrics.
8. Open `/docs` to show API documentation.

## Solo Capstone Delivery Plan

See [`docs/sprint-plan.md`](docs/sprint-plan.md) for the 14-week timeline, sprint goals, deliverables, and demonstration checkpoints.

## Architecture and Design

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/design-and-testing.md`](docs/design-and-testing.md)
- [`docs/threat-model.md`](docs/threat-model.md)
- [`docs/ai-evaluation.md`](docs/ai-evaluation.md)

## Testing

```bash
cd apps/api
pytest -q
```

Recommended final quality targets:

- Policy decision branches fully tested.
- Auth and role-based access tested.
- Critical API flows tested.
- End-to-end happy path recorded in the final demo.
- CI green before final submission.

## License

Use an appropriate license for your capstone repository, or keep the repository private and accessible to Quantic reviewers only.

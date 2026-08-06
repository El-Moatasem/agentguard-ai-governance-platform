# Running AgentGuard v0.2.0 Locally

## Recommended Environment

Use Docker Compose for the complete Sprint 2 environment because it starts PostgreSQL, applies Alembic migrations, starts FastAPI, and runs the React frontend.

## Prerequisites

- Docker Desktop with Docker Compose, or:
- Python 3.11 or newer
- Node.js 20 or newer
- Yarn 1.22 through Corepack
- PostgreSQL 16 when not using Docker and when testing the primary architecture

## Option A — Docker Compose with PostgreSQL

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

Services:

| Service | Address |
|---|---|
| Frontend | `http://localhost:5173` |
| API | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| Health | `http://localhost:8000/health` |
| PostgreSQL | `localhost:5432` |

Stop services:

```bash
docker compose down
```

Remove the local database volume and rebuild from migrations:

```bash
docker compose down -v
docker compose up --build
```

## Option B — Manual PostgreSQL Development

Create a PostgreSQL database and export a connection string:

```bash
export DATABASE_URL=postgresql+psycopg://agentguard:YOUR_PASSWORD@localhost:5432/agentguard
```

Run the backend:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Option C — Lightweight SQLite Fallback

SQLite is retained for isolated development or test convenience, not as the final production database.

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./agentguard.db
alembic upgrade head
uvicorn app.main:app --reload
```

Reset SQLite:

```bash
rm -f agentguard.db
alembic upgrade head
```

## Frontend with Yarn

In a separate terminal:

```bash
cd apps/web
corepack enable
corepack prepare yarn@1.22.22 --activate
yarn install --frozen-lockfile
yarn dev
```

Do not commit both `package-lock.json` and `yarn.lock`. AgentGuard uses `yarn.lock`.

## Demo Tokens

```text
admin-token
developer-token
approver-token
auditor-token
```

## Database Access

### Docker PostgreSQL shell

```bash
docker compose exec db psql -U agentguard -d agentguard
```

Useful commands:

```sql
\dt
SELECT id, name, effect, priority, active, version FROM policy ORDER BY priority DESC;
SELECT correlation_id, agent_name, action, resource_name, decision FROM actionrequest ORDER BY created_at DESC;
SELECT event_type, result, actor_email, created_at FROM auditevent ORDER BY created_at DESC;
\q
```

### Migration commands

```bash
cd apps/api
alembic current
alembic history
alembic upgrade head
```

## Verification

Backend tests:

```bash
cd apps/api
pytest -q
```

Frontend build:

```bash
cd apps/web
yarn build
```

## Common Problems

### Port 5432 already in use

Stop the existing PostgreSQL service or change the Docker host port while keeping the container port at 5432.

### Existing Sprint 1 schema conflicts

Sprint 2 adds a formal migration baseline and new required columns. Reset the local development database:

```bash
docker compose down -v
```

or remove the SQLite database and rerun `alembic upgrade head`.

### Frontend cannot reach the API

Confirm that `http://localhost:8000/health` works and that `VITE_API_BASE_URL` points to `http://localhost:8000/api/v1`.

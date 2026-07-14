# Running AgentGuard Locally

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- Docker Desktop with Docker Compose, if using the container option

## Option A: Docker Compose

From the repository root:

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:5173
- API documentation: http://localhost:8000/docs
- API health check: http://localhost:8000/health

Stop the project with `Ctrl+C`, then run:

```bash
docker compose down
```

## Option B: Run the Backend and Frontend Separately

### Backend

From the repository root:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The backend automatically creates the SQLite database and inserts demo data on first startup.

### Frontend

Open a second terminal from the repository root:

```bash
cd apps/web
npm ci
npm run dev
```

Open http://localhost:5173.

## Demo Tokens

The frontend defaults to `admin-token`. Other available tokens are:

```text
admin-token
developer-token
approver-token
auditor-token
```

To switch the active demo user, open the browser console and run:

```javascript
localStorage.setItem("agentguard_token", "approver-token");
location.reload();
```

## Verification

Run the backend tests:

```bash
cd apps/api
pytest -q
```

Build the frontend:

```bash
cd apps/web
npm ci
npm run build
```

Expected backend test result for the starter version: `6 passed`.

## Reset Demo Data

Stop the API and remove the local SQLite file:

```bash
rm -f apps/api/agentguard.db
```

Restart the API. The application will recreate and seed the database.

## Common Problems

### Port already in use

Stop the process using ports `8000` or `5173`, or start the service on a different port. If the API port changes, set `VITE_API_BASE_URL` before starting the frontend.

### Frontend cannot reach the API

Confirm that the API health endpoint works at http://localhost:8000/health and that CORS includes http://localhost:5173.

### Docker command not found

Install and start Docker Desktop, or use the manual backend/frontend steps instead.

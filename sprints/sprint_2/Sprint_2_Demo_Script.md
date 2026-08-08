# AgentGuard Sprint 2 Demonstration Script

**Target duration:** 8–12 minutes for the sprint review. This is separate from the final 15–20 minute Capstone presentation.

## Preparation

- Start the application using `docker compose up --build`.
- Confirm PostgreSQL, API, and frontend health.
- Open the web application and Swagger documentation.
- Keep a terminal ready for `pytest -q` and `alembic current`.

## Demo Sequence

| Time | Demonstration |
|---|---|
| 0:00–1:00 | State the Sprint 2 goal and show the Jira sprint board. |
| 1:00–2:00 | Show PostgreSQL in Docker Compose and the Alembic revision. |
| 2:00–3:30 | Create a new policy from the UI. Explain effect, priority, and conditions. |
| 3:30–4:30 | Update the policy through Swagger and show its version history. |
| 4:30–6:30 | Run allow, approval-required, and deny scenarios. Highlight matched policy and correlation ID. |
| 6:30–7:30 | Retrieve a stored action request and explain default deny and tie-breaking. |
| 7:30–9:00 | Filter audit events and export CSV and JSON. |
| 9:00–10:00 | Show metrics, automated tests, and CI workflows. |
| 10:00–11:00 | Summarize limitations and Sprint 3 work. |

## Required Scenarios

### Allow

```json
{
  "agent_name": "customer-support-agent",
  "user_email": "developer@demo.local",
  "action": "read",
  "resource_name": "customer_profile",
  "environment": "sandbox",
  "context": {"customer_id": "C-10045", "country": "Kenya"}
}
```

### Requires approval

Use the same user and agent with:

```json
{
  "action": "read",
  "resource_name": "customer_transactions",
  "environment": "sandbox"
}
```

### Deny

Use the support agent in production:

```json
{
  "action": "read",
  "resource_name": "customer_profile",
  "environment": "production"
}
```

## Evidence to Attach to Jira

- Screenshot or recording of the sprint demo.
- Backend test output.
- Frontend build output from the local machine or CI.
- `alembic current` output.
- Screenshot of PostgreSQL tables or Docker services.
- Links to commits or pull requests for each story.

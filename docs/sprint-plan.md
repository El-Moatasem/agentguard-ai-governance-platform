# AgentGuard Solo Capstone Sprint Plan

This plan organizes the project into four development sprints plus final submission preparation. The official task board should contain the detailed stories, tasks, evidence, and status history.

## Solo Roles

| Role | Owner |
|---|---|
| Product Owner | El-Moatasem Madani |
| Scrum Master | El-Moatasem Madani |
| Backend / Frontend Code Owner | El-Moatasem Madani |
| QA and Release Owner | El-Moatasem Madani |

## Project Conception — Weeks 1–2

- Confirm problem, users, value, scope, exclusions, and risks.
- Create repository and official agile board.
- Produce architecture, ADRs, product backlog, and Definition of Done.

## Sprint 1 — Weeks 3–5: Foundation and Registry

**Status:** Foundation implemented; verify and attach your own evidence before marking the board Done.

**Goal:** Establish authentication/RBAC, agent/tool/resource registries, React/FastAPI foundations, local execution, Docker, CI, and initial tests.

**Evidence:**

- `sprints/sprint_1/Sprint_1_User_Stories_and_Tasks.md`
- `sprints/sprint_1/AgentGuard_Sprint1_Release_Notes.md`
- `sprints/sprint_1/jira_import_sprint_1.csv`

## Sprint 2 — Weeks 6–8: Policy Engine, PostgreSQL, and Audit Trail

**Status:** v0.2.0 release candidate generated; keep Jira items In Review until locally verified.

**Goal:** Adopt PostgreSQL and Alembic, implement versioned contextual policies, persist decisions, add correlation and query APIs, and provide searchable/exportable audit evidence.

**Evidence:**

- `sprints/sprint_2/Sprint_2_User_Stories_and_Tasks.md`
- `sprints/sprint_2/AgentGuard_Sprint2_Release_Notes.md`
- `sprints/sprint_2/Sprint_2_Demo_Script.md`
- `sprints/sprint_2/jira_import_sprint_2.csv`

## Sprint 3 — Weeks 9–11: Human Approval, Real Agent/MCP, and AI Explanation

**Goal:** Complete human-in-the-loop behavior and prove AgentGuard can govern one real agent/tool integration.

**Planned stories:**

- Prevent a requester from approving their own request.
- Add approval expiry, review details, and execution state.
- Resume or execute an approved action through a safe mock or test integration.
- Integrate one agent framework and one MCP provider or local MCP server.
- Govern two or three non-destructive test tools.
- Connect an optional LLM explanation adapter with structured output and grounding.
- Test that AI output cannot change the policy decision.

## Sprint 4 — Weeks 12–13: Hardening, Deployment, and Documentation

**Goal:** Stabilize the architecture already selected rather than introducing major database or framework changes.

**Planned stories:**

- Complete RBAC, organization-isolation, security, and malformed-input tests.
- Add rate limiting, structured logging, and health/readiness checks.
- Run performance and recovery tests.
- Deploy API, frontend, and managed PostgreSQL.
- Complete architecture, design/testing, threat-model, deployment, and cost documentation.
- Freeze MVP scope and complete regression testing.

## Week 14 — Final Submission

- Record the 15–20 minute final demonstration.
- Verify repository and task-board permissions.
- Share the repository with `quantic-grader`.
- Confirm deployed application and video links work in an incognito browser.
- Submit the required links and signed group agreement page if applicable.

## Database Evolution

| Sprint | Database plan |
|---|---|
| Sprint 1 | SQLite is acceptable for the initial prototype and basic demonstration. |
| Sprint 2 | PostgreSQL becomes primary; add Alembic migrations, constraints, indexes, and seed scripts. |
| Sprint 3 | Build approvals, agent/MCP integration, and audit workflows using PostgreSQL. |
| Sprint 4 | Test, optimize, secure, deploy, and document without changing the main database architecture. |

## Definition of Done

A board item is Done only when:

- Acceptance criteria are demonstrated.
- Applicable automated tests pass.
- Code and documentation are committed.
- The board item links to evidence.
- No known critical defect blocks the feature.
- The work reflects your actual implementation and review process.

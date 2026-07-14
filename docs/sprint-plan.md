# AgentGuard Solo Capstone Sprint Plan

This timeline is designed for a solo MSSE capstone and maps the work into the required agile sprint structure. The goal is to produce a working deployed software/AI system, a GitHub repository, a task board, a design/testing document, and a 15-20 minute final demo.

## Roles

| Role | Owner |
|---|---|
| Product Owner | El-Moatasem Madani |
| Scrum Master | El-Moatasem Madani |
| Backend Code Owner | El-Moatasem Madani |
| Frontend Code Owner | El-Moatasem Madani |
| QA / Release Owner | El-Moatasem Madani |

## Week 1-2: Project Conception and Setup

**Goals**
- Confirm problem statement and scope.
- Create repository and task board.
- Define MVP, stretch goals, and risk boundaries.
- Produce initial architecture and user stories.

**Deliverables**
- README draft.
- Product backlog.
- Architecture diagram.
- Definition of Done.
- Sprint 1 plan.

## Sprint 1 — Weeks 3-5: Foundation and Registry

**Sprint Goal**
Build the foundation for the platform: authentication, agent registry, resource registry, database, and CI.

**User Stories**
- As an admin, I can authenticate using a demo token.
- As an admin, I can register and view AI agents.
- As an admin, I can register protected resources and tools.
- As a developer, I can view registered agents and resources.

**Engineering Tasks**
- FastAPI project structure.
- SQLModel database models.
- Seed demo data.
- React dashboard skeleton.
- Docker Compose setup.
- GitHub Actions backend and frontend workflows.

**Sprint Demo**
- Start the app.
- Show authentication and dashboard.
- Show agent/resource/tool registry.
- Show CI checks.

## Sprint 2 — Weeks 6-8: Policy Engine and Audit Trail

**Sprint Goal**
Evaluate agent requests against deterministic policies and audit every decision.

**User Stories**
- As an admin, I can create a policy.
- As a developer, I can simulate an agent action.
- As an auditor, I can review allowed, denied, and approval-required decisions.

**Engineering Tasks**
- Policy model and API.
- Deterministic policy evaluator.
- Request simulator endpoint.
- Audit event persistence.
- Dashboard metrics.
- Unit tests for policy matching and default-deny behavior.

**Sprint Demo**
- Create policies.
- Run allow, deny, and approval-required examples.
- Show audit records and tests.

## Sprint 3 — Weeks 9-11: Human Approval and AI Explanation

**Sprint Goal**
Add human-in-the-loop approval and AI-supported explanations.

**User Stories**
- As an approver, I can approve or reject sensitive requests.
- As an auditor, I can see who approved or rejected a request.
- As a developer, I can ask for a plain-language explanation of a policy decision.

**Engineering Tasks**
- Approval queue.
- Approval/rejection APIs.
- Audit events for review actions.
- Assistant explanation endpoint.
- Tests for approval transitions.
- Guardrail: AI cannot override policy decisions.

**Sprint Demo**
- Simulate a restricted transaction request.
- Approve the pending request.
- Show audit trail and explanation.

## Sprint 4 — Weeks 12-13: Hardening, Deployment, and Documentation

**Sprint Goal**
Prepare the final capstone submission and deployed demo.

**User Stories**
- As a reviewer, I can run the project locally from the README.
- As a reviewer, I can open the deployed application.
- As a reviewer, I can inspect tests, architecture, and CI evidence.

**Engineering Tasks**
- Finish documentation.
- Add security review and threat model.
- Run full regression tests.
- Deploy backend and frontend.
- Test production environment.
- Freeze MVP scope.

**Sprint Demo**
- Complete end-to-end run from login to audit.
- Show deployment link.
- Show test and CI evidence.

## Week 14: Final Submission

**Tasks**
- Record final 15-20 minute demo.
- Share repository with `quantic-grader`.
- Confirm task board is accessible.
- Confirm deployed app link works.
- Confirm Google Drive demo video permissions.
- Submit all links through the Quantic dashboard.

## Definition of Done

A task is Done when:

- The feature works locally.
- API behavior is tested when applicable.
- UI work has a screenshot or demo evidence.
- Documentation is updated.
- No known critical defect remains.
- Work is linked to a GitHub issue or board card.

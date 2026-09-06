# AgentGuard Final Requirements and Traceability Matrix

| Capability / requirement | Implementation evidence | Test / verification evidence | Final status |
|---|---|---|---|
| Agent registry | `apps/api/app/models.py`, agents router, UI | API/manual demo | Implemented |
| Protected resources/tools | Models + registry routes | API/manual demo | Implemented |
| Versioned policies | Policy + PolicyVersion models/routes | Sprint 2 policy tests | Implemented |
| Deterministic evaluation | `services/policy_engine.py` | Unit tests | Implemented |
| ALLOW | Decision/governance service | Decision tests + demo | Implemented |
| DENY | Decision/governance service | Production deny test + demo | Implemented |
| REQUIRES_APPROVAL | Decision/governance service | Decision/approval tests | Implemented |
| Human approval lifecycle | Approval model/router | Sprint 3 approval tests | Implemented |
| Self-approval prevention | Approval rules | Sprint 3 tests | Implemented |
| Governed tool execution | `services/tool_execution.py` | Sprint 3 execution tests | Implemented |
| Idempotency | ToolExecution idempotency key | Execution tests | Implemented |
| MCP adapter | integrations/execution services | Mock/security tests | Implemented adapter; real provider requires configuration |
| Agent runtime | agent runtime router/service | Sprint 3 tests | Implemented |
| AI explanations | AI provider + assistant router | Explanation tests | Implemented |
| AI cannot override auth | Architecture + deterministic engine | Code boundary/tests | Implemented |
| Audit trail | AuditEvent + audit service/router | Audit tests/export demo | Implemented |
| PostgreSQL | SQLModel/SQLAlchemy | GitHub CI Postgres 16 | Implemented |
| Alembic | migrations | CI `alembic upgrade head` | Implemented |
| Frontend UI | React/Vite | CI typecheck/build | Implemented |
| CI/CD | GitHub Actions | current `main` checks green | Implemented |
| Deployment link | external hosting | incognito smoke test | **Pending before submission** |
| Accessible Jira board | Jira | external access check | **Pending link before submission** |
| Final 15-20 min video | Google Drive | playback/access check | **Pending before submission** |
| `quantic-grader` access | GitHub collaborator | access verification | **Must verify before submission** |
| Production SSO/password auth | not in current code | none | Future work unless implemented |
| Rate-limit enforcement | config value only in current code | none | Future work unless implemented |
| Two-level approvals | not in current code | none | Future work |
| Browser Playwright E2E | not in current code | none | Future work unless implemented |

## Final Jira Rule

Do not mark a Jira story/task Done merely because the idea exists in a design document.

Use:

```text
Implementation
+ automated/manual verification
+ PR/commit evidence
+ acceptance criteria satisfied
= Done
```

If a Sprint 4 Jira item claims production authentication, rate limiting, Playwright E2E, performance testing, or disaster-recovery rehearsal and that evidence does not exist in the submitted code/project, either complete it or move it to future work with the scope decision documented.

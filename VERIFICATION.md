# Sprint 3 Generated-Release Verification

## Backend verification

A fresh SQLite validation database was used as a portable migration/test harness in the generation environment:

```bash
DATABASE_URL=sqlite:////tmp/agentguard_sprint3_test.db alembic upgrade head
DATABASE_URL=sqlite:////tmp/agentguard_sprint3_test.db pytest -q
```

Result:

```text
20260808_0002 (head)
37 passed
```

The repository CI remains PostgreSQL-backed and should be treated as the authoritative integration check after pushing the Sprint 3 branches.

## Frontend verification

The Sprint 3 TypeScript source passed strict `tsc --noEmit` checking in the generation environment using the uploaded project's React type packages.

Run the full Yarn production build locally/CI:

```bash
cd apps/web
yarn install --frozen-lockfile
yarn typecheck
yarn build
```

## Required user verification

Before merging Sprint 3 into `develop`, verify PostgreSQL migrations, all GitHub Actions checks, the approval-to-execution workflow, MCP mock/remote mode as applicable, agent guardrails, audit correlation, and the Sprint 3 demo scenarios.

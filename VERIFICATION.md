# Sprint 2 Generated-Release Verification

The source package was checked during generation using a clean validation database and the uploaded project's dependency metadata.

## Passed

- Python source compilation.
- Alembic baseline migration against a clean SQLite validation database.
- FastAPI startup and health/registry smoke requests.
- Backend automated test suite: **19 passed**.
- TypeScript strict type check: **passed**.
- Repository hygiene: no `.git`, virtual environment, `node_modules`, database file, `__pycache__`, or macOS metadata included in the release ZIP.

## To Run on Your Local Machine or GitHub Actions

```bash
cd apps/web
yarn install --frozen-lockfile
yarn build
```

A full Vite bundle was not produced in the generation container because the uploaded dependency folder contained a macOS-specific native Rolldown binding, while the generation environment was Linux and had no dependency-network access. The committed GitHub Actions workflow installs the correct platform dependencies before building.

## Before Moving Jira Stories to Done

- Run Docker Compose with PostgreSQL.
- Run `alembic current` and `pytest -q`.
- Run `yarn build`.
- Review and understand the code.
- Attach your own commits, screenshots, test output, and sprint-demo recording.

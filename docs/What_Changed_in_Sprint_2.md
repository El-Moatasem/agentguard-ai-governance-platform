# What Changed in Sprint 2

## At a Glance

The uploaded source already contained much of the basic policy, decision, approval, and audit prototype. Sprint 2 converts those prototypes into a more structured release with a production-oriented database path, formal migrations, versioned policies, richer deterministic evaluation, traceable requests, searchable exports, stronger UI workflows, and broader automated testing.

## Feature Comparison

| Area | Before Sprint 2 | Sprint 2 release candidate |
|---|---|---|
| Database | SQLite file and automatic table creation | PostgreSQL 16 in Docker, Alembic baseline migration, SQLite fallback |
| Schema integrity | Basic primary keys | Foreign keys, organization-scoped unique constraints, query indexes |
| Policies | Create, list, and deactivate | Create, retrieve, update, version history, activate, deactivate, filter |
| Policy matching | Scalar/list equality and priority order | Explicit tie-breaking, nested context paths, comparison/membership operators |
| Policy testing | Persisted simulation only | Dedicated dry-run evaluation without persistence |
| Decision records | Basic stored decision | Correlation ID, matched policy name, policy count, query APIs |
| Input validation | Request schema validation | Agent/resource existence plus condition-key/operator validation |
| Audit | Latest 100 events | Filters, pagination, correlation IDs, CSV export, JSON export |
| Dashboard | Counts for agents, policies, audits, pending approvals | Active-policy and decision-result breakdowns |
| Frontend | Fixed demo scenarios and simple lists | Role switcher, custom simulator, policy form/status controls, audit filters/exports |
| CI | Basic backend tests and npm build | PostgreSQL migration/test CI and Yarn frontend CI |
| Tests | 6 original backend tests | 19 passing backend tests in the generated release environment |
| Documentation | Foundation plans | Jira-ready stories, Sprint 2 release notes, database/migration and demo guidance |

## Important Scope Note

This package represents the **end-of-Sprint-2 release candidate**, not the final Capstone submission. Real agent/MCP integration, a completed approval-resume workflow, production authentication, AI explanations with a provider, production deployment, security hardening, and final presentation evidence belong to later sprints.

# Codebase Final Decisions - What Still Needs Code Changes?

## Short Answer

The Quantic handbook does **not** require production SSO, rate limiting, Playwright, multi-level approval, or enterprise-scale performance tooling by name.

It requires a working, high-quality system that meets its agreed requirements, documented architecture/testing, CI/CD, deployment, an accessible task board, and an outstanding final demonstration.

Therefore there are two different questions:

1. **What is required by Quantic?**
2. **What did your Sprint 4 Jira say you agreed to build?**

## Current Codebase Facts

The current `main` codebase:

- is tagged `v1.0.0`;
- has PostgreSQL/Alembic;
- has deterministic governance;
- has human approval;
- has governed execution;
- has agent/MCP adapters;
- has AI explanations;
- has audit evidence;
- has security headers;
- has 41 verified passing backend tests in GitHub CI;
- has a passing frontend type-check/build workflow.

## Code / Jira Mismatches to Resolve

### 1. Production authentication

Current code uses demonstration bearer tokens.

If Jira Story 410 says production-ready authentication is Done, either:

- implement production-oriented authentication; or
- change the story status/scope and document it as future work.

### 2. Rate limiting

`rate_limit_per_minute` exists in settings, but the current codebase does not contain rate-limit enforcement.

If Jira Task 432 is Done, either implement it or de-scope it.

### 3. Browser / component tests

Current frontend verification is TypeScript + production build. No Playwright/component suite is present.

If Jira Tasks 421/422 are Done, either implement those tests or de-scope them.

### 4. Performance / recovery verification

If Jira Stories 440/Tasks 441-443 are marked Done, there should be real performance, query-plan, backup/restore, and recovery evidence.

If not performed, keep them open or move them to future work.

### 5. CI branch filters

Current `main` CI is green. The workflow branch filters still emphasize earlier sprint branches.

This does not block final submission, but if you continue feature-branch development, update filters to match the active workflow.

## Recommended Minimal Submission Path

If you want to finalize quickly without expanding scope:

1. Keep the current codebase.
2. Make Jira accurately match what is implemented.
3. Do not claim production authentication/rate limiting/Playwright/multi-level approval.
4. Deploy the working system.
5. Complete the final documentation.
6. Record the deployed demo.
7. Submit.

## Recommended Stronger Engineering Path

If time allows, implement:

- production authentication;
- rate limiting;
- browser E2E;
- performance/recovery evidence.

These improve engineering depth, but deployment/documentation/video are more direct handbook blockers right now.

# Design and Testing Document

## Design Summary

AgentGuard provides a governance layer for AI agents. It evaluates each requested action against deterministic policies, records the result, and sends sensitive actions into a human approval queue.

## Key Design Decisions

### 1. Deterministic Policy Engine

The authorization result is produced by the policy engine, not by an LLM. This keeps the platform predictable, testable, and auditable.

### 2. Default Deny

If no active policy matches a request, the action is denied. This reduces accidental over-permission.

### 3. Human Approval for Sensitive Actions

Restricted resources and high-risk actions can return `requires_approval`, creating a pending approval record.

### 4. Audit Everything

Every decision and approval review is recorded as an audit event.

### 5. Demo Auth for Capstone MVP

The MVP uses demo bearer tokens to keep scope manageable. A production system would use OAuth/OIDC or enterprise SSO.

## Testing Plan

| Test Area | Examples |
|---|---|
| Unit tests | Policy matching, priority ordering, default deny |
| API tests | Auth required, dashboard returns metrics, decision flow |
| Integration tests | Decision creates action request and audit event |
| Security tests | Invalid token, wrong role, cross-organization access |
| Frontend tests | Simulator button actions, dashboard rendering |
| E2E tests | Agent action -> policy decision -> approval -> audit log |

## Current Automated Tests

- `tests/test_policy_engine.py`
- `tests/test_api_smoke.py`

## Manual Demo Test Script

1. Start backend and frontend.
2. Open API docs.
3. Use `admin-token` in the frontend.
4. Run customer-profile read simulation.
5. Run customer-transactions read simulation.
6. Approve a pending request.
7. Verify audit events updated.

## Acceptance Criteria

- All critical paths are demonstrable.
- Policy engine has test coverage for allow, deny, approval, and default-deny behavior.
- API documentation is available.
- Deployment link works from a clean browser session.
- README explains how to run and test the system.

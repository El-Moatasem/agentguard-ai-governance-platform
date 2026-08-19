from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

DEVELOPER = {"Authorization": "Bearer developer-token"}
APPROVER = {"Authorization": "Bearer approver-token"}
AUDITOR = {"Authorization": "Bearer auditor-token"}


def _execution(**overrides):
    payload = {
        "agent_name": "customer-support-agent",
        "tool_name": "Customer Profile API",
        "action": "read",
        "resource_name": "customer_profile",
        "environment": "sandbox",
        "arguments": {"customer_id": "C-10045"},
        "context": {"country": "Kenya"},
    }
    payload.update(overrides)
    return payload


def test_allowed_tool_request_executes_and_is_audited():
    with TestClient(app) as client:
        response = client.post("/api/v1/executions", headers=DEVELOPER, json=_execution())
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["decision"] == "allow"
        assert body["execution"]["status"] == "succeeded"
        events = client.get("/api/v1/audit-events", headers=AUDITOR, params={"correlation_id": body["correlation_id"]})
        assert events.status_code == 200
        assert {item["event_type"] for item in events.json()} >= {"policy_decision", "tool_execution"}


def test_denied_tool_request_is_never_executed():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/executions",
            headers=DEVELOPER,
            json=_execution(environment="production"),
        )
        assert response.status_code == 201
        body = response.json()
        assert body["decision"] == "deny"
        assert body["execution"]["status"] == "blocked"
        assert body["execution"]["attempt_count"] == 0


def test_approval_required_execution_runs_only_after_human_approval():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/executions",
            headers=DEVELOPER,
            json=_execution(
                agent_name="finance-ops-agent",
                tool_name="Refund API",
                action="execute",
                resource_name="refund_execution",
                arguments={"amount": 750, "currency": "USD"},
            ),
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["decision"] == "requires_approval"
        assert body["execution"]["status"] == "pending_approval"

        approved = client.post(
            f"/api/v1/approvals/{body['approval_id']}/approve",
            headers=APPROVER,
            json={"notes": "Validated refund evidence."},
        )
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "approved"

        execution = client.get(f"/api/v1/executions/{body['execution']['id']}", headers=APPROVER)
        assert execution.status_code == 200
        assert execution.json()["status"] == "succeeded"
        assert execution.json()["attempt_count"] == 1


def test_rejected_approval_cancels_pending_execution():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/executions",
            headers=DEVELOPER,
            json=_execution(
                agent_name="finance-ops-agent",
                tool_name="Refund API",
                action="execute",
                resource_name="refund_execution",
                arguments={"amount": 800},
            ),
        )
        body = response.json()
        rejected = client.post(
            f"/api/v1/approvals/{body['approval_id']}/reject",
            headers=APPROVER,
            json={"notes": "Insufficient evidence."},
        )
        assert rejected.status_code == 200
        execution = client.get(f"/api/v1/executions/{body['execution']['id']}", headers=APPROVER).json()
        assert execution["status"] == "cancelled"


def test_requester_can_cancel_pending_execution():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/executions",
            headers=DEVELOPER,
            json=_execution(
                agent_name="finance-ops-agent",
                tool_name="Refund API",
                action="execute",
                resource_name="refund_execution",
                arguments={"amount": 900},
            ),
        ).json()
        cancelled = client.post(
            f"/api/v1/approvals/{response['approval_id']}/cancel",
            headers=DEVELOPER,
            json={"notes": "Requester withdrew the action."},
        )
        assert cancelled.status_code == 200
        assert cancelled.json()["status"] == "cancelled"


def test_unallowlisted_tool_action_is_rejected_before_policy_evaluation():
    with TestClient(app) as client:
        response = client.post("/api/v1/executions", headers=DEVELOPER, json=_execution(action="delete"))
        assert response.status_code == 403


def test_idempotency_key_returns_same_execution_without_duplicate():
    key = f"idem-{uuid4().hex}"
    payload = _execution(idempotency_key=key)
    with TestClient(app) as client:
        first = client.post("/api/v1/executions", headers=DEVELOPER, json=payload)
        second = client.post("/api/v1/executions", headers=DEVELOPER, json=payload)
        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["execution"]["id"] == second.json()["execution"]["id"]
        executions = client.get("/api/v1/executions", headers=DEVELOPER).json()
        assert len([item for item in executions if item["idempotency_key"] == key]) == 1

from fastapi.testclient import TestClient
from app.main import app

ADMIN = {"Authorization": "Bearer admin-token"}
DEVELOPER = {"Authorization": "Bearer developer-token"}
AUDITOR = {"Authorization": "Bearer auditor-token"}


def _request(resource: str, action: str, environment: str = "sandbox", context: dict | None = None):
    return {
        "agent_name": "customer-support-agent",
        "user_email": "developer@demo.local",
        "action": action,
        "resource_name": resource,
        "environment": environment,
        "context": context or {"customer_id": "C-10045", "country": "Kenya"},
    }


def test_allow_decision_creates_request_and_audit_event():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/decisions/evaluate",
            headers=DEVELOPER,
            json=_request("customer_profile", "read"),
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["decision"] == "allow"
        assert body["correlation_id"]
        assert body["evaluated_policy_count"] >= 1

        request = client.get(f"/api/v1/decisions/requests/{body['action_request_id']}", headers=AUDITOR)
        assert request.status_code == 200
        assert request.json()["correlation_id"] == body["correlation_id"]

        events = client.get(
            "/api/v1/audit-events",
            headers=AUDITOR,
            params={"correlation_id": body["correlation_id"]},
        )
        assert events.status_code == 200
        assert len(events.json()) == 1
        assert events.json()[0]["result"] == "allow"


def test_approval_required_decision_creates_pending_approval():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/decisions/evaluate",
            headers=DEVELOPER,
            json=_request("customer_transactions", "read"),
        )
        assert response.status_code == 201
        body = response.json()
        assert body["decision"] == "requires_approval"
        assert body["approval_id"] is not None

        approvals = client.get("/api/v1/approvals", headers=ADMIN).json()
        assert any(item["id"] == body["approval_id"] and item["status"] == "pending" for item in approvals)


def test_production_support_access_is_denied():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/decisions/evaluate",
            headers=DEVELOPER,
            json=_request("customer_profile", "read", environment="production"),
        )
        assert response.status_code == 201
        assert response.json()["decision"] == "deny"
        assert "Deny production access" in response.json()["matched_policy_name"]


def test_unknown_agent_and_resource_are_rejected():
    with TestClient(app) as client:
        unknown_agent = _request("customer_profile", "read")
        unknown_agent["agent_name"] = "missing-agent"
        assert client.post("/api/v1/decisions/evaluate", headers=ADMIN, json=unknown_agent).status_code == 404

        unknown_resource = _request("missing_resource", "read")
        assert client.post("/api/v1/decisions/evaluate", headers=ADMIN, json=unknown_resource).status_code == 404


def test_audit_export_supports_csv_and_json():
    with TestClient(app) as client:
        csv_response = client.get("/api/v1/audit-events/export?format=csv", headers=AUDITOR)
        assert csv_response.status_code == 200
        assert csv_response.headers["content-type"].startswith("text/csv")
        assert "event_type" in csv_response.text

        json_response = client.get("/api/v1/audit-events/export?format=json", headers=AUDITOR)
        assert json_response.status_code == 200
        assert json_response.headers["content-type"].startswith("application/json")
        assert isinstance(json_response.json(), list)

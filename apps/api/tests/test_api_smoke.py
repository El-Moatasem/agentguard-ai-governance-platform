from fastapi.testclient import TestClient
from app.main import app

ADMIN = {"Authorization": "Bearer admin-token"}
DEVELOPER = {"Authorization": "Bearer developer-token"}
AUDITOR = {"Authorization": "Bearer auditor-token"}


def test_root_and_health():
    with TestClient(app) as client:
        assert client.get("/").json()["version"] == "0.3.0"
        assert client.get("/health").json()["status"] == "ok"


def test_auth_me_returns_role():
    with TestClient(app) as client:
        response = client.get("/api/v1/auth/me", headers=DEVELOPER)
        assert response.status_code == 200
        assert response.json()["role"] == "developer"


def test_dashboard_metrics_include_decision_breakdown():
    with TestClient(app) as client:
        response = client.get("/api/v1/dashboard/metrics", headers=ADMIN)
        assert response.status_code == 200
        body = response.json()
        assert "agents" in body
        assert "active_policies" in body
        assert set(body["decisions"]) == {"allow", "deny", "requires_approval"}


def test_evaluate_requires_auth():
    with TestClient(app) as client:
        response = client.post("/api/v1/decisions/evaluate", json={})
        assert response.status_code == 401


def test_auditor_cannot_create_policy():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/policies",
            headers=AUDITOR,
            json={
                "name": "Auditor should not create",
                "effect": "deny",
                "priority": 1,
                "conditions": {"action": "delete"},
            },
        )
        assert response.status_code == 403

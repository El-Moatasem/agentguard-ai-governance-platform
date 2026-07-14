from fastapi.testclient import TestClient
from app.main import app

headers = {"Authorization": "Bearer admin-token"}


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"


def test_dashboard_metrics():
    with TestClient(app) as client:
        response = client.get("/api/v1/dashboard/metrics", headers=headers)
        assert response.status_code == 200
        assert "agents" in response.json()


def test_evaluate_requires_auth():
    with TestClient(app) as client:
        response = client.post("/api/v1/decisions/evaluate", json={})
        assert response.status_code == 401

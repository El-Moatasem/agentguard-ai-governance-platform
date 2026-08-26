from fastapi.testclient import TestClient

from app.main import app

ADMIN = {"Authorization": "Bearer admin-token"}
AUDITOR = {"Authorization": "Bearer auditor-token"}
DEVELOPER = {"Authorization": "Bearer developer-token"}


def test_release_readiness_endpoint_reports_final_status():
    with TestClient(app) as client:
        response = client.get("/api/v1/release/readiness", headers=ADMIN)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["version"] == "1.0.0"
    assert body["overall_status"] == "ready"
    assert body["summary"]["agents"] >= 1
    assert any(check["name"] == "Deterministic policy decisions" for check in body["checks"])


def test_final_demo_flow_is_available_to_developer():
    with TestClient(app) as client:
        response = client.get("/api/v1/release/demo-flow", headers=DEVELOPER)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["duration_minutes"] == "15-20"
    assert len(body["steps"]) >= 8


def test_submission_checklist_available_to_auditor():
    with TestClient(app) as client:
        response = client.get("/api/v1/release/submission-checklist", headers=AUDITOR)
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert "GitHub repository shared with quantic-grader" in items
    assert "Final 15-20 minute demo video recorded and shared" in items


def test_security_headers_are_present():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-AgentGuard-Version"] == "1.0.0"

from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

ADMIN = {"Authorization": "Bearer admin-token"}
DEVELOPER = {"Authorization": "Bearer developer-token"}


def test_create_update_and_version_policy():
    name = f"Sprint2 policy {uuid4().hex[:8]}"
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/policies",
            headers=ADMIN,
            json={
                "name": name,
                "description": "Created by automated Sprint 2 test",
                "effect": "allow",
                "priority": 125,
                "conditions": {
                    "agent_name": "customer-support-agent",
                    "resource_name": "customer_profile",
                    "action": "read",
                    "context.country": {"$in": ["Kenya", "Egypt"]},
                },
            },
        )
        assert created.status_code == 201, created.text
        policy = created.json()
        assert policy["version"] == 1

        updated = client.patch(
            f"/api/v1/policies/{policy['id']}",
            headers=ADMIN,
            json={
                "effect": "requires_approval",
                "priority": 225,
                "change_summary": "Raise risk after Sprint 2 review",
            },
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["version"] == 2
        assert updated.json()["effect"] == "requires_approval"

        versions = client.get(f"/api/v1/policies/{policy['id']}/versions", headers=DEVELOPER)
        assert versions.status_code == 200
        assert [version["version"] for version in versions.json()] == [2, 1]


def test_rejects_unsupported_policy_condition_key():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/policies",
            headers=ADMIN,
            json={
                "name": f"Invalid {uuid4().hex[:8]}",
                "effect": "allow",
                "conditions": {"untrusted_field": "value"},
            },
        )
        assert response.status_code == 422


def test_policy_dry_run_does_not_create_action_request():
    payload = {
        "agent_name": "customer-support-agent",
        "user_email": "developer@demo.local",
        "action": "read",
        "resource_name": "customer_profile",
        "environment": "sandbox",
        "context": {"country": "Kenya"},
    }
    with TestClient(app) as client:
        before = client.get("/api/v1/decisions/requests", headers=DEVELOPER).json()
        response = client.post("/api/v1/policies/test/evaluate", headers=DEVELOPER, json=payload)
        after = client.get("/api/v1/decisions/requests", headers=DEVELOPER).json()
        assert response.status_code == 200
        assert response.json()["correlation_id"] == "dry-run"
        assert len(after) == len(before)

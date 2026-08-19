from datetime import timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import engine
from app.main import app
from app.models import Approval, utcnow

ADMIN = {"Authorization": "Bearer admin-token"}
DEVELOPER = {"Authorization": "Bearer developer-token"}
APPROVER = {"Authorization": "Bearer approver-token"}
AUDITOR = {"Authorization": "Bearer auditor-token"}


def _sensitive_decision(client: TestClient, headers=DEVELOPER):
    return client.post(
        "/api/v1/decisions/evaluate",
        headers=headers,
        json={
            "agent_name": "customer-support-agent",
            "user_email": "developer@demo.local",
            "action": "read",
            "resource_name": "customer_transactions",
            "environment": "sandbox",
            "context": {"customer_id": "C-10045"},
        },
    )


def test_self_approval_is_blocked_for_requesting_admin():
    with TestClient(app) as client:
        response = _sensitive_decision(client, headers=ADMIN)
        assert response.status_code == 201
        approval_id = response.json()["approval_id"]
        review = client.post(f"/api/v1/approvals/{approval_id}/approve", headers=ADMIN, json={"notes": "self"})
        assert review.status_code == 403


def test_approver_can_review_developer_request():
    with TestClient(app) as client:
        response = _sensitive_decision(client)
        review = client.post(
            f"/api/v1/approvals/{response.json()['approval_id']}/approve",
            headers=APPROVER,
            json={"notes": "Independent review completed."},
        )
        assert review.status_code == 200
        assert review.json()["status"] == "approved"


def test_expired_approval_is_marked_expired_on_read():
    with TestClient(app) as client:
        response = _sensitive_decision(client).json()
        with Session(engine) as session:
            approval = session.get(Approval, response["approval_id"])
            approval.expires_at = utcnow() - timedelta(minutes=1)
            session.add(approval)
            session.commit()
        fetched = client.get(f"/api/v1/approvals/{response['approval_id']}", headers=APPROVER)
        assert fetched.status_code == 200
        assert fetched.json()["status"] == "expired"


def test_decision_explanation_cannot_override_authorization():
    with TestClient(app) as client:
        response = _sensitive_decision(client).json()
        explanation = client.post(
            "/api/v1/assistant/explain-decision",
            headers=AUDITOR,
            json={"action_request_id": response["action_request_id"]},
        )
        assert explanation.status_code == 200, explanation.text
        body = explanation.json()
        assert body["provider"] == "deterministic-fallback"
        assert "cannot override authorization" in body["safety_note"]
        assert "decision" not in body

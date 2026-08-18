from fastapi.testclient import TestClient

from app.main import app

ADMIN = {"Authorization": "Bearer admin-token"}
DEVELOPER = {"Authorization": "Bearer developer-token"}
APPROVER = {"Authorization": "Bearer approver-token"}


def _request(resource: str, action: str, environment: str = "sandbox", context: dict | None = None):
    return {
        "agent_name": "customer-support-agent",
        "user_email": "developer@demo.local",
        "action": action,
        "resource_name": resource,
        "environment": environment,
        "context": context or {"customer_id": "C-10045", "country": "Kenya"},
    }


def test_approval_detail_and_status_transitions():
    with TestClient(app) as client:
        created = client.post("/api/v1/decisions/evaluate", headers=DEVELOPER, json=_request("customer_transactions", "read"))
        approval_id = created.json()["approval_id"]

        detail = client.get(f"/api/v1/approvals/{approval_id}", headers=APPROVER)
        assert detail.status_code == 200
        assert detail.json()["status"] == "pending"

        approved = client.post(f"/api/v1/approvals/{approval_id}/approve", headers=APPROVER, json={"notes": "Approved by the approver"})
        assert approved.status_code == 200
        assert approved.json()["status"] == "approved"

        duplicate = client.post(f"/api/v1/approvals/{approval_id}/approve", headers=APPROVER, json={"notes": "Again"})
        assert duplicate.status_code == 409


def test_expire_and_cancel_transitions_are_supported():
    with TestClient(app) as client:
        created = client.post("/api/v1/decisions/evaluate", headers=DEVELOPER, json=_request("customer_transactions", "read"))
        approval_id = created.json()["approval_id"]

        expired = client.post(f"/api/v1/approvals/{approval_id}/expire", headers=APPROVER, json={"notes": "Review expired"})
        assert expired.status_code == 200
        assert expired.json()["status"] == "expired"

        created_again = client.post("/api/v1/decisions/evaluate", headers=DEVELOPER, json=_request("customer_transactions", "read"))
        another_id = created_again.json()["approval_id"]

        cancelled = client.post(f"/api/v1/approvals/{another_id}/cancel", headers=ADMIN, json={"notes": "Cancelled by admin"})
        assert cancelled.status_code == 200
        assert cancelled.json()["status"] == "cancelled"


def test_self_approval_and_duplicate_processing_are_rejected():
    with TestClient(app) as client:
        created = client.post("/api/v1/decisions/evaluate", headers=DEVELOPER, json=_request("customer_transactions", "read"))
        approval_id = created.json()["approval_id"]

        self_approval = client.post(f"/api/v1/approvals/{approval_id}/approve", headers=DEVELOPER, json={"notes": "Attempt to self-approve"})
        assert self_approval.status_code == 403

        assigner = client.post(f"/api/v1/approvals/{approval_id}/reject", headers=APPROVER, json={"notes": "Rejected by policy approver"})
        assert assigner.status_code == 200

        second_try = client.post(f"/api/v1/approvals/{approval_id}/approve", headers=APPROVER, json={"notes": "Already processed"})
        assert second_try.status_code == 409

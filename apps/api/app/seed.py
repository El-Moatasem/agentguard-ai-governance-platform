from sqlmodel import Session, select
from .models import Agent, Policy, PolicyEffect, ProtectedResource, Tool, User, Role


def seed_demo_data(session: Session) -> None:
    existing = session.exec(select(User)).first()
    if existing:
        return

    users = [
        User(name="Demo Admin", email="admin@demo.local", role=Role.admin, token="admin-token"),
        User(name="Demo Developer", email="developer@demo.local", role=Role.developer, token="developer-token"),
        User(name="Demo Approver", email="approver@demo.local", role=Role.approver, token="approver-token"),
        User(name="Demo Auditor", email="auditor@demo.local", role=Role.auditor, token="auditor-token"),
    ]
    session.add_all(users)
    session.commit()

    support = Agent(name="customer-support-agent", purpose="Answer customer service questions and prepare workflow requests", owner_email="admin@demo.local", risk_level="medium")
    finance = Agent(name="finance-ops-agent", purpose="Prepare finance operations such as refund requests", owner_email="admin@demo.local", risk_level="high")
    session.add_all([support, finance])
    session.commit()
    session.refresh(support)
    session.refresh(finance)

    session.add_all([
        Tool(agent_id=support.id, name="Customer Profile API", endpoint="/mock/customer-profile", allowed_actions=["read"]),
        Tool(agent_id=finance.id, name="Refund API", endpoint="/mock/refunds", allowed_actions=["prepare", "execute"]),
        ProtectedResource(name="customer_profile", classification="internal", owner_team="support"),
        ProtectedResource(name="customer_transactions", classification="restricted", owner_team="finance"),
        ProtectedResource(name="refund_execution", classification="restricted", owner_team="finance"),
    ])

    session.add_all([
        Policy(
            name="Support may read customer profiles in sandbox",
            description="Customer support agent can read low-risk profile data in non-production workflows.",
            effect=PolicyEffect.allow,
            priority=200,
            conditions={"agent_name": "customer-support-agent", "resource_name": "customer_profile", "action": "read", "environment": "sandbox"},
        ),
        Policy(
            name="Transaction data requires approval",
            description="Access to transaction history is sensitive and requires human review.",
            effect=PolicyEffect.requires_approval,
            priority=300,
            conditions={"resource_name": "customer_transactions", "action": "read"},
        ),
        Policy(
            name="Refund execution requires approval",
            description="Agents may prepare refunds, but execution requires a human approver.",
            effect=PolicyEffect.requires_approval,
            priority=400,
            conditions={"resource_name": "refund_execution", "action": "execute"},
        ),
        Policy(
            name="Deny production access by default for support agent",
            description="Support agent is not allowed to directly access restricted resources in production.",
            effect=PolicyEffect.deny,
            priority=500,
            conditions={"agent_name": "customer-support-agent", "environment": "production"},
        ),
    ])
    session.commit()

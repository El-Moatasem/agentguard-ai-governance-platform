from sqlmodel import Session, select

from .models import Agent, Policy, PolicyEffect, PolicyVersion, ProtectedResource, Role, Tool, User


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

    support = Agent(
        name="customer-support-agent",
        purpose="Answer customer service questions and prepare governed workflow requests",
        owner_email="admin@demo.local",
        risk_level="medium",
    )
    finance = Agent(
        name="finance-ops-agent",
        purpose="Prepare finance operations such as governed refund requests",
        owner_email="admin@demo.local",
        risk_level="high",
    )
    session.add_all([support, finance])
    session.commit()
    session.refresh(support)
    session.refresh(finance)

    session.add_all([
        Tool(agent_id=support.id, name="Customer Profile API", endpoint="mock://customer-profile", allowed_actions=["read"]),
        Tool(agent_id=support.id, name="Team Notification MCP", endpoint="mcp://slack_send_message", allowed_actions=["send"]),
        Tool(agent_id=support.id, name="Case Notes MCP", endpoint="mcp://append_case_note", allowed_actions=["append"]),
        Tool(agent_id=finance.id, name="Refund API", endpoint="mock://refund", allowed_actions=["prepare", "execute"]),
        ProtectedResource(name="customer_profile", classification="internal", owner_team="support"),
        ProtectedResource(name="customer_transactions", classification="restricted", owner_team="finance"),
        ProtectedResource(name="refund_execution", classification="restricted", owner_team="finance"),
        ProtectedResource(name="team_notifications", classification="internal", owner_team="support"),
        ProtectedResource(name="case_notes", classification="confidential", owner_team="support"),
    ])
    session.commit()

    policies = [
        Policy(
            name="Support may read customer profiles in sandbox",
            description="Customer support agent can read low-risk profile data in non-production workflows.",
            effect=PolicyEffect.allow,
            priority=200,
            conditions={
                "agent_name": "customer-support-agent",
                "resource_name": "customer_profile",
                "action": "read",
                "environment": "sandbox",
            },
            created_by_email="admin@demo.local",
        ),
        Policy(
            name="Sandbox team notifications are allowed",
            description="The support agent may send non-destructive notifications through the allowlisted MCP tool in sandbox.",
            effect=PolicyEffect.allow,
            priority=210,
            conditions={
                "agent_name": "customer-support-agent",
                "resource_name": "team_notifications",
                "action": "send",
                "environment": "sandbox",
            },
            created_by_email="admin@demo.local",
        ),
        Policy(
            name="Sandbox case notes are allowed",
            description="The support agent may append a case note through the allowlisted MCP tool in sandbox.",
            effect=PolicyEffect.allow,
            priority=210,
            conditions={
                "agent_name": "customer-support-agent",
                "resource_name": "case_notes",
                "action": "append",
                "environment": "sandbox",
            },
            created_by_email="admin@demo.local",
        ),
        Policy(
            name="Transaction data requires approval",
            description="Access to transaction history is sensitive and requires human review.",
            effect=PolicyEffect.requires_approval,
            priority=300,
            conditions={"resource_name": "customer_transactions", "action": "read"},
            created_by_email="admin@demo.local",
        ),
        Policy(
            name="Large refund execution requires approval",
            description="Refund execution at or above USD 500 requires human approval.",
            effect=PolicyEffect.requires_approval,
            priority=450,
            conditions={
                "agent_name": "finance-ops-agent",
                "resource_name": "refund_execution",
                "action": "execute",
                "context.amount": {"$gte": 500},
            },
            created_by_email="admin@demo.local",
        ),
        Policy(
            name="Refund execution requires approval",
            description="Agents may prepare refunds, but execution requires a human approver.",
            effect=PolicyEffect.requires_approval,
            priority=400,
            conditions={"resource_name": "refund_execution", "action": "execute"},
            created_by_email="admin@demo.local",
        ),
        Policy(
            name="Deny production access by default for support agent",
            description="Support agent is not allowed to directly access protected resources in production.",
            effect=PolicyEffect.deny,
            priority=500,
            conditions={"agent_name": "customer-support-agent", "environment": "production"},
            created_by_email="admin@demo.local",
        ),
    ]
    session.add_all(policies)
    session.commit()

    for policy in policies:
        session.refresh(policy)
        session.add(
            PolicyVersion(
                organization_id=policy.organization_id,
                policy_id=policy.id,
                version=policy.version,
                name=policy.name,
                description=policy.description,
                effect=policy.effect,
                priority=policy.priority,
                active=policy.active,
                conditions=policy.conditions,
                changed_by_email=policy.created_by_email,
                change_summary="Initial seeded policy version",
            )
        )
    session.commit()

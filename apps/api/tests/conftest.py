import pytest
from sqlmodel import Session, delete

from app.database import engine
from app.models import (
    ActionRequest,
    Agent,
    Approval,
    AuditEvent,
    Policy,
    PolicyVersion,
    ProtectedResource,
    Tool,
    User,
)
from app.seed import seed_demo_data


@pytest.fixture(autouse=True)
def reset_test_database():
    """
    Reset application data before every test.

    This prevents tests that create or modify policies from affecting
    subsequent tests when using the persistent PostgreSQL test database.
    """

    with Session(engine) as session:
        # Delete child/dependent records first because of foreign keys.
        session.exec(delete(Approval))
        session.exec(delete(AuditEvent))
        session.exec(delete(ActionRequest))
        session.exec(delete(PolicyVersion))
        session.exec(delete(Tool))
        session.exec(delete(Policy))
        session.exec(delete(ProtectedResource))
        session.exec(delete(Agent))
        session.exec(delete(User))

        session.commit()

        # Restore deterministic baseline data.
        seed_demo_data(session)

    yield
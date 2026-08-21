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
        session.exec(delete(Approval))  # type: ignore[call-overload]
        session.exec(delete(AuditEvent))  # type: ignore[call-overload]
        session.exec(delete(ActionRequest))  # type: ignore[call-overload]
        session.exec(delete(PolicyVersion))  # type: ignore[call-overload]
        session.exec(delete(Tool))  # type: ignore[call-overload]
        session.exec(delete(Policy))  # type: ignore[call-overload]
        session.exec(delete(ProtectedResource))  # type: ignore[call-overload]
        session.exec(delete(Agent))  # type: ignore[call-overload]
        session.exec(delete(User))  # type: ignore[call-overload]

        session.commit()

        # Restore deterministic baseline data.
        seed_demo_data(session)

    yield
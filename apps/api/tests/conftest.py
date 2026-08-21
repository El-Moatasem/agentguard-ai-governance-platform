import pytest
from sqlmodel import SQLModel, Session, delete

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
    ToolExecution,
    User,
)
from app.seed import seed_demo_data


@pytest.fixture(scope="session", autouse=True)
def ensure_sqlite_schema_for_local_tests():
    # SQLite is a convenience fallback for local tests. PostgreSQL CI applies Alembic before pytest.
    if engine.dialect.name == "sqlite":
        SQLModel.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def reset_test_database():
    """Reset mutable application data before every test.

    CI applies Alembic migrations before pytest. This fixture then restores a
    deterministic seed for every test so policy or approval state cannot leak
    between cases.
    """
    with Session(engine) as session:
        session.exec(delete(ToolExecution))
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
        seed_demo_data(session)
    yield

from collections.abc import Generator
from sqlmodel import SQLModel, Session, create_engine
from .config import get_settings

settings = get_settings()
is_sqlite = settings.database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args=connect_args,
    pool_pre_ping=not is_sqlite,
)


def init_db() -> None:
    """Create tables for local/test convenience.

    PostgreSQL environments should also run `alembic upgrade head` so schema
    changes are versioned and repeatable.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine, expire_on_commit=False) as session:
        yield session

"""Create the current schema and insert AgentGuard demonstration records."""
from pathlib import Path
import sys

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
sys.path.insert(0, str(API_DIR))

from sqlmodel import Session  # noqa: E402
from app.database import engine, init_db  # noqa: E402
from app.seed import seed_demo_data  # noqa: E402


def main() -> None:
    init_db()
    with Session(engine, expire_on_commit=False) as session:
        seed_demo_data(session)
    print("AgentGuard demonstration data is ready.")


if __name__ == "__main__":
    main()

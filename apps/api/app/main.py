from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from .config import get_settings
from .database import engine, init_db
from .routers import agents, approvals, assistant, audit, auth, decisions, policies
from .seed import seed_demo_data

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with Session(engine) as session:
        seed_demo_data(session)


@app.get("/health")
def health():
    return {"status": "ok", "service": "agentguard-api"}


for router in [auth.router, agents.router, policies.router, decisions.router, approvals.router, audit.router, assistant.router]:
    app.include_router(router, prefix="/api/v1")

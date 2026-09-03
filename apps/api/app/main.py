from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .config import get_settings
from .database import engine, init_db
from .routers import agent_runtime, agents, approvals, assistant, audit, auth, decisions, executions, integrations, policies, release
from .seed import seed_demo_data

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if settings.seed_demo_data:
        with Session(engine, expire_on_commit=False) as session:
            seed_demo_data(session)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Deterministic AI-agent governance with policy enforcement, human approval, governed tool execution, MCP adapters, and auditability.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    if settings.security_headers_enabled:
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("X-AgentGuard-Version", settings.app_version)
    return response


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "agentguard-api",
        "version": settings.app_version,
        "environment": settings.environment,
        "mcp_mode": "mock" if settings.mcp_mock_mode or not settings.mcp_server_url else "remote",
        "ai_provider": settings.ai_provider,
        "release": settings.release_name,
    }


for router in [
    auth.router,
    agents.router,
    policies.router,
    decisions.router,
    approvals.router,
    executions.router,
    agent_runtime.router,
    integrations.router,
    release.router,
    audit.router,
    assistant.router,
]:
    app.include_router(router, prefix="/api/v1")

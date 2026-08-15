from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentGuard API"
    app_version: str = "0.3.0"
    environment: str = "development"
    database_url: str = "sqlite:///./agentguard.db"
    api_cors_origins: str = "http://localhost:5173,http://localhost:3000"
    demo_mode: bool = True
    seed_demo_data: bool = True
    database_echo: bool = False

    approval_ttl_minutes: int = 60
    max_tool_payload_bytes: int = 16_384
    tool_timeout_seconds: float = 10.0
    max_execution_attempts: int = 3

    # MCP: set MCP_SERVER_URL and MCP_AUTH_TOKEN to use a real streamable-HTTP MCP server.
    # With MCP_MOCK_MODE=true the same governed flow is fully testable without external services.
    mcp_server_url: str = ""
    mcp_auth_token: str = ""
    mcp_mock_mode: bool = True

    # AI provider: deterministic/mock mode is the safe default for local development and CI.
    # Set AI_PROVIDER=openai_compatible plus the URL/key/model to call a compatible chat-completions API.
    ai_provider: str = "mock"
    ai_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str = ""
    ai_model: str = "gpt-5-mini"
    ai_timeout_seconds: float = 15.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

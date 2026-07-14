from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AgentGuard API"
    database_url: str = "sqlite:///./agentguard.db"
    api_cors_origins: str = "http://localhost:5173,http://localhost:3000"
    demo_mode: bool = True

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentGuard API"
    app_version: str = "0.2.0"
    environment: str = "development"
    database_url: str = "sqlite:///./agentguard.db"
    api_cors_origins: str = "http://localhost:5173,http://localhost:3000"
    demo_mode: bool = True
    seed_demo_data: bool = True
    database_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

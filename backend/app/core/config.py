"""
Pydantic v2 Settings for Autonomous Research Agent Platform
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Self-Improving Autonomous Research Agent"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    SECRET_KEY: str = "research_agent_secret_key_33221100"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3006", "http://localhost:8006"]
    
    DATABASE_URL: str = "postgresql+asyncpg://research_user:research_secret_44@localhost:5438/research_agent_db"
    REDIS_URL: str = "redis://localhost:6385/0"
    QDRANT_URL: str = "http://localhost:6338"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

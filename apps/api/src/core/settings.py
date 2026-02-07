from functools import lru_cache
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings for the application."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    app_name: str = "Web-Starter API"
    
@lru_cache
def get_settings() -> Settings:
    """Get the settings for the application."""
    return Settings()

settings = get_settings()
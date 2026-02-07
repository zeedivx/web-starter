from functools import lru_cache
from typing import ClassVar
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = "Web-Starter API"
    env: str = Field(default="development", validation_alias="ENV")
    debug: bool = Field(default=True, validation_alias="DEBUG")

    # Database
    database_url: PostgresDsn = Field(default=..., validation_alias="DATABASE_URL")

    # Security
    secret_key: str = Field(default=..., validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    @property
    def async_database_url(self) -> str:
        """Get async database URL."""
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    """Get the settings for the application."""
    return Settings()


settings = get_settings()

"""Configuration settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class loaded from environment variables."""

    OPENAI_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"
    APP_VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiate the global settings object
settings = Settings()

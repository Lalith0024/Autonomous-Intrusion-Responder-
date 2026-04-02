"""Configuration settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class loaded from environment variables."""

    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"
    APP_VERSION: str = "0.1.0"

    # Default models
    OPENAI_MODEL: str = "gpt-4o-mini"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiate the global settings object
settings = Settings()

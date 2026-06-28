"""Configuration settings for the application — V2 Production."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class loaded from environment variables."""

    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"
    APP_VERSION: str = "2.0.0"

    # Default models
    OPENAI_MODEL: str = "gpt-4o-mini"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # V2: Redis configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_ENABLED: bool = False

    # V2: FAISS memory configuration
    VECTOR_INDEX_DIR: str = "data/vector_index"
    MEMORY_ENABLED: bool = True

    # V2: Tools configuration
    TOOLS_ENABLED: bool = True
    IP_API_URL: str = "http://ip-api.com/json"

    # V2: Data paths
    DATA_DIR: str = "data"
    BLOCKED_IPS_PATH: str = "data/blocked_ips.json"
    SAMPLE_LOGS_DIR: str = "data/sample_logs"
    BATCH_RESULTS_PATH: str = "data/results/batch_results.json"
    EVAL_RESULTS_PATH: str = "data/results/eval_results.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiate the global settings object
settings = Settings()

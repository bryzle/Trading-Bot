"""
Configuration settings for TradingEdge AI
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # API Info
    app_name: str = "TradingEdge AI"
    app_version: str = "0.1.0"

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o"  # GPT-4 with vision

    # Alpaca Configuration (from existing setup)
    alpaca_api_key: str = os.getenv("API_KEY", "")
    alpaca_api_secret: str = os.getenv("API_SECRET", "")
    alpaca_base_url: str = os.getenv("API_URL", "https://paper-api.alpaca.markets")

    # Application Settings
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

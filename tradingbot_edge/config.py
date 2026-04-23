"""
Configuration settings for TradingEdge AI
"""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # API Info
    app_name: str = "TradingEdge AI"
    app_version: str = "0.1.0"

    # Anthropic Configuration
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = "claude-opus-4-6"

    # Alpaca Configuration (from existing setup)
    alpaca_api_key: str = os.getenv("API_KEY", "PK5QRW6SI7XTRNV2CKGZJWH5UR")
    alpaca_api_secret: str = os.getenv("API_SECRET", "GyhU3zyjxUMhsB9nBPnQutzpmgpaK1McXWSarfDDXGDt")
    alpaca_base_url: str = os.getenv("API_URL", "https://paper-api.alpaca.markets")

    # Application Settings
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

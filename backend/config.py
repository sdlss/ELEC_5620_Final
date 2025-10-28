"""
config.py (OpenAI only)
Note: Minimal configuration wrapper using the public OpenAI API only.
Provides get_chat_client() → (client, model) and get_settings()
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import Tuple, Optional

# Load environment variables from .env file
load_dotenv()

@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", self.openai_base_url)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)

_settings = Settings()

def get_settings() -> Settings:
    """Get application settings singleton."""
    return _settings

def get_chat_client() -> Tuple[AsyncOpenAI, str]:
    """Get OpenAI chat client and model name"""
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url if settings.openai_base_url else None
    )
    return client, settings.openai_model


"""Configuration management for Research Assistant."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def load_config(env_file: Optional[str] = None) -> dict:
    """Load configuration from environment variables.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        dict: Configuration dictionary
    """
    if env_file:
        load_dotenv(env_file)
    else:
        # Try to load from .env in the current directory
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

    # Required settings
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )

    # Optional settings with defaults
    config = {
        "openai": {
            "api_key": openai_api_key,
            "model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
        },
        "output": {
            "base_dir": os.getenv("OUTPUT_DIR", "./results"),
            "download_dir": os.getenv("DOWNLOAD_DIR", "./papers"),
            "log_dir": os.getenv("LOG_DIR", "./logs"),
        },
    }

    return config


def get_api_key() -> str:
    """Get OpenAI API key from environment.
    
    Returns:
        str: API key
        
    Raises:
        ValueError: If API key is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )
    return api_key

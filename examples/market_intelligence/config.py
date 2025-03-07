"""Configuration management for Market Intelligence System"""
import os
from typing import Dict

def load_api_keys() -> Dict[str, str]:
    """Load API keys from environment variables or config"""
    return {
        "news_api": os.getenv("NEWS_API_KEY", "bb4833ea6d8d4df2a88aa5a4a3308bc1"),
        "financial_api": os.getenv("FINANCIAL_API_KEY", "dj0yJmk9aVdCTUxGdU03M09YJmQ9WVdrOVRXcFFRMEpDZFhBbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWY5")
    }

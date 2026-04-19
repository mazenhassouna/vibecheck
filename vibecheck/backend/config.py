"""Configuration management for vibecheck."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Apify API
    APIFY_API_KEY: str = os.getenv("APIFY_API_KEY", "")
    
    # Apify Actor IDs
    APIFY_PROFILE_SCRAPER: str = "apify/instagram-profile-scraper"
    APIFY_REEL_SCRAPER: str = "apify/instagram-reel-scraper"
    
    # Follower threshold for filtering (exclude personal friends)
    MIN_FOLLOWER_COUNT: int = 5000
    
    # LLM Settings
    LLM_MODEL: str = "gemini-1.5-flash-latest"
    LLM_TEMPERATURE: float = 0.0  # Deterministic outputs
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration. Returns list of missing keys."""
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.APIFY_API_KEY:
            missing.append("APIFY_API_KEY")
        return missing


config = Config()

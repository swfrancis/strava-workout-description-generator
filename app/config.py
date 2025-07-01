"""Centralised configuration management"""

import os
from typing import Optional


class Config:
    """Application configuration"""
    
    # Strava OAuth settings
    STRAVA_CLIENT_ID: str = os.getenv("STRAVA_CLIENT_ID", "")
    STRAVA_CLIENT_SECRET: str = os.getenv("STRAVA_CLIENT_SECRET", "")
    STRAVA_REDIRECT_URI: str = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/auth/callback")
    
    # Webhook settings
    STRAVA_WEBHOOK_VERIFY_TOKEN: str = os.getenv("STRAVA_WEBHOOK_VERIFY_TOKEN", "")
    
    # Environment settings
    RAILWAY_ENVIRONMENT: Optional[str] = os.getenv("RAILWAY_ENVIRONMENT")
    
    # API URLs
    STRAVA_AUTH_URL: str = "https://www.strava.com/oauth/authorize"
    STRAVA_TOKEN_URL: str = "https://www.strava.com/oauth/token"
    STRAVA_API_BASE_URL: str = "https://www.strava.com/api/v3"
    
    @classmethod
    def validate_required_settings(cls) -> None:
        """Validate that required settings are present"""
        required_settings = [
            ("STRAVA_CLIENT_ID", cls.STRAVA_CLIENT_ID),
            ("STRAVA_CLIENT_SECRET", cls.STRAVA_CLIENT_SECRET),
            ("STRAVA_WEBHOOK_VERIFY_TOKEN", cls.STRAVA_WEBHOOK_VERIFY_TOKEN),
        ]
        
        missing = [name for name, value in required_settings if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.RAILWAY_ENVIRONMENT == "production"


# Validate configuration on import
try:
    Config.validate_required_settings()
except ValueError as e:
    # In development, this might be expected
    if not os.getenv("SKIP_CONFIG_VALIDATION"):
        print(f"Configuration warning: {e}")
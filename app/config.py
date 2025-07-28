"""Centralised configuration management"""

import os
import logging
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
    def validate_required_settings(cls, strict: bool = True) -> bool:
        """Validate that required settings are present
        
        Args:
            strict: If True, raise exception on missing vars. If False, log warnings.
            
        Returns:
            bool: True if all required settings present, False otherwise
        """
        required_settings = [
            ("STRAVA_CLIENT_ID", cls.STRAVA_CLIENT_ID),
            ("STRAVA_CLIENT_SECRET", cls.STRAVA_CLIENT_SECRET),
            ("STRAVA_WEBHOOK_VERIFY_TOKEN", cls.STRAVA_WEBHOOK_VERIFY_TOKEN),
        ]
        
        missing = [name for name, value in required_settings if not value]
        if missing:
            message = f"Missing required environment variables: {', '.join(missing)}"
            if strict:
                raise ValueError(message)
            else:
                logging.warning(message)
                return False
        return True
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.RAILWAY_ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.RAILWAY_ENVIRONMENT != "production" or not cls.RAILWAY_ENVIRONMENT
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get appropriate log level for environment"""
        if cls.is_production():
            return os.getenv("LOG_LEVEL", "WARNING")
        return os.getenv("LOG_LEVEL", "INFO")


# Configure logging based on environment
def _configure_logging() -> None:
    """Configure application logging"""
    log_level = os.getenv("LOG_LEVEL", "INFO" if os.getenv("RAILWAY_ENVIRONMENT") != "production" else "WARNING")
    
    # Don't reconfigure if already configured
    if logging.getLogger().hasHandlers():
        return
        
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

_configure_logging()
logger = logging.getLogger(__name__)

# Validate configuration on import
def _validate_on_import() -> None:
    """Validate configuration when module is imported"""
    skip_validation = os.getenv("SKIP_CONFIG_VALIDATION", "false").lower() == "true"
    
    if skip_validation:
        logger.info("Configuration validation skipped (SKIP_CONFIG_VALIDATION=true)")
        return
    
    try:
        # Use non-strict validation in development, strict in production
        strict_mode = Config.is_production()
        is_valid = Config.validate_required_settings(strict=strict_mode)
        
        if is_valid:
            logger.info("Configuration validation passed")
        elif not strict_mode:
            logger.warning("Configuration validation failed but continuing in development mode")
            
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        if Config.is_production():
            raise
        else:
            logger.warning("Continuing in development mode despite configuration errors")
    except Exception as e:
        logger.error(f"Unexpected error during configuration validation: {e}")
        raise

# Run validation on import
_validate_on_import()
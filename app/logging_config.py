"""Logging configuration for the application"""

import os
import sys
import logging
from typing import Optional


class LogConfig:
    """Centralised logging configuration"""
    
    @staticmethod
    def setup_logging(
        level: Optional[str] = None,
        format_string: Optional[str] = None,
        include_file_handler: bool = False,
        log_file: str = "app.log"
    ) -> None:
        """
        Setup application logging configuration
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            format_string: Custom format string
            include_file_handler: Whether to include file logging
            log_file: Log file name if file handler enabled
        """
        # Determine log level
        if not level:
            level = os.getenv("LOG_LEVEL", "INFO")
            if os.getenv("RAILWAY_ENVIRONMENT") == "production":
                level = os.getenv("LOG_LEVEL", "WARNING")
        
        # Default format
        if not format_string:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Don't reconfigure if already configured
        root_logger = logging.getLogger()
        if root_logger.hasHandlers():
            return
        
        # Setup handlers
        handlers = [logging.StreamHandler(sys.stdout)]
        
        if include_file_handler:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(logging.Formatter(format_string))
                handlers.append(file_handler)
            except (OSError, PermissionError) as e:
                # Fallback to console only if file logging fails
                print(f"Warning: Could not setup file logging: {e}")
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format=format_string,
            handlers=handlers,
            force=True  # Override any existing configuration
        )
        
        # Set specific logger levels for noisy libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured with level: {level}")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance with proper configuration"""
        return logging.getLogger(name)


# Auto-configure logging when module is imported
LogConfig.setup_logging()
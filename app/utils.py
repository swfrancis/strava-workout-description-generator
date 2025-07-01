"""Utility functions for common operations"""

import logging
from typing import Callable, Any, Optional
from fastapi import HTTPException

from .strava_client import StravaAPIError

logger = logging.getLogger(__name__)


def handle_strava_api_errors(func: Callable) -> Callable:
    """Decorator to handle common Strava API errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StravaAPIError as e:
            logger.error(f"Strava API error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Strava API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return wrapper


def parse_activity_safely(activity_data: dict, activity_id: Optional[str] = None) -> Optional[Any]:
    """Safely parse activity data with error logging"""
    try:
        # This would be used with your Activity model
        # return Activity(**activity_data)
        return activity_data
    except Exception as e:
        identifier = activity_id or activity_data.get('id', 'unknown')
        logger.error(f"Error parsing activity {identifier}: {e}")
        return None


def parse_lap_safely(lap_data: dict, lap_index: Optional[int] = None) -> Optional[Any]:
    """Safely parse lap data with error logging"""
    try:
        # This would be used with your Lap model
        # return Lap(**lap_data)
        return lap_data
    except Exception as e:
        identifier = f"lap {lap_index}" if lap_index is not None else "unknown lap"
        logger.error(f"Error parsing {identifier}: {e}")
        return None
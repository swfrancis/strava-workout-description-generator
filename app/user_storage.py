"""Simple in-memory user storage for development.
In production, replace with a proper database like PostgreSQL."""

from typing import Dict, Optional
from datetime import datetime
from .models import User

# In-memory storage (replace with database in production)
users_db: Dict[int, User] = {}

class UserStorage:
    """Simple user storage interface"""
    
    @staticmethod
    def save_user(user: User) -> None:
        """Save or update user"""
        if not user or not user.strava_athlete_id:
            raise ValueError("User and athlete_id are required")
        users_db[user.strava_athlete_id] = user
    
    @staticmethod
    def get_user(athlete_id: int) -> Optional[User]:
        """Get user by athlete ID"""
        return users_db.get(athlete_id)
    
    @staticmethod
    def get_all_users() -> Dict[int, User]:
        """Get all users"""
        return users_db.copy()
    
    @staticmethod
    def delete_user(athlete_id: int) -> bool:
        """Delete user"""
        if athlete_id in users_db:
            del users_db[athlete_id]
            return True
        return False
    
    @staticmethod
    def update_tokens(athlete_id: int, access_token: str, refresh_token: str, expires_at: int) -> bool:
        """Update user tokens"""
        if not athlete_id or not access_token or not refresh_token:
            raise ValueError("athlete_id, access_token, and refresh_token are required")
        
        if athlete_id in users_db:
            user = users_db[athlete_id]
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.expires_at = expires_at
            user.updated_at = datetime.utcnow()
            return True
        return False
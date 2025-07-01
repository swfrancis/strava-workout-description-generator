import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StravaAPIError(Exception):
    """Custom exception for Strava API errors"""
    pass

class RateLimitError(StravaAPIError):
    """Raised when rate limit is exceeded"""
    pass

class StravaClient:
    """Client for interacting with Strava API v3"""
    
    BASE_URL = "https://www.strava.com/api/v3"
    
    def __init__(self, access_token: str, refresh_token: str = None, 
                 client_id: str = None, client_secret: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.athlete_id = None  # Set externally when needed for token updates
        self.session = requests.Session()
        self._setup_session()
        
    def _setup_session(self):
        """Configure session with auth headers"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Strava API with error handling"""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                rate_limit_reset = response.headers.get('X-RateLimit-Time')
                if rate_limit_reset:
                    wait_time = int(rate_limit_reset) - int(time.time())
                    raise RateLimitError(f"Rate limit exceeded. Reset in {wait_time} seconds")
                else:
                    raise RateLimitError("Rate limit exceeded")
            
            # Handle token expiration
            if response.status_code == 401:
                logger.warning(f"401 Unauthorized for {url}")
                logger.warning(f"Response: {response.text}")
                
                if self.refresh_token and self.client_id and self.client_secret:
                    logger.info("Access token unauthorized, attempting refresh")
                    self._refresh_access_token()
                    # Retry the request with new token
                    self._setup_session()
                    response = self.session.request(method, url, **kwargs)
                    
                    if response.status_code == 401:
                        logger.error("Still unauthorized after token refresh")
                        logger.error(f"Refresh response: {response.text}")
                else:
                    logger.error("No refresh token available for 401 error")
                    raise StravaAPIError("Access token expired and no refresh token available")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise StravaAPIError(f"API request failed: {str(e)}")
    
    def _refresh_access_token(self):
        """Refresh the access token using refresh token"""
        token_url = "https://www.strava.com/oauth/token"
        
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            logger.info(f"Attempting token refresh for client_id: {self.client_id}")
            response = requests.post(token_url, data=token_data)
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed with status {response.status_code}: {response.text}")
                
            response.raise_for_status()
            
            token_info = response.json()
            old_token = self.access_token[:10] + "..."
            self.access_token = token_info["access_token"]
            self.refresh_token = token_info["refresh_token"]
            new_token = self.access_token[:10] + "..."
            
            logger.info(f"Access token refreshed successfully: {old_token} -> {new_token}")
            
            # Update the user in storage with new tokens if athlete_id is available
            if hasattr(self, 'athlete_id') and self.athlete_id:
                from .user_storage import UserStorage
                expires_at = token_info.get("expires_at", int(time.time()) + 21600)  # Default 6 hours
                success = UserStorage.update_tokens(
                    athlete_id=self.athlete_id,
                    access_token=self.access_token,
                    refresh_token=self.refresh_token,
                    expires_at=expires_at
                )
                if success:
                    logger.info(f"Updated stored tokens for athlete {self.athlete_id}")
                else:
                    logger.warning(f"Failed to update stored tokens for athlete {self.athlete_id}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh request failed: {str(e)}")
            raise StravaAPIError(f"Failed to refresh access token: {str(e)}")
    
    def get_athlete(self) -> Dict[str, Any]:
        """Get current athlete information"""
        return self._make_request('GET', '/athlete')
    
    def get_activities(self, before: Optional[int] = None, after: Optional[int] = None, 
                      page: int = 1, per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Get list of activities for authenticated athlete
        
        Args:
            before: Unix timestamp, return activities before this time
            after: Unix timestamp, return activities after this time
            page: Page number (default 1)
            per_page: Number of activities per page (max 200, default 30)
        """
        params = {
            'page': page,
            'per_page': min(per_page, 200)  # Strava max is 200
        }
        
        if before:
            params['before'] = before
        if after:
            params['after'] = after
            
        return self._make_request('GET', '/athlete/activities', params=params)
    
    def get_activity_details(self, activity_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific activity"""
        return self._make_request('GET', f'/activities/{activity_id}')
    
    def get_activity_laps(self, activity_id: int) -> List[Dict[str, Any]]:
        """Get lap data for a specific activity"""
        return self._make_request('GET', f'/activities/{activity_id}/laps')
    
    def get_activity_streams(self, activity_id: int, 
                           keys: List[str] = None, 
                           key_by_type: bool = True) -> Dict[str, Any]:
        """
        Get streams (time series data) for a specific activity
        
        Args:
            activity_id: The activity ID
            keys: List of stream types to retrieve. Options include:
                  'time', 'distance', 'latlng', 'altitude', 'velocity_smooth',
                  'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth'
            key_by_type: Whether to return keyed by stream type
        """
        if keys is None:
            keys = ['time', 'distance', 'velocity_smooth', 'heartrate', 'cadence']
        
        params = {
            'keys': ','.join(keys),
            'key_by_type': str(key_by_type).lower()
        }
        
        return self._make_request('GET', f'/activities/{activity_id}/streams', params=params)
    
    def update_activity(self, activity_id: int, name: str = None, 
                       description: str = None, type: str = None, 
                       gear_id: str = None) -> Dict[str, Any]:
        """
        Update activity details
        
        Args:
            activity_id: The activity ID to update
            name: New activity name
            description: New activity description
            type: New activity type
            gear_id: Gear ID to associate with activity
        """
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if type is not None:
            data['type'] = type
        if gear_id is not None:
            data['gear_id'] = gear_id
        
        return self._make_request('PUT', f'/activities/{activity_id}', json=data)
    
    def get_recent_activities(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get activities from the last N days"""
        after_timestamp = int((datetime.now().timestamp() - (days * 24 * 3600)))
        return self.get_activities(after=after_timestamp)
    
    def get_activity_summary(self, activity_id: int) -> Dict[str, Any]:
        """Get a comprehensive summary of an activity including details, laps, and key streams"""
        try:
            # Get basic activity details
            activity = self.get_activity_details(activity_id)
            
            # Get lap data if available
            laps = []
            try:
                laps = self.get_activity_laps(activity_id)
            except StravaAPIError:
                logger.warning(f"Could not fetch laps for activity {activity_id}")
            
            # Get key streams for analysis
            streams = {}
            try:
                streams = self.get_activity_streams(activity_id)
            except StravaAPIError:
                logger.warning(f"Could not fetch streams for activity {activity_id}")
            
            return {
                'activity': activity,
                'laps': laps,
                'streams': streams
            }
            
        except StravaAPIError as e:
            logger.error(f"Error fetching activity summary for {activity_id}: {str(e)}")
            raise
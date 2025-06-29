from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from enum import Enum

class ActivityType(str, Enum):
    """Strava activity types"""
    RUN = "Run"
    RIDE = "Ride"
    SWIM = "Swim"
    HIKE = "Hike"
    WALK = "Walk"
    ALPINESKI = "AlpineSki"
    BACKCOUNTRYSKI = "BackcountrySki"
    CANOEING = "Canoeing"
    CROSSFIT = "Crossfit"
    EBIKERIDE = "EBikeRide"
    ELLIPTICAL = "Elliptical"
    GOLF = "Golf"
    HANDCYCLE = "Handcycle"
    ICESKATE = "IceSkate"
    INLINESKATE = "InlineSkate"
    KAYAKING = "Kayaking"
    KITESURF = "Kitesurf"
    NORDICSKI = "NordicSki"
    ROCKCLIMBING = "RockClimbing"
    ROLLERSKI = "RollerSki"
    ROWING = "Rowing"
    SNOWBOARD = "Snowboard"
    SNOWSHOE = "Snowshoe"
    SOCCER = "Soccer"
    STAIRSTEPPER = "StairStepper"
    STANDUPPADDLING = "StandUpPaddling"
    SURFING = "Surfing"
    VIRTUALRIDE = "VirtualRide"
    VIRTUALRUN = "VirtualRun"
    WEIGHTTRAINING = "WeightTraining"
    WINDSURF = "Windsurf"
    WORKOUT = "Workout"
    YOGA = "Yoga"

class Athlete(BaseModel):
    """Athlete information"""
    id: int
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    profile_medium: Optional[str] = None
    profile: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class Activity(BaseModel):
    """Basic activity information from activities list"""
    id: int
    name: str
    distance: float = Field(description="Distance in meters")
    moving_time: int = Field(description="Moving time in seconds")
    elapsed_time: int = Field(description="Elapsed time in seconds")
    total_elevation_gain: float = Field(description="Elevation gain in meters")
    type: str = Field(description="Activity type")
    sport_type: str = Field(description="Sport type")
    start_date: datetime = Field(description="Start date in UTC")
    start_date_local: datetime = Field(description="Start date in local timezone")
    timezone: str = Field(description="Timezone")
    utc_offset: float = Field(description="UTC offset in seconds")
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    achievement_count: int = 0
    kudos_count: int = 0
    comment_count: int = 0
    athlete_count: int = 1
    photo_count: int = 0
    trainer: bool = False
    commute: bool = False
    manual: bool = False
    private: bool = False
    visibility: str = "everyone"
    flagged: bool = False
    gear_id: Optional[str] = None
    average_speed: Optional[float] = Field(None, description="Average speed in m/s")
    max_speed: Optional[float] = Field(None, description="Max speed in m/s")
    average_cadence: Optional[float] = None
    average_watts: Optional[float] = None
    weighted_average_watts: Optional[int] = None
    kilojoules: Optional[float] = None
    device_watts: Optional[bool] = None
    has_heartrate: bool = False
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    heartrate_opt_out: bool = False
    display_hide_heartrate_option: bool = False
    elev_high: Optional[float] = None
    elev_low: Optional[float] = None
    upload_id: Optional[int] = None
    upload_id_str: Optional[str] = None
    external_id: Optional[str] = None
    from_accepted_tag: bool = False
    pr_count: int = 0
    total_photo_count: int = 0
    has_kudoed: bool = False

class Split(BaseModel):
    """Split/segment data"""
    distance: float = Field(description="Distance in meters")
    elapsed_time: int = Field(description="Elapsed time in seconds")
    elevation_difference: float = Field(description="Elevation difference in meters")
    moving_time: int = Field(description="Moving time in seconds")
    split: int = Field(description="Split number")
    average_speed: float = Field(description="Average speed in m/s")
    pace_zone: Optional[int] = None
    average_heartrate: Optional[float] = None
    average_grade_adjusted_speed: Optional[float] = None

class Lap(BaseModel):
    """Lap data for interval analysis"""
    id: int
    activity: Dict[str, Any] = Field(description="Reference to parent activity")
    athlete: Dict[str, Any] = Field(description="Athlete reference")
    average_cadence: Optional[float] = None
    average_speed: float = Field(description="Average speed in m/s")
    distance: float = Field(description="Distance in meters")
    elapsed_time: int = Field(description="Elapsed time in seconds")
    start_index: int = Field(description="Start index in activity streams")
    end_index: int = Field(description="End index in activity streams")
    lap_index: int = Field(description="Lap number (0-indexed)")
    max_speed: Optional[float] = Field(None, description="Max speed in m/s")
    moving_time: int = Field(description="Moving time in seconds")
    name: str = Field(description="Lap name")
    pace_zone: Optional[int] = None
    split: Optional[int] = None
    start_date: datetime = Field(description="Lap start time")
    start_date_local: datetime = Field(description="Lap start time local")
    total_elevation_gain: float = Field(description="Elevation gain in meters")
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    average_watts: Optional[float] = None
    device_watts: Optional[bool] = None

class StreamData(BaseModel):
    """Time series data point"""
    data: List[Union[float, int, List[float]]] = Field(description="Stream data points")
    series_type: str = Field(description="Type of data series")
    original_size: int = Field(description="Original number of data points")
    resolution: str = Field(description="Data resolution (low, medium, high)")

class ActivityDetail(Activity):
    """Detailed activity information"""
    description: Optional[str] = None
    calories: Optional[float] = None
    device_name: Optional[str] = None
    embed_token: Optional[str] = None
    splits_metric: List[Split] = Field(default_factory=list)
    splits_standard: List[Split] = Field(default_factory=list)
    laps: List[Lap] = Field(default_factory=list)
    gear: Optional[Dict[str, Any]] = None
    partner_brand_tag: Optional[str] = None
    photos: Optional[Dict[str, Any]] = None
    highlighted_kudosers: List[Dict[str, Any]] = Field(default_factory=list)
    hide_from_home: bool = False
    segment_efforts: List[Dict[str, Any]] = Field(default_factory=list)
    suffer_score: Optional[int] = None

class WorkoutPattern(BaseModel):
    """Detected workout pattern"""
    pattern_type: str = Field(description="Type of pattern (intervals, tempo, easy, etc.)")
    intervals: List[Dict[str, Any]] = Field(default_factory=list, description="Detected intervals")
    rest_periods: List[Dict[str, Any]] = Field(default_factory=list, description="Rest periods")
    confidence: float = Field(description="Confidence score 0-1")
    description: str = Field(description="Human readable pattern description")

class WorkoutAnalysis(BaseModel):
    """Generated workout analysis and description"""
    activity_id: int
    activity_name: str
    activity_type: str
    analysis_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Raw data summary
    total_distance: float = Field(description="Total distance in meters")
    total_time: int = Field(description="Total time in seconds")
    average_pace: Optional[float] = Field(None, description="Average pace in min/km")
    average_speed: Optional[float] = Field(None, description="Average speed in m/s")
    
    # Lap-based analysis
    has_laps: bool = Field(description="Whether activity has manual laps")
    lap_count: int = Field(description="Number of laps")
    lap_analysis: Optional[str] = Field(None, description="Analysis of lap structure")
    
    # Pattern detection
    detected_patterns: List[WorkoutPattern] = Field(default_factory=list)
    primary_pattern: Optional[WorkoutPattern] = None
    
    # Generated descriptions
    short_description: str = Field(description="Brief workout description")
    detailed_description: str = Field(description="Detailed workout analysis")
    suggested_title: Optional[str] = Field(None, description="Suggested activity title")
    
    # Metrics
    intensity_score: Optional[float] = Field(None, description="Workout intensity 0-10")
    workout_quality: Optional[str] = Field(None, description="Quality assessment")
    
    # Technical details
    analysis_method: str = Field(description="Method used for analysis (laps, ml, splits)")
    confidence: float = Field(description="Overall confidence in analysis 0-1")
    notes: Optional[str] = Field(None, description="Additional analysis notes")

class ActivitySummary(BaseModel):
    """Comprehensive activity summary with analysis"""
    activity: ActivityDetail
    laps: List[Lap] = Field(default_factory=list)
    streams: Dict[str, StreamData] = Field(default_factory=dict)
    analysis: Optional[WorkoutAnalysis] = None

# Response models for API endpoints
class ActivityListResponse(BaseModel):
    """Response for activities list endpoint"""
    activities: List[Activity]
    total_count: int
    page: int
    per_page: int

class ActivityResponse(BaseModel):
    """Response for single activity endpoint"""
    activity: ActivityDetail
    laps: List[Lap] = Field(default_factory=list)
    has_streams: bool = False
    stream_types: List[str] = Field(default_factory=list)

class AnalysisResponse(BaseModel):
    """Response for workout analysis endpoint"""
    activity_id: int
    analysis: WorkoutAnalysis
    success: bool = True
    message: Optional[str] = None

# Request models
class AnalysisRequest(BaseModel):
    """Request for workout analysis"""
    activity_id: int
    include_streams: bool = True
    analysis_type: str = "auto"  # auto, laps, ml, splits
    generate_description: bool = True
    update_activity: bool = False

# User and Webhook Models
class User(BaseModel):
    """User account with Strava tokens"""
    strava_athlete_id: int
    access_token: str
    refresh_token: str
    expires_at: int
    created_at: datetime
    updated_at: datetime

class WebhookEvent(BaseModel):
    """Strava webhook event payload"""
    object_type: str  # "activity" or "athlete"
    object_id: int
    aspect_type: str  # "create", "update", "delete"
    owner_id: int  # athlete ID
    subscription_id: int
    event_time: int

class WebhookSubscription(BaseModel):
    """Webhook subscription details"""
    id: int
    application_id: int
    callback_url: str
    created_at: datetime
    updated_at: datetime
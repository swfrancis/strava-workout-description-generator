from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging
import os
from datetime import datetime

from .strava_client import StravaClient, StravaAPIError
from .models import (
    Activity, ActivityDetail, Lap, ActivityListResponse, 
    ActivityResponse, AnalysisResponse, AnalysisRequest,
    ActivitySummary, WorkoutAnalysis
)
from .analysis import analyse_workout_from_laps

router = APIRouter(prefix="/activities", tags=["activities"])
logger = logging.getLogger(__name__)

def get_strava_client(access_token: str) -> StravaClient:
    """Create Strava client instance with token"""
    # In production, you'd get these from environment or database
    refresh_token = None  # Get from user session/database
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    
    return StravaClient(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret
    )

@router.get("/", response_model=ActivityListResponse)
async def get_activities(
    access_token: str = Query(..., description="Strava access token"),
    before: Optional[int] = Query(None, description="Unix timestamp, activities before this time"),
    after: Optional[int] = Query(None, description="Unix timestamp, activities after this time"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(30, ge=1, le=200, description="Activities per page (max 200)")
):
    """Get list of activities for authenticated athlete"""
    
    try:
        client = get_strava_client(access_token)
        activities_data = client.get_activities(
            before=before,
            after=after,
            page=page,
            per_page=per_page
        )
        
        # Convert to Pydantic models
        activities = []
        for activity_data in activities_data:
            try:
                activity = Activity(**activity_data)
                activities.append(activity)
            except (ValueError, TypeError) as e:
                # Log validation error but continue with other activities
                logger.error(f"Error parsing activity {activity_data.get('id', 'unknown')}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error parsing activity {activity_data.get('id', 'unknown')}: {e}")
                continue
        
        return ActivityListResponse(
            activities=activities,
            total_count=len(activities),
            page=page,
            per_page=per_page
        )
        
    except StravaAPIError as e:
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/recent", response_model=ActivityListResponse)
async def get_recent_activities(
    access_token: str = Query(..., description="Strava access token"),
    days: int = Query(7, ge=1, le=30, description="Number of days to look back (max 30)")
):
    """Get activities from the last N days"""
    
    try:
        client = get_strava_client(access_token)
        activities_data = client.get_recent_activities(days=days)
        
        activities = []
        for activity_data in activities_data:
            try:
                activity = Activity(**activity_data)
                activities.append(activity)
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing activity {activity_data.get('id', 'unknown')}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error parsing activity {activity_data.get('id', 'unknown')}: {e}")
                continue
        
        return ActivityListResponse(
            activities=activities,
            total_count=len(activities),
            page=1,
            per_page=len(activities)
        )
        
    except StravaAPIError as e:
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity_details(
    activity_id: int,
    access_token: str = Query(..., description="Strava access token"),
    include_laps: bool = Query(True, description="Include lap data"),
    include_streams: bool = Query(False, description="Include stream information (not data)")
):
    """Get detailed information about a specific activity"""
    
    try:
        client = get_strava_client(access_token)
        
        # Get activity details
        activity_data = client.get_activity_details(activity_id)
        activity = ActivityDetail(**activity_data)
        
        # Get laps if requested
        laps = []
        if include_laps:
            try:
                laps_data = client.get_activity_laps(activity_id)
                for lap_data in laps_data:
                    try:
                        lap = Lap(**lap_data)
                        laps.append(lap)
                    except Exception as e:
                        logger.error(f"Error parsing lap data: {e}")
                        continue
            except StravaAPIError:
                # Laps might not be available for all activities
                pass
        
        # Check available streams if requested
        stream_types = []
        if include_streams:
            try:
                streams = client.get_activity_streams(activity_id, keys=['time'])
                stream_types = list(streams.keys()) if streams else []
            except StravaAPIError:
                pass
        
        return ActivityResponse(
            activity=activity,
            laps=laps,
            has_streams=len(stream_types) > 0,
            stream_types=stream_types
        )
        
    except StravaAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Activity {activity_id} not found")
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{activity_id}/laps")
async def get_activity_laps(
    activity_id: int,
    access_token: str = Query(..., description="Strava access token")
):
    """Get lap data for a specific activity"""
    
    try:
        client = get_strava_client(access_token)
        laps_data = client.get_activity_laps(activity_id)
        
        laps = []
        for lap_data in laps_data:
            try:
                lap = Lap(**lap_data)
                laps.append(lap)
            except Exception as e:
                logger.error(f"Error parsing lap data: {e}")
                continue
        
        return {"activity_id": activity_id, "laps": laps, "lap_count": len(laps)}
        
    except StravaAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Activity {activity_id} not found")
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{activity_id}/streams")
async def get_activity_streams(
    activity_id: int,
    access_token: str = Query(..., description="Strava access token"),
    keys: str = Query("time,distance,velocity_smooth", description="Comma-separated stream types")
):
    """Get stream data for a specific activity"""
    
    try:
        client = get_strava_client(access_token)
        stream_keys = [k.strip() for k in keys.split(",")]
        streams_data = client.get_activity_streams(activity_id, keys=stream_keys)
        
        return {
            "activity_id": activity_id,
            "streams": streams_data,
            "available_streams": list(streams_data.keys()) if streams_data else []
        }
        
    except StravaAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Activity {activity_id} not found")
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{activity_id}/summary", response_model=ActivitySummary)
async def get_activity_summary(
    activity_id: int,
    access_token: str = Query(..., description="Strava access token")
):
    """Get comprehensive activity summary including details, laps, and key streams"""
    
    try:
        client = get_strava_client(access_token)
        summary_data = client.get_activity_summary(activity_id)
        
        # Parse activity details
        activity = ActivityDetail(**summary_data['activity'])
        
        # Parse laps
        laps = []
        for lap_data in summary_data.get('laps', []):
            try:
                lap = Lap(**lap_data)
                laps.append(lap)
            except Exception as e:
                logger.error(f"Error parsing lap data: {e}")
                continue
        
        # Parse streams (basic validation, not full parsing to StreamData models)
        streams = summary_data.get('streams', {})
        
        return ActivitySummary(
            activity=activity,
            laps=laps,
            streams=streams,
            analysis=None  # Will be added in analysis endpoints
        )
        
    except StravaAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Activity {activity_id} not found")
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/{activity_id}/analyse", response_model=AnalysisResponse)
async def analyse_activity(
    activity_id: int,
    request: AnalysisRequest,
    access_token: str = Query(..., description="Strava access token")
):
    """Analyze activity and generate workout description"""
    
    try:
        client = get_strava_client(access_token)
        
        # Get comprehensive activity data
        summary_data = client.get_activity_summary(activity_id)
        activity_data = summary_data['activity']
        laps_data = summary_data.get('laps', [])
        streams_data = summary_data.get('streams', {})
        
        # Try lap-based analysis first
        analysis = None
        if laps_data:
            # Convert lap data to Lap objects
            lap_objects = []
            for lap_data in laps_data:
                try:
                    lap = Lap(**lap_data)
                    lap_objects.append(lap)
                except Exception as e:
                    logger.error(f"Error parsing lap data for analysis: {e}")
                    continue
            
            # Analyze laps for interval patterns
            if lap_objects:
                analysis = analyse_workout_from_laps(
                    lap_objects,
                    activity_data.get('name', 'Untitled Activity'),
                    activity_data.get('type', 'Unknown')
                )
                if analysis:
                    analysis.activity_id = activity_id
        
        # Fallback to basic analysis if no lap analysis
        if not analysis:
            analysis = WorkoutAnalysis(
                activity_id=activity_id,
                activity_name=activity_data.get('name', 'Untitled Activity'),
                activity_type=activity_data.get('type', 'Unknown'),
                total_distance=activity_data.get('distance', 0),
                total_time=activity_data.get('elapsed_time', 0),
                has_laps=len(laps_data) > 0,
                lap_count=len(laps_data),
                short_description=f"{activity_data.get('type', 'Activity')} - {activity_data.get('distance', 0)/1000:.1f}km in {activity_data.get('elapsed_time', 0)//60}min",
                detailed_description=f"Completed a {activity_data.get('distance', 0)/1000:.1f}km {activity_data.get('type', 'activity').lower()} with {len(laps_data)} laps.",
                analysis_method="basic",
                confidence=0.3  # Low confidence for basic analysis
            )
        
        # Set appropriate message based on analysis method
        if analysis.analysis_method == "laps":
            message = f"Lap-based analysis completed. Detected: {analysis.short_description}"
        else:
            message = "Basic analysis completed. No interval pattern detected."
        
        return AnalysisResponse(
            activity_id=activity_id,
            analysis=analysis,
            success=True,
            message=message
        )
        
    except StravaAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Activity {activity_id} not found")
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.put("/{activity_id}/description")
async def update_activity_description(
    activity_id: int,
    access_token: str = Query(..., description="Strava access token"),
    description: str = Query(..., description="New activity description"),
    name: Optional[str] = Query(None, description="Optional new activity name")
):
    """Update activity description (and optionally name) on Strava"""
    
    try:
        client = get_strava_client(access_token)
        
        update_data = {"description": description}
        if name:
            update_data["name"] = name
            
        result = client.update_activity(activity_id, **update_data)
        
        return {
            "activity_id": activity_id,
            "updated": True,
            "message": "Activity updated successfully",
            "updated_fields": list(update_data.keys())
        }
        
    except StravaAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Activity {activity_id} not found")
        raise HTTPException(status_code=400, detail=f"Strava API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
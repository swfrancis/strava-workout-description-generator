"""Strava webhook handling for automatic activity processing"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import os
import logging
import time

from .models import WebhookEvent
from .user_storage import UserStorage
from .strava_client import StravaClient
from .analysis import analyse_workout_from_laps

router = APIRouter(prefix="/webhook", tags=["webhooks"])
logger = logging.getLogger(__name__)

# Webhook verification token from Strava app settings
WEBHOOK_VERIFY_TOKEN = os.getenv("STRAVA_WEBHOOK_VERIFY_TOKEN", "your_verify_token")

@router.get("/strava")
async def webhook_verification(request: Request):
    """Handle Strava webhook verification challenge"""
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")
    
    logger.info(f"Webhook verification: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verification successful")
        return {"hub.challenge": hub_challenge}
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/strava")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming Strava webhook events"""
    try:
        # Parse the webhook event
        event_data = await request.json()
        
        
        event = WebhookEvent(**event_data)
        logger.info(f"Received webhook: {event.object_type} {event.aspect_type} for athlete {event.owner_id}, object_id: {event.object_id}")
        
        # Only process activity creation events
        if event.object_type == "activity" and event.aspect_type == "create":
            logger.info(f"Processing activity creation for activity {event.object_id}")
            # Process in background to avoid blocking the webhook
            background_tasks.add_task(process_activity_creation, event)
        else:
            logger.info(f"Ignoring webhook: {event.object_type} {event.aspect_type} (not activity creation)")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_activity_creation(event: WebhookEvent):
    """Process new activity creation in background"""
    logger.info(f"Starting background processing for activity {event.object_id}")
    try:
        # Get user from storage
        user = UserStorage.get_user(event.owner_id)
        if not user:
            logger.warning(f"No user found for athlete {event.owner_id}. User must connect their account at https://web-production-6d50.up.railway.app/")
            return
        
        logger.info(f"Found user for athlete {event.owner_id}, token expires at {user.expires_at}")
        
        # Create Strava client with token refresh capability
        client = StravaClient(
            access_token=user.access_token,
            refresh_token=user.refresh_token,
            client_id=os.getenv("STRAVA_CLIENT_ID"),
            client_secret=os.getenv("STRAVA_CLIENT_SECRET")
        )
        
        # Store athlete_id for potential token refresh
        client.athlete_id = event.owner_id
        
        # Wait a bit for Strava to process the activity
        import asyncio
        await asyncio.sleep(30)  # Give Strava time to process laps
        
        # Get activity details
        activity = client.get_activity_details(event.object_id)
        if not activity:
            logger.warning(f"Could not fetch activity {event.object_id}")
            return
        
        # Only process running/cycling activities
        activity_type = activity.get("type", "")
        if activity_type not in ["Run", "Ride", "VirtualRun", "VirtualRide"]:
            logger.info(f"Skipping non-running/cycling activity: {activity_type}")
            return
        
        # Get lap data
        laps = client.get_activity_laps(event.object_id)
        logger.info(f"Activity {event.object_id} has {len(laps) if laps else 0} laps")
        
        # Check if activity has manual laps for interval detection
        if not laps or len(laps) < 2:
            logger.info(f"Activity {event.object_id} has no manual laps - skipping interval analysis")
            return
        
        # Analyse the workout
        activity_name = activity.get("name", "")
        analysis = analyse_workout_from_laps(laps, activity_name, activity_type)
        if not analysis:
            logger.info(f"No intervals detected in activity {event.object_id}")
            return
        
        # Update activity description if analysis was successful
        if analysis.confidence > 0.7:  # Only update if we're confident
            new_description = analysis.short_description
            
            # Preserve existing description if any
            existing_description = activity.get("description", "") or ""
            if existing_description and not existing_description.strip().startswith(analysis.short_description[:20]):
                new_description = f"{analysis.short_description}\n\n{existing_description}"
            
            # Update the activity
            client.update_activity(event.object_id, description=new_description)
            logger.info(f"Updated activity {event.object_id} with description: {analysis.short_description}")
        else:
            logger.info(f"Low confidence analysis for activity {event.object_id} - not updating")
            
    except Exception as e:
        logger.error(f"Error processing activity {event.object_id}: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        
        # Log specific error details for debugging
        if "401" in str(e) or "Unauthorized" in str(e):
            logger.error(f"Authentication failed for athlete {event.owner_id}")
            logger.error(f"User token expires at: {user.expires_at if 'user' in locals() else 'User not found'}")
            
            current_time = int(time.time())
            logger.error(f"Current timestamp: {current_time}")
            
            if 'user' in locals() and user:
                if user.expires_at < current_time:
                    logger.error("Token has expired - refresh should have been attempted")
                else:
                    logger.error("Token not expired - possible scope or authorization issue")
        
        # Re-raise for further handling
        raise


from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
import requests
import os
from urllib.parse import urlencode

router = APIRouter(prefix="/auth", tags=["authentication"])

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"

@router.get("/login")
async def login():
    """Redirect user to Strava authorization page"""
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": STRAVA_REDIRECT_URI,
        "approval_prompt": "force",
        "scope": "read,activity:read_all"
    }
    
    auth_url = f"{STRAVA_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(code: str = Query(...), scope: str = Query(None)):
    """Handle Strava OAuth callback and exchange code for access token"""
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorisation code not provided")
    
    # Exchange authorization code for access token
    token_data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(STRAVA_TOKEN_URL, data=token_data)
        response.raise_for_status()
        
        token_info = response.json()
        
        # Store token info (in production, save to database)
        access_token = token_info.get("access_token")
        refresh_token = token_info.get("refresh_token")
        expires_at = token_info.get("expires_at")
        athlete_info = token_info.get("athlete", {})
        
        # Redirect to success page with token (for popup flow)
        success_url = f"/auth/success?access_token={access_token}&athlete_id={athlete_info.get('id')}&expires_at={expires_at}"
        return RedirectResponse(url=success_url)
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to exchange code for token: {str(e)}")

@router.get("/success")
async def success_page(access_token: str = Query(...), athlete_id: str = Query(...), expires_at: int = Query(...)):
    """Success page after Strava authentication"""
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connected Successfully!</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .success {{ color: #22c55e; font-size: 2em; margin-bottom: 20px; }}
            .message {{ font-size: 1.2em; margin-bottom: 30px; }}
            .close-btn {{ background: #FC4C02; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="success">✅ Success!</div>
        <div class="message">Your Strava account is now connected!</div>
        <button class="close-btn" onclick="window.close()">Close Window</button>
        <script>
            // Notify parent window of success
            if (window.opener) {{
                window.opener.postMessage({{ 
                    type: 'strava_auth_success', 
                    access_token: '{access_token}',
                    athlete_id: '{athlete_id}',
                    expires_at: {expires_at}
                }}, '*');
                setTimeout(() => window.close(), 2000);
            }}
        </script>
    </body>
    </html>
    """)

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh Strava access token"""
    
    token_data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    try:
        response = requests.post(STRAVA_TOKEN_URL, data=token_data)
        response.raise_for_status()
        
        token_info = response.json()
        
        return {
            "access_token": token_info.get("access_token"),
            "refresh_token": token_info.get("refresh_token"),
            "expires_at": token_info.get("expires_at")
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to refresh token: {str(e)}")
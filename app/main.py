from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import logging

# Load environment variables first
load_dotenv()

# Import logging config (sets up logging)
from .logging_config import LogConfig
from .config import Config
from .auth import router as auth_router
from .activities import router as activities_router
from .webhooks import router as webhooks_router

logger = LogConfig.get_logger(__name__)

app = FastAPI(
    title="Strava Workout Description Generator",
    description="Automatically generates workout descriptions from Strava activity data",
    version="1.0.0"
)

# Configure CORS - restrict in production
if Config.is_production():
    allowed_origins = [
        "https://*.railway.app",
        "https://your-production-domain.com"  # TODO: Replace with actual domain
    ]
    logger.info("Running in production mode with restricted CORS")
else:
    allowed_origins = ["*"]
    logger.info("Running in development mode with open CORS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(auth_router)
app.include_router(activities_router)
app.include_router(webhooks_router)

@app.get("/")
async def root():
    """Serve the main landing page"""
    logger.debug("Serving landing page")
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {
        "status": "healthy", 
        "environment": Config.RAILWAY_ENVIRONMENT or "development",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Configure uvicorn logging
    log_level = Config.get_log_level().lower()
    
    logger.info(f"Starting server with log level: {log_level}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level=log_level,
        access_log=not Config.is_production()  # Disable access logs in production
    )
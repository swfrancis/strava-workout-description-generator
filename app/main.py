from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
from app.auth import router as auth_router
from app.activities import router as activities_router
from app.webhooks import router as webhooks_router

load_dotenv()

app = FastAPI(
    title="Strava Workout Description Generator",
    description="Automatically generates workout descriptions from Strava activity data",
    version="1.0.0"
)

# Configure CORS - restrict in production
allowed_origins = ["*"] if os.getenv("RAILWAY_ENVIRONMENT") != "production" else [
    "https://*.railway.app",
    "https://your-domain.com"  # Replace with your actual domain
]

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
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
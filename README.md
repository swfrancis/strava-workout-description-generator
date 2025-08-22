# LapLogic

Automatically generates intelligent workout descriptions from Strava activity data by analysing lap times and workout patterns.

## Features

- **Strava OAuth Integration** - Secure connection to your Strava account with mobile-friendly flow
- **Comprehensive Interval Detection** - Advanced pattern recognition system that analyses lap data and workout structures
- **Smart Workout Analysis** - Detects intervals, tempo runs, and structured workouts (e.g., "5 x 3mins @ 3:30min/km")
- **Professional Descriptions** - Generates clean, professional workout descriptions for Strava activities
- **Automatic Processing** - Analyses and generates descriptions immediately after workout completion

## Tech Stack

- **Backend**: FastAPI (Python)
- **Data Analysis**: pandas, numpy, scipy, scikit-learn
- **Authentication**: Strava OAuth 2.0
- **API**: RESTful endpoints with auto-generated documentation

## Setup

### Prerequisites
- Python 3.8+
- Strava API credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/laplogic.git
cd laplogic
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Strava API credentials
```

4. Get Strava API credentials:
   - Go to [developers.strava.com](https://developers.strava.com)
   - Create a new application
   - Add credentials to `.env`

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## Usage

1. **Authenticate**: Visit `http://localhost:8000/auth/login`
2. **API Documentation**: View interactive docs at `http://localhost:8000/docs`
3. **Health Check**: Test at `http://localhost:8000/health`

## API Endpoints

- `GET /auth/login` - Start Strava OAuth flow
- `GET /auth/callback` - Handle OAuth callback
- `POST /auth/refresh` - Refresh access token
- `GET /health` - Health check

## Development Status

🚀 **Core Features Implemented**

Currently implemented:
- ✅ FastAPI project structure with comprehensive API endpoints
- ✅ Strava OAuth authentication with mobile-friendly flow
- ✅ Comprehensive interval detection system with advanced pattern recognition
- ✅ Strava API client for activity data retrieval
- ✅ Lap data analysis with sophisticated clustering algorithms
- ✅ Professional workout description generation
- ✅ Optimised codebase with improved maintainability

Coming next:
- 🔄 Enhanced frontend interface
- 🔄 Additional workout pattern recognition
- 🔄 User customisation options

## Contributing

This project is in active development. Feel free to open issues or submit pull requests.

## License

MIT License
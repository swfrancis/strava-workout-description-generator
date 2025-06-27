# Strava Workout Description Generator

Automatically generates intelligent workout descriptions from Strava activity data by analyzing lap times and workout patterns.

## Features

- **Strava OAuth Integration** - Secure connection to your Strava account
- **Lap-based Analysis** - Detects intervals from lap data (e.g., "5 x 3mins @ 3:30min/km w/ 2mins rest")
- **Smart Pattern Recognition** - Uses machine learning to identify workout patterns when lap data isn't available
- **Automatic Processing** - Generates descriptions immediately after workout completion

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
git clone https://github.com/yourusername/strava-workout-description-generator.git
cd strava-workout-description-generator
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

🚧 **Work in Progress**

Currently implemented:
- ✅ FastAPI project structure
- ✅ Strava OAuth authentication
- ✅ Basic API endpoints

Coming next:
- 🔄 Strava API client for activity data
- 🔄 Lap data analysis with clustering
- 🔄 Spike detection for non-lap workouts
- 🔄 ML-based interval detection
- 🔄 Description generation
- 🔄 Frontend interface

## Contributing

This project is in active development. Feel free to open issues or submit pull requests.

## License

MIT License
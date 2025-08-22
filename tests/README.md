# Test Scripts

This directory contains test scripts for LapLogic.

## Test Files

### `test_client.py`
- Tests the basic Strava API client functionality
- Requires a valid Strava access token
- Usage: `python tests/test_client.py [access_token]`

### `test_api.py`  
- Tests all FastAPI endpoints with real Strava data
- Requires the FastAPI server to be running (`uvicorn app.main:app --reload`)
- Requires a valid Strava access token
- Usage: `python tests/test_api.py [access_token]`

### `test_imperial.py`
- Unit tests for imperial distance detection logic
- No external dependencies or tokens required
- Usage: `python tests/test_imperial.py`

## Getting a Strava Access Token

1. Start the FastAPI server: `uvicorn app.main:app --reload`
2. Visit: `http://localhost:8000/auth/login`
3. Complete the Strava OAuth flow
4. Use the returned access token in the test scripts

## Running Tests

```bash
# Test imperial distance detection (no token needed)
python tests/test_imperial.py

# Test Strava API client (token required)
python tests/test_client.py YOUR_ACCESS_TOKEN

# Test all API endpoints (server + token required)
uvicorn app.main:app --reload &
python tests/test_api.py YOUR_ACCESS_TOKEN
```
#!/usr/bin/env python3
"""
Simple test script for Strava API client
Run this after getting an access token from the auth flow
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.strava_client import StravaClient, StravaAPIError

def test_strava_client(access_token=None):
    """Test basic Strava client functionality"""
    
    # Get access token from parameter, environment, or command line
    if not access_token:
        access_token = os.getenv('STRAVA_ACCESS_TOKEN')
    
    if not access_token and len(sys.argv) > 1:
        access_token = sys.argv[1]
    
    if not access_token:
        try:
            access_token = input("Enter your Strava access token: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("No access token provided. Please run the auth flow first.")
            return False
    
    if not access_token:
        print("No access token provided. Please run the auth flow first.")
        return False

    # Create client
    client = StravaClient(access_token=access_token)

    try:
        print("🔍 Testing athlete info...")
        athlete = client.get_athlete()
        print(
            f"✅ Connected as: {athlete.get('firstname')} {athlete.get('lastname')}")
        print(f"   Athlete ID: {athlete.get('id')}")

        print("\n🏃 Testing recent activities...")
        activities = client.get_activities(per_page=5)
        print(f"✅ Found {len(activities)} recent activities:")

        for i, activity in enumerate(activities[:3], 1):
            print(f"   {i}. {activity.get('name')} ({activity.get('type')})")
            print(f"      Date: {activity.get('start_date_local')}")
            print(f"      Distance: {activity.get('distance', 0)/1000:.1f}km")
            print(f"      Duration: {activity.get('elapsed_time', 0)//60}min")

        if activities:
            activity_id = activities[0]['id']
            print(
                f"\n📊 Testing activity details for activity {activity_id}...")

            try:
                details = client.get_activity_details(activity_id)
                print(f"✅ Activity details retrieved")
                print(
                    f"   Splits: {len(details.get('splits_metric', []))} splits")
                print(f"   Kudos: {details.get('kudos_count', 0)}")

                print(f"\n🏁 Testing laps for activity {activity_id}...")
                laps = client.get_activity_laps(activity_id)
                print(f"✅ Found {len(laps)} laps")

                for i, lap in enumerate(laps[:3], 1):
                    elapsed = lap.get('elapsed_time', 0)
                    distance = lap.get('distance', 0)
                    print(
                        f"   Lap {i}: {elapsed//60}:{elapsed % 60:02d} - {distance/1000:.2f}km")

                print(f"\n📈 Testing streams for activity {activity_id}...")
                streams = client.get_activity_streams(
                    activity_id, keys=['time', 'distance', 'velocity_smooth'])
                print(f"✅ Streams retrieved: {list(streams.keys())}")

                if 'time' in streams:
                    time_data = streams['time']['data']
                    print(f"   Time stream: {len(time_data)} data points")

            except StravaAPIError as e:
                print(f"⚠️  Error testing activity details: {e}")

        print(f"\n✅ All tests completed successfully!")

    except StravaAPIError as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🧪 Strava API Client Test")
    print("=" * 30)
    print("First, make sure you have a valid access token.")
    print("You can get one by visiting: http://localhost:8000/auth/login")
    print("(Make sure your FastAPI server is running)")
    print()

    test_strava_client()

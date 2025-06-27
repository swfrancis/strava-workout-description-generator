#!/usr/bin/env python3
"""
Test script for the complete Strava API integration
Tests the FastAPI endpoints with real Strava data
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoints(access_token: str, base_url: str = "http://localhost:8000"):
    """Test all API endpoints with real Strava data"""
    
    print("🧪 Testing Strava API Integration")
    print("=" * 50)
    
    # Test 1: Get recent activities
    print("\n1️⃣ Testing GET /activities/recent")
    try:
        response = requests.get(f"{base_url}/activities/recent", params={
            "access_token": access_token,
            "days": 7
        })
        
        if response.status_code == 200:
            data = response.json()
            activities = data.get('activities', [])
            print(f"✅ Found {len(activities)} recent activities")
            
            if activities:
                activity = activities[0]
                print(f"   Latest: {activity.get('name')} ({activity.get('type')})")
                print(f"   Distance: {activity.get('distance', 0)/1000:.1f}km")
                
                # Store activity ID for further tests
                test_activity_id = activity.get('id')
                print(f"   Using activity {test_activity_id} for detailed tests")
            else:
                print("   No activities found - please ensure you have recent Strava activities")
                return False
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 2: Get activity details
    print(f"\n2️⃣ Testing GET /activities/{test_activity_id}")
    try:
        response = requests.get(f"{base_url}/activities/{test_activity_id}", params={
            "access_token": access_token,
            "include_laps": True,
            "include_streams": True
        })
        
        if response.status_code == 200:
            data = response.json()
            activity = data.get('activity', {})
            laps = data.get('laps', [])
            print(f"✅ Activity details retrieved")
            print(f"   Name: {activity.get('name')}")
            print(f"   Type: {activity.get('type')}")
            print(f"   Laps: {len(laps)}")
            print(f"   Has streams: {data.get('has_streams', False)}")
            print(f"   Stream types: {data.get('stream_types', [])}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 3: Get activity laps
    print(f"\n3️⃣ Testing GET /activities/{test_activity_id}/laps")
    try:
        response = requests.get(f"{base_url}/activities/{test_activity_id}/laps", params={
            "access_token": access_token
        })
        
        if response.status_code == 200:
            data = response.json()
            laps = data.get('laps', [])
            print(f"✅ Found {len(laps)} laps")
            
            for i, lap in enumerate(laps[:3], 1):
                elapsed = lap.get('elapsed_time', 0)
                distance = lap.get('distance', 0)
                speed = lap.get('average_speed', 0)
                print(f"   Lap {i}: {elapsed//60}:{elapsed%60:02d}, {distance/1000:.2f}km, {speed*3.6:.1f}km/h")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 4: Get activity streams
    print(f"\n4️⃣ Testing GET /activities/{test_activity_id}/streams")
    try:
        response = requests.get(f"{base_url}/activities/{test_activity_id}/streams", params={
            "access_token": access_token,
            "keys": "time,distance,velocity_smooth"
        })
        
        if response.status_code == 200:
            data = response.json()
            streams = data.get('streams', {})
            print(f"✅ Streams retrieved: {list(streams.keys())}")
            
            for stream_type, stream_data in streams.items():
                if 'data' in stream_data:
                    print(f"   {stream_type}: {len(stream_data['data'])} data points")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 5: Get activity summary
    print(f"\n5️⃣ Testing GET /activities/{test_activity_id}/summary")
    try:
        response = requests.get(f"{base_url}/activities/{test_activity_id}/summary", params={
            "access_token": access_token
        })
        
        if response.status_code == 200:
            data = response.json()
            activity = data.get('activity', {})
            laps = data.get('laps', [])
            streams = data.get('streams', {})
            print(f"✅ Activity summary retrieved")
            print(f"   Activity: {activity.get('name')} - {activity.get('distance', 0)/1000:.1f}km")
            print(f"   Laps: {len(laps)}")
            print(f"   Streams: {len(streams)} types")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 6: Analyze activity
    print(f"\n6️⃣ Testing POST /activities/{test_activity_id}/analyze")
    try:
        response = requests.post(f"{base_url}/activities/{test_activity_id}/analyze", 
            params={"access_token": access_token},
            json={
                "activity_id": test_activity_id,
                "include_streams": True,
                "analysis_type": "auto",
                "generate_description": True,
                "update_activity": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            print(f"✅ Activity analysis completed")
            print(f"   Method: {analysis.get('analysis_method')}")
            print(f"   Confidence: {analysis.get('confidence', 0):.2f}")
            print(f"   Short description: {analysis.get('short_description')}")
            print(f"   Detailed description: {analysis.get('detailed_description')}")
            if analysis.get('lap_analysis'):
                print(f"   Lap analysis: {analysis.get('lap_analysis')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    print(f"\n✅ All API tests completed successfully!")
    print(f"🎉 Your Strava API integration is working perfectly!")
    
    return True

def main():
    if len(sys.argv) > 1:
        access_token = sys.argv[1]
    else:
        access_token = input("Enter your Strava access token: ").strip()
    
    if not access_token:
        print("❌ No access token provided")
        print("Get one from: http://localhost:8000/auth/login")
        return False
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ FastAPI server not responding. Please start it with:")
            print("   uvicorn app.main:app --reload")
            return False
    except:
        print("❌ FastAPI server not running. Please start it with:")
        print("   uvicorn app.main:app --reload")
        return False
    
    return test_api_endpoints(access_token)

if __name__ == "__main__":
    main()
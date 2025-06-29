#!/usr/bin/env python3
"""
Test script for imperial distance detection
"""

import sys
import os
# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analysis import LapAnalyser
from app.models import Lap

def test_imperial_distance_detection():
    """Test imperial distance detection logic"""
    print("🧪 Testing Imperial Distance Detection")
    print("=" * 50)
    
    analyser = LapAnalyser()
    
    # Test distances in meters
    test_cases = [
        (1609.344, "1 mile"),      # Exactly 1 mile
        (1600, "1 mile"),          # Close to 1 mile (within 5%)
        (2414.016, "1.5 miles"),   # 1.5 miles
        (3218.688, "2 miles"),     # 2 miles
        (4023.36, "2.5 miles"),    # 2.5 miles
        (8046.72, "5 miles"),      # 5 miles
        (1000, "not imperial"),    # 1km - should not match
        (800, "not imperial"),     # 800m - should not match
        (500, "not imperial"),     # 500m - should not match
    ]
    
    print("\n🔍 Testing _is_imperial_distance():")
    for distance_meters, expected in test_cases:
        is_imperial, display = analyzer._is_imperial_distance(distance_meters)
        
        if expected == "not imperial":
            expected_result = False
            success = not is_imperial
        else:
            expected_result = True
            success = is_imperial and display == expected
        
        status = "✅" if success else "❌"
        print(f"   {status} {distance_meters}m -> {is_imperial}, '{display}' (expected: {expected})")
    
    # Test workout classification
    print("\n🏃 Testing _is_distance_based_workout():")
    distance_time_cases = [
        (1609.344, 300, True),   # 1 mile in 5 min - should be distance-based
        (1000, 180, True),       # 1km in 3 min - should be distance-based  
        (400, 90, True),         # 400m in 90s - should be distance-based
        (200, 30, True),         # 200m in 30s - distance-based (standard track distance)
        (100, 15, True),         # 100m in 15s - distance-based (standard track distance)
        (2414.016, 600, True),   # 1.5 miles - should be distance-based
    ]
    
    for distance, time, expected in distance_time_cases:
        result = analyzer._is_distance_based_workout(distance, time)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {distance}m, {time}s -> {result} (expected: {expected})")
    
    # Test full description generation
    print("\n📝 Testing full description generation:")
    description_cases = [
        (3, 1609.344, 300, "3 x 1 mile"),          # 3 x 1 mile
        (5, 2414.016, 480, "5 x 1.5 miles"),       # 5 x 1.5 miles  
        (4, 1000, 240, "4 x 1km"),                 # 4 x 1km (metric)
        (6, 180, 30, "6 x 30s"),                   # 6 x 30s (time-based)
        (8, 400, 90, "8 x 400m"),                  # 8 x 400m (metric distance)
    ]
    
    for count, distance, time, expected in description_cases:
        description = analyzer._generate_pattern_description(count, distance, time, [])
        status = "✅" if description == expected else "❌"
        print(f"   {status} {count} x {distance}m, {time}s -> '{description}' (expected: '{expected}')")
    
    print("\n🎉 Imperial distance detection test completed!")

if __name__ == "__main__":
    test_imperial_distance_detection()
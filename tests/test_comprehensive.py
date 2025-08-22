#!/usr/bin/env python3
"""
Comprehensive test suite for LapLogic
Tests all aspects of interval detection and pattern recognition
"""

import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.models import Lap
from app.analysis import analyse_workout_from_laps, LapAnalyser

# Import test cases from same directory
try:
    from lap_test_cases import TEST_CASES, get_test_case_by_name
except ImportError:
    from tests.lap_test_cases import TEST_CASES, get_test_case_by_name
from datetime import datetime

def create_lap_from_dict(lap_data):
    """Convert test case lap data to Lap object"""
    return Lap(
        id=lap_data["lap_index"],
        activity={"id": 1},
        athlete={"id": 1},
        lap_index=lap_data["lap_index"],
        distance=lap_data["distance"],
        elapsed_time=lap_data["time"],
        moving_time=lap_data["time"],
        average_speed=lap_data["distance"] / lap_data["time"] if lap_data["time"] > 0 else 0,
        start_index=0,
        end_index=100,
        name=f"Lap {lap_data['lap_index']}",
        start_date=datetime.fromisoformat("2024-01-01T00:00:00+00:00"),
        start_date_local=datetime.fromisoformat("2024-01-01T00:00:00+00:00"),
        total_elevation_gain=0
    )

def test_basic_functionality():
    """Test core interval detection functionality"""
    print("🧪 Basic Functionality Tests")
    print("=" * 50)
    
    key_cases = [
        "Case 1A",  # 4x30s with rest
        "Case 2A",  # 5x400m with rest
        "Case 7A",  # Auto-lap (should fail)
        "Case 8A",  # User's 20s case
        "Case 8C",  # 3x400m pattern
        "Case 8D",  # Complex/chaotic (should fail)
    ]
    
    for case in TEST_CASES:
        case_name = case["name"]
        if any(key in case_name for key in key_cases):
            print(f"\n--- {case_name} ---")
            
            # Convert test data to Lap objects
            laps = [create_lap_from_dict(lap_data) for lap_data in case["laps"]]
            
            # Run analysis
            result = analyse_workout_from_laps(laps)
            
            if result and result.primary_pattern:
                actual = result.primary_pattern.description
                print(f"Expected: {case['expected']}")
                print(f"Actual: {actual}")
                
                if actual == case['expected']:
                    print("✅ PASS")
                else:
                    print("❌ FAIL")
            else:
                print(f"Expected: {case['expected']}")
                print("Actual: No intervals detected")
                
                if case['expected'] is None:
                    print("✅ PASS")
                else:
                    print("❌ FAIL")

def test_pattern_detection():
    """Test different pattern types"""
    print("\n\n🧪 Pattern Detection Tests")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Regular intervals: 4 x 400m",
            "laps": [
                {"time": 88, "distance": 400, "lap_index": 1},
                {"time": 180, "distance": 350, "lap_index": 2},  # rest
                {"time": 90, "distance": 400, "lap_index": 3},
                {"time": 175, "distance": 360, "lap_index": 4},  # rest
                {"time": 92, "distance": 400, "lap_index": 5},
                {"time": 182, "distance": 355, "lap_index": 6},  # rest
                {"time": 89, "distance": 400, "lap_index": 7},
            ],
            "expected": "4 x 400m"
        },
        {
            "name": "Distance pyramid: 200-400-800-400-200m",
            "laps": [
                {"time": 42, "distance": 200, "lap_index": 1},
                {"time": 120, "distance": 300, "lap_index": 2},  # rest
                {"time": 88, "distance": 400, "lap_index": 3},
                {"time": 180, "distance": 400, "lap_index": 4},  # rest
                {"time": 185, "distance": 800, "lap_index": 5},
                {"time": 240, "distance": 500, "lap_index": 6},  # rest
                {"time": 90, "distance": 400, "lap_index": 7},
                {"time": 120, "distance": 300, "lap_index": 8},  # rest
                {"time": 45, "distance": 200, "lap_index": 9},
            ],
            "expected": "200m-400m-800m-400m-200m"
        },
        {
            "name": "Distance ladder: 200-400-600-800m",
            "laps": [
                {"time": 55, "distance": 200, "lap_index": 1},
                {"time": 120, "distance": 300, "lap_index": 2},  # rest
                {"time": 88, "distance": 400, "lap_index": 3},
                {"time": 180, "distance": 350, "lap_index": 4},  # rest
                {"time": 138, "distance": 600, "lap_index": 5},
                {"time": 200, "distance": 400, "lap_index": 6},  # rest
                {"time": 185, "distance": 800, "lap_index": 7},
            ],
            "expected": "200m-400m-600m-800m"
        },
        {
            "name": "Mixed intervals: 400-800-400-800m",
            "laps": [
                {"time": 90, "distance": 400, "lap_index": 1},
                {"time": 180, "distance": 400, "lap_index": 2},  # rest
                {"time": 180, "distance": 800, "lap_index": 3},
                {"time": 240, "distance": 500, "lap_index": 4},  # rest
                {"time": 88, "distance": 400, "lap_index": 5},
                {"time": 185, "distance": 400, "lap_index": 6},  # rest
                {"time": 178, "distance": 800, "lap_index": 7},
            ],
            "expected": "400m-800m-400m-800m"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        
        laps = [create_lap_from_dict(lap_data) for lap_data in case["laps"]]
        result = analyse_workout_from_laps(laps)
        
        if result and result.primary_pattern:
            actual = result.primary_pattern.description
            print(f"Expected: {case['expected']}")
            print(f"Actual: {actual}")
            
            if actual == case['expected']:
                print("✅ PASS")
            else:
                print("❌ FAIL")
        else:
            print("❌ FAIL: No intervals detected")

def test_repeated_patterns():
    """Test repeated pattern detection"""
    print("\n\n🧪 Repeated Pattern Tests")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "3 x (200m-400m-200m) - Repeated Pyramids",
            "laps": [
                # First pyramid: 200-400-200
                {"time": 42, "distance": 200, "lap_index": 1},
                {"time": 120, "distance": 300, "lap_index": 2},  # rest
                {"time": 88, "distance": 400, "lap_index": 3},
                {"time": 180, "distance": 350, "lap_index": 4},  # rest
                {"time": 44, "distance": 200, "lap_index": 5},
                {"time": 120, "distance": 300, "lap_index": 6},  # rest
                
                # Second pyramid: 200-400-200
                {"time": 43, "distance": 200, "lap_index": 7},
                {"time": 125, "distance": 310, "lap_index": 8},  # rest
                {"time": 90, "distance": 400, "lap_index": 9},
                {"time": 175, "distance": 340, "lap_index": 10}, # rest
                {"time": 45, "distance": 200, "lap_index": 11},
                {"time": 122, "distance": 305, "lap_index": 12}, # rest
                
                # Third pyramid: 200-400-200
                {"time": 41, "distance": 200, "lap_index": 13},
                {"time": 127, "distance": 315, "lap_index": 14}, # rest
                {"time": 92, "distance": 400, "lap_index": 15},
                {"time": 178, "distance": 345, "lap_index": 16}, # rest
                {"time": 46, "distance": 200, "lap_index": 17},
            ],
            "expected": "3 x (200m-400m-200m)"
        },
        {
            "name": "4 x (400m-800m) - Repeated Alternating",
            "laps": [
                {"time": 88, "distance": 400, "lap_index": 1},
                {"time": 180, "distance": 400, "lap_index": 2},  # rest
                {"time": 185, "distance": 800, "lap_index": 3},
                {"time": 240, "distance": 500, "lap_index": 4},  # rest
                {"time": 90, "distance": 400, "lap_index": 5},
                {"time": 175, "distance": 420, "lap_index": 6},  # rest
                {"time": 188, "distance": 800, "lap_index": 7},
                {"time": 235, "distance": 480, "lap_index": 8},  # rest
                {"time": 89, "distance": 400, "lap_index": 9},
                {"time": 182, "distance": 410, "lap_index": 10}, # rest
                {"time": 190, "distance": 800, "lap_index": 11},
                {"time": 245, "distance": 490, "lap_index": 12}, # rest
                {"time": 87, "distance": 400, "lap_index": 13},
                {"time": 178, "distance": 430, "lap_index": 14}, # rest
                {"time": 187, "distance": 800, "lap_index": 15},
            ],
            "expected": "4 x (400m-800m)"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        
        laps = [create_lap_from_dict(lap_data) for lap_data in case["laps"]]
        result = analyse_workout_from_laps(laps)
        
        if result and result.primary_pattern:
            actual = result.primary_pattern.description
            print(f"Expected: {case['expected']}")
            print(f"Actual: {actual}")
            
            if actual == case['expected']:
                print("✅ PASS")
            else:
                print("❌ FAIL")
        else:
            print("❌ FAIL: No intervals detected")

def test_consistency_checking():
    """Test consistency validation"""
    print("\n\n🧪 Consistency Checking Tests")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Consistent intervals (CV ~2%): 4 x 400m",
            "laps": [
                {"time": 88, "distance": 400, "lap_index": 1},
                {"time": 180, "distance": 350, "lap_index": 2},  # rest
                {"time": 90, "distance": 400, "lap_index": 3},
                {"time": 175, "distance": 360, "lap_index": 4},  # rest
                {"time": 92, "distance": 400, "lap_index": 5},
                {"time": 182, "distance": 355, "lap_index": 6},  # rest
                {"time": 89, "distance": 400, "lap_index": 7},
            ],
            "expected": "4 x 400m"
        },
        {
            "name": "Chaotic intervals (should reject)",
            "laps": [
                {"time": 90, "distance": 400, "lap_index": 1},   # 400m interval
                {"time": 180, "distance": 400, "lap_index": 2},  # rest
                {"time": 30, "distance": 150, "lap_index": 3},   # 30s sprint
                {"time": 120, "distance": 200, "lap_index": 4},  # rest
                {"time": 180, "distance": 600, "lap_index": 5},  # 3min tempo
                {"time": 240, "distance": 400, "lap_index": 6},  # rest
                {"time": 45, "distance": 200, "lap_index": 7},   # 45s interval
                {"time": 200, "distance": 350, "lap_index": 8},  # rest
                {"time": 240, "distance": 1000, "lap_index": 9}, # 4min threshold
            ],
            "expected": None
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        
        laps = [create_lap_from_dict(lap_data) for lap_data in case["laps"]]
        result = analyse_workout_from_laps(laps)
        
        if result and result.primary_pattern:
            actual = result.primary_pattern.description
            print(f"Expected: {case['expected']}")
            print(f"Actual: {actual}")
            
            if actual == case['expected']:
                print("✅ PASS")
            else:
                print("❌ FAIL")
        else:
            print(f"Expected: {case['expected']}")
            print("Actual: No intervals detected")
            
            if case['expected'] is None:
                print("✅ PASS")
            else:
                print("❌ FAIL")

def main():
    """Run all test suites"""
    print("🏃‍♂️ LapLogic - Comprehensive Test Suite")
    print("=" * 80)
    
    test_basic_functionality()
    test_pattern_detection()
    test_repeated_patterns()
    test_consistency_checking()
    
    print("\n" + "=" * 80)
    print("✅ All test suites completed!")

if __name__ == "__main__":
    main()
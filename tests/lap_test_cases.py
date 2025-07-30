"""
Test cases for interval detection logic
These define the expected behavior for different workout types
"""

from typing import List, Dict, Any

# Test case format: (laps_data, expected_description, notes)
TEST_CASES = [
    
    # 1. TIME-BASED INTERVALS
    {
        "name": "Case 1A: 4 x 30s sprints with rest",
        "laps": [
            {"time": 30, "distance": 120, "lap_index": 1},  # work
            {"time": 90, "distance": 180, "lap_index": 2},  # 90s rest
            {"time": 30, "distance": 125, "lap_index": 3},  # work
            {"time": 92, "distance": 175, "lap_index": 4},  # 92s rest
            {"time": 30, "distance": 118, "lap_index": 5},  # work
            {"time": 88, "distance": 185, "lap_index": 6},  # 88s rest
            {"time": 30, "distance": 122, "lap_index": 7}   # work
        ],
        "expected": "4 x 30s",
        "notes": "Times consistent, should identify work vs rest laps"
    },
    
    {
        "name": "Case 1B: 6 x 3min tempo with warmup and rest",
        "laps": [
            {"time": 480, "distance": 1200, "lap_index": 1},  # 8min warmup
            {"time": 180, "distance": 800, "lap_index": 2},   # work
            {"time": 120, "distance": 300, "lap_index": 3},   # 2min rest
            {"time": 182, "distance": 795, "lap_index": 4},   # work
            {"time": 118, "distance": 295, "lap_index": 5},   # 2min rest
            {"time": 178, "distance": 805, "lap_index": 6},   # work
            {"time": 122, "distance": 305, "lap_index": 7},   # 2min rest
            {"time": 181, "distance": 798, "lap_index": 8},   # work
            {"time": 119, "distance": 298, "lap_index": 9},   # 2min rest
            {"time": 179, "distance": 802, "lap_index": 10},  # work
            {"time": 121, "distance": 302, "lap_index": 11},  # 2min rest
            {"time": 180, "distance": 800, "lap_index": 12}   # work
        ],
        "expected": "6 x 3min",
        "notes": "3 minute intervals with warmup and rest periods to identify"
    },
    
    # 2. DISTANCE-BASED INTERVALS
    {
        "name": "Case 2A: 5 x 400m track with rest",
        "laps": [
            {"time": 90, "distance": 400, "lap_index": 1},   # work
            {"time": 180, "distance": 400, "lap_index": 2},  # 3min rest jog
            {"time": 88, "distance": 400, "lap_index": 3},   # work
            {"time": 178, "distance": 395, "lap_index": 4},  # 3min rest jog
            {"time": 92, "distance": 400, "lap_index": 5},   # work
            {"time": 182, "distance": 405, "lap_index": 6},  # 3min rest jog
            {"time": 89, "distance": 400, "lap_index": 7},   # work
            {"time": 179, "distance": 398, "lap_index": 8},  # 3min rest jog
            {"time": 91, "distance": 400, "lap_index": 9}    # work
        ],
        "expected": "5 x 400m",
        "notes": "Distances consistent for work, times vary - rest laps are slower"
    },
    
    {
        "name": "Case 2B: 3 x 1km road with rest and cooldown",
        "laps": [
            {"time": 250, "distance": 1000, "lap_index": 1},  # work
            {"time": 240, "distance": 600, "lap_index": 2},   # 4min rest jog
            {"time": 245, "distance": 1000, "lap_index": 3},  # work
            {"time": 238, "distance": 595, "lap_index": 4},   # 4min rest jog
            {"time": 255, "distance": 1000, "lap_index": 5},  # work
            {"time": 600, "distance": 1500, "lap_index": 6}   # 10min cooldown
        ],
        "expected": "3 x 1km",
        "notes": "1km intervals with rest periods and cooldown to filter"
    },
    
    # 3. PYRAMID INTERVALS
    {
        "name": "Case 3A: Time-based pyramid",
        "laps": [
            {"time": 60, "distance": 240, "lap_index": 1},
            {"time": 120, "distance": 520, "lap_index": 2},
            {"time": 180, "distance": 780, "lap_index": 3},
            {"time": 120, "distance": 480, "lap_index": 4},
            {"time": 60, "distance": 220, "lap_index": 5}
        ],
        "expected": "1-2-3-2-1min",
        "notes": "Times consistent in pattern, distances vary with pacing"
    },
    
    {
        "name": "Case 3B: Distance-based pyramid",
        "laps": [
            {"time": 42, "distance": 200, "lap_index": 1},
            {"time": 88, "distance": 400, "lap_index": 2},
            {"time": 205, "distance": 800, "lap_index": 3},
            {"time": 98, "distance": 400, "lap_index": 4},
            {"time": 48, "distance": 200, "lap_index": 5}
        ],
        "expected": "200-400-800-400-200m",
        "notes": "Distances consistent in pattern, times vary with fatigue"
    },
    
    # 4. LADDER INTERVALS
    {
        "name": "Case 4A: Time-based ladder with warmup and cooldown",
        "laps": [
            {"time": 600, "distance": 1800, "lap_index": 1},  # 10min warmup
            {"time": 60, "distance": 280, "lap_index": 2},
            {"time": 120, "distance": 540, "lap_index": 3},
            {"time": 180, "distance": 720, "lap_index": 4},
            {"time": 240, "distance": 920, "lap_index": 5},
            {"time": 480, "distance": 1200, "lap_index": 6}  # 8min cooldown
        ],
        "expected": "1-2-3-4min",
        "notes": "Times consistent progression with warmup/cooldown to filter"
    },
    
    {
        "name": "Case 4B: Distance-based ladder",
        "laps": [
            {"time": 185, "distance": 800, "lap_index": 1},
            {"time": 148, "distance": 600, "lap_index": 2},
            {"time": 102, "distance": 400, "lap_index": 3},
            {"time": 55, "distance": 200, "lap_index": 4}
        ],
        "expected": "800-600-400-200m",
        "notes": "Distances consistent progression, times vary"
    },
    
    # 5. COMPLEX/MIXED INTERVALS
    {
        "name": "Case 5A: Mixed intervals",
        "laps": [
            {"time": 90, "distance": 400, "lap_index": 1},
            {"time": 180, "distance": 800, "lap_index": 2},
            {"time": 88, "distance": 400, "lap_index": 3},
            {"time": 178, "distance": 800, "lap_index": 4}
        ],
        "expected": "2 x 400m, 2 x 800m",  # or "4 intervals"
        "notes": "Two different interval types mixed"
    },
    
    # 6. WITH REST PERIODS  
    {
        "name": "Case 6A: With recovery",
        "work_laps": [
            {"time": 90, "distance": 400, "lap_index": 1},
            {"time": 88, "distance": 400, "lap_index": 3},
            {"time": 92, "distance": 400, "lap_index": 5}
        ],
        "rest_laps": [
            {"time": 150, "distance": 200, "lap_index": 2},
            {"time": 155, "distance": 200, "lap_index": 4}
        ],
        "expected": "3 x 400m",
        "notes": "Clear work/rest pattern"
    },
    
    # 7. EDGE CASES
    {
        "name": "Case 7A: Auto-lap (should skip)",
        "laps": [
            {"time": 270, "distance": 1000, "lap_index": 1},
            {"time": 265, "distance": 1000, "lap_index": 2},
            {"time": 275, "distance": 1000, "lap_index": 3},
            {"time": 135, "distance": 500, "lap_index": 4}  # partial last lap
        ],
        "expected": None,  # No intervals detected
        "notes": "Auto-generated 1km laps with partial final lap"
    },
    
    {
        "name": "Case 7B: Too few intervals",
        "laps": [
            {"time": 90, "distance": 400, "lap_index": 1},
            {"time": 88, "distance": 400, "lap_index": 2}
        ],
        "expected": None,  # No intervals detected
        "notes": "Only 2 laps - need 3+ for intervals"
    },
    
    # 8. REAL-WORLD EDGE CASES
    {
        "name": "Case 8A: Short intervals with warmup and rest (like user's 20s case)",
        "laps": [
            {"time": 360, "distance": 900, "lap_index": 1},  # 6min warmup
            {"time": 20, "distance": 105, "lap_index": 2},   # work
            {"time": 40, "distance": 80, "lap_index": 3},    # 40s rest walk
            {"time": 20, "distance": 109, "lap_index": 4},   # work
            {"time": 42, "distance": 75, "lap_index": 5},    # 42s rest walk
            {"time": 20, "distance": 112, "lap_index": 6},   # work
            {"time": 38, "distance": 85, "lap_index": 7},    # 38s rest walk
            {"time": 20, "distance": 110, "lap_index": 8}    # work
        ],
        "expected": "4 x 20s",
        "notes": "Short time intervals with warmup and rest - should identify work vs rest"
    },
    
    {
        "name": "Case 8B: Close to standard distance",
        "laps": [
            {"time": 92, "distance": 395, "lap_index": 1},
            {"time": 89, "distance": 402, "lap_index": 2},
            {"time": 91, "distance": 398, "lap_index": 3}
        ],
        "expected": "3 x 400m",
        "notes": "Close to 400m - should be recognized as distance-based"
    },
    
    {
        "name": "Case 8C: Simple 3 x 400m pattern (should pass)",
        "laps": [
            {"time": 480, "distance": 1200, "lap_index": 1},  # 8min warmup
            {"time": 88, "distance": 400, "lap_index": 2},    # 400m (1:28)
            {"time": 240, "distance": 400, "lap_index": 3},   # 4min rest walk
            {"time": 90, "distance": 400, "lap_index": 4},    # 400m (1:30)
            {"time": 245, "distance": 410, "lap_index": 5},   # 4min rest walk
            {"time": 92, "distance": 400, "lap_index": 6},    # 400m (1:32)
            {"time": 600, "distance": 1500, "lap_index": 7}   # 10min cooldown
        ],
        "expected": "3 x 400m",
        "notes": "Simple 3x400m pattern with clear work/rest - should detect correctly"
    },
    
    {
        "name": "Case 8D: Very complex/chaotic workout (should reject)",
        "laps": [
            {"time": 480, "distance": 1200, "lap_index": 1},  # 8min warmup
            {"time": 90, "distance": 400, "lap_index": 2},    # 400m interval
            {"time": 30, "distance": 150, "lap_index": 3},    # 30s sprint
            {"time": 180, "distance": 600, "lap_index": 4},   # 3min tempo
            {"time": 45, "distance": 200, "lap_index": 5},    # 45s interval
            {"time": 240, "distance": 1000, "lap_index": 6},  # 4min threshold
            {"time": 15, "distance": 80, "lap_index": 7},     # 15s strides
            {"time": 300, "distance": 1500, "lap_index": 8},  # 5min easy
            {"time": 60, "distance": 300, "lap_index": 9},    # 1min pickup
            {"time": 120, "distance": 200, "lap_index": 10},  # 2min hills
            {"time": 25, "distance": 120, "lap_index": 11},   # 25s sprint
            {"time": 600, "distance": 1800, "lap_index": 12}  # 10min cooldown
        ],
        "expected": None,
        "notes": "Chaotic mix - no consistent pattern, too varied to be intervals"
    },
    
    # 9. COMPLEX LADDER PATTERNS
    {
        "name": "Case 9A: Distance ladder with rest and cooldown",
        "laps": [
            {"time": 300, "distance": 800, "lap_index": 1},   # 5min warmup
            {"time": 55, "distance": 200, "lap_index": 2},    # 200m
            {"time": 120, "distance": 300, "lap_index": 3},   # 2min rest
            {"time": 88, "distance": 400, "lap_index": 4},    # 400m
            {"time": 180, "distance": 350, "lap_index": 5},   # 3min rest
            {"time": 138, "distance": 600, "lap_index": 6},   # 600m
            {"time": 200, "distance": 400, "lap_index": 7},   # 3:20 rest
            {"time": 185, "distance": 800, "lap_index": 8},   # 800m
            {"time": 480, "distance": 1200, "lap_index": 9}   # 8min cooldown
        ],
        "expected": "200-400-600-800m",
        "notes": "Distance ladder with different rest periods and cooldown"
    },
    
    {
        "name": "Case 9B: Time ladder ending with rest then cooldown",
        "laps": [
            {"time": 360, "distance": 900, "lap_index": 1},   # 6min warmup
            {"time": 60, "distance": 250, "lap_index": 2},    # 1min
            {"time": 90, "distance": 200, "lap_index": 3},    # 1:30 rest
            {"time": 120, "distance": 450, "lap_index": 4},   # 2min
            {"time": 120, "distance": 250, "lap_index": 5},   # 2min rest
            {"time": 180, "distance": 650, "lap_index": 6},   # 3min
            {"time": 150, "distance": 300, "lap_index": 7},   # 2:30 rest
            {"time": 240, "distance": 850, "lap_index": 8},   # 4min
            {"time": 180, "distance": 400, "lap_index": 9},   # 3min rest after last interval
            {"time": 600, "distance": 1500, "lap_index": 10}  # 10min cooldown
        ],
        "expected": "1-2-3-4min",
        "notes": "Time ladder ending with rest period before cooldown"
    },
    
    # 10. PYRAMID PATTERNS WITH COMPLICATIONS
    {
        "name": "Case 10A: Distance pyramid with uneven rest",
        "laps": [
            {"time": 420, "distance": 1000, "lap_index": 1},  # 7min warmup
            {"time": 88, "distance": 400, "lap_index": 2},    # 400m
            {"time": 180, "distance": 350, "lap_index": 3},   # 3min rest
            {"time": 185, "distance": 800, "lap_index": 4},   # 800m
            {"time": 240, "distance": 500, "lap_index": 5},   # 4min rest
            {"time": 275, "distance": 1200, "lap_index": 6},  # 1200m
            {"time": 300, "distance": 600, "lap_index": 7},   # 5min rest
            {"time": 190, "distance": 800, "lap_index": 8},   # 800m
            {"time": 200, "distance": 400, "lap_index": 9},   # 3:20 rest
            {"time": 92, "distance": 400, "lap_index": 10},   # 400m
            {"time": 180, "distance": 350, "lap_index": 11},  # 3min rest after pyramid
            {"time": 480, "distance": 1200, "lap_index": 12}  # 8min cooldown
        ],
        "expected": "400-800-1200-800-400m",
        "notes": "Classic pyramid with rest after completion and cooldown"
    },
    
    {
        "name": "Case 10B: Time pyramid with final rest",
        "laps": [
            {"time": 300, "distance": 750, "lap_index": 1},   # 5min warmup
            {"time": 60, "distance": 280, "lap_index": 2},    # 1min
            {"time": 90, "distance": 200, "lap_index": 3},    # 1:30 rest
            {"time": 120, "distance": 520, "lap_index": 4},   # 2min
            {"time": 120, "distance": 250, "lap_index": 5},   # 2min rest
            {"time": 180, "distance": 720, "lap_index": 6},   # 3min
            {"time": 180, "distance": 350, "lap_index": 7},   # 3min rest
            {"time": 122, "distance": 510, "lap_index": 8},   # 2min
            {"time": 92, "distance": 190, "lap_index": 9},    # 1:32 rest
            {"time": 58, "distance": 270, "lap_index": 10},   # 1min
            {"time": 240, "distance": 500, "lap_index": 11},  # 4min rest after pyramid
            {"time": 420, "distance": 1000, "lap_index": 12}  # 7min cooldown
        ],
        "expected": "1-2-3-2-1min",
        "notes": "Time pyramid with extended rest before cooldown"
    },
    
    # 11. MIXED INTERVAL TYPES WITH COMPLICATIONS
    {
        "name": "Case 11A: Mixed intervals with multiple rest patterns",
        "laps": [
            {"time": 480, "distance": 1200, "lap_index": 1},  # 8min warmup
            {"time": 88, "distance": 400, "lap_index": 2},    # 400m
            {"time": 180, "distance": 400, "lap_index": 3},   # 3min rest jog
            {"time": 92, "distance": 400, "lap_index": 4},    # 400m
            {"time": 240, "distance": 500, "lap_index": 5},   # 4min rest jog
            {"time": 185, "distance": 800, "lap_index": 6},   # 800m
            {"time": 300, "distance": 600, "lap_index": 7},   # 5min rest jog
            {"time": 188, "distance": 800, "lap_index": 8},   # 800m
            {"time": 180, "distance": 350, "lap_index": 9},   # 3min rest after workout
            {"time": 540, "distance": 1350, "lap_index": 10}  # 9min cooldown
        ],
        "expected": "2 x 400m, 2 x 800m",
        "notes": "Mixed intervals with varying rest periods and post-workout rest"
    },
    
    # 12. VERY SHORT INTERVALS WITH COMPLICATIONS
    {
        "name": "Case 12A: 15s sprints with walk recovery and cooldown",
        "laps": [
            {"time": 600, "distance": 1500, "lap_index": 1},  # 10min warmup
            {"time": 15, "distance": 85, "lap_index": 2},     # 15s sprint
            {"time": 45, "distance": 90, "lap_index": 3},     # 45s walk
            {"time": 15, "distance": 88, "lap_index": 4},     # 15s sprint
            {"time": 48, "distance": 85, "lap_index": 5},     # 48s walk
            {"time": 15, "distance": 82, "lap_index": 6},     # 15s sprint
            {"time": 42, "distance": 95, "lap_index": 7},     # 42s walk
            {"time": 15, "distance": 90, "lap_index": 8},     # 15s sprint
            {"time": 45, "distance": 88, "lap_index": 9},     # 45s walk
            {"time": 15, "distance": 85, "lap_index": 10},    # 15s sprint
            {"time": 120, "distance": 200, "lap_index": 11},  # 2min walk rest
            {"time": 480, "distance": 1200, "lap_index": 12}  # 8min cooldown
        ],
        "expected": "5 x 15s",
        "notes": "Very short intervals with walk recovery and extended rest before cooldown"
    },
    
    # 13. LONG INTERVALS WITH COMPLICATIONS
    {
        "name": "Case 13A: 5min tempo intervals with jog recovery",
        "laps": [
            {"time": 600, "distance": 1800, "lap_index": 1},  # 10min warmup
            {"time": 300, "distance": 1350, "lap_index": 2},  # 5min tempo
            {"time": 180, "distance": 500, "lap_index": 3},   # 3min recovery jog
            {"time": 305, "distance": 1340, "lap_index": 4},  # 5min tempo
            {"time": 185, "distance": 490, "lap_index": 5},   # 3min recovery jog
            {"time": 298, "distance": 1360, "lap_index": 6},  # 5min tempo
            {"time": 240, "distance": 600, "lap_index": 7},   # 4min recovery after workout
            {"time": 720, "distance": 1800, "lap_index": 8}   # 12min cooldown
        ],
        "expected": "3 x 5min",
        "notes": "Long tempo intervals with jog recovery and extended cooldown"
    },
    
    # 14. EDGE CASE: INTERVALS WITH VERY LONG COOLDOWN
    {
        "name": "Case 14A: 4x200m with massive cooldown",
        "laps": [
            {"time": 360, "distance": 900, "lap_index": 1},   # 6min warmup
            {"time": 42, "distance": 200, "lap_index": 2},    # 200m
            {"time": 90, "distance": 200, "lap_index": 3},    # 1:30 jog recovery
            {"time": 44, "distance": 200, "lap_index": 4},    # 200m
            {"time": 88, "distance": 195, "lap_index": 5},    # 1:28 jog recovery
            {"time": 43, "distance": 200, "lap_index": 6},    # 200m
            {"time": 92, "distance": 205, "lap_index": 7},    # 1:32 jog recovery
            {"time": 41, "distance": 200, "lap_index": 8},    # 200m
            {"time": 180, "distance": 400, "lap_index": 9},   # 3min recovery walk
            {"time": 900, "distance": 2250, "lap_index": 10}  # 15min cooldown!
        ],
        "expected": "4 x 200m",
        "notes": "Standard intervals but with exceptionally long cooldown period"
    }
]

def get_test_case_by_name(name: str) -> Dict[str, Any]:
    """Get a specific test case by name"""
    for case in TEST_CASES:
        if case["name"].startswith(name):
            return case
    raise ValueError(f"Test case '{name}' not found")

def list_test_cases() -> List[str]:
    """List all available test case names"""
    return [case["name"] for case in TEST_CASES]
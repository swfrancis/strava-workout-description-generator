# Interval Detection Testing Documentation

This document outlines the comprehensive testing framework for the Strava workout description generator's interval detection system.

## Overview

The system detects and analyses different types of interval patterns from Strava lap data, generating appropriate descriptions using a sophisticated predictability hierarchy.

## Core Pattern Detection Hierarchy

The system uses a hierarchical approach to determine pattern types:

1. **Arithmetic Progressions (Ladders)** - Consistently increasing/decreasing values
2. **Symmetry (Pyramids)** - Values increase to peak, then mirror decrease  
3. **Repeating Sub-patterns** - Multiple repetitions of structured patterns
4. **Mixed Patterns** - Irregular but structured variations
5. **Consistent Intervals** - Regular repeats with CV ≤ 15%
6. **Chaotic Rejection** - No predictable pattern detected

## Test Execution

### Running the Comprehensive Test Suite

From the root directory:
```bash
python tests/test_comprehensive.py
```

Or from within the tests directory:
```bash
cd tests && python test_comprehensive.py
```

This single command runs all test categories:

- **Basic Functionality Tests** - Core interval detection
- **Pattern Detection Tests** - Different pattern types
- **Repeated Pattern Tests** - Complex repeated structures  
- **Consistency Checking Tests** - Validation and rejection logic

### Test Categories

#### 1. Basic Functionality Tests

**Purpose**: Verify core interval detection works for standard patterns

**Key Test Cases**:
- **Case 1A**: 4 x 30s sprints with rest
- **Case 2A**: 5 x 400m track with rest  
- **Case 7A**: Auto-lap rejection (1km splits)
- **Case 8A**: Short intervals with warmup (user's 20s case)
- **Case 8C**: Simple 3 x 400m pattern
- **Case 8D**: Chaotic workout (should reject)

#### 2. Pattern Detection Tests

**Purpose**: Verify advanced pattern recognition

**Pattern Types Tested**:
- **Regular Intervals**: `4 x 400m` - Consistent distance repeats
- **Pyramid Patterns**: `200m-400m-800m-400m-200m` - Symmetrical progression
- **Ladder Patterns**: `200m-400m-600m-800m` - Monotonic progression  
- **Mixed Patterns**: `400m-800m-400m-800m` - Alternating distances

#### 3. Repeated Pattern Tests

**Purpose**: Verify detection of repeated structured sub-patterns

**Repeated Structures Tested**:
- **Repeated Pyramids**: `3 x (200m-400m-200m)`
- **Repeated Alternating**: `4 x (400m-800m)`
- **Repeated Time Pyramids**: `3 x (30s-1min-30s)`
- **Repeated Ladders**: `2 x (200m-400m-600m)`

#### 4. Consistency Checking Tests

**Purpose**: Verify proper validation and rejection logic

**Consistency Scenarios**:
- **Consistent Intervals**: CV ≤ 15% → Accept as regular intervals
- **Structured Patterns**: High CV but clear structure → Accept with pattern description
- **Chaotic Workouts**: High CV without structure → Reject (return nothing)

## Technical Implementation

### Work Interval Detection
- **Pace Clustering**: Groups laps by similar pace (±60 sec/km tolerance)
- **Fastest Group Selection**: Identifies group with fastest average pace
- **Pace Gap Validation**: Requires ≥60 sec/km gap to slower groups
- **Minimum Count**: Requires ≥3 work intervals

### Distance vs Time Classification
- **Distance Rules**:
  - Up to 2km: All multiples of 100m (100m, 200m, ..., 2000m)
  - After 2km: Only multiples of 500m (2500m, 3000m, ..., 50000m)  
  - Miles: Only whole mile multiples (1609m≈1mi, 3218m≈2mi, etc.)
- **Time-based**: Anything not matching distance rules

### Pattern Structure Detection
- **Pyramids**: Values increase to peak, then decrease (≥5 intervals)
- **Ladders**: Values consistently increase/decrease (≥4 intervals)
- **Repeated**: Sub-patterns that repeat 2+ times with ≤10% variation
- **Mixed**: High variation (CV 0.3-0.8) without clear structure
- **Regular**: Low variation (CV ≤ 15%) indicating consistent intervals

### Description Generation
- **Regular intervals**: Average-based (e.g., `"4 x 400m"`)
- **Structured patterns**: Individual values (e.g., `"200m-400m-800m"`)
- **Repeated patterns**: Concise repetition (e.g., `"3 x (200m-400m-200m)"`)
- **Time formatting**: Seconds for <60s, minutes:seconds for ≥60s
- **Distance formatting**: Meters or kilometres based on value

## Success Criteria

### ✅ Core Functionality
- Correctly identifies regular intervals (4 x 400m, 5 x 30s)
- Detects structured patterns (pyramids, ladders, mixed)
- Filters out auto-laps and warmup/cooldown periods
- Distinguishes distance vs time-based workouts
- Generates appropriate descriptions for each pattern type

### ✅ Advanced Features  
- Detects repeated structured patterns with concise descriptions
- Validates consistency using coefficient of variation
- Rejects chaotic workouts without predictable structure
- Handles GPS measurement variations and real-world data

### ✅ Robustness
- **Tolerance**: 60 sec/km pace grouping, 5% distance tolerance
- **Minimum requirements**: ≥3 work intervals, ≥60 sec/km pace gap
- **Pattern complexity**: Handles up to 12+ lap workouts
- **Real-world ready**: Works with Strava GPS measurement variations

## Test Data Sources

All test cases are defined in `tests/lap_test_cases.py` which contains:
- 14+ comprehensive test scenarios
- Real-world workout patterns
- Edge cases and boundary conditions
- Expected results for validation

## Australian English Compliance

All code and descriptions use Australian English spelling:
- analyse (not analyze)
- recognise (not recognize) 
- colour (not color)
- behaviour (not behavior)

---

*This testing framework ensures the interval detection system reliably identifies and describes the full spectrum of running interval patterns found in real-world Strava data.*
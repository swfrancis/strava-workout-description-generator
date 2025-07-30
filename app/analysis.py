from typing import List, Dict, Optional
from .models import Lap, WorkoutPattern, WorkoutAnalysis
import statistics


class LapAnalyser:
    """
    Comprehensive interval detection system for Strava workout analysis.
    
    Detects different types of interval patterns:
    - Regular intervals (e.g., "4 x 400m", "5 x 30s")  
    - Pyramid patterns (e.g., "200m-400m-800m-400m-200m")
    - Ladder patterns (e.g., "200m-400m-600m-800m")
    - Mixed patterns (e.g., "400m-800m-400m-800m")
    """
    
    # Configurable thresholds
    MIN_TOTAL_LAPS = 3              # Minimum total laps required
    MIN_WORK_INTERVALS = 2          # Minimum work intervals required
    PACE_CLUSTERING_TOLERANCE = 60  # Pace grouping tolerance (sec/km)
    PACE_GAP_THRESHOLD = 60         # Required pace gap between work and rest (sec/km)
    CONSISTENCY_CV_THRESHOLD = 0.15 # CV threshold for consistent intervals (15%)
    MIXED_PATTERN_CV_RANGE = (0.3, 0.8)  # CV range for mixed patterns
    REPEATED_PATTERN_TOLERANCE = 0.1      # Tolerance for repeated pattern matching (10%)
    DISTANCE_TOLERANCE = 0.05             # Distance matching tolerance (5%)
    AUTO_LAP_TOLERANCE = 5                # Auto-lap detection tolerance (5m)

    def analyse_laps(self, laps: List[Lap]) -> List[WorkoutPattern]:
        """Main analysis - find intervals or return empty list"""

        # Need at least minimum total laps
        if len(laps) < self.MIN_TOTAL_LAPS:
            return []

        # Skip auto-generated laps (1km or 1mile splits)
        if self._is_auto_laps(laps):
            return []

        # Find work intervals using pace analysis
        work_laps = self._find_work_intervals(laps)
        if len(work_laps) < self.MIN_WORK_INTERVALS:
            return []

        # Sort work laps by lap index to maintain chronological order
        work_laps.sort(key=lambda lap: lap.lap_index)

        # Determine if time or distance based
        is_distance_based = self._is_distance_based(work_laps)

        # Detect specific pattern type
        pattern_type = self._detect_pattern_type(work_laps, is_distance_based)
        
        # Reject chaotic patterns
        if pattern_type is None:
            return []

        # Generate description
        description = self._make_description(work_laps, is_distance_based, pattern_type)

        # Create pattern
        intervals = []
        for i, lap in enumerate(work_laps, 1):
            intervals.append({
                "number": i,
                "distance": lap.distance,
                "time": lap.elapsed_time,
                "lap_index": lap.lap_index
            })

        pattern = WorkoutPattern(
            pattern_type="intervals",
            intervals=intervals,
            rest_periods=[],
            confidence=0.8,
            description=description
        )

        return [pattern]

    def _is_auto_laps(self, laps: List[Lap]) -> bool:
        """Check for 1km or 1mile auto-laps"""
        distances = [lap.distance for lap in laps]

        # Check 1km auto-laps
        km_matches = sum(1 for d in distances if abs(d - 1000) < self.AUTO_LAP_TOLERANCE)
        if km_matches >= len(distances) - 1:  # Allow one partial lap at end
            return True

        # Check 1mile auto-laps
        mi_matches = sum(1 for d in distances if abs(d - 1609) < self.AUTO_LAP_TOLERANCE)
        if mi_matches >= len(distances) - 1:  # Allow one partial lap at end
            return True

        return False

    def _find_work_intervals(self, laps: List[Lap]) -> List[Lap]:
        """Find work intervals using improved clustering approach"""

        # Calculate pace for each lap (seconds per km)
        lap_paces = []
        for lap in laps:
            if lap.distance > 0:
                pace = lap.elapsed_time / (lap.distance / 1000)  # sec/km
                lap_paces.append((lap, pace))

        if len(lap_paces) < self.MIN_WORK_INTERVALS:
            return []

        # Sort by pace (fastest first)
        lap_paces.sort(key=lambda x: x[1])

        # Use clustering approach to find work intervals
        return self._identify_work_intervals_by_clustering(lap_paces)

    def _identify_work_intervals_by_clustering(self, lap_paces: List[tuple]) -> List[Lap]:
        """Identify work intervals using pace clustering"""
        
        # Group laps by similar pace
        pace_groups = []
        for lap, pace in lap_paces:
            placed = False
            for group in pace_groups:
                # Check if pace is similar to group average
                group_avg_pace = sum(p for _, p in group) / len(group)
                if abs(pace - group_avg_pace) <= self.PACE_CLUSTERING_TOLERANCE:
                    group.append((lap, pace))
                    placed = True
                    break
            
            if not placed:
                pace_groups.append([(lap, pace)])
        
        # Find the group with fastest average pace that has enough intervals
        work_group = None
        min_avg_pace = float('inf')
        
        for group in pace_groups:
            if len(group) >= self.MIN_WORK_INTERVALS:
                avg_pace = sum(p for _, p in group) / len(group)
                if avg_pace < min_avg_pace:
                    min_avg_pace = avg_pace
                    work_group = group
        
        if work_group:
            work_laps = [lap for lap, _ in work_group]
            
            # Additional filtering: check if there's a significant pace gap to slower groups
            other_paces = []
            for group in pace_groups:
                if group != work_group:
                    other_paces.extend([p for _, p in group])
            
            if other_paces:
                fastest_other_pace = min(other_paces)
                if fastest_other_pace - min_avg_pace >= self.PACE_GAP_THRESHOLD:
                    return work_laps
                else:
                    # Gap not significant enough, might be steady-state workout
                    return []
            else:
                # Only one group found, check if it's reasonable for intervals
                if len(work_laps) >= self.MIN_WORK_INTERVALS:
                    return work_laps
        
        return []

    def _is_distance_based(self, work_laps: List[Lap]) -> bool:
        """Check if all work intervals match common running distances"""
        distances = [lap.distance for lap in work_laps]
        
        # Common running distances in meters
        common_distances = []
        
        # Add multiples of 100m up to 2km
        for i in range(1, 21):  # 100m to 2000m
            common_distances.append(i * 100)
        
        # Add multiples of 500m from 2.5km to 50km
        for i in range(5, 101):  # 2500m to 50000m (2.5km to 50km)
            common_distances.append(i * 500)
        
        # Add multiples of 1 mile starting from 1 mile
        mile = 1609  # 1609.344m rounded
        for i in range(1, 32):  # 1 mile to 31 miles (roughly 50km)
            common_distances.append(i * mile)
        
        # Remove duplicates and sort
        common_distances = sorted(set(common_distances))
        
        # Check if all distances match common distances (within tolerance)
        for distance in distances:
            matches_common = False
            for common_dist in common_distances:
                # Allow configurable tolerance or minimum 10m
                tolerance = max(common_dist * self.DISTANCE_TOLERANCE, 10)
                if abs(distance - common_dist) <= tolerance:
                    matches_common = True
                    break
            
            if not matches_common:
                return False  # At least one distance doesn't match common distances
        
        return True  # All distances match common running distances

    def _detect_pattern_type(self, work_laps: List[Lap], is_distance_based: bool) -> str:
        """Detect the specific pattern type using predictability hierarchy"""
        if len(work_laps) < self.MIN_WORK_INTERVALS:
            return None  # Reject if insufficient work intervals
        
        values = []
        if is_distance_based:
            values = [lap.distance for lap in work_laps]
        else:
            values = [lap.elapsed_time for lap in work_laps]
        
        # Hierarchy of predictability checks:
        # 1. Check for arithmetic progressions (ladders)
        if self._is_ladder_pattern(values):
            return "ladder"
        
        # 2. Check for symmetry (pyramids) 
        elif self._is_pyramid_pattern(values):
            return "pyramid"
        
        # 3. Check for repeating sub-patterns (repeated structures)
        elif self._is_repeated_pattern(values):
            return "repeated"
        
        # 4. Check for mixed patterns (different interval types)
        elif self._is_mixed_pattern(values):
            return "mixed"
        
        # 5. Check for low CV consistency (regular intervals)
        elif self._is_consistent_intervals(values):
            return "intervals"
        
        # 6. Reject everything else as chaotic
        else:
            return None

    def _is_pyramid_pattern(self, values: List[float]) -> bool:
        """Check if values form a pyramid (up then down) pattern"""
        if len(values) < 5:  # Need at least 5 for meaningful pyramid
            return False
        
        # Find the peak (maximum value)
        max_val = max(values)
        max_idx = values.index(max_val)
        
        # Peak should not be at the edges
        if max_idx <= 1 or max_idx >= len(values) - 2:
            return False
        
        # Check if values increase up to peak, then decrease
        # Allow some tolerance for measurement variations
        increasing = True
        for i in range(max_idx):
            if values[i + 1] < values[i] * 0.9:  # 10% tolerance
                increasing = False
                break
        
        decreasing = True
        for i in range(max_idx, len(values) - 1):
            if values[i + 1] > values[i] * 1.1:  # 10% tolerance
                decreasing = False
                break
        
        return increasing and decreasing

    def _is_ladder_pattern(self, values: List[float]) -> bool:
        """Check if values form a ladder (consistently increasing or decreasing)"""
        if len(values) < 4:  # Need at least 4 for meaningful ladder
            return False
        
        # Check for increasing ladder
        increasing = True
        for i in range(len(values) - 1):
            if values[i + 1] < values[i] * 1.05:  # Must increase by at least 5%
                increasing = False
                break
        
        # Check for decreasing ladder
        decreasing = True
        for i in range(len(values) - 1):
            if values[i + 1] > values[i] * 0.95:  # Must decrease by at least 5%
                decreasing = False
                break
        
        return increasing or decreasing

    def _is_mixed_pattern(self, values: List[float]) -> bool:
        """Check if values represent a mixed pattern (different interval types)"""
        if len(values) < 4:
            return False
        
        # Calculate coefficient of variation manually
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return False
        
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / mean_val
        
        # If CV is within mixed pattern range, consider it mixed
        return self.MIXED_PATTERN_CV_RANGE[0] < cv < self.MIXED_PATTERN_CV_RANGE[1]

    def _is_consistent_intervals(self, values: List[float]) -> bool:
        """Check if values represent consistent regular intervals (CV <= 15%)"""
        if len(values) < self.MIN_WORK_INTERVALS:
            return False
        
        # Calculate coefficient of variation
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return False
        
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / mean_val
        
        # Accept intervals with CV below threshold (consistent)
        return cv <= self.CONSISTENCY_CV_THRESHOLD

    def _is_repeated_pattern(self, values: List[float]) -> bool:
        """Check if values represent a repeated sub-pattern (e.g., 3x pyramid, 4x ladder)"""
        if len(values) < 6:  # Need at least 6 values for meaningful repetition
            return False
        
        # Try different sub-pattern lengths (2 to half the total length)
        for pattern_length in range(2, len(values) // 2 + 1):
            if len(values) % pattern_length == 0:  # Must divide evenly
                # Extract the first pattern
                first_pattern = values[:pattern_length]
                
                # Check if this pattern repeats throughout
                is_repeated = True
                repetitions = len(values) // pattern_length
                
                for i in range(1, repetitions):
                    start_idx = i * pattern_length
                    end_idx = start_idx + pattern_length
                    current_pattern = values[start_idx:end_idx]
                    
                    # Check if current pattern matches first pattern (with tolerance)
                    for j in range(pattern_length):
                        tolerance = max(first_pattern[j] * self.REPEATED_PATTERN_TOLERANCE, 5)
                        if abs(current_pattern[j] - first_pattern[j]) > tolerance:
                            is_repeated = False
                            break
                    
                    if not is_repeated:
                        break
                
                if is_repeated:
                    # Additional check: the sub-pattern should have some structure
                    # (not just repeated identical values)
                    if self._has_sub_pattern_structure(first_pattern):
                        # Store the pattern info for description generation
                        self._repeated_sub_pattern = first_pattern
                        self._repetition_count = repetitions
                        return True
        
        return False

    def _has_sub_pattern_structure(self, pattern: List[float]) -> bool:
        """Check if a sub-pattern has meaningful structure (not just identical values)"""
        if len(pattern) < 2:
            return False
        
        # Check if it's a pyramid, ladder, or alternating pattern
        if len(pattern) >= 3:
            # Check for pyramid structure in sub-pattern
            if len(pattern) >= 3:
                max_val = max(pattern)
                max_idx = pattern.index(max_val)
                # Simple pyramid check: peak not at edges and some variation
                if 0 < max_idx < len(pattern) - 1:
                    return True
            
            # Check for ladder structure (monotonic)
            is_increasing = all(pattern[i] <= pattern[i+1] * 1.1 for i in range(len(pattern)-1))
            is_decreasing = all(pattern[i] >= pattern[i+1] * 0.9 for i in range(len(pattern)-1))
            if is_increasing or is_decreasing:
                return True
        
        # Check for alternating pattern (A-B or A-B-A)
        if len(pattern) >= 2:
            # Calculate coefficient of variation - some variation indicates structure
            mean_val = sum(pattern) / len(pattern)
            if mean_val > 0:
                variance = sum((x - mean_val) ** 2 for x in pattern) / len(pattern)
                std_dev = variance ** 0.5
                cv = std_dev / mean_val
                # Has meaningful variation (not all identical)
                return cv > 0.05
        
        return False

    def _make_description(self, work_laps: List[Lap], is_distance_based: bool, pattern_type: str) -> str:
        """Generate description string based on pattern type"""
        count = len(work_laps)
        
        # For repeated patterns, show the repetition structure
        if pattern_type == "repeated":
            return self._make_repeated_description(work_laps, is_distance_based)
        
        # For structured patterns (pyramid, ladder, mixed), show individual values
        if pattern_type in ["pyramid", "ladder", "mixed"]:
            return self._make_structured_description(work_laps, is_distance_based)
        
        # For regular intervals, show average
        avg_distance = statistics.mean([lap.distance for lap in work_laps])
        avg_time = statistics.mean([lap.elapsed_time for lap in work_laps])
        
        if is_distance_based:
            # Use actual average distance, don't just round to km
            if avg_distance >= 1000:
                # Check if it's close to a whole km
                km_value = avg_distance / 1000
                if abs(km_value - round(km_value)) < 0.05:  # Within 50m of whole km
                    return f"{count} x {int(round(km_value))}km"
                else:
                    return f"{count} x {int(round(avg_distance))}m"
            else:
                return f"{count} x {int(round(avg_distance))}m"
        else:
            if avg_time >= 60:
                minutes = int(avg_time // 60)
                seconds = int(avg_time % 60)
                if seconds == 0:
                    return f"{count} x {minutes}min"
                else:
                    return f"{count} x {minutes}:{seconds:02d}"
            else:
                return f"{count} x {int(round(avg_time))}s"

    def _make_structured_description(self, work_laps: List[Lap], is_distance_based: bool) -> str:
        """Generate description for structured patterns (ladder/pyramid/mixed)"""
        formatted_values = []
        
        if is_distance_based:
            # Format distances
            for lap in work_laps:
                distance = lap.distance
                if distance >= 1000:
                    km_value = distance / 1000
                    if abs(km_value - round(km_value)) < 0.05:  # Within 50m of whole km
                        formatted_values.append(f"{int(round(km_value))}km")
                    else:
                        formatted_values.append(f"{int(round(distance))}m")
                else:
                    formatted_values.append(f"{int(round(distance))}m")
        else:
            # Format times
            for lap in work_laps:
                time = lap.elapsed_time
                if time >= 60:
                    minutes = int(time // 60)
                    seconds = int(time % 60)
                    if seconds == 0:
                        formatted_values.append(f"{minutes}min")
                    else:
                        formatted_values.append(f"{minutes}:{seconds:02d}")
                else:
                    formatted_values.append(f"{int(round(time))}s")
        
        return "-".join(formatted_values)

    def _make_repeated_description(self, work_laps: List[Lap], is_distance_based: bool) -> str:
        """Generate description for repeated patterns (e.g., '3 x (200m-400m-200m)')"""
        pattern_length = len(self._repeated_sub_pattern)
        repetitions = self._repetition_count
        
        # Format the sub-pattern
        sub_pattern_laps = work_laps[:pattern_length]
        formatted_values = []
        
        if is_distance_based:
            # Format distances
            for lap in sub_pattern_laps:
                distance = lap.distance
                if distance >= 1000:
                    km_value = distance / 1000
                    if abs(km_value - round(km_value)) < 0.05:  # Within 50m of whole km
                        formatted_values.append(f"{int(round(km_value))}km")
                    else:
                        formatted_values.append(f"{int(round(distance))}m")
                else:
                    formatted_values.append(f"{int(round(distance))}m")
        else:
            # Format times
            for lap in sub_pattern_laps:
                time = lap.elapsed_time
                if time >= 60:
                    minutes = int(time // 60)
                    seconds = int(time % 60)
                    if seconds == 0:
                        formatted_values.append(f"{minutes}min")
                    else:
                        formatted_values.append(f"{minutes}:{seconds:02d}")
                else:
                    formatted_values.append(f"{int(round(time))}s")
        
        sub_pattern_desc = "-".join(formatted_values)
        return f"{repetitions} x ({sub_pattern_desc})"


def analyse_workout_from_laps(laps: List[Lap], activity_name: str = "", activity_type: str = "") -> Optional[WorkoutAnalysis]:
    """Main analysis function"""
    if not laps:
        return None

    analyser = LapAnalyser()
    patterns = analyser.analyse_laps(laps)

    if not patterns:
        return None

    pattern = patterns[0]
    total_distance = sum(lap.distance for lap in laps)
    total_time = sum(lap.elapsed_time for lap in laps)

    return WorkoutAnalysis(
        activity_id=0,
        activity_name=activity_name,
        activity_type=activity_type,
        total_distance=total_distance,
        total_time=total_time,
        has_laps=True,
        lap_count=len(laps),
        lap_analysis=f"Detected intervals: {pattern.description}",
        detected_patterns=patterns,
        primary_pattern=pattern,
        short_description=pattern.description,
        detailed_description=f"Workout structure: {pattern.description}. Total: {total_distance/1000:.1f}km in {total_time//60}:{total_time % 60:02.0f}",
        analysis_method="laps",
        confidence=pattern.confidence
    )

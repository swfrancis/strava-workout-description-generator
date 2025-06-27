from typing import List, Dict, Optional
from .models import Lap, WorkoutPattern, WorkoutAnalysis
import statistics


class LapAnalyzer:
    """Analyzes lap data to detect interval patterns"""

    def __init__(self):
        self.min_interval_count = 2  # Minimum intervals to consider a pattern
        self.distance_tolerance = 0.1  # 10% tolerance for distance grouping
        self.time_tolerance = 0.1  # 15% tolerance for time grouping

    def analyze_laps(self, laps: List[Lap]) -> List[WorkoutPattern]:
        """
        Analyze laps to detect interval patterns
        Returns a list of WorkoutPatterns if intervals are detected, empty list otherwise
        """
        if len(laps) < self.min_interval_count:
            return []

        # First check if these are auto-generated laps (not manual intervals)
        if self._are_auto_laps(laps):
            return []

        # Filter out warmup/cooldown laps (very long laps at start/end)
        filtered_laps = self._filter_warmup_cooldown(laps)
        
        if len(filtered_laps) < self.min_interval_count:
            return []

        # Try to identify work vs rest laps
        work_laps, rest_laps = self._identify_work_and_rest_laps(filtered_laps)
        
        # If we found clear work/rest separation, analyze work laps only
        if work_laps and rest_laps:
            # Group work laps by similar characteristics
            interval_groups = self._group_similar_laps(work_laps)
            patterns = self._find_all_patterns(interval_groups, work_laps)
            
            # Add rest information to patterns
            if patterns:
                for pattern in patterns:
                    pattern.rest_periods = self._calculate_rest_info(work_laps, rest_laps, filtered_laps)
                    # Update description to include recovery info
                    if pattern.rest_periods:
                        avg_rest_time = sum(r['time'] for r in pattern.rest_periods) / len(pattern.rest_periods)
                        rest_str = self._format_time(avg_rest_time)
                        pattern.description += f" w/ {rest_str} recovery"
            
            return patterns
        else:
            # Standard analysis without work/rest separation
            interval_groups = self._group_similar_laps(filtered_laps)
            patterns = self._find_all_patterns(interval_groups, filtered_laps)

        return patterns
    
    def _are_auto_laps(self, laps: List[Lap]) -> bool:
        """
        Detect if laps are auto-generated (e.g., every 1km) rather than manual intervals
        Auto-laps typically have:
        - Consistent round distances (1km, 1mi, etc.)
        - Sequential lap indices with no gaps
        - All laps similar distance except possibly the last one
        """
        if len(laps) < 2:
            return False
        
        distances = [lap.distance for lap in laps if lap.distance > 0]
        
        # Check if most laps have the same round distance
        # Common auto-lap distances: 1000m (1km), 1609m (1mi), 5000m (5km)
        common_distances = [1000, 1609, 5000, 400, 800]  # meters
        
        for auto_distance in common_distances:
            # Count how many laps match this auto-distance (within 5% tolerance)
            matching_laps = 0
            for dist in distances:
                if abs(dist - auto_distance) / auto_distance < 0.05:
                    matching_laps += 1
            
            # If most laps (excluding possibly last partial lap) match an auto-distance
            if matching_laps >= len(distances) - 1 and matching_laps >= len(distances) * 0.8:
                # Additional check: last lap should be significantly shorter if it's partial
                if len(distances) > 1:
                    last_lap_dist = distances[-1]
                    second_last_dist = distances[-2]
                    
                    # If last lap is much shorter, this looks like auto-laps with partial final lap
                    if last_lap_dist < second_last_dist * 0.7:
                        return True
                    # If all laps are same distance, also likely auto-laps
                    elif abs(last_lap_dist - auto_distance) / auto_distance < 0.05:
                        return True
        
        # Additional check: if all laps have very similar distances (not intervals)
        if len(distances) > 2:
            avg_distance = sum(distances[:-1]) / (len(distances) - 1)  # Exclude last lap
            consistent_count = 0
            
            for dist in distances[:-1]:  # Check all but last lap
                if abs(dist - avg_distance) / avg_distance < 0.05:  # Within 5%
                    consistent_count += 1
            
            # If 90%+ of laps are very similar distance, likely auto-laps
            if consistent_count >= (len(distances) - 1) * 0.9:
                return True
        
        return False

    def _group_similar_laps(self, laps: List[Lap]) -> List[List[Lap]]:
        """Group laps with similar distance and time characteristics"""
        groups = []

        for lap in laps:
            placed = False

            # Try to place lap in existing group
            for group in groups:
                if self._laps_are_similar(lap, group[0]):
                    group.append(lap)
                    placed = True
                    break

            # Create new group if no match found
            if not placed:
                groups.append([lap])

        return groups
    
    def _identify_work_and_rest_laps(self, laps: List[Lap]) -> tuple[List[Lap], List[Lap]]:
        """
        Identify which laps are work intervals vs rest periods
        Returns (work_laps, rest_laps)
        """
        if len(laps) < 3:
            return laps, []
        
        # Calculate pace for each lap (seconds per km)
        lap_paces = []
        for lap in laps:
            if lap.distance > 0 and lap.elapsed_time > 0:
                pace_per_km = (lap.elapsed_time / (lap.distance / 1000))
                lap_paces.append((lap, pace_per_km))
        
        if len(lap_paces) < 3:
            return laps, []
        
        # Sort by pace to identify fast vs slow laps
        lap_paces.sort(key=lambda x: x[1])
        
        # Find natural break between fast (work) and slow (rest) paces
        # Look for the biggest gap in pace
        pace_gaps = []
        for i in range(len(lap_paces) - 1):
            gap = lap_paces[i + 1][1] - lap_paces[i][1]
            pace_gaps.append((i, gap))
        
        # Find the largest gap
        if pace_gaps:
            largest_gap_idx = max(pace_gaps, key=lambda x: x[1])[0]
            
            # Split into fast (work) and slow (rest) groups
            work_laps = [lap for lap, pace in lap_paces[:largest_gap_idx + 1]]
            rest_laps = [lap for lap, pace in lap_paces[largest_gap_idx + 1:]]
            
            # Additional validation: work intervals should be reasonably consistent
            if len(work_laps) >= 2 and len(rest_laps) >= 1:
                # Check if work laps have similar distances (within 20% tolerance)
                work_distances = [lap.distance for lap in work_laps]
                avg_work_dist = sum(work_distances) / len(work_distances)
                
                consistent_work = sum(1 for d in work_distances 
                                    if abs(d - avg_work_dist) / avg_work_dist < 0.2)
                
                # If most work laps are consistent, this is likely work/rest pattern
                if consistent_work >= len(work_laps) * 0.7:
                    return work_laps, rest_laps
        
        # Fallback: treat all as work intervals
        return laps, []
    
    def _filter_warmup_cooldown(self, laps: List[Lap]) -> List[Lap]:
        """Filter out obvious warmup/cooldown laps (very long laps at start/end)"""
        if len(laps) <= 2:
            return laps
        
        filtered = laps[:]
        
        # Remove first lap if it's much longer than the others (warmup)
        if len(filtered) > 2:
            first_dist = filtered[0].distance
            second_dist = filtered[1].distance
            third_dist = filtered[2].distance
            avg_middle = (second_dist + third_dist) / 2
            
            # If first lap is >3x longer than average of next two, likely warmup
            if first_dist > avg_middle * 3:
                filtered = filtered[1:]
        
        # Remove last lap if it's much longer than the others (cooldown)
        if len(filtered) > 2:
            last_dist = filtered[-1].distance
            second_last_dist = filtered[-2].distance
            third_last_dist = filtered[-3].distance
            avg_middle = (second_last_dist + third_last_dist) / 2
            
            # If last lap is >3x longer than average of previous two, likely cooldown
            if last_dist > avg_middle * 3:
                filtered = filtered[:-1]
        
        return filtered
    
    def _calculate_rest_info(self, work_laps: List[Lap], rest_laps: List[Lap], all_laps: List[Lap]) -> List[Dict]:
        """Calculate rest period information"""
        rest_periods = []
        
        # Simple approach: average the rest laps
        if rest_laps:
            avg_rest_time = sum(lap.elapsed_time for lap in rest_laps) / len(rest_laps)
            avg_rest_dist = sum(lap.distance for lap in rest_laps) / len(rest_laps)
            
            rest_periods.append({
                "time": avg_rest_time,
                "distance": avg_rest_dist,
                "lap_count": len(rest_laps)
            })
        
        return rest_periods
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into MM:SS or SS format with rounding"""
        rounded_seconds = self._round_time(seconds)
        minutes = int(rounded_seconds // 60)
        secs = int(rounded_seconds % 60)
        
        if minutes > 0:
            return f"{minutes}:{secs:02d}"
        else:
            return f"{secs}s"
    
    def _round_time(self, seconds: float) -> float:
        """
        Round time to nearest 5 seconds for times over 10 seconds
        Keep exact seconds for times <= 10 seconds
        """
        if seconds <= 10:
            return round(seconds)  # Round to nearest second for short intervals
        else:
            return round(seconds / 5) * 5  # Round to nearest 5 seconds for longer intervals

    def _laps_are_similar(self, lap1: Lap, lap2: Lap) -> bool:
        """Check if two laps are similar in distance and time"""
        # Compare distances
        dist1, dist2 = lap1.distance, lap2.distance
        if dist1 > 0 and dist2 > 0:
            dist_diff = abs(dist1 - dist2) / max(dist1, dist2)
            if dist_diff > self.distance_tolerance:
                return False

        # Compare times
        time1, time2 = lap1.elapsed_time, lap2.elapsed_time
        if time1 > 0 and time2 > 0:
            time_diff = abs(time1 - time2) / max(time1, time2)
            if time_diff > self.time_tolerance:
                return False

        return True

    def _find_all_patterns(self, groups: List[List[Lap]], all_laps: List[Lap]) -> List[WorkoutPattern]:
        """Find all interval patterns including complex multi-group patterns"""
        patterns = []
        
        # First, check for simple single-group patterns
        interval_groups = [g for g in groups if len(g) >= self.min_interval_count]
        
        for group in interval_groups:
            pattern = self._create_workout_pattern(group, all_laps, f"intervals_{len(patterns)+1}")
            patterns.append(pattern)
        
        # Check for complex repeating patterns (e.g., 3 x (800m, 600m, 400m))
        complex_pattern = self._detect_complex_pattern(groups, all_laps)
        if complex_pattern:
            patterns.append(complex_pattern)
        
        return patterns
    
    def _detect_complex_pattern(self, groups: List[List[Lap]], all_laps: List[Lap]) -> Optional[WorkoutPattern]:
        """Detect complex repeating patterns like pyramids or ladder intervals"""
        if len(groups) < 2:
            return None
        
        # Look for repeating sequences of different lap types
        # Sort groups by average distance to identify pattern order
        sorted_groups = sorted(groups, key=lambda g: sum(lap.distance for lap in g) / len(g))
        
        # Try to find repeating sequences
        for seq_length in range(2, min(len(sorted_groups) + 1, 6)):  # Max sequence length of 5
            pattern_sequence = self._find_repeating_sequence(sorted_groups, seq_length, all_laps)
            if pattern_sequence:
                return pattern_sequence
        
        return None
    
    def _find_repeating_sequence(self, groups: List[List[Lap]], seq_length: int, all_laps: List[Lap]) -> Optional[WorkoutPattern]:
        """Find if there's a repeating sequence of interval types"""
        if len(groups) < seq_length:
            return None
        
        # Create a sequence pattern from lap indices
        lap_sequence = []
        group_to_type = {}
        
        # Assign each group a type identifier
        for i, group in enumerate(groups):
            group_to_type[id(group)] = f"type_{i}"
            for lap in group:
                lap_sequence.append((lap.lap_index, f"type_{i}", lap))
        
        # Sort by lap index to get chronological order
        lap_sequence.sort(key=lambda x: x[0])
        
        # Look for repeating patterns in the sequence
        type_sequence = [item[1] for item in lap_sequence]
        
        # Check if we have enough repetitions
        if len(type_sequence) < seq_length * 2:  # Need at least 2 full repetitions
            return None
        
        # Check for exact repetitions
        pattern = type_sequence[:seq_length]
        repetitions = 0
        
        for i in range(0, len(type_sequence), seq_length):
            if i + seq_length <= len(type_sequence):
                if type_sequence[i:i + seq_length] == pattern:
                    repetitions += 1
                else:
                    break
        
        if repetitions >= 2:  # Found a repeating pattern
            # Extract the laps that form this pattern
            pattern_laps = []
            for i in range(repetitions * seq_length):
                pattern_laps.append(lap_sequence[i][2])
            
            return self._create_complex_workout_pattern(pattern_laps, pattern, repetitions, all_laps)
        
        return None
    
    def _create_complex_workout_pattern(self, pattern_laps: List[Lap], pattern_types: List[str], 
                                      repetitions: int, all_laps: List[Lap]) -> WorkoutPattern:
        """Create a WorkoutPattern for complex repeating patterns"""
        
        seq_length = len(pattern_types)
        
        # Group laps by their position in the sequence
        sequence_groups = [[] for _ in range(seq_length)]
        
        for i, lap in enumerate(pattern_laps):
            sequence_groups[i % seq_length].append(lap)
        
        # Calculate average distances for each position in sequence
        avg_distances = []
        for group in sequence_groups:
            if group:
                avg_dist = sum(lap.distance for lap in group) / len(group)
                avg_distances.append(avg_dist)
        
        # Generate description for complex pattern
        distance_parts = []
        for dist in avg_distances:
            if dist >= 1000:
                distance_parts.append(f"{dist/1000:.1f}km")
            else:
                distance_parts.append(f"{int(dist)}m")
        
        description = f"{repetitions} x ({', '.join(distance_parts)})"
        
        # Create interval data
        intervals = []
        for i, lap in enumerate(pattern_laps):
            intervals.append({
                "number": i + 1,
                "distance": lap.distance,
                "time": lap.elapsed_time,
                "lap_index": lap.lap_index,
                "sequence_position": i % seq_length,
                "repetition": i // seq_length + 1
            })
        
        return WorkoutPattern(
            pattern_type="complex_intervals",
            intervals=intervals,
            rest_periods=self._detect_rest_periods(pattern_laps, all_laps),
            confidence=self._calculate_complex_confidence(pattern_laps, sequence_groups),
            description=description
        )
    
    def _calculate_complex_confidence(self, pattern_laps: List[Lap], sequence_groups: List[List[Lap]]) -> float:
        """Calculate confidence for complex patterns"""
        if not sequence_groups or not pattern_laps:
            return 0.1
        
        # Check consistency within each position of the sequence
        position_consistencies = []
        
        for group in sequence_groups:
            if len(group) > 1:
                distances = [lap.distance for lap in group if lap.distance > 0]
                times = [lap.elapsed_time for lap in group if lap.elapsed_time > 0]
                
                dist_consistency = 1.0
                time_consistency = 1.0
                
                if len(distances) > 1:
                    dist_cv = statistics.stdev(distances) / statistics.mean(distances)
                    dist_consistency = max(0, 1 - dist_cv * 3)
                
                if len(times) > 1:
                    time_cv = statistics.stdev(times) / statistics.mean(times)
                    time_consistency = max(0, 1 - time_cv * 2)
                
                position_consistencies.append((dist_consistency + time_consistency) / 2)
            else:
                position_consistencies.append(0.5)
        
        avg_consistency = statistics.mean(position_consistencies) if position_consistencies else 0.5
        
        # Bonus for having multiple repetitions
        repetition_bonus = min(0.2, len(pattern_laps) / (len(sequence_groups) * 10))
        
        return min(1.0, max(0.1, avg_consistency + repetition_bonus))

    def _create_workout_pattern(self, interval_laps: List[Lap], all_laps: List[Lap], pattern_id: str = "intervals") -> WorkoutPattern:
        """Create a WorkoutPattern from detected interval laps"""

        # Calculate interval statistics
        distances = [lap.distance for lap in interval_laps]
        times = [lap.elapsed_time for lap in interval_laps]

        avg_distance = statistics.mean(distances) if distances else 0
        avg_time = statistics.mean(times) if times else 0

        # Detect rest periods between intervals
        rest_periods = self._detect_rest_periods(interval_laps, all_laps)

        # Generate description
        description = self._generate_pattern_description(
            len(interval_laps), avg_distance, avg_time, rest_periods
        )

        # Create interval data
        intervals = []
        for i, lap in enumerate(interval_laps, 1):
            intervals.append({
                "number": i,
                "distance": lap.distance,
                "time": lap.elapsed_time,
                "lap_index": lap.lap_index
            })

        return WorkoutPattern(
            pattern_type="intervals",
            intervals=intervals,
            rest_periods=rest_periods,
            confidence=self._calculate_confidence(interval_laps, all_laps),
            description=description
        )

    def _detect_rest_periods(self, interval_laps: List[Lap], all_laps: List[Lap]) -> List[Dict]:
        """Detect rest periods between interval laps"""
        if len(interval_laps) < 2:
            return []

        rest_periods = []
        interval_indices = {lap.lap_index for lap in interval_laps}

        # Find laps between intervals
        for i in range(len(all_laps) - 1):
            current_lap = all_laps[i]
            next_lap = all_laps[i + 1]

            # If current is interval and next is interval, check for rest in between
            if (current_lap.lap_index in interval_indices and
                next_lap.lap_index in interval_indices and
                    next_lap.lap_index - current_lap.lap_index > 1):

                # Find rest laps between these intervals
                rest_laps = []
                for j in range(current_lap.lap_index + 1, next_lap.lap_index):
                    for lap in all_laps:
                        if lap.lap_index == j:
                            rest_laps.append(lap)
                            break

                if rest_laps:
                    total_rest_time = sum(
                        lap.elapsed_time for lap in rest_laps)
                    total_rest_distance = sum(
                        lap.distance for lap in rest_laps)

                    rest_periods.append({
                        "time": total_rest_time,
                        "distance": total_rest_distance,
                        "lap_count": len(rest_laps)
                    })

        return rest_periods

    def _generate_pattern_description(self, count: int, avg_distance: float,
                                      avg_time: int, rest_periods: List[Dict]) -> str:
        """Generate human-readable description of the interval pattern"""

        # Format distance
        if avg_distance >= 1000:
            distance_str = f"{avg_distance/1000:.1f}km"
        else:
            distance_str = f"{int(avg_distance)}m"

        # Format time with rounding for intervals > 10 seconds
        rounded_time = self._round_time(avg_time)
        minutes = int(rounded_time // 60)
        seconds = int(rounded_time % 60)
        if minutes > 0:
            time_str = f"{minutes}:{seconds:02d}"
        else:
            time_str = f"{seconds}s"

        # Determine if this is clearly a distance-based workout
        is_distance_based = self._is_distance_based_workout(avg_distance, avg_time)
        
        # Show either time or distance, never both
        if is_distance_based:
            description = f"{count} x {distance_str}"
        else:
            # Time-based description (default)
            description = f"{count} x {time_str}"

        # Add recovery information if detected
        if rest_periods:
            rest_period = rest_periods[0]  # Take first/average rest period
            avg_rest_time = rest_period['time']
            avg_rest_distance = rest_period.get('distance', 0)
            
            # Determine if recovery should be described by time or distance
            recovery_is_distance_based = self._is_distance_based_workout(avg_rest_distance, avg_rest_time)
            
            if recovery_is_distance_based:
                # Distance-based recovery
                if avg_rest_distance >= 1000:
                    recovery_str = f"{avg_rest_distance/1000:.1f}km"
                else:
                    recovery_str = f"{int(avg_rest_distance)}m"
            else:
                # Time-based recovery (default) with rounding
                rounded_rest_time = self._round_time(avg_rest_time)
                rest_minutes = int(rounded_rest_time // 60)
                rest_seconds = int(rounded_rest_time % 60)
                
                if rest_minutes > 0:
                    recovery_str = f"{rest_minutes}:{rest_seconds:02d}"
                else:
                    recovery_str = f"{rest_seconds}s"
            
            description += f" w/ {recovery_str} recovery"

        return description
    
    def _is_distance_based_workout(self, avg_distance: float, avg_time: int) -> bool:
        """
        Determine if workout is clearly distance-based rather than time-based
        Returns True for distance-based workouts
        """
        # Standard track/road distances (meters)
        standard_distances = [
            100, 200, 300, 400, 600, 800, 1000, 1200, 1500, 1600, 1609,  # Track/mile
            2000, 3000, 5000, 10000  # Road distances
        ]
        
        # Check if average distance is close to a standard distance
        for std_dist in standard_distances:
            if abs(avg_distance - std_dist) / std_dist < 0.1:  # Within 10%
                return True
        
        # Check for round distances (e.g., 500m, 750m, 2500m)
        # Round to nearest 50m and see if it's close to original
        rounded_distance = round(avg_distance / 50) * 50
        if abs(avg_distance - rounded_distance) / avg_distance < 0.1:
            # If it rounds to a "nice" number, likely distance-based
            if rounded_distance % 100 == 0 or rounded_distance % 50 == 0:
                return True
        
        # Additional check: very short intervals (<20 seconds) are usually time-based
        if avg_time < 20:
            return False
        
        # Default: assume time-based (removed long interval check)
        return False

    def _calculate_confidence(self, interval_laps: List[Lap], all_laps: List[Lap]) -> float:
        """Calculate confidence score for the detected pattern"""

        # Base confidence on consistency of intervals
        if len(interval_laps) < 3:
            return 0.5

        # Check distance consistency
        distances = [lap.distance for lap in interval_laps if lap.distance > 0]
        if len(distances) > 1:
            dist_cv = statistics.stdev(distances) / statistics.mean(distances)
            # Penalize high coefficient of variation
            dist_consistency = max(0, 1 - dist_cv * 5)
        else:
            dist_consistency = 0.5

        # Check time consistency
        times = [lap.elapsed_time for lap in interval_laps if lap.elapsed_time > 0]
        if len(times) > 1:
            time_cv = statistics.stdev(times) / statistics.mean(times)
            time_consistency = max(0, 1 - time_cv * 3)
        else:
            time_consistency = 0.5

        # Proportion of workout that is intervals
        interval_proportion = len(interval_laps) / len(all_laps)

        # Combined confidence score
        confidence = (dist_consistency * 0.4 +
                      time_consistency * 0.4 +
                      interval_proportion * 0.2)

        return min(1.0, max(0.1, confidence))


def analyze_workout_from_laps(laps: List[Lap], activity_name: str = "",
                              activity_type: str = "") -> Optional[WorkoutAnalysis]:
    """
    Main function to analyze workout from lap data
    Returns WorkoutAnalysis if patterns detected, None otherwise
    """
    if not laps:
        return None

    analyzer = LapAnalyzer()
    patterns = analyzer.analyze_laps(laps)

    if not patterns:
        return None

    # Calculate basic workout stats
    total_distance = sum(lap.distance for lap in laps)
    total_time = sum(lap.elapsed_time for lap in laps)

    # Choose primary pattern (highest confidence or complex pattern if available)
    primary_pattern = None
    if patterns:
        # Prefer complex patterns, then highest confidence
        complex_patterns = [p for p in patterns if p.pattern_type == "complex_intervals"]
        if complex_patterns:
            primary_pattern = max(complex_patterns, key=lambda p: p.confidence)
        else:
            primary_pattern = max(patterns, key=lambda p: p.confidence)

    # Generate comprehensive description
    if len(patterns) == 1:
        short_desc = primary_pattern.description
        detailed_desc = f"Workout structure: {primary_pattern.description}"
    else:
        # Multiple patterns detected
        pattern_descriptions = [p.description for p in patterns]
        short_desc = " + ".join(pattern_descriptions)
        detailed_desc = f"Complex workout with multiple patterns: {', '.join(pattern_descriptions)}"

    # Create workout analysis
    analysis = WorkoutAnalysis(
        activity_id=0,  # Will be set by caller
        activity_name=activity_name,
        activity_type=activity_type,
        total_distance=total_distance,
        total_time=total_time,
        has_laps=True,
        lap_count=len(laps),
        lap_analysis=f"Detected {len(patterns)} pattern(s): {short_desc}",
        detected_patterns=patterns,
        primary_pattern=primary_pattern,
        short_description=short_desc,
        detailed_description=f"{detailed_desc}. Total: {total_distance/1000:.1f}km in {total_time//60}:{total_time % 60:02.0f}",
        analysis_method="laps",
        confidence=primary_pattern.confidence if primary_pattern else 0.1
    )

    return analysis

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

        # Group laps by similar characteristics
        interval_groups = self._group_similar_laps(laps)

        # Find all interval patterns (simple and complex)
        patterns = self._find_all_patterns(interval_groups, laps)

        return patterns

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

        # Format time
        minutes = avg_time // 60
        seconds = avg_time % 60
        if minutes > 0:
            time_str = f"{minutes}:{seconds:02d}"
        else:
            time_str = f"{seconds}s"

        # Basic pattern description
        description = f"{count} x {distance_str}"

        # Add average time if significant
        if avg_time > 30:  # Only add time if longer than 30 seconds
            description += f" (avg {time_str})"

        # Add rest information if detected
        if rest_periods:
            avg_rest = statistics.mean([r['time'] for r in rest_periods])
            rest_minutes = int(avg_rest // 60)
            rest_seconds = int(avg_rest % 60)

            if rest_minutes > 0:
                rest_str = f"{rest_minutes}:{rest_seconds:02d}"
            else:
                rest_str = f"{rest_seconds}s"

            description += f" w/ {rest_str} rest"

        return description

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
        detailed_description=f"{detailed_desc}. Total: {total_distance/1000:.1f}km in {total_time//60}:{total_time % 60:02d}",
        analysis_method="laps",
        confidence=primary_pattern.confidence if primary_pattern else 0.1
    )

    return analysis

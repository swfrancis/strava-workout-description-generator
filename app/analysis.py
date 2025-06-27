from typing import List, Dict, Optional
from .models import Lap, WorkoutPattern, WorkoutAnalysis
import statistics


class LapAnalyzer:
    """Analyzes lap data to detect interval patterns"""

    def __init__(self):
        self.min_interval_count = 2  # Minimum intervals to consider a pattern
        self.distance_tolerance = 0.1  # 10% tolerance for distance grouping
        self.time_tolerance = 0.1  # 15% tolerance for time grouping

    def analyze_laps(self, laps: List[Lap]) -> Optional[WorkoutPattern]:
        """
        Analyze laps to detect interval patterns
        Returns a WorkoutPattern if intervals are detected, None otherwise
        """
        if len(laps) < self.min_interval_count:
            return None

        # Group laps by similar characteristics
        interval_groups = self._group_similar_laps(laps)

        # Find the most common interval pattern
        main_pattern = self._find_main_pattern(interval_groups)

        if main_pattern:
            return self._create_workout_pattern(main_pattern, laps)

        return None

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

    def _find_main_pattern(self, groups: List[List[Lap]]) -> Optional[List[Lap]]:
        """Find the group that represents the main interval pattern"""
        # Filter groups with minimum interval count
        interval_groups = [g for g in groups if len(
            g) >= self.min_interval_count]

        if not interval_groups:
            return None

        # Return the largest group (most common interval type)
        return max(interval_groups, key=len)

    def _create_workout_pattern(self, interval_laps: List[Lap], all_laps: List[Lap]) -> WorkoutPattern:
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
    Returns WorkoutAnalysis if pattern detected, None otherwise
    """
    if not laps:
        return None

    analyzer = LapAnalyzer()
    pattern = analyzer.analyze_laps(laps)

    if not pattern:
        return None

    # Calculate basic workout stats
    total_distance = sum(lap.distance for lap in laps)
    total_time = sum(lap.elapsed_time for lap in laps)

    # Create workout analysis
    analysis = WorkoutAnalysis(
        activity_id=0,  # Will be set by caller
        activity_name=activity_name,
        activity_type=activity_type,
        total_distance=total_distance,
        total_time=total_time,
        has_laps=True,
        lap_count=len(laps),
        lap_analysis=f"Detected {pattern.description}",
        detected_patterns=[pattern],
        primary_pattern=pattern,
        short_description=pattern.description,
        detailed_description=f"Workout structure: {pattern.description}. Total: {total_distance/1000:.1f}km in {total_time//60}:{total_time % 60:02d}",
        analysis_method="laps",
        confidence=pattern.confidence
    )

    return analysis

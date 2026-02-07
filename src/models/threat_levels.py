"""Threat level definitions and calculation logic for correlation engine.

This module provides the state machine for threat level transitions and scoring logic.
Separate from LLM output schemas - this is for the correlation engine's internal state.
"""

from enum import Enum

# Threat level thresholds (tunable constants)
GREEN_THRESHOLD = 30
RED_THRESHOLD = 70


class ThreatLevel(Enum):
    """Threat level states with monotonic escalation enforcement.

    Values are ordered to enforce one-way transitions (escalation only).
    The correlation engine never de-escalates automatically - only new analysis
    starting from scratch can produce a lower threat level.
    """

    GREEN = 1
    AMBER = 2
    RED = 3

    def can_transition_to(self, new_level: "ThreatLevel") -> bool:
        """Check if transition to new_level is allowed (monotonic escalation).

        Args:
            new_level: Target threat level

        Returns:
            True if new_level.value >= self.value (allows staying same or escalating)
            False if new_level.value < self.value (prevents de-escalation)
        """
        return new_level.value >= self.value


def determine_threat_level(composite_score: float) -> ThreatLevel:
    """Map composite correlation score to threat level.

    Args:
        composite_score: 0-100 composite score from correlation analysis

    Returns:
        ThreatLevel enum value based on threshold boundaries
    """
    if composite_score < GREEN_THRESHOLD:
        return ThreatLevel.GREEN
    elif composite_score < RED_THRESHOLD:
        return ThreatLevel.AMBER
    else:
        return ThreatLevel.RED


def calculate_confidence(narrative_count: int, movement_count: int, geo_match: bool) -> int:
    """Calculate confidence score for correlation result.

    Confidence is based on:
    - Event volume (more events = higher confidence)
    - Geographic alignment (geo match = bonus)
    - Temporal density (always within 72h window = bonus)

    Args:
        narrative_count: Number of narrative events correlated
        movement_count: Number of movement events correlated
        geo_match: Whether geographic focus matches Taiwan Strait

    Returns:
        Integer confidence score 0-95 (never 100% - always acknowledge uncertainty)
    """
    # Base confidence from event counts
    # Narrative events weighted higher (15 pts each, cap 40)
    narrative_confidence = min(narrative_count * 15, 40)

    # Movement events weighted lower (5 pts each, cap 30)
    movement_confidence = min(movement_count * 5, 30)

    # Geographic match bonus
    geo_bonus = 20 if geo_match else 0

    # Time density bonus (always applies since we filter to 72h window)
    time_bonus = 10

    # Sum and cap at 95 (never claim 100% certainty)
    total = narrative_confidence + movement_confidence + geo_bonus + time_bonus
    return min(total, 95)

"""Correlation engine for matching narrative and movement events.

This is the core of Dragon Watch - correlating state media coordination signals
with civilian movement indicators to produce threat assessments.

Pattern: Follows established batch processor pattern from batch_articles.py and batch_posts.py.
"""

import asyncio
import structlog
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple

from src.database.client import get_supabase
from src.models.threat_levels import (
    ThreatLevel,
    determine_threat_level,
    calculate_confidence,
    GREEN_THRESHOLD,
    RED_THRESHOLD,
)
from src.models.correlation import CorrelationResult, SubScores, AlertUpsertData
from src.utils.geo_utils import (
    is_in_taiwan_strait,
    check_narrative_geo_match,
    normalize_min_max,
)

logger = structlog.get_logger()

# Constants for correlation window and scoring
CORRELATION_WINDOW_HOURS = 72
WEIGHTS = {"outlet": 0.30, "phrase": 0.25, "volume": 0.20, "geo": 0.25}

# Normalization ranges (tuned for demo data: 60 articles, 120 posts, 4 outlets)
OUTLET_MIN, OUTLET_MAX = 1, 4
PHRASE_MIN, PHRASE_MAX = 0, 10
VOLUME_MIN, VOLUME_MAX = 0, 50


async def fetch_narrative_events(hours: int = 72) -> List[Dict[str, Any]]:
    """Fetch recent narrative events from database.

    Args:
        hours: Lookback window in hours (default: 72)

    Returns:
        List of narrative event dicts
    """
    client = await get_supabase()
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)

    response = (
        await client.table("narrative_events")
        .select("*")
        .gte("created_at", cutoff.isoformat())
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


async def fetch_movement_events(hours: int = 72) -> List[Dict[str, Any]]:
    """Fetch recent movement events from database.

    Args:
        hours: Lookback window in hours (default: 72)

    Returns:
        List of movement event dicts
    """
    client = await get_supabase()
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)

    response = (
        await client.table("movement_events")
        .select("*")
        .gte("created_at", cutoff.isoformat())
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def match_events_by_time_window(
    narrative_events: List[Dict[str, Any]],
    movement_events: List[Dict[str, Any]],
    window_hours: int = 72,
) -> List[Dict[str, Any]]:
    """Match narrative events with temporally proximate movement events.

    Args:
        narrative_events: List of narrative events
        movement_events: List of movement events
        window_hours: Time window for matching (default: 72)

    Returns:
        List of dicts with structure: {"narrative": event, "movements": [matched_events]}
    """
    matches = []

    for narr_event in narrative_events:
        # Parse narrative event timestamp
        narr_ts_str = narr_event.get("created_at")
        if not narr_ts_str:
            continue

        # Handle both 'Z' and '+00:00' suffixes
        narr_ts = datetime.fromisoformat(narr_ts_str.replace("Z", "+00:00"))

        # Find all movement events within window
        matched_movements = []
        for move_event in movement_events:
            move_ts_str = move_event.get("created_at")
            if not move_ts_str:
                continue

            move_ts = datetime.fromisoformat(move_ts_str.replace("Z", "+00:00"))

            # Check if within window
            time_diff = abs((narr_ts - move_ts).total_seconds() / 3600)  # hours
            if time_diff <= window_hours:
                matched_movements.append(move_event)

        # Only include narrative events that match at least one movement event
        if matched_movements:
            matches.append({"narrative": narr_event, "movements": matched_movements})

    return matches


def calculate_composite_score(
    narrative_event: Dict[str, Any],
    matched_movements: List[Dict[str, Any]],
    geo_match: bool,
) -> Tuple[float, SubScores]:
    """Calculate composite correlation score from weighted sub-factors.

    Args:
        narrative_event: Narrative event dict
        matched_movements: List of matched movement events
        geo_match: Whether geographic focus matches Taiwan Strait

    Returns:
        Tuple of (composite_score, SubScores)
    """
    # Extract raw values
    outlet_count = narrative_event.get("outlet_count", 1)
    phrase_count = len(narrative_event.get("synchronized_phrases", []))
    post_volume = len(matched_movements)
    geo_proximity = 100.0 if geo_match else 0.0

    # Normalize using min-max normalization
    outlet_score = normalize_min_max(outlet_count, OUTLET_MIN, OUTLET_MAX)
    phrase_score = normalize_min_max(phrase_count, PHRASE_MIN, PHRASE_MAX)
    volume_score = normalize_min_max(post_volume, VOLUME_MIN, VOLUME_MAX)
    geo_score = geo_proximity  # Already 0-100

    # Calculate weighted composite
    composite = (
        outlet_score * WEIGHTS["outlet"]
        + phrase_score * WEIGHTS["phrase"]
        + volume_score * WEIGHTS["volume"]
        + geo_score * WEIGHTS["geo"]
    )

    sub_scores = SubScores(
        outlet_score=outlet_score,
        phrase_score=phrase_score,
        volume_score=volume_score,
        geo_score=geo_score,
    )

    return composite, sub_scores


def build_evidence_summary(
    narrative_event: Dict[str, Any], matched_movements: List[Dict[str, Any]]
) -> str:
    """Generate plain-English evidence summary.

    Args:
        narrative_event: Narrative event dict
        matched_movements: List of matched movement events

    Returns:
        One-line evidence summary string
    """
    outlet_count = narrative_event.get("outlet_count", 0)
    geographic_focus = narrative_event.get("geographic_focus", "unknown region")
    movement_count = len(matched_movements)

    return (
        f"{outlet_count} state media outlets detected coordinating on '{geographic_focus}' themes, "
        f"correlating with {movement_count} civilian movement reports in region."
    )


async def upsert_alert(correlation: CorrelationResult) -> None:
    """Upsert alert to database with monotonic escalation enforcement.

    Args:
        correlation: Complete correlation result
    """
    client = await get_supabase()

    # Query for existing active alert in Taiwan Strait
    existing_response = (
        await client.table("alerts")
        .select("*")
        .eq("region", "Taiwan Strait")
        .is_("resolved_at", "null")
        .execute()
    )

    # Prepare new alert data
    now = datetime.now(timezone.utc).isoformat()

    detection_history_entry = {
        "detected_at": correlation.detected_at.isoformat(),
        "score": correlation.composite_score,
        "level": correlation.threat_level,
    }

    if existing_response.data:
        # Update existing alert with monotonic escalation check
        existing_alert = existing_response.data[0]
        current_level_str = existing_alert.get("threat_level", "GREEN")

        # Parse current threat level
        try:
            current_level = ThreatLevel[current_level_str]
        except KeyError:
            logger.warning(
                "invalid_existing_threat_level",
                level=current_level_str,
                defaulting_to="GREEN",
            )
            current_level = ThreatLevel.GREEN

        # Check if new level can transition (monotonic enforcement)
        new_level = ThreatLevel[correlation.threat_level]

        if not current_level.can_transition_to(new_level):
            logger.warning(
                "monotonic_escalation_prevented",
                current=current_level.name,
                attempted=new_level.name,
                action="keeping_current_level",
            )
            # Keep current level, don't update
            return

        # Prepare update data
        existing_metadata = existing_alert.get("correlation_metadata", {})
        existing_history = existing_metadata.get("detection_history", [])
        existing_history.append(detection_history_entry)

        update_data = {
            "threat_level": correlation.threat_level,
            "threat_score": correlation.composite_score,
            "confidence": correlation.confidence,
            "sub_scores": correlation.sub_scores.model_dump(),
            "correlation_metadata": {
                "narrative_event_ids": correlation.narrative_event_ids,
                "movement_event_ids": correlation.movement_event_ids,
                "evidence_summary": correlation.evidence_summary,
                "detection_history": existing_history,
            },
            "updated_at": now,
        }

        await client.table("alerts").update(update_data).eq(
            "id", existing_alert["id"]
        ).execute()

        logger.info(
            "alert_updated",
            alert_id=existing_alert["id"],
            threat_level=correlation.threat_level,
            score=correlation.composite_score,
        )

    else:
        # Insert new alert
        insert_data = {
            "region": correlation.region,
            "threat_level": correlation.threat_level,
            "threat_score": correlation.composite_score,
            "confidence": correlation.confidence,
            "sub_scores": correlation.sub_scores.model_dump(),
            "correlation_metadata": {
                "narrative_event_ids": correlation.narrative_event_ids,
                "movement_event_ids": correlation.movement_event_ids,
                "evidence_summary": correlation.evidence_summary,
                "detection_history": [detection_history_entry],
            },
            "updated_at": now,
        }

        response = await client.table("alerts").insert(insert_data).execute()

        logger.info(
            "alert_created",
            alert_id=response.data[0]["id"] if response.data else None,
            threat_level=correlation.threat_level,
            score=correlation.composite_score,
        )


async def correlate_events_batch() -> Dict[str, Any]:
    """Main correlation pipeline orchestrator.

    Matches narrative coordination events with movement events by time and geography,
    calculates composite threat scores, and upserts alerts to database.

    Returns:
        Summary dict with status, correlations_found, highest_score, threat_level, confidence
    """
    logger.info("pipeline_start", pipeline="correlate_events")

    try:
        # 1. Fetch both event streams concurrently
        narrative_events, movement_events = await asyncio.gather(
            fetch_narrative_events(), fetch_movement_events()
        )

        # Check if either stream is empty
        if not narrative_events:
            logger.info("pipeline_complete", status="no_narrative_events")
            return {"status": "no_narrative_events", "correlations_found": 0}

        if not movement_events:
            logger.info("pipeline_complete", status="no_movement_events")
            return {"status": "no_movement_events", "correlations_found": 0}

        logger.info(
            "events_fetched",
            narrative_count=len(narrative_events),
            movement_count=len(movement_events),
        )

        # 2. Match events by time window
        matches = match_events_by_time_window(narrative_events, movement_events)

        if not matches:
            logger.info("pipeline_complete", status="no_temporal_matches")
            return {"status": "no_temporal_matches", "correlations_found": 0}

        logger.info("temporal_matches_found", count=len(matches))

        # 3. Calculate composite scores for each match
        correlations = []

        for match in matches:
            narrative = match["narrative"]
            movements = match["movements"]

            # Check geographic proximity
            narrative_geo = check_narrative_geo_match(
                narrative.get("geographic_focus")
            )

            # Check if ANY matched movement has location in Taiwan Strait
            movement_geo = False
            for movement in movements:
                lat = movement.get("location_lat")
                lon = movement.get("location_lon")
                if lat is not None and lon is not None:
                    if is_in_taiwan_strait(lat, lon):
                        movement_geo = True
                        break

            # Both must match for geographic correlation
            geo_match = narrative_geo and movement_geo

            # Calculate composite score
            composite_score, sub_scores = calculate_composite_score(
                narrative, movements, geo_match
            )

            # Build evidence summary
            evidence_summary = build_evidence_summary(narrative, movements)

            # Create correlation result
            correlation = CorrelationResult(
                narrative_event_ids=[narrative["id"]],
                movement_event_ids=[m["id"] for m in movements],
                composite_score=composite_score,
                sub_scores=sub_scores,
                threat_level="",  # Will be set below
                confidence=0,  # Will be set below
                geo_match=geo_match,
                region="Taiwan Strait",
                evidence_summary=evidence_summary,
                detected_at=datetime.now(timezone.utc),
            )

            correlations.append(correlation)

        # 4. Take the correlation with highest composite score
        if not correlations:
            logger.info("pipeline_complete", status="no_correlations")
            return {"status": "no_correlations", "correlations_found": 0}

        highest_correlation = max(correlations, key=lambda c: c.composite_score)

        # 5. Determine threat level and confidence
        threat_level = determine_threat_level(highest_correlation.composite_score)
        confidence = calculate_confidence(
            narrative_count=len(highest_correlation.narrative_event_ids),
            movement_count=len(highest_correlation.movement_event_ids),
            geo_match=highest_correlation.geo_match,
        )

        # Update correlation with threat level and confidence
        highest_correlation.threat_level = threat_level.name
        highest_correlation.confidence = confidence

        # 6. Upsert alert
        await upsert_alert(highest_correlation)

        # 7. Return summary
        summary = {
            "status": "success",
            "correlations_found": len(correlations),
            "highest_score": highest_correlation.composite_score,
            "threat_level": threat_level.name,
            "confidence": confidence,
        }

        logger.info("pipeline_complete", **summary)
        return summary

    except Exception as e:
        logger.error("pipeline_failed", error=str(e))
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    asyncio.run(correlate_events_batch())

"""Demo runner for Dragon Watch correlation engine.

Demonstrates the full correlation pipeline working against demo data
(or synthetic fallback if Phase 2 LLM processing hasn't run yet).

This script shows GREEN -> AMBER -> RED threat escalation over the 72-hour
Taiwan Strait scenario.

Run directly: python scripts/run_correlation_demo.py
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from src.database.client import get_supabase
from src.processors.correlate_events import correlate_events_batch

# Base timestamp matching load_demo_data.py
BASE_TIME = datetime(2026, 2, 5, 0, 0, 0, tzinfo=timezone.utc)


async def check_events_exist() -> Dict[str, int]:
    """Check if narrative and movement events exist from Phase 2 processing.

    Returns:
        Dict with narrative_count and movement_count
    """
    client = await get_supabase()

    narrative_response = await client.table("narrative_events").select("id", count="exact").execute()
    movement_response = await client.table("movement_events").select("id", count="exact").execute()

    return {
        "narrative_count": len(narrative_response.data) if narrative_response.data else 0,
        "movement_count": len(movement_response.data) if movement_response.data else 0,
    }


async def insert_synthetic_events() -> None:
    """Insert synthetic narrative and movement events for demo.

    This simulates the output of Phase 2 LLM pipeline when API keys aren't
    available. Creates events matching the 3-phase demo scenario.
    """
    client = await get_supabase()

    print("\nInserting synthetic events (Phase 2 LLM pipeline fallback)...")

    # Synthetic narrative events (3 events, one per phase)
    narrative_events = [
        {
            "coordination_score": 15,
            "outlet_count": 2,
            "synchronized_phrases": ["peaceful development", "cross-strait"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["cooperation"],
            "confidence": 40,
            "article_ids": [1, 2, 3],
            "created_at": (BASE_TIME + timedelta(hours=12)).isoformat(),
        },
        {
            "coordination_score": 55,
            "outlet_count": 3,
            "synchronized_phrases": [
                "reunification inevitable",
                "sovereignty non-negotiable",
                "separatist forces",
            ],
            "geographic_focus": "Taiwan Strait",
            "themes": ["sovereignty", "reunification"],
            "confidence": 70,
            "article_ids": [21, 22, 23],
            "created_at": (BASE_TIME + timedelta(hours=36)).isoformat(),
        },
        {
            "coordination_score": 85,
            "outlet_count": 4,
            "synchronized_phrases": [
                "live-fire exercises",
                "combat readiness",
                "decisive action",
                "safeguard sovereignty",
            ],
            "geographic_focus": "Taiwan Strait",
            "themes": ["military", "exercises", "readiness"],
            "confidence": 90,
            "article_ids": [41, 42, 43],
            "created_at": (BASE_TIME + timedelta(hours=60)).isoformat(),
        },
    ]

    for event in narrative_events:
        await client.table("narrative_events").insert(event).execute()

    print(f"  Inserted {len(narrative_events)} narrative events")

    # Synthetic movement events (9 events across phases)
    movement_events = [
        # GREEN phase (2 events)
        {
            "category": "naval",
            "location_name": "Taiwan Strait",
            "location_lat": 24.5,
            "location_lon": 120.0,
            "confidence": 30,
            "source_post_ids": [5, 6],
            "created_at": (BASE_TIME + timedelta(hours=12)).isoformat(),
        },
        {
            "category": "naval",
            "location_name": "Taiwan Strait",
            "location_lat": 24.8,
            "location_lon": 119.5,
            "confidence": 35,
            "source_post_ids": [10, 11],
            "created_at": (BASE_TIME + timedelta(hours=20)).isoformat(),
        },
        # AMBER phase (3 events)
        {
            "category": "convoy",
            "location_name": "Taiwan Strait",
            "location_lat": 24.2,
            "location_lon": 119.8,
            "confidence": 60,
            "source_post_ids": [45, 46, 47],
            "created_at": (BASE_TIME + timedelta(hours=28)).isoformat(),
        },
        {
            "category": "naval",
            "location_name": "Taiwan Strait",
            "location_lat": 25.1,
            "location_lon": 120.2,
            "confidence": 70,
            "source_post_ids": [50, 51, 52],
            "created_at": (BASE_TIME + timedelta(hours=36)).isoformat(),
        },
        {
            "category": "restricted_zone",
            "location_name": "Taiwan Strait",
            "location_lat": 24.6,
            "location_lon": 119.3,
            "confidence": 75,
            "source_post_ids": [55, 56],
            "created_at": (BASE_TIME + timedelta(hours=40)).isoformat(),
        },
        # RED phase (4 events)
        {
            "category": "naval",
            "location_name": "Taiwan Strait",
            "location_lat": 24.3,
            "location_lon": 119.6,
            "confidence": 85,
            "source_post_ids": [85, 86, 87],
            "created_at": (BASE_TIME + timedelta(hours=50)).isoformat(),
        },
        {
            "category": "convoy",
            "location_name": "Taiwan Strait",
            "location_lat": 24.9,
            "location_lon": 120.1,
            "confidence": 90,
            "source_post_ids": [90, 91, 92, 93],
            "created_at": (BASE_TIME + timedelta(hours=55)).isoformat(),
        },
        {
            "category": "flight",
            "location_name": "Taiwan Strait",
            "location_lat": 25.2,
            "location_lon": 119.7,
            "confidence": 88,
            "source_post_ids": [95, 96],
            "created_at": (BASE_TIME + timedelta(hours=60)).isoformat(),
        },
        {
            "category": "restricted_zone",
            "location_name": "Taiwan Strait",
            "location_lat": 24.7,
            "location_lon": 120.3,
            "confidence": 95,
            "source_post_ids": [100, 101, 102],
            "created_at": (BASE_TIME + timedelta(hours=65)).isoformat(),
        },
    ]

    for event in movement_events:
        await client.table("movement_events").insert(event).execute()

    print(f"  Inserted {len(movement_events)} movement events")
    print("  Synthetic events ready for correlation\n")


async def fetch_current_alert() -> Dict[str, Any] | None:
    """Fetch current active alert for Taiwan Strait.

    Returns:
        Alert dict or None if no active alert exists
    """
    client = await get_supabase()

    response = (
        await client.table("alerts")
        .select("*")
        .eq("region", "Taiwan Strait")
        .is_("resolved_at", "null")
        .execute()
    )

    if response.data:
        return response.data[0]
    return None


def format_subscores(sub_scores: Dict[str, float]) -> str:
    """Format sub-scores into readable string."""
    return (
        f"    Outlet:  {sub_scores.get('outlet_score', 0):.1f}/100\n"
        f"    Phrase:  {sub_scores.get('phrase_score', 0):.1f}/100\n"
        f"    Volume:  {sub_scores.get('volume_score', 0):.1f}/100\n"
        f"    Geo:     {sub_scores.get('geo_score', 0):.1f}/100"
    )


async def main() -> None:
    """Main demo orchestrator."""
    print("=" * 70)
    print("Dragon Watch Correlation Engine Demo")
    print("=" * 70)
    print()

    # Check if processed events exist
    print("Checking for processed events from Phase 2...")
    counts = await check_events_exist()

    print(f"  Narrative events: {counts['narrative_count']}")
    print(f"  Movement events:  {counts['movement_count']}")

    # If no events, insert synthetic fallback
    if counts["narrative_count"] == 0 or counts["movement_count"] == 0:
        print("\nNo processed events found. Using synthetic fallback data.")
        await insert_synthetic_events()
    else:
        print("\nProcessed events found. Using real Phase 2 output.\n")

    # Run correlation engine
    print("-" * 70)
    print("Running correlation engine...")
    print("-" * 70)
    print()

    result = await correlate_events_batch()

    # Display results
    print("Correlation Results:")
    print(f"  Status: {result.get('status')}")

    if result.get("status") == "success":
        print(f"  Correlations found: {result.get('correlations_found')}")
        print(f"  Highest composite score: {result.get('highest_score'):.2f}/100")
        print(f"  Threat level: {result.get('threat_level')}")
        print(f"  Confidence: {result.get('confidence')}%")
    else:
        print(f"  Message: {result.get('error', 'No correlations found')}")

    print()

    # Fetch and display current alert state
    print("-" * 70)
    print("Current Alert State:")
    print("-" * 70)
    print()

    alert = await fetch_current_alert()

    if alert:
        print(f"Alert ID: {alert['id']}")
        print(f"Region: {alert['region']}")
        print(f"Threat Level: {alert['threat_level']}")
        print(f"Threat Score: {alert.get('threat_score', 0):.2f}/100")
        print(f"Confidence: {alert.get('confidence', 0)}%")
        print()

        # Sub-scores breakdown
        sub_scores = alert.get("sub_scores", {})
        if sub_scores:
            print("Sub-Scores Breakdown:")
            print(format_subscores(sub_scores))
            print()

        # Evidence chain
        metadata = alert.get("correlation_metadata", {})
        if metadata:
            print("Evidence Chain:")
            print(f"  Narrative event IDs: {metadata.get('narrative_event_ids', [])}")
            print(f"  Movement event IDs: {metadata.get('movement_event_ids', [])}")
            print(f"  Summary: {metadata.get('evidence_summary', 'N/A')}")
            print()

            # Detection history (shows escalation)
            history = metadata.get("detection_history", [])
            if history:
                print("Detection History (Escalation Timeline):")
                for idx, entry in enumerate(history, 1):
                    detected_at = entry.get("detected_at", "unknown")
                    score = entry.get("score", 0)
                    level = entry.get("level", "UNKNOWN")
                    print(f"  {idx}. {detected_at[:19]} - Score: {score:.2f} - Level: {level}")

        print()
        print(f"Created: {alert.get('created_at', 'N/A')[:19]}")
        print(f"Updated: {alert.get('updated_at', 'N/A')[:19]}")
    else:
        print("No active alert found.")

    print()
    print("=" * 70)
    print("Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

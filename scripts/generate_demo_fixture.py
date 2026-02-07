"""Generate complete pre-computed demo fixture for Dragon Watch playback engine.

This script creates a single JSON file containing ALL data for the 72-hour Taiwan Strait
escalation scenario, including:
- Raw intelligence (articles, social_posts, vessel_positions) from Phase 1
- Processed intelligence (narrative_events, movement_events) from Phase 2
- Correlation outputs (alerts, briefs) from Phase 3

The fixture enables the demo playback engine to drip-feed pre-computed data into Supabase
without requiring any live API calls.

Run: python scripts/generate_demo_fixture.py
Validate: python scripts/generate_demo_fixture.py --validate
"""

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Import existing generators for raw data
from load_demo_data import (
    BASE_TIME,
    generate_demo_articles,
    generate_demo_posts,
    generate_demo_positions,
)

# Base timestamp for scenario (matches load_demo_data.py)
FIXTURE_BASE_TIME = datetime(2026, 2, 5, 0, 0, 0, tzinfo=timezone.utc)

# Demo timing constants
SIMULATED_HOURS = 72
NORMAL_DURATION_SECONDS = 300  # 5 minutes at "Normal" speed
SECONDS_PER_HOUR = NORMAL_DURATION_SECONDS / SIMULATED_HOURS  # ~4.167 seconds per simulated hour


def hours_to_demo_offset(hours: float) -> float:
    """Convert simulated hours to demo playback offset in seconds.

    Args:
        hours: Simulated time in hours (0-72)

    Returns:
        Demo offset in seconds (0-300)
    """
    return (hours / SIMULATED_HOURS) * NORMAL_DURATION_SECONDS


def add_jitter(offset: float, max_jitter: float = 3.0) -> float:
    """Add random jitter to prevent exact timestamp collisions.

    Args:
        offset: Base offset in seconds
        max_jitter: Maximum jitter to add (default 3 seconds)

    Returns:
        Offset with jitter added
    """
    return offset + random.uniform(0.1, max_jitter)


def convert_datetimes_to_iso(obj):
    """Recursively convert datetime objects to ISO strings for JSON serialization.

    Args:
        obj: Object to convert (dict, list, datetime, or primitive)

    Returns:
        Object with all datetimes converted to ISO strings
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_datetimes_to_iso(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes_to_iso(item) for item in obj]
    else:
        return obj


def generate_narrative_events() -> list[dict]:
    """Generate pre-computed narrative events following 5-beat arc.

    Returns:
        List of narrative event records with demo metadata
    """
    events = []

    # Beat 1: Baseline (T+0-14h) - 1 event
    events.append({
        "hours_offset": 12,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Routine cross-strait coverage with peaceful development themes",
            "confidence": 35,
            "source_ids": [1, 2, 3, 4],
            "coordination_score": 12,
            "outlet_count": 2,
            "synchronized_phrases": ["peaceful development", "cross-strait cooperation"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["cooperation"],
            "article_ids": [1, 2, 3, 4],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=12)).isoformat(),
        }
    })

    # Beat 2: First signals (T+14-28h) - 2 events
    events.append({
        "hours_offset": 18,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Increased sovereignty messaging across multiple state outlets",
            "confidence": 55,
            "source_ids": [21, 22, 23],
            "coordination_score": 35,
            "outlet_count": 2,
            "synchronized_phrases": ["sovereignty non-negotiable", "territorial integrity"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["sovereignty"],
            "article_ids": [21, 22, 23],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=18)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 26,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Reunification messaging with coordinated phrasing",
            "confidence": 60,
            "source_ids": [24, 25, 26, 27],
            "coordination_score": 42,
            "outlet_count": 3,
            "synchronized_phrases": ["reunification inevitable", "historical responsibility"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["sovereignty", "reunification"],
            "article_ids": [24, 25, 26, 27],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=26)).isoformat(),
        }
    })

    # Beat 3: Coordination detected (T+28-42h) - 2 events
    events.append({
        "hours_offset": 32,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Strong coordination spike with separatist forces warnings",
            "confidence": 70,
            "source_ids": [28, 29, 30, 31],
            "coordination_score": 62,
            "outlet_count": 3,
            "synchronized_phrases": ["separatist forces", "national unity", "resolve unshakeable"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["sovereignty", "reunification", "anti-separatism"],
            "article_ids": [28, 29, 30, 31],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=32)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 40,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Military tone emerging with reunification timeline acceleration",
            "confidence": 72,
            "source_ids": [35, 36, 37, 38],
            "coordination_score": 68,
            "outlet_count": 3,
            "synchronized_phrases": ["reunification timeline", "not sole option", "foreign interference"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["sovereignty", "military", "reunification"],
            "article_ids": [35, 36, 37, 38],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=40)).isoformat(),
        }
    })

    # Beat 4: Movement confirmed (T+42-56h) - 2 events
    events.append({
        "hours_offset": 48,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Full-spectrum military readiness messaging across all outlets",
            "confidence": 82,
            "source_ids": [41, 42, 43, 44],
            "coordination_score": 75,
            "outlet_count": 4,
            "synchronized_phrases": ["live-fire exercises", "combat readiness", "safeguard sovereignty"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["military", "exercises", "readiness"],
            "article_ids": [41, 42, 43, 44],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=48)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 54,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Coordinated military operations announcement with decisive action framing",
            "confidence": 85,
            "source_ids": [45, 46, 47, 48],
            "coordination_score": 80,
            "outlet_count": 4,
            "synchronized_phrases": ["joint military operations", "decisive action", "high combat readiness"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["military", "exercises", "operations"],
            "article_ids": [45, 46, 47, 48],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=54)).isoformat(),
        }
    })

    # Beat 5: Full alert (T+56-72h) - 2 events
    events.append({
        "hours_offset": 60,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Maximum coordination: blockade and encirclement capabilities showcased",
            "confidence": 90,
            "source_ids": [52, 53, 54, 55],
            "coordination_score": 88,
            "outlet_count": 4,
            "synchronized_phrases": ["blockade capability", "encirclement", "prepared for decisive action"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["military", "operations", "decisive_action"],
            "article_ids": [52, 53, 54, 55],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=60)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 68,
        "data": {
            "event_type": "narrative_coordination",
            "summary": "Peak coordination: imminent action framing across all state media",
            "confidence": 92,
            "source_ids": [56, 57, 58, 59, 60],
            "coordination_score": 93,
            "outlet_count": 4,
            "synchronized_phrases": ["forces prepared", "highest alert status", "seize control by force"],
            "geographic_focus": "Taiwan Strait",
            "themes": ["military", "decisive_action", "readiness"],
            "article_ids": [56, 57, 58, 59, 60],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=68)).isoformat(),
        }
    })

    return events


def generate_movement_events() -> list[dict]:
    """Generate pre-computed movement events following 5-beat arc.

    Returns:
        List of movement event records with demo metadata
    """
    events = []

    # Beat 1: Baseline (T+0-14h) - 2 events
    events.append({
        "hours_offset": 8,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.5,
            "location_lon": 120.0,
            "description": "Routine coast guard patrol observed in Taiwan Strait",
            "category": "naval",
            "location_name": "Taiwan Strait",
            "confidence": 30,
            "source_post_ids": [5, 6],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=8)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 14,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.8,
            "location_lon": 119.5,
            "description": "Standard naval patrol near Fujian coast",
            "category": "naval",
            "location_name": "Taiwan Strait",
            "confidence": 28,
            "source_post_ids": [12, 13],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=14)).isoformat(),
        }
    })

    # Beat 2: First signals (T+14-28h) - 3 events
    events.append({
        "hours_offset": 20,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": 412100005,
            "location_lat": 24.2,
            "location_lon": 119.8,
            "description": "Multiple naval vessels departing Ningbo port",
            "category": "naval",
            "location_name": "Taiwan Strait",
            "confidence": 55,
            "source_post_ids": [42, 43],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=20)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 24,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.6,
            "location_lon": 119.3,
            "description": "Military convoy activity increased near Xiamen",
            "category": "convoy",
            "location_name": "Taiwan Strait",
            "confidence": 52,
            "source_post_ids": [48, 49, 50],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=24)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 28,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": 412100008,
            "location_lat": 25.1,
            "location_lon": 120.2,
            "description": "Type 052D destroyers concentrated south of Wenzhou",
            "category": "naval",
            "location_name": "Taiwan Strait",
            "confidence": 58,
            "source_post_ids": [52, 53],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=28)).isoformat(),
        }
    })

    # Beat 3: Coordination detected (T+28-42h) - 3 events
    events.append({
        "hours_offset": 34,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.3,
            "location_lon": 119.6,
            "description": "Amphibious ships loading at Zhanjiang, unusual activity level",
            "category": "convoy",
            "location_name": "Taiwan Strait",
            "confidence": 68,
            "source_post_ids": [60, 61, 62],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=34)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 38,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.9,
            "location_lon": 120.1,
            "description": "NOTAM issued for restricted airspace over Taiwan Strait",
            "category": "restricted_zone",
            "location_name": "Taiwan Strait",
            "confidence": 72,
            "source_post_ids": [66, 67],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=38)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 42,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": 412100015,
            "location_lat": 25.2,
            "location_lon": 119.7,
            "description": "Naval aviation base showing increased sortie rates",
            "category": "flight",
            "location_name": "Taiwan Strait",
            "confidence": 70,
            "source_post_ids": [70, 71, 72],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=42)).isoformat(),
        }
    })

    # Beat 4: Movement confirmed (T+42-56h) - 4 events
    events.append({
        "hours_offset": 46,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": 412100018,
            "location_lat": 24.4,
            "location_lon": 119.9,
            "description": "Large-scale PLA exercise announced, live-fire zones declared",
            "category": "naval",
            "location_name": "Taiwan Strait",
            "confidence": 82,
            "source_post_ids": [82, 83, 84],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=46)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 50,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.7,
            "location_lon": 120.3,
            "description": "Multiple amphibious assault ships departing Zhanjiang",
            "category": "convoy",
            "location_name": "Taiwan Strait",
            "confidence": 85,
            "source_post_ids": [88, 89, 90],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=50)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 54,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.1,
            "location_lon": 119.4,
            "description": "Combat aircraft sorties increased 300% past 12 hours",
            "category": "flight",
            "location_name": "Taiwan Strait",
            "confidence": 88,
            "source_post_ids": [94, 95, 96],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=54)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 56,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 25.0,
            "location_lon": 120.0,
            "description": "Six no-sail zones declared surrounding Taiwan",
            "category": "restricted_zone",
            "location_name": "Taiwan Strait",
            "confidence": 90,
            "source_post_ids": [98, 99, 100],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=56)).isoformat(),
        }
    })

    # Beat 5: Full alert (T+56-72h) - 3 events
    events.append({
        "hours_offset": 62,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": 412100025,
            "location_lat": 24.5,
            "location_lon": 119.8,
            "description": "Naval blockade formation visible, at least 20 major combatants",
            "category": "naval",
            "location_name": "Taiwan Strait",
            "confidence": 92,
            "source_post_ids": [105, 106, 107, 108],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=62)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 66,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.8,
            "location_lon": 120.1,
            "description": "Rocket Force TELs moving to coastal launch positions",
            "category": "convoy",
            "location_name": "Taiwan Strait",
            "confidence": 90,
            "source_post_ids": [112, 113, 114],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=66)).isoformat(),
        }
    })

    events.append({
        "hours_offset": 70,
        "data": {
            "event_type": "military_movement",
            "vessel_mmsi": None,
            "location_lat": 24.3,
            "location_lon": 119.5,
            "description": "Amphibious assault wave launched, landing craft in water",
            "category": "convoy",
            "location_name": "Taiwan Strait",
            "confidence": 95,
            "source_post_ids": [118, 119, 120],
            "created_at": (FIXTURE_BASE_TIME + timedelta(hours=70)).isoformat(),
        }
    })

    return events


def generate_alerts() -> list[dict]:
    """Generate pre-computed alert updates following 5-beat escalation.

    Returns:
        List of alert records with demo metadata (first INSERT, rest UPDATEs)
    """
    alerts = []

    # Beat 1: Initial GREEN alert (INSERT)
    alerts.append({
        "hours_offset": 14,
        "action": "insert",
        "data": {
            "region": "Taiwan Strait",
            "threat_level": "GREEN",
            "threat_score": 12,
            "confidence": 30,
            "severity": "low",
            "title": "Baseline Activity",
            "description": "Normal cross-strait patterns observed",
            "event_ids": [],
            "sub_scores": {
                "outlet_score": 15,
                "phrase_score": 10,
                "volume_score": 8,
                "geo_score": 15
            },
            "correlation_metadata": {
                "narrative_event_ids": [1],
                "movement_event_ids": [1, 2],
                "evidence_summary": "Routine coverage and standard naval patrols",
                "detection_history": [
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=14)).isoformat(),
                        "score": 12,
                        "level": "GREEN"
                    }
                ]
            },
            "updated_at": (FIXTURE_BASE_TIME + timedelta(hours=14)).isoformat(),
        }
    })

    # Beat 2: First elevation to GREEN with higher score (UPDATE)
    alerts.append({
        "hours_offset": 28,
        "action": "update",
        "data": {
            "region": "Taiwan Strait",
            "threat_level": "GREEN",
            "threat_score": 28,
            "confidence": 52,
            "severity": "low",
            "title": "Increased Rhetoric",
            "description": "Sovereignty messaging elevated across state outlets",
            "event_ids": [],
            "sub_scores": {
                "outlet_score": 32,
                "phrase_score": 28,
                "volume_score": 22,
                "geo_score": 30
            },
            "correlation_metadata": {
                "narrative_event_ids": [1, 2, 3],
                "movement_event_ids": [1, 2, 3, 4, 5],
                "evidence_summary": "Coordinated sovereignty messaging with increased naval activity",
                "detection_history": [
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=14)).isoformat(),
                        "score": 12,
                        "level": "GREEN"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=28)).isoformat(),
                        "score": 28,
                        "level": "GREEN"
                    }
                ]
            },
            "updated_at": (FIXTURE_BASE_TIME + timedelta(hours=28)).isoformat(),
        }
    })

    # Beat 3: Escalation to AMBER (UPDATE)
    alerts.append({
        "hours_offset": 42,
        "action": "update",
        "data": {
            "region": "Taiwan Strait",
            "threat_level": "AMBER",
            "threat_score": 52,
            "confidence": 71,
            "severity": "medium",
            "title": "Coordination Detected",
            "description": "Significant narrative coordination aligned with military movements",
            "event_ids": [],
            "sub_scores": {
                "outlet_score": 58,
                "phrase_score": 52,
                "volume_score": 45,
                "geo_score": 55
            },
            "correlation_metadata": {
                "narrative_event_ids": [1, 2, 3, 4, 5],
                "movement_event_ids": [1, 2, 3, 4, 5, 6, 7, 8],
                "evidence_summary": "Strong narrative coordination spike with amphibious ship loading and restricted airspace",
                "detection_history": [
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=14)).isoformat(),
                        "score": 12,
                        "level": "GREEN"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=28)).isoformat(),
                        "score": 28,
                        "level": "GREEN"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=42)).isoformat(),
                        "score": 52,
                        "level": "AMBER"
                    }
                ]
            },
            "updated_at": (FIXTURE_BASE_TIME + timedelta(hours=42)).isoformat(),
        }
    })

    # Beat 4: Higher AMBER (UPDATE)
    alerts.append({
        "hours_offset": 56,
        "action": "update",
        "data": {
            "region": "Taiwan Strait",
            "threat_level": "AMBER",
            "threat_score": 68,
            "confidence": 84,
            "severity": "high",
            "title": "Movement Confirmed",
            "description": "Military readiness messaging synchronized with live-fire exercise announcement",
            "event_ids": [],
            "sub_scores": {
                "outlet_score": 72,
                "phrase_score": 68,
                "volume_score": 62,
                "geo_score": 70
            },
            "correlation_metadata": {
                "narrative_event_ids": [1, 2, 3, 4, 5, 6, 7],
                "movement_event_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "evidence_summary": "Full military readiness narrative with large-scale exercise and no-sail zones declared",
                "detection_history": [
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=14)).isoformat(),
                        "score": 12,
                        "level": "GREEN"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=28)).isoformat(),
                        "score": 28,
                        "level": "GREEN"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=42)).isoformat(),
                        "score": 52,
                        "level": "AMBER"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=56)).isoformat(),
                        "score": 68,
                        "level": "AMBER"
                    }
                ]
            },
            "updated_at": (FIXTURE_BASE_TIME + timedelta(hours=56)).isoformat(),
        }
    })

    # Beat 5: Escalation to RED (UPDATE)
    alerts.append({
        "hours_offset": 70,
        "action": "update",
        "data": {
            "region": "Taiwan Strait",
            "threat_level": "RED",
            "threat_score": 82,
            "confidence": 92,
            "severity": "critical",
            "title": "Full Alert",
            "description": "Peak coordination with naval blockade and amphibious assault operations",
            "event_ids": [],
            "sub_scores": {
                "outlet_score": 88,
                "phrase_score": 82,
                "volume_score": 78,
                "geo_score": 85
            },
            "correlation_metadata": {
                "narrative_event_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                "movement_event_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                "evidence_summary": "Maximum narrative coordination with imminent action framing and amphibious assault wave launched",
                "detection_history": [
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=14)).isoformat(),
                        "score": 12,
                        "level": "GREEN"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=28)).isoformat(),
                        "score": 28,
                        "level": "GREEN"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=42)).isoformat(),
                        "score": 52,
                        "level": "AMBER"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=56)).isoformat(),
                        "score": 68,
                        "level": "AMBER"
                    },
                    {
                        "detected_at": (FIXTURE_BASE_TIME + timedelta(hours=70)).isoformat(),
                        "score": 82,
                        "level": "RED"
                    }
                ]
            },
            "updated_at": (FIXTURE_BASE_TIME + timedelta(hours=70)).isoformat(),
        }
    })

    return alerts


def generate_briefs() -> list[dict]:
    """Generate pre-computed intelligence briefs at key escalation moments.

    Returns:
        List of brief records with demo metadata
    """
    briefs = []

    # Beat 2: First brief at GREEN elevation (T+28h)
    briefs.append({
        "hours_offset": 29,
        "data": {
            "title": "Taiwan Strait Escalation - Initial Assessment",
            "threat_level": "GREEN",
            "confidence": 52,
            "summary": "State media outlets showing coordinated increase in sovereignty-focused messaging around Taiwan. Naval activity remains within normal parameters but messaging coordination suggests deliberate campaign.",
            "evidence_chain": [
                "Xinhua, Global Times, and People's Daily published synchronized sovereignty articles within 6-hour window",
                "Key phrases 'sovereignty non-negotiable' and 'territorial integrity' appearing across outlets",
                "Naval vessels departing Ningbo port per OSINT reporting",
                "Military convoy activity near Xiamen slightly elevated"
            ],
            "timeline": "Narrative shift detected at T+18h. Naval movements observed T+20h to T+28h.",
            "information_gaps": [
                "Intent behind messaging campaign unclear",
                "Scale of naval deployment not yet confirmed",
                "No official PLA announcements regarding exercises"
            ],
            "collection_priorities": [
                "Monitor for military press releases",
                "Track naval vessel movements via AIS",
                "Assess messaging volume over next 24 hours"
            ],
            "key_developments": [
                "Sovereignty messaging coordinated across state outlets",
                "Naval departures from eastern ports",
                "No official military announcements yet"
            ],
            "narrative_event_ids": [1, 2, 3],
            "movement_event_ids": [1, 2, 3, 4, 5],
            "generated_at": (FIXTURE_BASE_TIME + timedelta(hours=29)).isoformat(),
        }
    })

    # Beat 4: Second brief at AMBER escalation (T+48h)
    briefs.append({
        "hours_offset": 48,
        "data": {
            "title": "Taiwan Strait Escalation - AMBER Alert",
            "threat_level": "AMBER",
            "confidence": 80,
            "summary": "Significant escalation detected. State media narrative coordination now synchronized with concrete military movements including amphibious ship loading and live-fire exercise announcements. Pattern indicates deliberate pre-conflict signaling.",
            "evidence_chain": [
                "All four major state outlets using identical 'live-fire exercises' and 'combat readiness' framing",
                "PLA Eastern Theater Command announced large-scale exercises with live-fire zones",
                "Amphibious assault ships loading at Zhanjiang (confirmed via satellite imagery per OSINT)",
                "NOTAM issued for restricted airspace over Taiwan Strait",
                "Combat aircraft sortie rates increased 300% according to OSINT sources",
                "Type 052D destroyer concentration south of Wenzhou"
            ],
            "timeline": "Narrative coordination strengthened T+28h to T+42h. Military movements confirmed T+42h to T+48h. Official exercise announcement at T+46h.",
            "information_gaps": [
                "Exercise duration and end date not specified",
                "Number of vessels involved in naval component unclear",
                "No indication of ground force deployments yet"
            ],
            "collection_priorities": [
                "Track amphibious vessel movements closely",
                "Monitor for civilian evacuation notices",
                "Watch for Rocket Force deployments",
                "Assess international diplomatic responses"
            ],
            "key_developments": [
                "Live-fire exercise officially announced",
                "Amphibious ships loading confirmed",
                "Six no-sail zones declared surrounding Taiwan",
                "Narrative coordination at 75/100"
            ],
            "narrative_event_ids": [1, 2, 3, 4, 5, 6, 7],
            "movement_event_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "generated_at": (FIXTURE_BASE_TIME + timedelta(hours=48)).isoformat(),
        }
    })

    # Beat 5: Third brief at RED escalation (T+68h)
    briefs.append({
        "hours_offset": 68,
        "data": {
            "title": "Taiwan Strait Escalation - RED ALERT",
            "threat_level": "RED",
            "confidence": 92,
            "summary": "Imminent threat assessment. Peak narrative coordination using 'decisive action' and 'seize control by force' framing synchronized with naval blockade formation and amphibious assault wave launch. All indicators suggest transition from exercise to potential combat operations within hours.",
            "evidence_chain": [
                "Maximum state media coordination (93/100) with imminent action framing across all outlets",
                "Naval blockade formation visible with at least 20 major combatants confirmed via AIS",
                "Rocket Force TELs observed moving to coastal launch positions",
                "Amphibious assault wave launched - landing craft confirmed in water per OSINT",
                "All civilian shipping diverted from strait",
                "Electronic warfare jamming detected across multiple frequencies",
                "Six no-sail zones now fully enforced with military-only traffic"
            ],
            "timeline": "Threat level RED reached at T+70h. Amphibious wave launched T+70h. Blockade formation established T+62h to T+68h. Peak narrative coordination T+68h.",
            "information_gaps": [
                "Actual beach landing locations not confirmed",
                "Taiwanese defensive response posture unknown",
                "International military response pending"
            ],
            "collection_priorities": [
                "CRITICAL: Monitor for beach assault indicators",
                "CRITICAL: Track missile launch preparations",
                "URGENT: Assess air superiority status",
                "URGENT: Monitor for cyber attacks on critical infrastructure"
            ],
            "key_developments": [
                "Amphibious assault operations initiated",
                "Naval blockade fully established",
                "State media using imminent action framing",
                "Threat score 82/100 with 92% confidence"
            ],
            "narrative_event_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "movement_event_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "generated_at": (FIXTURE_BASE_TIME + timedelta(hours=68)).isoformat(),
        }
    })

    return briefs


def generate_fixture() -> dict:
    """Generate complete demo fixture with all table types.

    Returns:
        Complete fixture dict ready for JSON serialization
    """
    print("Generating demo fixture...")
    print()

    # Generate raw intelligence data (Phase 1)
    print("Generating Phase 1 raw intelligence...")
    articles = generate_demo_articles(FIXTURE_BASE_TIME, count=60)
    posts = generate_demo_posts(FIXTURE_BASE_TIME, count=120)
    positions = generate_demo_positions(FIXTURE_BASE_TIME, count=200)
    print(f"  Articles: {len(articles)}")
    print(f"  Social posts: {len(posts)}")
    print(f"  Vessel positions: {len(positions)}")
    print()

    # Generate processed intelligence (Phase 2)
    print("Generating Phase 2 processed intelligence...")
    narrative_events = generate_narrative_events()
    movement_events = generate_movement_events()
    print(f"  Narrative events: {len(narrative_events)}")
    print(f"  Movement events: {len(movement_events)}")
    print()

    # Generate correlation outputs (Phase 3)
    print("Generating Phase 3 correlation outputs...")
    alerts = generate_alerts()
    briefs = generate_briefs()
    print(f"  Alerts: {len(alerts)}")
    print(f"  Briefs: {len(briefs)}")
    print()

    # Convert to fixture format with demo timing
    records = []

    # Add articles
    for article in articles:
        hours_offset = (article["published_at"] - FIXTURE_BASE_TIME).total_seconds() / 3600
        demo_offset = add_jitter(hours_to_demo_offset(hours_offset))

        records.append({
            "_table": "articles",
            "_demo_offset_seconds": round(demo_offset, 3),
            "_demo_action": "insert",
            "data": convert_datetimes_to_iso(article)
        })

    # Add social posts
    for post in posts:
        hours_offset = (post["timestamp"] - FIXTURE_BASE_TIME).total_seconds() / 3600
        demo_offset = add_jitter(hours_to_demo_offset(hours_offset))

        records.append({
            "_table": "social_posts",
            "_demo_offset_seconds": round(demo_offset, 3),
            "_demo_action": "insert",
            "data": convert_datetimes_to_iso(post)
        })

    # Add vessel positions
    for position in positions:
        hours_offset = (position["timestamp"] - FIXTURE_BASE_TIME).total_seconds() / 3600
        demo_offset = add_jitter(hours_to_demo_offset(hours_offset))

        records.append({
            "_table": "vessel_positions",
            "_demo_offset_seconds": round(demo_offset, 3),
            "_demo_action": "insert",
            "data": convert_datetimes_to_iso(position)
        })

    # Add narrative events
    for event in narrative_events:
        demo_offset = add_jitter(hours_to_demo_offset(event["hours_offset"]))

        records.append({
            "_table": "narrative_events",
            "_demo_offset_seconds": round(demo_offset, 3),
            "_demo_action": "insert",
            "data": event["data"]
        })

    # Add movement events
    for event in movement_events:
        demo_offset = add_jitter(hours_to_demo_offset(event["hours_offset"]))

        records.append({
            "_table": "movement_events",
            "_demo_offset_seconds": round(demo_offset, 3),
            "_demo_action": "insert",
            "data": event["data"]
        })

    # Add alerts
    for alert in alerts:
        demo_offset = add_jitter(hours_to_demo_offset(alert["hours_offset"]))

        records.append({
            "_table": "alerts",
            "_demo_offset_seconds": round(demo_offset, 3),
            "_demo_action": alert["action"],
            "data": alert["data"]
        })

    # Add briefs
    for brief in briefs:
        demo_offset = add_jitter(hours_to_demo_offset(brief["hours_offset"]))

        records.append({
            "_table": "briefs",
            "_demo_offset_seconds": round(demo_offset, 3),
            "_demo_action": "insert",
            "data": brief["data"]
        })

    # Sort by demo offset for sequential playback
    records.sort(key=lambda r: r["_demo_offset_seconds"])

    # Count records by table
    record_counts = {}
    for record in records:
        table = record["_table"]
        record_counts[table] = record_counts.get(table, 0) + 1

    # Build fixture
    fixture = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "base_time": FIXTURE_BASE_TIME.isoformat(),
            "simulated_hours": SIMULATED_HOURS,
            "normal_duration_seconds": NORMAL_DURATION_SECONDS,
            "total_records": len(records),
            "record_counts": record_counts
        },
        "records": records
    }

    print("Fixture generation complete!")
    print()
    print("Summary:")
    print(f"  Total records: {len(records)}")
    print(f"  Time range: 0 to {records[-1]['_demo_offset_seconds']:.1f} seconds")
    print(f"  Tables: {', '.join(sorted(record_counts.keys()))}")

    return fixture


def validate_fixture(fixture: dict) -> tuple[bool, list[str]]:
    """Validate fixture data structure and content.

    Args:
        fixture: Complete fixture dict

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    print("Validating fixture...")
    print()

    # Check metadata
    if "metadata" not in fixture:
        errors.append("Missing 'metadata' key")
        return False, errors

    metadata = fixture["metadata"]
    required_meta = ["generated_at", "base_time", "simulated_hours", "normal_duration_seconds", "total_records", "record_counts"]
    for key in required_meta:
        if key not in metadata:
            errors.append(f"Missing metadata key: {key}")

    # Check records
    if "records" not in fixture:
        errors.append("Missing 'records' key")
        return False, errors

    records = fixture["records"]

    # Validate record structure
    print("Validating record structure...")
    expected_tables = {"articles", "social_posts", "vessel_positions", "narrative_events", "movement_events", "alerts", "briefs"}
    found_tables = set()

    for idx, record in enumerate(records):
        # Check required fields
        for key in ["_table", "_demo_offset_seconds", "_demo_action", "data"]:
            if key not in record:
                errors.append(f"Record {idx}: Missing key '{key}'")

        # Collect table types
        if "_table" in record:
            found_tables.add(record["_table"])

    # Check all 7 tables present
    missing_tables = expected_tables - found_tables
    if missing_tables:
        errors.append(f"Missing table types: {missing_tables}")

    print(f"  Tables found: {len(found_tables)}/7")
    for table in sorted(found_tables):
        count = sum(1 for r in records if r.get("_table") == table)
        print(f"    {table}: {count} records")
    print()

    # Validate required fields per table type
    print("Validating required fields per table...")
    required_fields = {
        "articles": ["url", "title", "domain", "published_at", "tone_score"],
        "social_posts": ["telegram_id", "channel", "text", "timestamp", "views"],
        "vessel_positions": ["mmsi", "ship_name", "latitude", "longitude", "speed", "course", "timestamp"],
        "narrative_events": ["event_type", "summary", "confidence", "source_ids", "coordination_score", "outlet_count", "synchronized_phrases", "geographic_focus", "themes", "article_ids", "created_at"],
        "movement_events": ["event_type", "description", "location_lat", "location_lon", "confidence", "category", "location_name", "source_post_ids", "created_at"],
        "alerts": ["region", "threat_level", "threat_score", "confidence", "sub_scores", "correlation_metadata"],
        "briefs": ["threat_level", "confidence", "summary", "evidence_chain", "timeline", "collection_priorities", "narrative_event_ids", "movement_event_ids"]
    }

    field_errors_found = False
    for table, fields in required_fields.items():
        table_records = [r for r in records if r.get("_table") == table]
        if table_records:
            sample = table_records[0]["data"]
            missing_fields = [f for f in fields if f not in sample]
            if missing_fields:
                errors.append(f"{table}: Missing required fields: {missing_fields}")
                field_errors_found = True

    if not field_errors_found:
        print(f"  ✓ All required fields present across table types")
    print()

    # Validate sorting
    print("Validating timing...")
    offsets = [r["_demo_offset_seconds"] for r in records if "_demo_offset_seconds" in r]
    if offsets != sorted(offsets):
        errors.append("Records not sorted by _demo_offset_seconds")
    else:
        print(f"  ✓ Records sorted by offset")

    # Check offset range
    if offsets:
        min_offset = min(offsets)
        max_offset = max(offsets)
        if min_offset < 0:
            errors.append(f"Negative offset found: {min_offset}")
        if max_offset > NORMAL_DURATION_SECONDS + 5:  # Allow small buffer
            errors.append(f"Offset exceeds duration: {max_offset} > {NORMAL_DURATION_SECONDS}")
        else:
            print(f"  ✓ Offset range: {min_offset:.1f} to {max_offset:.1f} seconds")

    # Check for exact duplicate offsets (jitter should prevent this)
    offset_counts = {}
    for offset in offsets:
        offset_counts[offset] = offset_counts.get(offset, 0) + 1

    duplicates = [off for off, cnt in offset_counts.items() if cnt > 1]
    if duplicates:
        errors.append(f"Found {len(duplicates)} duplicate offsets (jitter failed)")
    else:
        print(f"  ✓ No duplicate offsets (jitter applied)")
    print()

    # Validate 5-beat arc
    print("Validating 5-beat escalation arc...")
    alert_records = [r for r in records if r.get("_table") == "alerts"]
    if len(alert_records) == 5:
        print(f"  ✓ 5 alert states present")

        # Check escalation pattern
        expected_levels = ["GREEN", "GREEN", "AMBER", "AMBER", "RED"]
        actual_levels = [r["data"].get("threat_level") for r in alert_records]

        if actual_levels == expected_levels:
            print(f"  ✓ Alert escalation: GREEN → GREEN → AMBER → AMBER → RED")
        else:
            errors.append(f"Alert escalation incorrect: {actual_levels} != {expected_levels}")

        # Check threat scores are monotonic
        scores = [r["data"].get("threat_score", 0) for r in alert_records]
        if scores == sorted(scores):
            print(f"  ✓ Threat scores monotonically increasing: {scores}")
        else:
            errors.append(f"Threat scores not monotonic: {scores}")
    else:
        errors.append(f"Expected 5 alerts, found {len(alert_records)}")
    print()

    # Validate alert actions
    print("Validating alert actions...")
    if alert_records:
        if alert_records[0].get("_demo_action") == "insert":
            print(f"  ✓ First alert is INSERT")
        else:
            errors.append("First alert should be INSERT action")

        update_count = sum(1 for r in alert_records[1:] if r.get("_demo_action") == "update")
        if update_count == len(alert_records) - 1:
            print(f"  ✓ Subsequent {update_count} alerts are UPDATE")
        else:
            errors.append(f"Expected {len(alert_records) - 1} UPDATE alerts, found {update_count}")
    print()

    # Summary
    if errors:
        print(f"❌ Validation FAILED with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
        return False, errors
    else:
        print("✅ Validation PASSED - fixture is valid")
        return True, []


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate or validate demo fixture")
    parser.add_argument("--validate", action="store_true", help="Validate existing fixture instead of generating")
    args = parser.parse_args()

    fixture_path = Path(__file__).parent / "demo_fixture.json"

    if args.validate:
        # Validate mode
        print("=" * 70)
        print("Demo Fixture Validation")
        print("=" * 70)
        print()

        if not fixture_path.exists():
            print(f"❌ Fixture file not found: {fixture_path}")
            print()
            print("Run without --validate to generate fixture first.")
            return

        with open(fixture_path) as f:
            fixture = json.load(f)

        is_valid, errors = validate_fixture(fixture)

        if not is_valid:
            print()
            print("Fix errors and run validation again.")
            exit(1)
    else:
        # Generate mode
        print("=" * 70)
        print("Dragon Watch Demo Fixture Generator")
        print("=" * 70)
        print()

        fixture = generate_fixture()

        print()
        print(f"Writing fixture to {fixture_path}...")
        with open(fixture_path, "w") as f:
            json.dump(fixture, f, indent=2)

        print()
        print("=" * 70)
        print("Fixture generation complete!")
        print("=" * 70)
        print()
        print(f"Output: {fixture_path}")
        print(f"Size: {fixture_path.stat().st_size / 1024:.1f} KB")
        print()
        print("Run with --validate flag to validate fixture structure:")
        print(f"  python {Path(__file__).name} --validate")


if __name__ == "__main__":
    main()

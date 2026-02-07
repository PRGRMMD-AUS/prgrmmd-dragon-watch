"""Verification script for Dragon Watch Phase 3 requirements.

Tests all CORR-01 through CORR-04 requirements programmatically using
pure logic checks (no Supabase connection needed).

Run directly: python scripts/verify_phase_3.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta, timezone
from typing import Dict, Any

# Import Phase 3 modules to verify
from src.processors.correlate_events import (
    match_events_by_time_window,
    calculate_composite_score,
)
from src.models.threat_levels import (
    ThreatLevel,
    determine_threat_level,
    calculate_confidence,
    GREEN_THRESHOLD,
    RED_THRESHOLD,
)
from src.models.correlation import CorrelationResult, SubScores
from src.utils.geo_utils import (
    is_in_taiwan_strait,
    check_narrative_geo_match,
    normalize_min_max,
)


def check_corr_01_time_window() -> bool:
    """CORR-01: Verify time-window matching logic.

    Tests that events within 72h window are matched and events outside
    the window are not matched.

    Returns:
        True if all time-window tests pass
    """
    print("\nCORR-01: Time-window matching")
    print("-" * 50)

    base_time = datetime(2026, 2, 5, 12, 0, 0, tzinfo=timezone.utc)

    # Mock narrative event
    narrative_events = [
        {
            "id": 1,
            "created_at": base_time.isoformat(),
            "coordination_score": 50,
            "outlet_count": 3,
            "synchronized_phrases": ["phrase1", "phrase2"],
            "geographic_focus": "Taiwan Strait",
        }
    ]

    # Mock movement events at different time offsets
    movement_events = [
        # Within window (36h before)
        {
            "id": 101,
            "created_at": (base_time - timedelta(hours=36)).isoformat(),
            "category": "naval",
            "location_lat": 24.5,
            "location_lon": 120.0,
        },
        # Within window (36h after)
        {
            "id": 102,
            "created_at": (base_time + timedelta(hours=36)).isoformat(),
            "category": "convoy",
            "location_lat": 24.8,
            "location_lon": 119.5,
        },
        # Outside window (80h after - beyond 72h)
        {
            "id": 103,
            "created_at": (base_time + timedelta(hours=80)).isoformat(),
            "category": "naval",
            "location_lat": 25.0,
            "location_lon": 120.5,
        },
    ]

    # Test matching
    matches = match_events_by_time_window(narrative_events, movement_events, window_hours=72)

    # Verify results
    if not matches:
        print("  FAIL: No matches found")
        return False

    matched_movement_ids = [m["id"] for m in matches[0]["movements"]]

    # Should match 101 and 102 (within 72h), not 103 (outside 72h)
    if 101 not in matched_movement_ids:
        print("  FAIL: Event 36h before not matched")
        return False

    if 102 not in matched_movement_ids:
        print("  FAIL: Event 36h after not matched")
        return False

    if 103 in matched_movement_ids:
        print("  FAIL: Event 80h after incorrectly matched (should be outside window)")
        return False

    print("  PASS: Events within 72h window matched correctly")
    print(f"  Matched movement IDs: {matched_movement_ids}")
    return True


def check_corr_02_geographic_proximity() -> bool:
    """CORR-02: Verify geographic proximity scoring.

    Tests that points inside Taiwan Strait bounding box return True
    and points outside return False. Tests narrative focus matching.

    Returns:
        True if all geographic tests pass
    """
    print("\nCORR-02: Geographic proximity scoring")
    print("-" * 50)

    # Test 1: Point inside strait
    inside_point = (24.5, 120.0)  # Center of strait
    if not is_in_taiwan_strait(*inside_point):
        print(f"  FAIL: Point {inside_point} should be inside Taiwan Strait")
        return False

    print(f"  PASS: Point {inside_point} correctly identified as inside strait")

    # Test 2: Point outside strait
    outside_point = (10.0, 100.0)  # Far south and west
    if is_in_taiwan_strait(*outside_point):
        print(f"  FAIL: Point {outside_point} should be outside Taiwan Strait")
        return False

    print(f"  PASS: Point {outside_point} correctly identified as outside strait")

    # Test 3: Narrative focus matching - positive
    if not check_narrative_geo_match("Taiwan Strait"):
        print("  FAIL: 'Taiwan Strait' should match geographic focus")
        return False

    print("  PASS: 'Taiwan Strait' matched as valid geographic focus")

    # Test 4: Narrative focus matching - negative
    if check_narrative_geo_match("South China Sea"):
        print("  FAIL: 'South China Sea' should not match (wrong region)")
        return False

    print("  PASS: 'South China Sea' correctly rejected (wrong region)")

    # Test 5: Narrative focus matching - case insensitive
    if not check_narrative_geo_match("TAIWAN STRAIT"):
        print("  FAIL: Case-insensitive matching failed")
        return False

    print("  PASS: Case-insensitive matching works")

    # Test 6: Null focus
    if check_narrative_geo_match(None):
        print("  FAIL: None focus should return False")
        return False

    print("  PASS: None focus correctly handled")

    return True


def check_corr_03_threat_level() -> bool:
    """CORR-03: Verify threat level calculation.

    Tests that composite scores map to correct threat levels and that
    sub-scores are calculated properly.

    Returns:
        True if all threat level tests pass
    """
    print("\nCORR-03: Threat level calculation")
    print("-" * 50)

    # Test 1: Score < 30 should be GREEN
    score_15 = 15
    level_15 = determine_threat_level(score_15)
    if level_15 != ThreatLevel.GREEN:
        print(f"  FAIL: Score {score_15} should be GREEN, got {level_15.name}")
        return False

    print(f"  PASS: Score {score_15} -> GREEN (< {GREEN_THRESHOLD})")

    # Test 2: Score 30-69 should be AMBER
    score_50 = 50
    level_50 = determine_threat_level(score_50)
    if level_50 != ThreatLevel.AMBER:
        print(f"  FAIL: Score {score_50} should be AMBER, got {level_50.name}")
        return False

    print(f"  PASS: Score {score_50} -> AMBER ({GREEN_THRESHOLD}-{RED_THRESHOLD-1})")

    # Test 3: Score >= 70 should be RED
    score_85 = 85
    level_85 = determine_threat_level(score_85)
    if level_85 != ThreatLevel.RED:
        print(f"  FAIL: Score {score_85} should be RED, got {level_85.name}")
        return False

    print(f"  PASS: Score {score_85} -> RED (>= {RED_THRESHOLD})")

    # Test 4: Composite score calculation
    mock_narrative = {
        "outlet_count": 3,
        "synchronized_phrases": ["phrase1", "phrase2", "phrase3"],
        "geographic_focus": "Taiwan Strait",
    }
    mock_movements = [{"id": 1}, {"id": 2}]  # 2 movements
    geo_match = True

    composite, sub_scores = calculate_composite_score(mock_narrative, mock_movements, geo_match)

    # Verify composite is in valid range
    if not (0 <= composite <= 100):
        print(f"  FAIL: Composite score {composite} outside 0-100 range")
        return False

    print(f"  PASS: Composite score {composite:.2f} in valid range [0-100]")

    # Verify sub-scores are non-negative
    if sub_scores.outlet_score < 0:
        print(f"  FAIL: Outlet score {sub_scores.outlet_score} is negative")
        return False

    if sub_scores.phrase_score < 0:
        print(f"  FAIL: Phrase score {sub_scores.phrase_score} is negative")
        return False

    if sub_scores.volume_score < 0:
        print(f"  FAIL: Volume score {sub_scores.volume_score} is negative")
        return False

    if sub_scores.geo_score < 0:
        print(f"  FAIL: Geo score {sub_scores.geo_score} is negative")
        return False

    print(f"  PASS: All sub-scores are non-negative")
    print(f"    Outlet: {sub_scores.outlet_score:.1f}")
    print(f"    Phrase: {sub_scores.phrase_score:.1f}")
    print(f"    Volume: {sub_scores.volume_score:.1f}")
    print(f"    Geo: {sub_scores.geo_score:.1f}")

    return True


def check_corr_04_evidence_chain() -> bool:
    """CORR-04: Verify evidence chain structure.

    Tests that CorrelationResult contains proper evidence linking
    back to specific event IDs.

    Returns:
        True if evidence chain tests pass
    """
    print("\nCORR-04: Evidence chain")
    print("-" * 50)

    # Create a correlation result with evidence
    correlation = CorrelationResult(
        narrative_event_ids=[1, 2],
        movement_event_ids=[101, 102, 103],
        composite_score=65.5,
        sub_scores=SubScores(
            outlet_score=75.0,
            phrase_score=60.0,
            volume_score=50.0,
            geo_score=80.0,
        ),
        threat_level="AMBER",
        confidence=85,
        geo_match=True,
        region="Taiwan Strait",
        evidence_summary="3 state media outlets coordinating on Taiwan Strait themes with 3 movement reports",
        detected_at=datetime.now(timezone.utc),
    )

    # Verify narrative event IDs exist and are non-empty
    if not correlation.narrative_event_ids:
        print("  FAIL: Narrative event IDs list is empty")
        return False

    print(f"  PASS: Narrative event IDs present: {correlation.narrative_event_ids}")

    # Verify movement event IDs exist and are non-empty
    if not correlation.movement_event_ids:
        print("  FAIL: Movement event IDs list is empty")
        return False

    print(f"  PASS: Movement event IDs present: {correlation.movement_event_ids}")

    # Verify evidence summary is non-empty
    if not correlation.evidence_summary or not correlation.evidence_summary.strip():
        print("  FAIL: Evidence summary is empty")
        return False

    print(f"  PASS: Evidence summary present")
    print(f"    '{correlation.evidence_summary}'")

    # Verify all required fields are present
    required_fields = [
        "composite_score",
        "sub_scores",
        "threat_level",
        "confidence",
        "region",
        "detected_at",
    ]

    for field in required_fields:
        if not hasattr(correlation, field):
            print(f"  FAIL: Missing required field '{field}'")
            return False

    print(f"  PASS: All required fields present")

    return True


def check_monotonic_escalation() -> bool:
    """Verify monotonic escalation enforcement.

    Tests that threat levels can only escalate (GREEN->AMBER->RED)
    and cannot de-escalate.

    Returns:
        True if monotonic escalation tests pass
    """
    print("\nMonotonic escalation enforcement")
    print("-" * 50)

    # Test 1: GREEN can transition to AMBER
    if not ThreatLevel.GREEN.can_transition_to(ThreatLevel.AMBER):
        print("  FAIL: GREEN should be able to transition to AMBER")
        return False

    print("  PASS: GREEN -> AMBER allowed")

    # Test 2: AMBER can transition to RED
    if not ThreatLevel.AMBER.can_transition_to(ThreatLevel.RED):
        print("  FAIL: AMBER should be able to transition to RED")
        return False

    print("  PASS: AMBER -> RED allowed")

    # Test 3: RED cannot transition to AMBER
    if ThreatLevel.RED.can_transition_to(ThreatLevel.AMBER):
        print("  FAIL: RED should NOT be able to transition to AMBER (de-escalation)")
        return False

    print("  PASS: RED -> AMBER blocked (de-escalation prevented)")

    # Test 4: RED cannot transition to GREEN
    if ThreatLevel.RED.can_transition_to(ThreatLevel.GREEN):
        print("  FAIL: RED should NOT be able to transition to GREEN (de-escalation)")
        return False

    print("  PASS: RED -> GREEN blocked (de-escalation prevented)")

    # Test 5: Same level transitions allowed (updates without escalation)
    if not ThreatLevel.AMBER.can_transition_to(ThreatLevel.AMBER):
        print("  FAIL: Same-level transitions should be allowed")
        return False

    print("  PASS: AMBER -> AMBER allowed (same level update)")

    return True


def check_confidence_scoring() -> bool:
    """Verify confidence score calculation.

    Tests that confidence scores are in valid range and that
    higher event counts produce higher confidence.

    Returns:
        True if confidence scoring tests pass
    """
    print("\nConfidence scoring")
    print("-" * 50)

    # Test 1: Basic confidence calculation
    conf_1 = calculate_confidence(narrative_count=1, movement_count=5, geo_match=True)

    if not isinstance(conf_1, int):
        print(f"  FAIL: Confidence should be int, got {type(conf_1)}")
        return False

    if not (0 <= conf_1 <= 95):
        print(f"  FAIL: Confidence {conf_1} outside valid range [0-95]")
        return False

    print(f"  PASS: Confidence {conf_1} in valid range [0-95]")

    # Test 2: Higher event counts produce higher confidence
    conf_low = calculate_confidence(narrative_count=1, movement_count=2, geo_match=False)
    conf_high = calculate_confidence(narrative_count=3, movement_count=10, geo_match=True)

    if conf_high <= conf_low:
        print(f"  FAIL: Higher event counts should produce higher confidence")
        print(f"    Low events: {conf_low}, High events: {conf_high}")
        return False

    print(f"  PASS: Higher event counts produce higher confidence")
    print(f"    Low events (1 narr, 2 move, no geo): {conf_low}")
    print(f"    High events (3 narr, 10 move, geo match): {conf_high}")

    # Test 3: Never 100% confidence (max 95)
    conf_max = calculate_confidence(narrative_count=100, movement_count=100, geo_match=True)

    if conf_max > 95:
        print(f"  FAIL: Confidence should be capped at 95, got {conf_max}")
        return False

    print(f"  PASS: Confidence capped at 95 (got {conf_max} for max inputs)")

    return True


def check_module_imports() -> bool:
    """Verify all Phase 3 modules import cleanly.

    Returns:
        True if all imports successful
    """
    print("\nModule imports")
    print("-" * 50)

    try:
        from src.processors import correlate_events
        print("  PASS: correlate_events imports")

        from src.models import threat_levels
        print("  PASS: threat_levels imports")

        from src.models import correlation
        print("  PASS: correlation imports")

        from src.utils import geo_utils
        print("  PASS: geo_utils imports")

        return True

    except ImportError as e:
        print(f"  FAIL: Import error - {e}")
        return False


def main() -> None:
    """Run all Phase 3 verification checks."""
    print("=" * 70)
    print("Dragon Watch Phase 3 Verification")
    print("=" * 70)

    checks = [
        ("CORR-01", check_corr_01_time_window),
        ("CORR-02", check_corr_02_geographic_proximity),
        ("CORR-03", check_corr_03_threat_level),
        ("CORR-04", check_corr_04_evidence_chain),
        ("Monotonic Escalation", check_monotonic_escalation),
        ("Confidence Scoring", check_confidence_scoring),
        ("Module Imports", check_module_imports),
    ]

    results = []
    for name, check_func in checks:
        try:
            passed = check_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n  ERROR: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    print()

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {name}: {status}")

    print()
    print(f"Total: {passed_count}/{total_count} checks passed")
    print()

    if passed_count == total_count:
        print("Phase 3 verification: SUCCESS")
        print("All requirements validated.")
    else:
        print("Phase 3 verification: FAILED")
        print(f"{total_count - passed_count} check(s) failed.")

    print("=" * 70)


if __name__ == "__main__":
    main()

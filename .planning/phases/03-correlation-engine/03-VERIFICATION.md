---
phase: 03-correlation-engine
verified: 2026-02-07T21:30:00Z
status: passed
score: 4/4 must-haves verified
---

# Phase 3: Correlation Engine Verification Report

**Phase Goal:** Two independent intelligence streams converge to produce threat-level alerts
**Verified:** 2026-02-07T21:30:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Time-window matching detects narrative coordination spike within 72 hours of movement cluster and triggers correlation | ✓ VERIFIED | `match_events_by_time_window()` correctly matches events within 72h window (101 at -36h, 102 at +36h matched; 103 at +80h excluded) |
| 2 | Geographic proximity scoring calculates when narrative geographic focus matches movement cluster region | ✓ VERIFIED | `check_narrative_geo_match()` identifies "Taiwan Strait" keywords; `is_in_taiwan_strait()` performs Shapely containment check for coordinates (24.5, 120.0) → True, (10.0, 100.0) → False |
| 3 | Threat level calculation produces GREEN (<30) / AMBER (30-70) / RED (>70) scores based on outlet count, phrase novelty, post volume, and geographic proximity | ✓ VERIFIED | `determine_threat_level()` maps scores correctly (25→GREEN, 50→AMBER, 85→RED); `calculate_composite_score()` produces weighted composite from 4 sub-factors with min-max normalization |
| 4 | Each alert links to specific articles and posts that triggered it, creating complete evidence chains | ✓ VERIFIED | `CorrelationResult` model contains `narrative_event_ids` and `movement_event_ids` lists; `upsert_alert()` writes `correlation_metadata` JSONB with evidence_summary and detection_history |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/models/threat_levels.py` | ThreatLevel enum with monotonic escalation | ✓ VERIFIED | 87 lines, exports ThreatLevel/determine_threat_level/calculate_confidence, monotonic enforcement works (RED→GREEN blocked), thresholds GREEN<30/RED<70 correct |
| `src/models/correlation.py` | Pydantic models for correlation results | ✓ VERIFIED | 69 lines, exports CorrelationResult/SubScores/AlertUpsertData, validates composite scores 0-100, JSONB-ready |
| `src/utils/geo_utils.py` | Geographic containment utilities | ✓ VERIFIED | 82 lines, exports is_in_taiwan_strait/check_narrative_geo_match/normalize_min_max/TAIWAN_STRAIT_BBOX, Shapely Point/box containment works |
| `src/processors/correlate_events.py` | Core correlation engine | ✓ VERIFIED | 443 lines (exceeds 150 min), exports correlate_events_batch, implements 7 functions (fetch, match, score, upsert), no TODO/FIXME/placeholder patterns |
| `src/main.py` | FastAPI endpoints for correlation | ✓ VERIFIED | POST /api/correlate and GET /api/alerts/current endpoints exist and import correlate_events_batch |
| `scripts/verify_phase_3.py` | Verification script | ✓ VERIFIED | 519 lines (exceeds 80 min), all 7 checks pass (CORR-01 through CORR-04 + monotonic + confidence + imports) |
| `scripts/run_correlation_demo.py` | Demo runner | ✓ VERIFIED | 322 lines (exceeds 50 min), handles synthetic fallback, calls correlate_events_batch(), reads back alerts |
| `requirements.txt` | Shapely dependency | ✓ VERIFIED | Contains "shapely>=2.0,<3.0" entry |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| correlate_events.py | database.client | async Supabase client | ✓ WIRED | Imports `get_supabase`, uses `await client.table()` for narrative_events, movement_events, alerts |
| correlate_events.py | threat_levels.py | ThreatLevel enum | ✓ WIRED | Imports ThreatLevel/determine_threat_level/calculate_confidence, uses in scoring and monotonic checks |
| correlate_events.py | geo_utils.py | Geographic containment | ✓ WIRED | Imports is_in_taiwan_strait/check_narrative_geo_match/normalize_min_max, uses in geo scoring |
| correlate_events.py | correlation.py | Pydantic models | ✓ WIRED | Imports CorrelationResult/SubScores/AlertUpsertData, creates instances for upsert |
| main.py | correlate_events.py | Pipeline trigger | ✓ WIRED | Imports correlate_events_batch, calls in POST /api/correlate endpoint |
| run_correlation_demo.py | correlate_events.py | Demo execution | ✓ WIRED | Imports correlate_events_batch, calls in main() after event setup |
| verify_phase_3.py | All Phase 3 modules | Logic testing | ✓ WIRED | Imports match_events_by_time_window, calculate_composite_score, all models, all utils |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| CORR-01: Time-window matching | ✓ SATISFIED | None — match_events_by_time_window() verified with 72h window |
| CORR-02: Geographic proximity scoring | ✓ SATISFIED | None — both narrative focus and movement coordinate checks verified |
| CORR-03: Threat level calculation | ✓ SATISFIED | None — weighted composite scoring with GREEN/AMBER/RED thresholds verified |
| CORR-04: Evidence chain | ✓ SATISFIED | None — correlation_metadata contains event IDs and evidence_summary |

### Anti-Patterns Found

**None.** No TODO/FIXME/placeholder comments, no empty returns, no stub patterns detected.

All files contain substantive implementations:
- correlate_events.py: 443 lines with complete pipeline
- threat_levels.py: 87 lines with full state machine
- correlation.py: 69 lines with validated Pydantic models
- geo_utils.py: 82 lines with Shapely containment logic

### Human Verification Required

None. All success criteria are programmatically verifiable and have been verified.

The verification script (`scripts/verify_phase_3.py`) provides automated testing of all Phase 3 requirements without human intervention. It passed 7/7 checks.

---

## Detailed Verification Evidence

### Truth 1: Time-Window Matching

**Verification method:** Direct function call with mock events at known time offsets

**Test case:**
- Narrative event at T+0
- Movement events at T-36h (within), T+36h (within), T+80h (outside)
- Window: 72 hours

**Result:**
```python
matched_ids = [101, 102]  # 103 excluded (80h > 72h window)
```

**Code location:** `src/processors/correlate_events.py:87-131` (match_events_by_time_window)

**Evidence:** Function correctly uses `abs((narr_ts - move_ts).total_seconds() / 3600) <= window_hours` for temporal proximity check. Handles both 'Z' and '+00:00' timestamp suffixes.

### Truth 2: Geographic Proximity Scoring

**Verification method:** Point containment tests and string matching tests

**Test cases:**
1. Point (24.5, 120.0) — center of Taiwan Strait → `is_in_taiwan_strait() = True`
2. Point (10.0, 100.0) — far south/west → `is_in_taiwan_strait() = False`
3. Narrative focus "Taiwan Strait" → `check_narrative_geo_match() = True`
4. Narrative focus "South China Sea" → `check_narrative_geo_match() = False`

**Result:** All 4 tests pass. Shapely box containment and keyword matching work correctly.

**Code location:**
- `src/utils/geo_utils.py:20-40` (is_in_taiwan_strait)
- `src/utils/geo_utils.py:43-60` (check_narrative_geo_match)

**Evidence:** TAIWAN_STRAIT_BBOX coordinates (118-122E, 23-26N) match demo data from load_demo_data.py. Shapely `Point(lon, lat)` and `box().contains()` used correctly.

### Truth 3: Threat Level Calculation

**Verification method:** Score-to-level mapping tests and composite scoring tests

**Test cases:**
1. Score 15 → GREEN (< 30 threshold)
2. Score 50 → AMBER (30-69 range)
3. Score 85 → RED (≥ 70 threshold)
4. Mock correlation (3 outlets, 3 phrases, 2 movements, geo_match=True) → composite 53.30

**Result:** All mappings correct. Composite scoring produces expected range (40-80 for test inputs).

**Code location:**
- `src/models/threat_levels.py:39-53` (determine_threat_level)
- `src/processors/correlate_events.py:134-176` (calculate_composite_score)

**Evidence:** 
- Thresholds defined as module constants (GREEN_THRESHOLD=30, RED_THRESHOLD=70)
- Composite = weighted sum of 4 normalized sub-factors (outlet 30%, phrase 25%, volume 20%, geo 25%)
- Sub-scores breakdown visible in test output: outlet=66.7, phrase=30.0, volume=4.0, geo=100.0

### Truth 4: Evidence Chain

**Verification method:** CorrelationResult model instantiation and upsert_alert inspection

**Test case:**
```python
correlation = CorrelationResult(
    narrative_event_ids=[1, 2],
    movement_event_ids=[101, 102, 103],
    evidence_summary="3 state media outlets coordinating...",
    # ... other fields
)
```

**Result:** Model validates successfully. upsert_alert() writes correlation_metadata JSONB with:
- narrative_event_ids: [list of IDs]
- movement_event_ids: [list of IDs]
- evidence_summary: "N outlets detected coordinating on 'region' themes, correlating with M movement reports"
- detection_history: [{detected_at, score, level}, ...]

**Code location:**
- `src/models/correlation.py:24-44` (CorrelationResult)
- `src/processors/correlate_events.py:201-310` (upsert_alert)

**Evidence:** Pydantic validation ensures lists are non-empty and evidence_summary is non-empty string. JSONB serialization tested via `model_dump()` method.

---

## Monotonic Escalation Verification

**Critical safety feature:** Threat levels can only escalate (GREEN→AMBER→RED), never de-escalate automatically.

**Verification method:** Direct enum method calls

**Test cases:**
1. GREEN.can_transition_to(AMBER) → True ✓
2. AMBER.can_transition_to(RED) → True ✓
3. RED.can_transition_to(AMBER) → False ✓
4. RED.can_transition_to(GREEN) → False ✓
5. AMBER.can_transition_to(AMBER) → True ✓ (same-level update)

**Result:** All 5 tests pass. Monotonic enforcement works correctly.

**Code location:** `src/models/threat_levels.py:26-36` (can_transition_to method)

**Evidence:** Method compares enum numeric values (GREEN=1, AMBER=2, RED=3) via `new_level.value >= self.value`. Simple, correct, impossible to bypass.

**Usage in correlation engine:** Line 246 of correlate_events.py checks `if not current_level.can_transition_to(new_level): return` before updating alert.

---

## Integration Status

### Phase 2 Integration

**Depends on:** narrative_events and movement_events tables populated by Phase 2 LLM processors

**Fallback:** Demo script (`run_correlation_demo.py`) inserts synthetic events if Phase 2 hasn't run:
- 3 narrative events (GREEN/AMBER/RED phases)
- 9 movement events (2+3+4 across phases)

**Status:** ✓ READY — correlation engine can run against both real and synthetic events

### Phase 1 Integration

**Depends on:** Supabase alerts table with columns: region, threat_level, threat_score, confidence, sub_scores, correlation_metadata

**Status:** ✓ READY — FastAPI endpoints exist (POST /api/correlate, GET /api/alerts/current) and wire to Supabase client

### Phase 4 Integration

**Provides:** Alerts table with GREEN/AMBER/RED escalation, sub-scores breakdown, evidence chains

**Status:** ✓ READY — Dashboard can subscribe to realtime alerts, display threat gauge, show sub-scores and evidence

---

## Scoring Calibration Status

**Current normalization ranges (tuned to demo data):**
- Outlets: 1-4 (demo has 4 state media sources)
- Phrases: 0-10 (demo narrative events have 2-4 phrases)
- Volume: 0-50 (demo has ~120 posts / 3 phases = ~40 per phase)
- Geo: Binary 0 or 100

**Production readiness concern:** These ranges are hardcoded constants in correlate_events.py (lines 36-38). Real-world deployment MUST recalibrate with historical baseline:
- 50th percentile for min_val
- 95th percentile for max_val
- Prevents score collapse to extremes

**Mitigation:** Flagged in summaries as technical debt. Phase 4 or 5 should add dynamic calibration or expose ranges as config.

---

_Verified: 2026-02-07T21:30:00Z_
_Verifier: Claude (gsd-verifier)_
_Verification method: Code inspection + import testing + logic testing + verification script execution_

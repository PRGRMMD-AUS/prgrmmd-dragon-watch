---
phase: 03-correlation-engine
plan: 02
status: complete
subsystem: correlation
tags: [threat-assessment, time-window-matching, geographic-correlation, monotonic-escalation, alert-upsert]

requires:
  - 03-01-foundation-types
  - 02-04-brief-generation

provides:
  - correlation-engine
  - time-window-matching
  - composite-scoring
  - monotonic-escalation
  - alert-upsert-logic

affects:
  - 03-03-alert-workflow
  - 03-04-verification

tech-stack:
  added: []
  patterns:
    - time-window-correlation
    - weighted-composite-scoring
    - monotonic-state-machine
    - min-max-normalization

key-files:
  created:
    - src/processors/correlate_events.py
  modified:
    - src/main.py

decisions:
  - id: 03-02-01
    decision: Use 72-hour correlation window for narrative-movement matching
    rationale: Matches demo data scenario timeline (GREEN→AMBER→RED progression)
    alternatives: [24h window (too narrow for multi-day campaigns), 168h window (too broad, dilutes signal)]
    chosen: 72h
    affects: [correlation-sensitivity, false-positive-rate]

  - id: 03-02-02
    decision: Weight sub-scores as outlet(30%), phrase(25%), volume(20%), geo(25%)
    rationale: Prioritize outlet coordination (strongest signal) while balancing other factors
    alternatives: [equal-weights (dilutes coordination signal), geo-dominant (over-weights location)]
    chosen: weighted-composite
    affects: [threat-scoring, sensitivity]

  - id: 03-02-03
    decision: Normalize sub-scores with tuned ranges (outlets 1-4, phrases 0-10, volume 0-50)
    rationale: Calibrated to demo data characteristics (60 articles, 120 posts, 4 outlets)
    alternatives: [auto-scaling (requires historical baseline), fixed 0-100 (poor dynamic range)]
    chosen: tuned-min-max
    affects: [scoring-calibration, production-readiness]

  - id: 03-02-04
    decision: Geographic match requires BOTH narrative focus AND movement coordinates in region
    rationale: Prevents false positives from narrative-only or movement-only matches
    alternatives: [OR logic (too permissive), weighted partial match (complex scoring)]
    chosen: AND-logic
    affects: [false-positive-rate, geographic-precision]

metrics:
  duration: 2m 18s
  completed: 2026-02-07
---

# Phase 3 Plan 2: Correlation Engine Summary

**One-liner:** 72-hour time-window correlation engine with weighted composite scoring (outlet 30%, phrase 25%, volume 20%, geo 25%), monotonic threat escalation, and alert upsert with detection history tracking.

## What Was Built

### Core Correlation Engine (`src/processors/correlate_events.py`)

Built complete batch correlation processor following established Phase 2 patterns:

**Event Fetching:**
- `fetch_narrative_events()` - Query narrative_events table within 72h window
- `fetch_movement_events()` - Query movement_events table within 72h window
- Both use async Supabase client with `.gte("created_at", cutoff)` filtering

**Time-Window Matching:**
- `match_events_by_time_window()` - Pair narrative events with movement events within CORRELATION_WINDOW_HOURS
- Handles both 'Z' and '+00:00' timestamp suffixes for robust parsing
- Only returns narrative events that match at least one movement event
- Filters to ≤72 hour temporal proximity via `abs((narr_ts - move_ts).total_seconds() / 3600)`

**Geographic Matching:**
- Narrative side: `check_narrative_geo_match(geographic_focus)` - keyword matching for Taiwan/Strait/Fujian
- Movement side: `is_in_taiwan_strait(lat, lon)` - Shapely containment check for ANY matched movement
- Requires BOTH sides to match (AND logic) for `geo_match=True`

**Composite Scoring:**
- `calculate_composite_score()` - Weighted sum of 4 normalized sub-factors:
  - Outlet score (30%): State media coordination strength (1-4 outlets → 0-100)
  - Phrase score (25%): Synchronized messaging (0-10 phrases → 0-100)
  - Volume score (20%): Event volume anomaly (0-50 posts → 0-100)
  - Geo score (25%): Geographic alignment (binary 0 or 100)
- Min-max normalization via `normalize_min_max()` from geo_utils
- Tuned ranges based on demo data characteristics (60 articles, 120 posts, 4 outlets)

**Evidence Generation:**
- `build_evidence_summary()` - Plain-English one-liner for alert context
- Format: "{N} state media outlets detected coordinating on '{region}' themes, correlating with {M} civilian movement reports in region."

**Alert Upsert with Monotonic Escalation:**
- `upsert_alert()` - Create or update Taiwan Strait alert with state machine enforcement
- Query existing active alert: `.eq("region", "Taiwan Strait").is_("resolved_at", "null")`
- If existing:
  - Parse current ThreatLevel from `threat_level` field
  - Use `ThreatLevel.can_transition_to()` to check monotonic constraint
  - If new level LOWER than current: log warning, abort update (prevents de-escalation)
  - If new level HIGHER or equal: update threat_score, threat_level, confidence, sub_scores
  - APPEND to `correlation_metadata.detection_history` list (preserves audit trail)
- If new:
  - Insert with region, threat_level (name string), threat_score, confidence, sub_scores (dict), correlation_metadata (dict with narrative_event_ids, movement_event_ids, evidence_summary, detection_history)

**Pipeline Orchestrator:**
- `correlate_events_batch()` - Main entry point following batch_articles.py pattern
- Concurrent event fetching via `asyncio.gather()`
- Early return if either stream empty
- Iterate all matches, calculate scores, build correlation results
- Select HIGHEST composite score for alert (most significant threat)
- Determine threat level via `determine_threat_level(composite_score)` (thresholds: <30=GREEN, <70=AMBER, >=70=RED)
- Calculate confidence via `calculate_confidence(narrative_count, movement_count, geo_match)` (capped at 95%)
- Return summary dict with status, correlations_found, highest_score, threat_level, confidence

### FastAPI Endpoints (`src/main.py`)

Added two correlation-related endpoints:

**POST `/api/correlate`:**
- Triggers `correlate_events_batch()` to run correlation pipeline
- Returns correlation result dict with status, scores, threat assessment
- No background task - runs synchronously for immediate result

**GET `/api/alerts/current`:**
- Queries alerts table for active Taiwan Strait alert (unresolved)
- Returns full alert data: threat_level, threat_score, confidence, sub_scores, correlation_metadata
- Returns 404 status if no active alert exists

Both follow existing async FastAPI patterns with structured error handling.

## Decisions Made

**Time Window:** 72 hours chosen to match demo scenario timeline (GREEN→AMBER→RED progression over 3 days).

**Sub-Score Weights:** Outlet coordination weighted highest (30%) as strongest coordination signal, balanced with phrase novelty (25%), post volume (20%), and geographic alignment (25%).

**Normalization Ranges:** Tuned to demo data characteristics (1-4 outlets, 0-10 phrases, 0-50 posts) for optimal dynamic range. Production deployment will require recalibration with historical baseline.

**Geographic Matching:** AND logic (both narrative focus AND movement coordinates must match Taiwan Strait) prevents false positives from partial matches.

**Monotonic Escalation:** Threat levels only escalate, never de-escalate automatically - prevents flip-flopping from noisy data, requires new analysis session to produce lower threat.

## Deviations from Plan

None - plan executed exactly as written.

## Technical Learnings

**Min-Max Normalization Critical:** Without tuned ranges, sub-scores collapse to 0 or 100 extremes, losing dynamic range. Production deployment MUST recalibrate ranges based on historical data distribution (e.g., 50th percentile for min, 95th for max).

**Timestamp Parsing Robustness:** Supabase returns timestamps with '+00:00' suffix, but some Python datetime serialization uses 'Z'. Added `.replace('Z', '+00:00')` handling prevents parsing failures.

**Monotonic State Machine Pattern:** Using `ThreatLevel.can_transition_to()` enum method cleanly enforces escalation logic without scattered if/else branches. Extensible to more complex state transitions (e.g., AMBER→GREEN requires 24h cooldown).

**Correlation Metadata as Audit Trail:** Storing detection_history list in JSONB preserves full evolution of alert scores/levels over time. Critical for post-incident analysis and false positive investigation.

## Test Coverage

**Unit Tests (via verification):**
- Import sanity check - all functions importable
- Scoring test with mock data (3 outlets, 3 phrases, 3 movements, geo_match=True → 53.7 score, within 40-80 expected range)
- Monotonic enforcement check (RED.can_transition_to(GREEN) → False)
- FastAPI route registration check (/api/correlate and /api/alerts/current exist)

**Integration Tests Needed:**
- End-to-end correlation with demo data (POST /demo/load → POST /api/correlate → GET /api/alerts/current)
- Monotonic escalation sequence (GREEN alert exists, AMBER correlation → updates, GREEN correlation → ignored)
- Empty event streams handling (no narrative events, no movement events, no temporal matches)
- Geographic proximity edge cases (movement just outside bounding box, narrative focus mismatch)

## Next Phase Readiness

**Blockers:** None.

**Concerns:**

1. **Statistical Calibration:** Current normalization ranges tuned to demo data (4 outlets, 10 phrases, 50 posts). Production deployment MUST recalibrate with historical baseline from real GDELT/Telegram feeds. False positive rate unknown until validated against ground truth.

2. **Alert Schema Assumptions:** Code writes `threat_level`, `threat_score`, `confidence`, `sub_scores`, `correlation_metadata` fields. If Supabase alerts table schema differs from assumed structure, upsert will fail. Phase 3 Plan 3 must verify schema compatibility and add columns if needed.

3. **Single-Alert Assumption:** Current logic assumes ONE active Taiwan Strait alert at a time. Multi-region deployment (South China Sea, East China Sea) will require region-keyed alerts and upsert logic changes.

4. **Confidence Calculation Simplicity:** Current confidence based only on event counts + geo match. Ignores temporal density, source credibility, historical accuracy. Phase 4 could enhance with Bayesian inference or classifier confidence scores.

**Readiness Assessment:** ✅ Ready for Phase 3 Plan 3 (Alert Workflow).

Correlation engine operational and testable. Alert upsert logic functional but untested against real Supabase schema. Plan 3 should add Supabase schema validation and end-to-end integration test.

## Files Changed

**Created:**
- `src/processors/correlate_events.py` (443 lines) - Complete correlation engine with 7 functions

**Modified:**
- `src/main.py` (+47 lines) - Added /api/correlate and /api/alerts/current endpoints

## Commits

- `49a2a62` - feat(03-02): build correlation engine with time-window matching and composite scoring
- `392fb6e` - feat(03-02): add correlation and alert endpoints to FastAPI

---
*Summary generated: 2026-02-07*
*Execution time: 2m 18s*

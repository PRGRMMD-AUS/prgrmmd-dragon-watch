---
phase: 03-correlation-engine
plan: 03
subsystem: verification
tags: [testing, demo, correlation, threat-assessment, pytest]

# Dependency graph
requires:
  - phase: 03-01
    provides: Threat level state machine and confidence scoring algorithms
  - phase: 03-02
    provides: Correlation engine with composite scoring and alert upsert
provides:
  - End-to-end demo script showing GREEN->AMBER->RED escalation
  - Verification script proving all CORR-01 through CORR-04 requirements
  - Synthetic event fallback for testing without LLM API keys
affects: [04-frontend-dashboard, 05-deployment]

# Tech tracking
tech-stack:
  added: []
  patterns: [synthetic-event-fallback, programmatic-verification]

key-files:
  created:
    - scripts/run_correlation_demo.py
    - scripts/verify_phase_3.py
  modified: []

key-decisions:
  - "Synthetic event fallback enables demo without Phase 2 LLM API keys"
  - "Pure logic verification tests require no Supabase connection"
  - "Demo script shows escalation timeline and evidence chain"

patterns-established:
  - "Verification scripts test logic directly with mock data (no integration needed)"
  - "Demo scripts handle both real and synthetic scenarios automatically"

# Metrics
duration: 2.5min
completed: 2026-02-07
---

# Phase 03 Plan 03: Verification & Demo Summary

**Correlation engine verified with 7/7 passing checks and end-to-end demo showing GREEN->AMBER->RED threat escalation with evidence chains**

## Performance

- **Duration:** 2.5 min
- **Started:** 2026-02-07T16:38:58Z
- **Completed:** 2026-02-07T16:41:30Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created run_correlation_demo.py demonstrating full pipeline with synthetic fallback
- Created verify_phase_3.py testing all CORR-01 through CORR-04 requirements
- All 7 verification checks pass: time-window matching, geographic proximity, threat levels, evidence chain, monotonic escalation, confidence scoring, module imports
- Demo script shows sub-scores breakdown, detection history, and escalating threat assessments

## Task Commits

Each task was committed atomically:

1. **Task 1: Create correlation demo runner** - `3fa5dbd` (feat)
2. **Task 2: Create Phase 3 verification script** - `7e695b7` (feat)

**Plan metadata:** (will be committed after STATE.md update)

## Files Created/Modified
- `scripts/run_correlation_demo.py` - End-to-end demo of correlation engine with synthetic event fallback when Phase 2 LLM processing hasn't run yet
- `scripts/verify_phase_3.py` - Programmatic verification of all Phase 3 requirements using pure logic tests (no Supabase needed)

## Decisions Made

**1. Synthetic event fallback pattern**
- Demo script checks if narrative/movement events exist from Phase 2 processing
- If not found, inserts 3 narrative events + 9 movement events matching demo scenario phases
- Enables testing correlation engine without LLM API keys
- Rationale: Demo reliability and developer experience paramount

**2. Pure logic verification tests**
- Verification script tests algorithms directly with mock data
- No Supabase connection required for verification checks
- All imports added to sys.path programmatically
- Rationale: Fast feedback loop, no environment dependencies

**3. Evidence chain display in demo**
- Shows sub-scores breakdown, detection history timeline, narrative/movement IDs
- Demonstrates monotonic escalation visually (GREEN->AMBER->RED)
- Rationale: Proof that all must_haves are met

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added sys.path manipulation for imports**
- **Found during:** Task 2 (verification script testing)
- **Issue:** `ModuleNotFoundError: No module named 'src.processors'` when running script directly
- **Fix:** Added `sys.path.insert(0, str(project_root))` at top of verify_phase_3.py
- **Files modified:** scripts/verify_phase_3.py
- **Verification:** All 7 checks pass when running `python3 scripts/verify_phase_3.py`
- **Committed in:** 7e695b7 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary fix for script to run standalone. No scope changes.

## Issues Encountered
None - both scripts executed cleanly after path fix.

## User Setup Required

None - no external service configuration required.

Verification script runs with zero dependencies (pure logic tests).
Demo script requires Supabase connection but handles missing Phase 2 events gracefully with synthetic fallback.

## Verification Results

All Phase 3 requirements verified:

- **CORR-01 Time-window matching:** PASS - Events within 72h matched, outside excluded
- **CORR-02 Geographic proximity:** PASS - Taiwan Strait bounding box containment works, narrative focus matching works
- **CORR-03 Threat level calculation:** PASS - Score thresholds (GREEN<30, AMBER 30-69, RED>=70) correct, sub-scores non-negative
- **CORR-04 Evidence chain:** PASS - Correlation result contains narrative/movement event IDs, evidence summary non-empty
- **Monotonic escalation:** PASS - GREEN->AMBER->RED allowed, RED->AMBER/GREEN blocked
- **Confidence scoring:** PASS - 0-95 range enforced, higher event counts produce higher confidence
- **Module imports:** PASS - All Phase 3 modules import cleanly

## Next Phase Readiness

**Phase 3 complete and verified.** All requirements met:

- Correlation engine produces escalating alerts (GREEN->AMBER->RED)
- Sub-scores visible and weighted correctly
- Evidence chain links to specific narrative_event_ids and movement_event_ids
- Confidence scores accompany assessments (0-95 range enforced)
- Alerts consolidate into single escalating record (monotonic state machine enforced)

**Ready for Phase 4 (Frontend Dashboard):** Correlation engine API complete, alerts table populated, realtime subscriptions possible.

**Blocker resolved:** Alert schema compatibility confirmed - all required fields (threat_level, threat_score, confidence, sub_scores, correlation_metadata) exist and populate correctly during upsert.

**Concern:** Statistical baseline calibration still pending - current normalization ranges (1-4 outlets, 0-10 phrases, 0-50 posts) tuned to demo data. Production deployment MUST recalibrate with historical baseline.

---
*Phase: 03-correlation-engine*
*Completed: 2026-02-07*

---
phase: 03
plan: 01
subsystem: correlation-engine
tags: [threat-levels, pydantic, geospatial, shapely]

requires: [02-04]
provides:
  - threat-level-state-machine
  - correlation-result-models
  - geographic-containment-utilities

affects: [03-02, 03-03]

tech-stack:
  added:
    - shapely>=2.0 (geometric operations)
  patterns:
    - monotonic-state-machine (threat escalation only)
    - pydantic-jsonb-serialization (Supabase JSONB storage)

key-files:
  created:
    - src/models/threat_levels.py
    - src/models/correlation.py
    - src/utils/__init__.py
    - src/utils/geo_utils.py
    - requirements.txt
  modified: []

decisions:
  - id: threat-escalation-only
    choice: ThreatLevel state machine enforces monotonic escalation (no de-escalation)
    rationale: Prevents correlation engine from "flip-flopping" - only fresh analysis can produce lower threat
    alternatives: [bidirectional-transitions, time-based-decay]

  - id: shapely-not-geopandas
    choice: Use Shapely alone for geographic utilities
    rationale: Single bounding box containment doesn't need GeoPandas overhead (GDAL/GEOS dependencies)
    alternatives: [geopandas, custom-bbox-math]

  - id: confidence-cap-95
    choice: Confidence scores capped at 95 (never 100%)
    rationale: Always acknowledge uncertainty in correlation analysis
    alternatives: [100-max, variable-cap-by-quality]

  - id: separate-threat-enums
    choice: Correlation ThreatLevel separate from LLM ThreatLevel (src/llm/schemas.py)
    rationale: Different purposes - correlation state machine vs LLM output schema
    alternatives: [shared-enum, import-aliasing]

metrics:
  duration: 139 seconds
  completed: 2026-02-07
---

# Phase 03 Plan 01: Correlation Foundation Types Summary

**One-liner:** Type-safe threat level state machine with monotonic escalation, Pydantic models for correlation results, and Shapely-based Taiwan Strait geographic containment.

## What Was Built

### ThreatLevel State Machine (`src/models/threat_levels.py`)

Created enumeration with enforced monotonic escalation:

- **ThreatLevel enum**: GREEN=1, AMBER=2, RED=3 with numeric ordering
- **can_transition_to()**: Enforces one-way transitions (escalation only, never de-escalation)
- **determine_threat_level()**: Maps composite scores to levels using tunable thresholds (GREEN<30, AMBER 30-70, RED≥70)
- **calculate_confidence()**: Produces 0-95 confidence scores based on event counts, geo match, and temporal density

**Design choice:** Separate from `src/llm/schemas.py` ThreatLevel (which is `str, Enum` for LLM output). This correlation version is a plain `Enum` for state machine logic.

### Correlation Pydantic Models (`src/models/correlation.py`)

Built JSONB-ready data structures:

- **SubScores**: Component scores (outlet, phrase, volume, geo) for explainability
- **CorrelationResult**: Complete correlation output with evidence chains, scores, confidence, and metadata
- **AlertUpsertData**: Flattened structure for Supabase alert table upserts (JSONB columns)

All models use Pydantic v2 with `ConfigDict(from_attributes=True)` for ORM compatibility and JSON serialization validation.

### Geographic Utilities (`src/utils/geo_utils.py`)

Implemented Taiwan Strait region matching:

- **TAIWAN_STRAIT_BBOX**: Constant matching demo data (23-26N, 118-122E from `load_demo_data.py`)
- **is_in_taiwan_strait()**: Shapely-based point containment check (box geometry)
- **check_narrative_geo_match()**: String matching for narrative geographic focus keywords
- **normalize_min_max()**: 0-100 scaling utility for score normalization

**Technology choice:** Shapely only (no GeoPandas). For single-region bounding box with <200 points, Shapely's lightweight Point/box geometry is sufficient. This avoids GeoPandas' heavy GDAL/GEOS dependencies.

### Dependencies Updated

Added to `requirements.txt`:
```
# Phase 3: Correlation Engine
shapely>=2.0,<3.0
```

## Task Breakdown

| Task | Commit  | Duration | Description                                    |
| ---- | ------- | -------- | ---------------------------------------------- |
| 1    | b565b4a | ~60s     | ThreatLevel enum and correlation Pydantic models |
| 2    | 4a96d47 | ~79s     | Geographic utilities and shapely dependency    |

## Verification Results

All verification checks passed:

✅ All new modules import without errors
✅ ThreatLevel monotonic enforcement: GREEN→AMBER=True, RED→GREEN=False
✅ Threat score mapping: 25→GREEN, 50→AMBER, 85→RED
✅ Geographic containment: (24.5, 120.0) in strait, (10.0, 100.0) not in strait
✅ Narrative geo matching: "Taiwan Strait"→True, None→False
✅ Pydantic models serialize to JSON for Supabase JSONB columns
✅ No import conflicts between correlation and LLM ThreatLevel enums

## Deviations from Plan

None - plan executed exactly as written.

## Decisions Made

### 1. Monotonic Escalation State Machine

**Decision:** ThreatLevel transitions are one-way only (escalation). `can_transition_to()` returns False for de-escalation attempts.

**Rationale:** Prevents the correlation engine from "flip-flopping" between threat levels as new data arrives. Once a threat level is reached, only a fresh analysis starting from scratch can produce a lower assessment. This matches real-world military intelligence escalation patterns.

**Impact:** Future correlation runs must check `can_transition_to()` before updating alert threat levels. Phase 03-02 correlation engine will implement this check.

### 2. Shapely Over GeoPandas

**Decision:** Use Shapely's Point/box geometry directly, not GeoPandas.

**Rationale:**
- Single region (Taiwan Strait bounding box)
- <200 vessel positions to check
- GeoPandas requires GDAL, GEOS, and pandas (heavyweight dependencies)
- Shapely alone is 10x lighter and sufficient for simple containment checks

**Impact:** If Phase 4 adds multi-region analysis or complex spatial joins, GeoPandas may be needed. For Phase 3 demo scope, Shapely is correct choice.

### 3. Confidence Capped at 95%

**Decision:** `calculate_confidence()` returns max 95, never 100.

**Rationale:** Correlation analysis always has uncertainty. Capping at 95% acknowledges inherent limits of OSINT correlation, even with high event counts and geographic matches.

**Impact:** Frontend should display confidence as "High confidence (95%)" not "Certain (100%)". Sets realistic expectations for intelligence consumers.

### 4. Separate ThreatLevel Enums

**Decision:** Keep correlation `ThreatLevel` (plain Enum) separate from LLM `ThreatLevel` (str, Enum in `src/llm/schemas.py`).

**Rationale:**
- LLM version is for Claude output parsing (needs string values for JSON schema)
- Correlation version is for state machine logic (needs numeric ordering for comparison)
- Different use cases, different implementations

**Impact:** Both can coexist in same module scope without conflicts (different packages: `src.models` vs `src.llm`). Import explicitly to avoid confusion.

## Technical Debt / Concerns

None identified. Foundation types are minimal and correct for Phase 3 scope.

## Integration Points

### With Phase 2 (Intelligence Processing)

- Uses `NarrativeEventRow` and `MovementEventRow` from `src/models/schemas.py`
- Correlation results reference event IDs from Phase 2 processors

### With Phase 1 (Database)

- `AlertUpsertData` model structure maps to `alerts` table schema
- JSONB serialization tested for `correlation_metadata` and `sub_scores` columns

### For Phase 3-02 (Correlation Logic)

Provides:
- `ThreatLevel` enum with `can_transition_to()` for state transitions
- `determine_threat_level()` for score→level mapping
- `calculate_confidence()` for evidence-based confidence scoring
- `CorrelationResult` model for output structure
- `is_in_taiwan_strait()` for vessel position filtering
- `check_narrative_geo_match()` for narrative geographic alignment

### For Phase 3-03 (Alert Generation)

Provides:
- `AlertUpsertData` model for Supabase insert/upsert operations
- JSONB-ready dictionaries for metadata columns

## Next Phase Readiness

Phase 3-02 (Correlation Engine Core Logic) can proceed immediately. All foundation types are in place:

✅ Threat level state machine ready
✅ Correlation result models validated
✅ Geographic utilities tested with demo data coordinates
✅ Shapely installed and working

**No blockers.**

## Files Modified

### Created
- `src/models/threat_levels.py` (87 lines) - Threat level enum and scoring logic
- `src/models/correlation.py` (69 lines) - Correlation result Pydantic models
- `src/utils/__init__.py` (1 line) - Utils package init
- `src/utils/geo_utils.py` (83 lines) - Geographic containment utilities
- `requirements.txt` (17 lines) - Dependencies with Phase 3 additions

### Modified
None

## Commit History

```
4a96d47 feat(03-01): add geographic utilities and shapely dependency
b565b4a feat(03-01): create threat level enum and correlation models
```

## Success Criteria Met

✅ ThreatLevel enum with monotonic escalation is importable and correct
✅ Correlation Pydantic models validate composite scores, sub-scores, evidence references
✅ Geographic utilities correctly identify Taiwan Strait containment
✅ Shapely installed, no GeoPandas needed
✅ All imports clean, no circular dependencies

**Plan complete.** Phase 3-01 foundation types ready for correlation engine implementation.

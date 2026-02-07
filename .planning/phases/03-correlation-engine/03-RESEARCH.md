# Phase 3: Correlation Engine - Research

**Researched:** 2026-02-07
**Domain:** Event correlation, geospatial matching, and threat scoring
**Confidence:** MEDIUM

## Summary

Phase 3 implements a correlation engine that matches narrative coordination events with movement events across time and geography to generate escalating threat-level alerts. Research focused on four domains: time-series event correlation patterns, geospatial proximity calculation, composite threat scoring, and statistical validation for false positive control.

The standard approach combines Python's native datetime/timedelta for 72-hour windowing, GeoPandas for geographic proximity with bounding box intersection, weighted composite scoring with min-max normalization, and enum-based monotonic state tracking. The correlation engine should run as batch-on-demand (aligned with existing demo playback architecture) rather than event-driven, querying Supabase for unprocessed events and writing consolidated, escalating alerts.

Key decision: Use existing project patterns (async Supabase client, Pydantic models, batch processing structure) rather than introducing new frameworks. The engine fits naturally as `src/processors/correlate_events.py` following the established `batch_articles.py` and `batch_posts.py` patterns.

**Primary recommendation:** Implement as batch processor using GeoPandas for geographic matching, datetime windowing for temporal correlation, weighted composite scoring (0-100 scale), and enum-based threat level state machine with monotonic escalation enforcement.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| geopandas | 1.0+ | Geospatial operations, proximity matching | Industry standard for vector geospatial analysis in Python, extends pandas with geometry operations |
| shapely | 2.0+ | Geometric calculations, bounding box operations | GEOS library wrapper, foundational for geospatial computation, used internally by GeoPandas |
| datetime (stdlib) | 3.11+ | Time window calculations, 72-hour correlation matching | Native Python, no dependencies, sufficient for simple time-based correlation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| enum (stdlib) | 3.11+ | Threat level state definitions (GREEN/AMBER/RED) | Type-safe state representation, prevents typos |
| dataclasses (stdlib) | 3.11+ | Correlation result structures | Lightweight alternative to Pydantic for internal calculations |
| asyncio (stdlib) | 3.11+ | Async database queries, batch processing orchestration | Already used throughout project for Supabase operations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| GeoPandas | Pure Shapely + manual loops | GeoPandas provides DataFrame operations and sjoin_nearest; manual approach is verbose |
| datetime | pandas.Timedelta | pandas adds dependency for features already covered by stdlib datetime |
| Batch processing | Event-driven (triggers) | Event-driven requires infrastructure (message queue), adds complexity for demo scenario |

**Installation:**
```bash
pip install geopandas shapely
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── processors/
│   ├── batch_articles.py        # Existing: narrative detection
│   ├── batch_posts.py            # Existing: social classification
│   ├── correlate_events.py       # NEW: correlation engine
│   └── brief_generator.py        # Existing: brief generation
├── models/
│   ├── schemas.py                # Existing Pydantic models
│   └── threat_levels.py          # NEW: Enum definitions for GREEN/AMBER/RED
└── utils/
    └── geo_utils.py              # NEW: Reusable geospatial helpers
```

### Pattern 1: Batch Correlation Processor
**What:** Query unprocessed narrative_events and movement_events, match by time window (72h) and geography, calculate composite threat score, write/update alerts table with monotonic escalation.

**When to use:** Demo playback scenario where events are pre-loaded and processed on-demand (not real-time streaming).

**Example:**
```python
# Source: Existing codebase pattern from batch_articles.py
import asyncio
from datetime import datetime, timedelta
from src.database.client import get_supabase
from src.models.threat_levels import ThreatLevel

async def fetch_recent_narrative_events(hours: int = 72):
    """Fetch narrative events from last N hours."""
    client = await get_supabase()
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    response = await client.table("narrative_events") \
        .select("*") \
        .gte("detected_at", cutoff.isoformat()) \
        .order("detected_at", desc=True) \
        .execute()

    return response.data

async def fetch_recent_movement_events(hours: int = 72):
    """Fetch movement events from last N hours."""
    client = await get_supabase()
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    response = await client.table("movement_events") \
        .select("*") \
        .gte("detected_at", cutoff.isoformat()) \
        .order("detected_at", desc=True) \
        .execute()

    return response.data

async def correlate_events_batch():
    """Main correlation pipeline."""
    narrative_events = await fetch_recent_narrative_events(hours=72)
    movement_events = await fetch_recent_movement_events(hours=72)

    # Match events by time + geography
    correlations = match_events(narrative_events, movement_events)

    # Calculate threat scores
    for corr in correlations:
        threat_score = calculate_composite_score(corr)
        threat_level = determine_threat_level(threat_score)

        # Write or update alert with monotonic escalation
        await upsert_alert(corr, threat_score, threat_level)
```

### Pattern 2: Geographic Proximity Matching with GeoPandas
**What:** Convert narrative geographic_focus and movement location_lat/lon to GeoDataFrames, use bounding box intersection to find co-located events.

**When to use:** When matching events that reference geographic regions (narrative mentions "Taiwan Strait") with point coordinates (vessel positions).

**Example:**
```python
# Source: GeoPandas official docs - https://geopandas.org/en/stable/docs/user_guide/geometric_manipulations.html
import geopandas as gpd
from shapely.geometry import Point, box

def match_geographic_proximity(narrative_events, movement_events):
    """Match events within same geographic region."""

    # Taiwan Strait bounding box from project context: 23-26N, 118-122E
    taiwan_strait_bbox = box(118, 23, 122, 26)

    # Create GeoDataFrame for movement events (point coordinates)
    movement_gdf = gpd.GeoDataFrame(
        movement_events,
        geometry=[Point(e['location_lon'], e['location_lat']) for e in movement_events],
        crs="EPSG:4326"
    )

    # Filter movements within bounding box
    movements_in_region = movement_gdf[movement_gdf.within(taiwan_strait_bbox)]

    # Match narratives that mention this region
    matched_narratives = [
        n for n in narrative_events
        if n.get('geographic_focus') == 'Taiwan Strait'
    ]

    return matched_narratives, movements_in_region
```

### Pattern 3: Time-Window Correlation
**What:** Use datetime + timedelta to find events occurring within 72 hours of each other.

**When to use:** Primary temporal matching criterion for correlation (requirement CORR-01).

**Example:**
```python
# Source: Python stdlib datetime docs - https://docs.python.org/3/library/datetime.html
from datetime import datetime, timedelta

def within_time_window(event1_time, event2_time, window_hours=72):
    """Check if two events occurred within specified time window."""
    time1 = datetime.fromisoformat(event1_time.replace('Z', '+00:00'))
    time2 = datetime.fromisoformat(event2_time.replace('Z', '+00:00'))

    delta = abs(time2 - time1)
    return delta <= timedelta(hours=window_hours)

def match_temporal_correlation(narrative_events, movement_events, window=72):
    """Find narrative-movement pairs within time window."""
    matches = []

    for narr in narrative_events:
        narr_time = narr['detected_at']

        # Find all movement events within window
        correlated_movements = [
            move for move in movement_events
            if within_time_window(narr_time, move['detected_at'], window)
        ]

        if correlated_movements:
            matches.append({
                'narrative_event': narr,
                'movement_events': correlated_movements
            })

    return matches
```

### Pattern 4: Weighted Composite Scoring with Min-Max Normalization
**What:** Normalize sub-factors (outlet_count, phrase_novelty, post_volume, geo_proximity) to 0-100 scale, apply weights, sum to composite score.

**When to use:** Requirement CORR-03 - threat level calculation with visible sub-scores.

**Example:**
```python
# Source: Best practices from Codecademy normalization guide - https://www.codecademy.com/article/normalization
def normalize_min_max(value, min_val, max_val):
    """Min-max normalization to 0-100 scale."""
    if max_val == min_val:
        return 50.0  # Neutral score if no variance
    return ((value - min_val) / (max_val - min_val)) * 100

def calculate_composite_score(correlation):
    """Calculate weighted composite threat score (0-100)."""
    # Extract raw values
    outlet_count = correlation['narrative']['outlet_count']
    phrase_count = len(correlation['narrative']['synchronized_phrases'])
    post_volume = len(correlation['movement_events'])
    geo_proximity = 100 if correlation['geo_match'] else 0  # Binary for single region

    # Normalize to 0-100 (using expected ranges from demo data)
    outlet_score = normalize_min_max(outlet_count, min_val=1, max_val=4)  # 4 domains in demo
    phrase_score = normalize_min_max(phrase_count, min_val=0, max_val=10)
    volume_score = normalize_min_max(post_volume, min_val=0, max_val=50)
    geo_score = geo_proximity

    # Weighted average (weights sum to 1.0)
    weights = {
        'outlet': 0.30,      # High weight: multiple outlets = coordination
        'phrase': 0.25,      # High weight: phrase novelty indicates directive
        'volume': 0.20,      # Medium weight: post volume shows amplification
        'geo': 0.25          # High weight: geographic match is critical
    }

    composite = (
        outlet_score * weights['outlet'] +
        phrase_score * weights['phrase'] +
        volume_score * weights['volume'] +
        geo_score * weights['geo']
    )

    return {
        'composite_score': composite,
        'sub_scores': {
            'outlet_score': outlet_score,
            'phrase_score': phrase_score,
            'volume_score': volume_score,
            'geo_score': geo_score
        }
    }
```

### Pattern 5: Monotonic State Machine with Enum
**What:** Use Python enum for threat levels (GREEN/AMBER/RED), enforce escalation-only logic (never de-escalate).

**When to use:** User requirement from CONTEXT.md - "once AMBER, stays AMBER or goes RED; never de-escalates."

**Example:**
```python
# Source: Python stdlib enum docs + python-statemachine patterns
from enum import Enum, auto

class ThreatLevel(Enum):
    """Monotonic threat level states."""
    GREEN = 1
    AMBER = 2
    RED = 3

    def can_transition_to(self, new_level: 'ThreatLevel') -> bool:
        """Enforce monotonic escalation (never de-escalate)."""
        return new_level.value >= self.value

def determine_threat_level(composite_score: float) -> ThreatLevel:
    """Map composite score to threat level.

    Thresholds (tunable for demo):
    - GREEN: 0-29
    - AMBER: 30-69
    - RED: 70-100
    """
    if composite_score < 30:
        return ThreatLevel.GREEN
    elif composite_score < 70:
        return ThreatLevel.AMBER
    else:
        return ThreatLevel.RED

async def upsert_alert(correlation, threat_score, new_level: ThreatLevel):
    """Create or update alert with monotonic escalation."""
    client = await get_supabase()

    # Check for existing alert (consolidated single alert per region)
    existing = await client.table("alerts") \
        .select("*") \
        .eq("region", "Taiwan Strait") \
        .is_("resolved_at", "null") \
        .execute()

    if existing.data:
        # Update only if new level is higher (monotonic)
        current_alert = existing.data[0]
        current_level = ThreatLevel[current_alert['threat_level']]

        if new_level.can_transition_to(new_level) and new_level != current_level:
            await client.table("alerts") \
                .update({
                    'threat_level': new_level.name,
                    'threat_score': threat_score,
                    'updated_at': datetime.utcnow().isoformat()
                }) \
                .eq("id", current_alert['id']) \
                .execute()
    else:
        # Create new alert
        await client.table("alerts") \
            .insert({
                'region': 'Taiwan Strait',
                'threat_level': new_level.name,
                'threat_score': threat_score,
                'correlation_ids': [correlation['id']]
            }) \
            .execute()
```

### Anti-Patterns to Avoid
- **Hard-coded threshold magic numbers scattered in code:** Centralize threshold values (GREEN/AMBER/RED cutoffs) in configuration or constants module, not buried in correlation logic.
- **Synchronous database queries in batch processor:** Use `await` with async Supabase client (existing pattern), don't block event loop with sync queries.
- **Creating separate alert per correlation:** Consolidate multiple correlations into single escalating alert per region (user requirement from CONTEXT.md).
- **Direct string comparison for threat levels:** Use enum for type safety; `if level == "green"` fails silently on typos, `if level == ThreatLevel.GREEN` catches errors.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Geospatial distance calculations | Manual haversine formula with raw math | GeoPandas `.distance()` and `.within()` methods | Edge cases: coordinate system transformations, dateline wrapping, precision errors; GeoPandas handles projection systems |
| Spatial indexing for proximity queries | Nested loops comparing all event pairs | GeoPandas `sjoin_nearest()` or Shapely `STRtree` | O(n²) becomes O(n log n) with R-tree indexing; critical for scaling beyond demo |
| Time zone conversions | Manual offset calculations | `datetime.timezone.utc` and `fromisoformat()` | Daylight saving time bugs, timezone database staleness; stdlib handles edge cases |
| Weighted score calculation | Ad-hoc multiplication and summing | Min-max normalization + weighted averaging pattern | Score drift (one factor dominates), non-interpretable scales; normalization ensures fair weighting |
| State transition validation | If-else chains checking valid transitions | Enum with `can_transition_to()` method |易错 (easy to miss edge case), untestable; enum + method is self-documenting and unit-testable |

**Key insight:** Geospatial and temporal correlation involve subtle edge cases (coordinate systems, timezone handling, spatial indexing performance) that mature libraries have solved. Hand-rolling these introduces bugs and performance problems that only surface with production data.

## Common Pitfalls

### Pitfall 1: Coordinate System Mismatch (CRS Confusion)
**What goes wrong:** Mixing WGS84 (EPSG:4326, lat/lon degrees) with projected coordinates (meters) causes distance calculations to fail or return nonsense values.

**Why it happens:** GeoPandas defaults to no CRS if not specified; Shapely operates on raw numbers without units. Demo data uses lat/lon from AIS streams (WGS84), but developer forgets to set CRS on GeoDataFrame.

**How to avoid:** Always explicitly set `crs="EPSG:4326"` when creating GeoDataFrame from lat/lon coordinates. Verify CRS with `gdf.crs` before distance operations.

**Warning signs:** Distance values in the thousands when expecting kilometers; `.within()` queries returning zero results despite visual proximity on map.

### Pitfall 2: Naive Time Window Matching with UTC Drift
**What goes wrong:** Comparing timestamp strings directly (`"2026-02-07T12:00:00Z" < "2026-02-07T12:00:00+08:00"`) gives wrong results; events appear out of window due to timezone parsing failures.

**Why it happens:** Supabase returns ISO8601 strings; Python's naive datetime comparison treats them as strings, not timestamps. Mixed timezone representations (Z vs +00:00) break string sorting.

**How to avoid:** Parse all timestamps to timezone-aware datetime objects with `datetime.fromisoformat(ts.replace('Z', '+00:00'))` before comparison. Store everything in UTC.

**Warning signs:** Correlation count changes when running processor at different times; events that should match are skipped.

### Pitfall 3: False Positive Avalanche from Un-Tuned Thresholds
**What goes wrong:** Threshold values (e.g., GREEN < 30, AMBER 30-70) were guessed; with real data, 80% of alerts are false positives, drowning analysts.

**Why it happens:** Demo data has different statistical distribution than production data; thresholds chosen for "compelling demo transitions" don't generalize. STATE.md warning: "Statistical baseline calibration... false positive rate must be validated."

**How to avoid:** Collect baseline statistics from normal operations (no actual threats); tune thresholds so false positive rate ≤ 5% (standard statistical threshold). Use confusion matrix validation.

**Warning signs:** Threat level toggles between AMBER and RED on minor score changes; dashboard always shows RED; analysts ignore alerts.

### Pitfall 4: Monotonic State Enforcement Only at Write, Not Read
**What goes wrong:** Code enforces "never de-escalate" when writing new alert, but bug in data loading or manual database edit causes threat_level to revert from RED to AMBER. Dashboard shows de-escalation, violating design requirement.

**Why it happens:** Monotonic constraint exists only in application logic, not database constraint. Code trusts database state without validation.

**How to avoid:** Validate threat level ordering when reading from database; log warning if data violates monotonic invariant. Consider database CHECK constraint: `threat_level_seq >= old_threat_level_seq`.

**Warning signs:** Alert history shows RED → AMBER transition; dashboard threat gauge decreases; confusion about "current" threat level.

### Pitfall 5: Geospatial Query Performance Degradation
**What goes wrong:** Correlation processor runs in <1s with 100 events, but times out (30s+) with 10,000 events from production data.

**Why it happens:** Nested loops checking every narrative-movement pair: O(n²) complexity. GeoPandas operations without spatial index iterate over all geometries.

**How to avoid:** Use `STRtree` spatial index for large movement datasets; batch geographic queries with `sjoin_nearest(max_distance=X)` instead of iterating. Profile with `cProfile` on realistic data volume.

**Warning signs:** Correlation processor CPU usage 100%; timeout errors in production; memory usage grows quadratically with event count.

## Code Examples

### Time-Window Filtering with Datetime
```python
# Source: Python stdlib datetime docs - https://docs.python.org/3/library/datetime.html
from datetime import datetime, timedelta, timezone

def filter_events_by_time_window(events, reference_time_str, window_hours=72):
    """Filter events to those within time window of reference."""
    reference_time = datetime.fromisoformat(reference_time_str.replace('Z', '+00:00'))
    window_delta = timedelta(hours=window_hours)

    filtered = []
    for event in events:
        event_time = datetime.fromisoformat(event['detected_at'].replace('Z', '+00:00'))

        # Check if within window (before or after reference)
        if abs(event_time - reference_time) <= window_delta:
            filtered.append(event)

    return filtered
```

### Geographic Bounding Box Intersection
```python
# Source: Shapely docs - https://shapely.readthedocs.io/en/stable/reference/shapely.intersection.html
from shapely.geometry import Point, box

def check_point_in_region(lat, lon, region_name):
    """Check if point falls within predefined region bounding box."""
    regions = {
        'Taiwan Strait': box(118, 23, 122, 26),  # lon_min, lat_min, lon_max, lat_max
        'South China Sea': box(105, 5, 120, 23)
    }

    point = Point(lon, lat)
    region_bbox = regions.get(region_name)

    if not region_bbox:
        return False

    return region_bbox.contains(point)
```

### Async Batch Processing with Supabase
```python
# Source: Existing project pattern from src/processors/batch_articles.py
import asyncio
from src.database.client import get_supabase

async def write_correlation_event(correlation_data):
    """Write correlation event to database."""
    client = await get_supabase()

    response = await client.table("correlation_events").insert({
        'narrative_event_id': correlation_data['narrative_id'],
        'movement_event_ids': correlation_data['movement_ids'],
        'composite_score': correlation_data['composite_score'],
        'sub_scores': correlation_data['sub_scores'],  # JSONB column
        'detected_at': datetime.now(timezone.utc).isoformat()
    }).execute()

    return response.data[0] if response.data else None
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| String-based state comparison | Enum with type safety | Python 3.4+ (enum stdlib) | Catch typos at development time, not runtime |
| Manual geospatial loops | GeoPandas vectorized operations + spatial indexing | GeoPandas 0.8+ (2020) | O(n²) → O(n log n) with STRtree |
| Sync database queries | Async/await with asyncio | Python 3.7+ (stable asyncio) | Non-blocking I/O for batch processing |
| Z-score normalization for bounded scores | Min-max normalization to 0-100 | Modern practice for interpretable scores | Sub-scores directly comparable, analyst-friendly |

**Deprecated/outdated:**
- **GeoPandas 0.x spatial joins:** Pre-0.10 lacked `sjoin_nearest()`; required manual distance matrix. Current version (1.0+) has built-in nearest neighbor join.
- **Supabase sync client:** `create_client()` is sync-only, lacks realtime. Project uses `acreate_client()` for async support (critical for FastAPI).

## Open Questions

### 1. False Positive Rate Baseline
**What we know:** User requirement from STATE.md: "Statistical baseline calibration... false positive rate must be validated against real data during Phase 3 testing." Demo data has artificial clean escalation.

**What's unclear:** Without real-world baseline (normal Taiwan Strait activity with no actual threat), threshold tuning (GREEN < 30, AMBER 30-70, RED > 70) is guesswork. How to validate?

**Recommendation:**
- **Phase 3 scope:** Implement correlation with configurable thresholds (environment variables or config file)
- **Post-Phase 3:** Collect 30-day baseline from real feeds, calculate score distribution, tune thresholds for 5% false positive rate
- **For now:** Document thresholds as "tuned for demo scenario" with LOW confidence

### 2. Evidence Storage: References vs. Denormalized Snapshots
**What we know:** User marked as "Claude's discretion" in CONTEXT.md - "decide between foreign key references only vs denormalized snapshots based on brief generator and dashboard query needs."

**What's unclear:** Brief generator (Phase 4) needs article text, post content, vessel positions to create narrative. If source records are deleted/updated, foreign keys break evidence chain.

**Recommendation:**
- **For Phase 3:** Use foreign key references (`narrative_event_id`, `movement_event_ids[]`) - simpler, avoids data duplication
- **Prepare for Phase 4:** Add `evidence_snapshot` JSONB column to alerts table for denormalized copy of key fields (title, text snippets, coordinates)
- **Tradeoff:** Foreign keys = live data, but brittle; snapshots = stable evidence, but stale if source updates

### 3. Correlation Event vs. Alert Table Design
**What we know:** Requirements mention both "correlation events" (detected matches) and "alerts" (threat-level assessments). Schema has `alerts` table. Should correlation events be separate table?

**What's unclear:** One alert can be updated by multiple correlation events over time (consolidated escalating alert). Should we store intermediate correlation events or just update alert directly?

**Recommendation:**
- **Single table approach:** Write directly to `alerts` table with `correlation_metadata` JSONB column containing sub-scores and matched event IDs
- **Two table approach:** Create `correlation_events` table (detection log), then `alerts` references most recent correlation
- **For Phase 3:** Single table (simpler); two-table if audit trail of all correlations (not just current alert state) is needed for calibration analysis

## Sources

### Primary (HIGH confidence)
- GeoPandas Official Documentation - Geometric Manipulations: https://geopandas.org/en/stable/docs/user_guide/geometric_manipulations.html
- GeoPandas Official Documentation - Merging Data (sjoin_nearest): https://geopandas.org/en/stable/docs/user_guide/mergingdata.html
- Shapely Official Documentation - Intersection Function: https://shapely.readthedocs.io/en/stable/reference/shapely.intersection.html
- Python Official Documentation - datetime module: https://docs.python.org/3/library/datetime.html
- Python Official Documentation - enum module: https://docs.python.org/3/library/enum.html
- Python Official Documentation - asyncio module: https://docs.python.org/3/library/asyncio.html

### Secondary (MEDIUM confidence)
- [Distance and proximity analysis in Python – WALKER DATA](https://walker-data.com/posts/proximity-analysis/)
- [12 Python Libraries for Geospatial Data Analysis | Geoapify](https://www.geoapify.com/python-geospatial-data-analysis/)
- [Normalization: Min-Max and Z-Score Normalization | Codecademy](https://www.codecademy.com/article/normalization)
- [python-statemachine Documentation - States](https://python-statemachine.readthedocs.io/en/latest/states.html)
- [3 essential async patterns for building a Python service | Elastic Blog](https://www.elastic.co/blog/async-patterns-building-python-service)

### Tertiary (LOW confidence - WebSearch only)
- [Event-Driven vs. Batch Processing: Choose the Right Approach](https://datanimbus.com/blog/event-driven-vs-batch-processing-choosing-the-right-approach-for-your-data-platform/) - General architectural guidance, not Python-specific
- [Algorithm Perception When Using Threat Intelligence in Vulnerability Risk Assessment - Wiley](https://onlinelibrary.wiley.com/doi/10.1111/risa.70178?af=R) - Academic paper on threat intelligence scoring, requires verification with project needs
- [Time Series Pattern Recognition with Air Quality Sensor Data | Towards Data Science](https://towardsdatascience.com/time-series-pattern-recognition-with-air-quality-sensor-data-4b94710bb290/) - Blog post on pattern matching, needs official library docs verification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - GeoPandas, Shapely, datetime verified with official docs; patterns match existing project structure
- Architecture: MEDIUM - Batch processing pattern from existing codebase (HIGH), but correlation-specific patterns untested with demo data (MEDIUM)
- Pitfalls: MEDIUM - CRS and timezone issues documented in official sources (HIGH), but false positive baseline and threshold tuning unverified without real data (LOW)
- Composite scoring: MEDIUM - Min-max normalization is standard practice (multiple sources agree), but weight values (outlet=0.30, phrase=0.25, etc.) are informed guesses requiring calibration (LOW)

**Research date:** 2026-02-07
**Valid until:** 2026-03-07 (30 days) - GeoPandas/Shapely are stable libraries; asyncio patterns are mature. Threat intelligence scoring methodologies may evolve, but core geospatial and temporal correlation approaches are established.

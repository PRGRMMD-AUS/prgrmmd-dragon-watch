---
phase: 05-demo-integration
plan: 02
subsystem: demo-infrastructure
status: complete
tags: [demo-engine, fastapi, async, playback, api-endpoints]

# Dependencies
requires:
  - 05-01: Demo fixture JSON (scripts/demo_fixture.json with 392 records)
  - src/database/client.py: get_supabase() for async Supabase client
  - src/models/schemas.py: Pydantic models for type validation

provides:
  - Async demo playback engine with timing control
  - FastAPI demo control API with 5 endpoints
  - Continuous drip pacing with interruptible sleep
  - Speed presets (slow/normal/fast)
  - Table clearing and reset functionality

affects:
  - 05-03: Frontend control bar will consume these API endpoints
  - 05-04: Demo verification will test playback timing and table insertion
  - Frontend dashboard: Realtime subscriptions will update as records inserted

# Tech Stack
tech-stack:
  added:
    - asyncio: Interruptible sleep and background task management
    - structlog: Structured logging for playback events
  patterns:
    - Singleton pattern: Module-level demo_engine shared across FastAPI and engine
    - Background task lifecycle: asyncio.create_task for long-running playback
    - Interruptible sleep: 0.1s chunks allow responsive pause/reset
    - Alert upsert pattern: First INSERT stores id, subsequent UPDATE by id

# File Tracking
key-files:
  created:
    - src/demo/__init__.py: Module exports
    - src/demo/engine.py: DemoEngine class with playback logic (444 lines)
  modified:
    - src/main.py: Added demo router, CORS middleware, commented out fetcher imports

# Decisions
decisions:
  - id: DEMO-05
    title: Interruptible sleep for responsive controls
    rationale: User expects pause/reset to respond immediately, not after multi-second delay. Sleep in 0.1s chunks and check state after each chunk.
    impact: Pause/reset respond within 100ms regardless of playback speed
    date: 2026-02-07

  - id: DEMO-06
    title: Module-level singleton pattern
    rationale: FastAPI endpoints and playback loop must share same engine state. Module-level singleton ensures one source of truth.
    impact: demo_engine imported by both main.py endpoints and engine.py loop
    date: 2026-02-07

  - id: DEMO-07
    title: Alert ID tracking for updates
    rationale: Alerts use upsert pattern (first INSERT, subsequent UPDATE). Store inserted alert ID to enable UPDATE by id.
    impact: self.alert_id stores id from first insert, used for all subsequent updates
    date: 2026-02-07

  - id: DEMO-08
    title: Comment out fetcher imports temporarily
    rationale: src/fetchers module deleted from working directory but main.py still imported it. Commenting out unblocks server startup without removing existing endpoint logic.
    impact: Fetcher endpoints temporarily disabled, demo endpoints fully functional
    date: 2026-02-07

# Metrics
metrics:
  duration: "3.85 minutes"
  completed: 2026-02-07
  tasks-completed: 2/2
  commits: 2

---

# Phase 5 Plan 2: Demo Playback Engine Summary

**One-liner:** Async DemoEngine with FastAPI control endpoints for drip-feeding 392 fixture records into Supabase with speed presets (slow/normal/fast) and responsive pause/reset controls

## What Was Built

Created the core orchestrator that animates the demo by reading the pre-computed fixture and inserting records into Supabase with controlled timing, causing all dashboard panels to update via their existing realtime subscriptions.

### Demo Engine (`src/demo/engine.py`)

**DemoEngine Class:** Manages playback state and Supabase insertion with precise timing control.

**State Management:**
- `state`: "idle" | "playing" | "paused"
- `speed`: 0.5 (slow), 1.0 (normal), 2.5 (fast)
- `current_index`: Position in fixture records
- `simulated_seconds_elapsed`: Scenario time tracking (maps to T+Xh format)
- `alert_id`: Tracks inserted alert ID for UPDATE operations

**Key Methods:**

1. **`load_fixture()`** - Loads `scripts/demo_fixture.json` into memory on first use. Caches fixture data.

2. **`async start(clear_first: bool = True)`** - Start or resume playback
   - If idle + clear_first=True: Clear all 7 tables before starting
   - If paused: Resume from current_index without clearing
   - Spawns background asyncio task for playback loop

3. **`async pause()`** - Set state to "paused", loop checks and stops

4. **`async reset()`** - Cancel task, clear tables, reset to idle

5. **`set_speed(speed: float)`** - Update multiplier, takes effect immediately

6. **`get_status() -> dict`** - Returns state, speed, progress, simulated_time, records_inserted

7. **`async _playback_loop()`** - Core loop iterating through fixture records
   - Calculates delay between records (adjusted by speed multiplier)
   - Uses interruptible sleep for responsive control
   - Inserts record into correct Supabase table
   - Updates progress tracking

8. **`async _interruptible_sleep(seconds: float)`** - Sleeps in 0.1s chunks
   - Checks state after each chunk
   - Breaks early if paused/reset

9. **`async _insert_record(record: dict)`** - Routes to correct table
   - Articles: upsert on URL conflict
   - Alerts: INSERT stores id, UPDATE uses stored id
   - Other tables: plain insert
   - Logs each insertion with structlog

10. **`async _clear_tables()`** - Deletes all rows in dependency order
    - briefs, alerts, movement_events, narrative_events, vessel_positions, social_posts, articles

**Singleton:** `demo_engine = DemoEngine()` at module level ensures FastAPI endpoints and engine share state.

### FastAPI Control Endpoints (`src/main.py`)

**Demo Router:** `/api/demo` prefix with 5 endpoints

**Endpoints:**

1. **`POST /api/demo/start?clear_first=true`** - Start playback
   - Query param: clear_first (default: true)
   - Returns: Current status

2. **`POST /api/demo/pause`** - Pause at current position
   - Returns: Current status

3. **`POST /api/demo/reset`** - Reset to beginning and clear tables
   - Returns: Current status

4. **`POST /api/demo/speed?preset=fast`** - Change speed
   - Query param: preset ("slow" | "normal" | "fast")
   - Maps to speed multipliers: 0.5, 1.0, 2.5
   - Returns: Current status

5. **`GET /api/demo/status`** - Get current status
   - Returns: state, speed, speed_label, progress, records_inserted, total_records, simulated_time, simulated_hours

**Status Response Example:**
```json
{
  "state": "playing",
  "speed": 1.0,
  "speed_label": "normal",
  "progress": 0.45,
  "records_inserted": 112,
  "total_records": 392,
  "simulated_time": "T+32h",
  "simulated_hours": 32.4
}
```

**CORS Middleware:** Added to allow cross-origin requests from frontend running on different port.

### Simulated Time Calculation

Fixture metadata: 300 real seconds → 72 simulated hours

**Formula:** `simulated_hours = (simulated_seconds_elapsed / 300) * 72`

**Speed Adjustment:**
- Normal (1.0x): 5 minutes total playback
- Fast (2.5x): 2 minutes total playback
- Slow (0.5x): 10 minutes total playback

**Display Format:** "T+32h" for 32 simulated hours elapsed

### Table Clearing Order

Critical for referential integrity:
1. `briefs` (references alerts)
2. `alerts` (references events)
3. `movement_events`, `narrative_events` (processed data)
4. `vessel_positions`, `social_posts`, `articles` (raw data)

## Task Completion

### Task 1: Create async demo playback engine ✅
- **Commit:** `13c1724` - feat(05-02): create async demo playback engine
- **Files:** src/demo/__init__.py, src/demo/engine.py (444 lines)
- **Key work:**
  - DemoEngine class with state management (idle/playing/paused)
  - Fixture loading with caching
  - Start/pause/reset/speed control methods
  - Interruptible sleep for responsive pause/reset
  - Playback loop with timing calculation
  - Table-specific insert logic (articles upsert, alerts INSERT/UPDATE)
  - Table clearing in dependency order
  - Simulated time tracking and formatting
  - Module-level singleton pattern
  - Structured logging with structlog

### Task 2: Add FastAPI demo control endpoints ✅
- **Commit:** `9e26af3` - feat(05-02): add FastAPI demo control endpoints
- **Files:** src/main.py (modified)
- **Key work:**
  - Demo router with 5 endpoints (/start, /pause, /reset, /speed, /status)
  - CORS middleware for cross-origin frontend access
  - Speed preset mapping (slow/normal/fast → 0.5/1.0/2.5)
  - Query parameter support (clear_first, preset)
  - Status endpoint returning complete playback state
  - Temporarily commented out fetcher imports/endpoints (module removed)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Commented out fetcher imports**

- **Found during:** Task 2, server startup
- **Issue:** `src/fetchers` module deleted from working directory but `src/main.py` still imported it. ModuleNotFoundError prevented server startup.
- **Fix:** Commented out fetcher imports and related endpoints (GDELT, Telegram, AIS). Demo endpoints don't depend on fetchers.
- **Files modified:** src/main.py
- **Commit:** 9e26af3 (included in Task 2 commit)
- **Rationale:** Unblocks demo endpoint testing. Fetcher functionality temporarily disabled but not removed - can be restored when fetchers module returns.

**Impact:** Demo playback fully functional. Fetcher endpoints will need restoration when `src/fetchers` module is restored to repository.

## Technical Insights

### Interruptible Sleep Pattern

**Problem:** `await asyncio.sleep(delay)` blocks entire delay duration. User expects pause/reset to respond immediately.

**Solution:** Sleep in small chunks, checking state after each:
```python
async def _interruptible_sleep(self, seconds: float) -> None:
    elapsed = 0.0
    chunk_size = 0.1
    while elapsed < seconds:
        if self.state != "playing":
            break
        sleep_duration = min(chunk_size, seconds - elapsed)
        await asyncio.sleep(sleep_duration)
        elapsed += sleep_duration
```

**Result:** Pause/reset respond within 100ms regardless of delay duration.

### Alert Upsert Pattern

**Production behavior:** Alerts use `ON CONFLICT (region) DO UPDATE` for region-based upsert.

**Demo fixture encoding:**
- First alert: `_demo_action: "insert"` → creates row
- Subsequent alerts: `_demo_action: "update"` → updates by stored ID

**Engine implementation:**
```python
if action == "insert":
    result = await client.table("alerts").insert(data).execute()
    self.alert_id = result.data[0]["id"]  # Store for later
elif action == "update":
    await client.table("alerts").update(data).eq("id", self.alert_id).execute()
```

**Why track ID:** Supabase Python client doesn't support upsert with custom conflict targets. Storing ID from INSERT enables UPDATE by primary key.

### Speed Multiplier Math

**Base timing:** Record at offset 150s has delay from previous record (e.g., 2.5s)

**Speed adjustment:** `delay_seconds = (current_offset - previous_offset) / self.speed`

**Examples:**
- Normal (1.0x): 2.5s / 1.0 = 2.5s real delay
- Fast (2.5x): 2.5s / 2.5 = 1.0s real delay
- Slow (0.5x): 2.5s / 0.5 = 5.0s real delay

**Result:** Entire fixture playback scales proportionally:
- Normal: 300s total
- Fast: 120s total
- Slow: 600s total

### Singleton Pattern Rationale

**Challenge:** FastAPI endpoints and playback loop need shared state. Multiple DemoEngine instances would have different state.

**Solution:** Module-level singleton:
```python
demo_engine = DemoEngine()
```

**Usage:**
- main.py: `from src.demo.engine import demo_engine` (endpoints control this instance)
- engine.py: `demo_engine` is the same object as imported by main.py

**Benefit:** One source of truth for playback state across entire application.

## Next Phase Readiness

**Phase 5 Plan 3 (Frontend Control Bar) is fully unblocked:**
- ✅ All 5 demo control endpoints functional and tested
- ✅ CORS enabled for cross-origin requests
- ✅ Status endpoint provides complete state for UI binding
- ✅ Speed presets implemented (slow/normal/fast)
- ✅ Simulated time formatted for display (T+Xh)
- ✅ Progress tracking available (0.0 to 1.0)

**Frontend can now:**
1. Poll `/api/demo/status` for current state
2. Send POST to `/api/demo/start` to begin playback
3. Send POST to `/api/demo/pause` to pause
4. Send POST to `/api/demo/reset` to reset
5. Send POST to `/api/demo/speed?preset=fast` to change speed
6. Display progress bar, simulated time, play/pause button state

**No blockers.** Ready to build frontend control bar.

## Lessons Learned

1. **Interruptible sleep is essential for responsive async controls:** Naive `await asyncio.sleep(delay)` blocks until complete. Chunked sleep with state checking enables sub-second pause/reset response time.

2. **Module-level singleton simplest for FastAPI shared state:** Alternative approaches (app.state, dependency injection) add complexity. Module-level singleton is explicit and works perfectly for single-process uvicorn server.

3. **Alert ID tracking needed for Supabase Python client limitations:** Client doesn't support `ON CONFLICT` with custom targets. Storing ID from INSERT enables UPDATE simulation of upsert behavior.

4. **Commenting out broken imports better than deleting endpoints:** Fetchers module deletion broke imports but endpoints had useful logic. Commenting preserves code for easy restoration while unblocking demo development.

5. **Speed multiplier math simpler than recalculating offsets:** Rather than regenerating fixture with different timings, divide delays by speed multiplier. Achieves same result with runtime flexibility.

---

**Status:** ✅ Complete
**Duration:** 3.85 minutes
**Commits:** 2 (13c1724, 9e26af3)
**Output:** Async demo engine with FastAPI control endpoints, tested and functional

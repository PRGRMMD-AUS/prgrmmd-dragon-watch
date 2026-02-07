# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-07)

**Core value:** Correlation of state media narrative coordination with civilian movement indicators provides pre-conflict warning hours before official announcements — a capability no existing OSINT vendor offers.
**Current focus:** Phase 2 - Intelligence Processing

## Current Position

Phase: 2 of 5 (Intelligence Processing)
Plan: 0 of 4 in current phase
Status: Not started (phase needs planning)
Last activity: 2026-02-07 — Completed Phase 1 (Foundation) — all 4 plans executed

Progress: [██░░░░░░░░] 20% (1/5 phases completed)

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: 2.75 minutes
- Total execution time: 0.18 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 1 | 4/4 | 11 min | 2.75 min |

**Recent Trend:**
- Last 5 plans: 01-01 (2 min), 01-02 (3 min), 01-03 (3 min), 01-04 (3 min)
- Trend: Consistent velocity, stable at ~3 min/plan

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Lovable for frontend, not Streamlit (better visual quality, decoupled via Supabase realtime)
- Supabase as middleware layer (managed Postgres + built-in realtime subscriptions)
- Simulated data first, live feeds second (demo reliability paramount)
- Claude for narrative analysis, GPT-4o Mini for bulk classification (cost optimization)
- GDELT over direct media scraping (free, no auth, 15-min updates)
- Use acreate_client() for async Supabase client (01-01: sync client lacks realtime support)
- Separate Create and Row Pydantic models per table (01-01: clearer type safety for insert vs read)
- Use domain_exact not domain in GDELT filters (01-02: partial matching causes false positives)
- Lazy initialization for Telegram client (01-02: allows import without credentials, better error messages)
- Programmatic Python loader over SQL-only for demo data (01-03: validates through Pydantic, more flexible)
- Taiwan Strait bounding box 23-26N, 118-122E (01-03: prevents AISstream message overflow)
- 72-hour GREEN/AMBER/RED escalation scenario (01-03: shows clear pattern progression for demo)
- asyncio.create_task for AIS stream, BackgroundTasks for one-shot fetchers (01-04: lifecycle management)

### Pending Todos

None yet.

### Blockers/Concerns

**Phase 1 (resolved 01-01):** Package version validation required — verified supabase>=2.27.3, pydantic>=2.0 install successfully on Python 3.13.

**Phase 1 (pending):** User must manually set REPLICA IDENTITY FULL on all 7 tables after migration (requires Supabase SQL Editor access, cannot be automated).

**Phase 1 (pending - now in code):** GDELT Chinese state media coverage needs validation during first fetch — verify Xinhua, Global Times, CCTV, People's Daily actually indexed (01-02: fetcher implemented with TODO comment for tone score).

**Phase 1 (pending):** User must obtain Telegram API credentials (api_id, api_hash) from https://my.telegram.org/apps before Telegram scraper can run (01-02: see 01-02-USER-SETUP.md).

**Phase 1 (pending):** User must obtain AISstream API key from https://aisstream.io before AIS tracker can connect (01-03: see 01-03-USER-SETUP.md). Note: Demo dataset does NOT require this - only live vessel tracking needs it.

**Phase 2:** Novel prompt engineering for narrative coordination detection (sparse public examples) — may require iteration during Phase 2 LLM wrapper development.

**Phase 3:** Statistical baseline calibration for correlation engine — false positive rate must be validated against real data during Phase 3 testing.

**Phase 4:** Lovable-generated code quality for Supabase realtime unknown — schedule early integration testing at Phase 4 start to catch issues.

## Session Continuity

Last session: 2026-02-07 (phase execution)
Stopped at: Completed Phase 1 (Foundation) — all 4 plans, 8 commits, 2041 lines of code
Resume file: None

---
*State initialized: 2026-02-07*
*Last updated: 2026-02-07*

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-07)

**Core value:** Correlation of state media narrative coordination with civilian movement indicators provides pre-conflict warning hours before official announcements — a capability no existing OSINT vendor offers.
**Current focus:** Phase 4 Complete — ready for Phase 5

## Current Position

Phase: 5 of 5 (Demo Integration)
Plan: 0 of TBD in current phase
Status: Not started
Last activity: 2026-02-07 — Phase 4 approved by user, all 5 dashboard zones working

Progress: [██████████████░] 82% (14/17 plans completed)

## Performance Metrics

**Velocity:**
- Total plans completed: 14
- Average duration: ~3.0 minutes
- Total execution time: ~1.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 1 | 4/4 | 11 min | 2.75 min |
| Phase 2 | 4/4 | 20 min | 5 min |
| Phase 3 | 3/3 | 7.1 min | 2.4 min |
| Phase 4 | 4/4 | 13.85 min | 3.46 min |

**Recent Trend:**
- Last 5 plans: 04-01 (3 min), 04-02 (3 min), 04-03 (4 min), 04-04 (3.85 min)
- Trend: Phase 4 complete. UI tasks average 3.46 min (slightly above overall 3.0 min average due to component complexity)

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
- Monotonic threat escalation only (03-01: prevents correlation engine flip-flopping)
- Shapely over GeoPandas for single-region containment (03-01: avoids heavyweight GDAL/GEOS dependencies)
- Confidence capped at 95% max (03-01: always acknowledge OSINT correlation uncertainty)
- Separate correlation and LLM ThreatLevel enums (03-01: different purposes, different implementations)
- 72-hour correlation window for narrative-movement matching (03-02: matches demo scenario timeline)
- Weight sub-scores as outlet(30%), phrase(25%), volume(20%), geo(25%) (03-02: prioritize outlet coordination signal)
- Geographic match requires BOTH narrative focus AND movement coordinates (03-02: prevents false positives from partial matches)
- Normalize with tuned ranges: outlets 1-4, phrases 0-10, volume 0-50 (03-02: calibrated to demo data)
- Synthetic event fallback enables demo without Phase 2 LLM API keys (03-03: developer experience)
- Pure logic verification tests require no Supabase connection (03-03: fast feedback loop)
- Tailwind CSS v3 with @tailwindcss/vite plugin (04-01: cleaner configuration than separate config file)
- Manual shadcn/ui dependencies install (04-01: avoids interactive prompts)
- CSS Grid with grid-template-areas for dashboard layout (04-01: named zones for clarity)
- Light theme (white/gray-50) for dashboard (04-01: modern SaaS analytics feel, not dark command center)
- Threat banner pulse animation on escalation (04-02: Tailwind animate-pulse for 2 seconds when level changes)
- Map fixed to Taiwan Strait view with disabled interaction (04-02: display panel not exploration tool)
- Vessel markers as rotated SVG triangles (04-02: show directional heading from course field)
- Heatmap layer below vessel markers (04-02: movement event density visualization)
- Narrative regions from keyword extraction (04-02: simple keyword-to-polygon mapping, no geocoding API)
- Fallback SVG map without Mapbox token (04-02: developer experience, works without account)
- Temporal matching for movement events (04-03: 5-minute window for post-to-event association, acceptable for demo)
- Coordination signals via narrative_events.source_ids Set (04-03: O(1) lookup for purple "COORDINATED" badge)
- Interleaved feed sorted by timestamp (04-03: unified intelligence flow regardless of source)
- Recharts ComposedChart for timeline (04-03: area chart + scatter overlay for threat score and narrative events)
- Brief type fix: evidence_chain is string[] not Record, timeline is string not Record (04-04: matches Python IntelligenceBrief schema)
- Slate palette for consistency (04-04: replaced gray-* with slate-* for professional SaaS appearance)
- Typography hierarchy: headers (text-slate-500), body (text-slate-700), metadata (text-slate-400) (04-04: semantic visual hierarchy)
- Inter font from Google Fonts (04-04: modern screen-readable typeface for analytics dashboard)

### Pending Todos

None yet.

### Blockers/Concerns

**Phase 1 (resolved 01-01):** Package version validation required — verified supabase>=2.27.3, pydantic>=2.0 install successfully on Python 3.13.

**Phase 1 (pending):** User must manually set REPLICA IDENTITY FULL on all 7 tables after migration (requires Supabase SQL Editor access, cannot be automated).

**Phase 1 (pending - now in code):** GDELT Chinese state media coverage needs validation during first fetch — verify Xinhua, Global Times, CCTV, People's Daily actually indexed (01-02: fetcher implemented with TODO comment for tone score).

**Phase 1 (pending):** User must obtain Telegram API credentials (api_id, api_hash) from https://my.telegram.org/apps before Telegram scraper can run (01-02: see 01-02-USER-SETUP.md).

**Phase 1 (pending):** User must obtain AISstream API key from https://aisstream.io before AIS tracker can connect (01-03: see 01-03-USER-SETUP.md). Note: Demo dataset does NOT require this - only live vessel tracking needs it.

**Phase 2:** Novel prompt engineering for narrative coordination detection (sparse public examples) — may require iteration during Phase 2 LLM wrapper development.

**Phase 3 (active):** Statistical baseline calibration for correlation engine — current normalization ranges tuned to demo data (4 outlets, 10 phrases, 50 posts). Production deployment MUST recalibrate with historical baseline from real GDELT/Telegram feeds. False positive rate unknown until validated against ground truth.

**Phase 3 (resolved 03-03):** Alert schema compatibility — verified all required fields (threat_level, threat_score, confidence, sub_scores, correlation_metadata) exist and populate correctly during upsert. Demo script confirms schema works.

**Phase 4 (resolved 04-01):** Lovable-generated code quality for Supabase realtime unknown — built custom React project with Vite instead, implemented generic useRealtimeSubscription hook with full TypeScript types. Direct control over realtime integration.

**Phase 4 (pending):** Optional Mapbox token setup for full map rendering — fallback SVG works without token but production deployment should set VITE_MAPBOX_TOKEN for Mapbox Light style. Get token from https://account.mapbox.com/access-tokens/

## Session Continuity

Last session: 2026-02-07 (phase execution)
Stopped at: Phase 4 complete. Ready for Phase 5 (Demo Integration).
Resume file: None

---
*State initialized: 2026-02-07*
*Last updated: 2026-02-07 (Phase 4 complete, approved by user)*

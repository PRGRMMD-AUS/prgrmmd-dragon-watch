# Roadmap: Dragon Watch

## Overview

Dragon Watch builds from data ingestion through LLM-powered intelligence processing to real-time visualization and demo reliability. The journey starts with establishing Supabase schema and multi-source data pipelines (Phase 1), processes raw data into narrative and movement intelligence streams (Phase 2), correlates those streams to detect threats (Phase 3), visualizes the intelligence in real-time (Phase 4), and wraps everything in a reliable demo experience (Phase 5). Each phase delivers a coherent capability that unblocks the next, optimized for 48-hour hackathon execution.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - Supabase schema and multi-source data ingestion
- [x] **Phase 2: Intelligence Processing** - LLM-powered narrative and movement analysis
- [x] **Phase 3: Correlation Engine** - Dual-stream threat detection
- [ ] **Phase 4: Visualization** - Real-time dashboard with all panels
- [ ] **Phase 5: Demo Integration** - Playback engine and offline reliability

## Phase Details

### Phase 1: Foundation
**Goal**: Data flows from all sources into Supabase tables with realtime enabled
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05
**Success Criteria** (what must be TRUE):
  1. Supabase schema exists with all tables (articles, social_posts, vessel_positions, narrative_events, movement_events, alerts, briefs) and realtime subscriptions enabled
  2. GDELT fetcher queries Chinese state media domains and writes articles with tone scores to Supabase
  3. Telegram scraper pulls messages from OSINT channels and writes to Supabase
  4. AIS vessel tracker receives WebSocket data for Taiwan Strait and writes positions to Supabase
  5. Simulated Taiwan Strait demo dataset (50+ articles, 100+ posts, AIS data) loaded and available in Supabase
**Plans**: 4 plans

Plans:
- [x] 01-01-PLAN.md — Project scaffolding, Supabase schema, Pydantic models, async DB client
- [x] 01-02-PLAN.md — GDELT article fetcher and Telegram OSINT scraper
- [x] 01-03-PLAN.md — AIS WebSocket vessel tracker and simulated demo dataset
- [x] 01-04-PLAN.md — FastAPI app wiring and integration verification

### Phase 2: Intelligence Processing
**Goal**: Raw data is processed into structured intelligence events with LLM-powered analysis
**Depends on**: Phase 1 (requires data in Supabase)
**Requirements**: LLM-01, LLM-02, LLM-03, LLM-04
**Success Criteria** (what must be TRUE):
  1. Narrative coordination detector analyzes article batches and writes coordination scores (0-100) with synchronized phrasing themes to narrative_events table
  2. Civilian post classifier processes social posts and writes military-relevant classifications (convoy, naval, flight, restricted zone) with locations and confidence to movement_events table
  3. Entity extraction pulls structured data (military units, equipment types, locations with lat/lon, timestamps) from unstructured text
  4. Intelligence brief generator produces formatted assessments with threat level, confidence, evidence chain, timeline, and collection priorities
**Plans**: 4 plans

Plans:
- [ ] 02-01-PLAN.md — LLM foundation: config, Pydantic schemas, async clients, retry/logging utilities
- [ ] 02-02-PLAN.md — Narrative coordination detector (LLM-01) + entity extraction (LLM-03) + batch article pipeline
- [ ] 02-03-PLAN.md — Civilian post classifier (LLM-02) + batch post pipeline
- [ ] 02-04-PLAN.md — Intelligence brief generator (LLM-04) + brief generation pipeline

### Phase 3: Correlation Engine
**Goal**: Two independent intelligence streams converge to produce threat-level alerts
**Depends on**: Phase 2 (requires narrative_events and movement_events)
**Requirements**: CORR-01, CORR-02, CORR-03, CORR-04
**Success Criteria** (what must be TRUE):
  1. Time-window matching detects narrative coordination spike within 72 hours of movement cluster and triggers correlation
  2. Geographic proximity scoring calculates when narrative geographic focus matches movement cluster region
  3. Threat level calculation produces GREEN (<30) / AMBER (30-70) / RED (>70) scores based on outlet count, phrase novelty, post volume, and geographic proximity
  4. Each alert links to specific articles and posts that triggered it, creating complete evidence chains
**Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — Foundation types: ThreatLevel enum, correlation Pydantic models, geographic utilities
- [x] 03-02-PLAN.md — Core correlation engine: time-window matching, composite scoring, alert upsert with monotonic escalation
- [x] 03-03-PLAN.md — Integration verification: demo runner and Phase 3 requirement verification scripts

### Phase 4: Visualization
**Goal**: Real-time intelligence flows to dashboard panels via Supabase realtime subscriptions
**Depends on**: Phase 3 (requires alerts and correlation_events to display)
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06
**Success Criteria** (what must be TRUE):
  1. Interactive map displays Taiwan Strait with movement markers, vessel icons, heatmap overlay, and narrative focus regions
  2. Narrative correlation timeline (bottom panel) shows threat score building over time with color-coded GREEN/AMBER/RED zones and narrative event data points (replaces dual-axis chart per user decision — DASH-02 is now "narrative timeline")
  3. Narrative stream feed displays real-time scrollable articles with coordination signals highlighted
  4. Movement stream feed displays real-time scrollable posts with location and category tags
  5. Threat gauge displays current GREEN/AMBER/RED status with confidence score and auto-updates from alerts table
  6. Intelligence brief panel displays formatted LLM-generated assessment with classification markings
**Plans**: 4 plans

Plans:
- [ ] 04-01-PLAN.md — Schema migration + React project scaffold + layout shell + Supabase client
- [ ] 04-02-PLAN.md — Threat status banner + Taiwan Strait map with vessel markers
- [ ] 04-03-PLAN.md — Event feed cards (left panel) + Narrative timeline (bottom panel)
- [ ] 04-04-PLAN.md — Intelligence brief sidebar + Visual polish + Human verification

### Phase 5: Demo Integration
**Goal**: Demo runs reliably GREEN to RED in 5 minutes with no live API dependencies
**Depends on**: Phase 4 (requires complete technical system)
**Requirements**: DEMO-01, DEMO-02, DEMO-03, DEMO-04, DEMO-05
**Success Criteria** (what must be TRUE):
  1. Demo playback engine steps through Taiwan Strait scenario at controlled speed, inserting time-sliced data with sequence control
  2. Live data tab shows real GDELT and Telegram data flowing through the pipeline (separate from demo, optional)
  3. Offline/fallback mode runs demo fully with pre-loaded data and cached LLM responses, no live API calls required
  4. All dashboard panels update via Supabase realtime subscriptions with proper sequencing (no race conditions)
  5. Demo scenario completes GREEN to RED escalation in approximately 5 minutes showing 24-48 hour simulated advance warning
**Plans**: TBD

Plans:
- [ ] TBD during phase planning

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2026-02-07 |
| 2. Intelligence Processing | 4/4 | Complete | 2026-02-07 |
| 3. Correlation Engine | 3/3 | Complete | 2026-02-07 |
| 4. Visualization | 0/4 | Not started | - |
| 5. Demo Integration | 0/TBD | Not started | - |

---
*Roadmap created: 2026-02-07*
*Last updated: 2026-02-07 (Phase 3 complete)*

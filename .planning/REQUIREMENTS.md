# Requirements: Dragon Watch

**Defined:** 2026-02-07
**Core Value:** Automated correlation of state media narrative coordination with civilian movement indicators provides pre-conflict warning hours before official announcements — a capability no existing OSINT vendor offers.

## v1 Requirements

### Data Ingestion

- [x] **DATA-01**: GDELT fetcher queries Chinese state media domains (Xinhua, Global Times, CCTV, People's Daily) and writes articles with tone scores to Supabase
- [x] **DATA-02**: Telegram scraper pulls messages from 5-10 public OSINT/military channels via Telethon and writes to Supabase
- [x] **DATA-03**: AIS vessel tracker connects to AISstream.io WebSocket, filters Taiwan Strait bounding box, writes positions to Supabase
- [x] **DATA-04**: Simulated Taiwan Strait demo dataset (50+ articles, 100+ civilian posts, AIS data) loaded in Supabase
- [x] **DATA-05**: Supabase schema with realtime enabled on all tables (articles, social_posts, vessel_positions, alerts, correlation_events, briefs)

### LLM Analysis

- [ ] **LLM-01**: Narrative coordination detector — Claude analyzes article batches for synchronized phrasing across outlets, scores coordination (0-100), extracts themes and geographic focus
- [ ] **LLM-02**: Civilian post classifier — GPT-4o Mini classifies posts as military-relevant (convoy, naval, flight, restricted zone), extracts location and confidence
- [ ] **LLM-03**: Entity extraction — structured data from text (military units, equipment types, locations with lat/lon, timestamps)
- [ ] **LLM-04**: Intelligence brief generator — produces formatted assessments with threat level, confidence, evidence chain, timeline, information gaps, collection priorities

### Correlation Engine

- [x] **CORR-01**: Time-window matching — narrative coordination spike within 72hrs of movement cluster triggers correlation
- [x] **CORR-02**: Geographic proximity scoring — narrative geographic focus matches movement cluster region
- [x] **CORR-03**: Threat level calculation — GREEN (<30) / AMBER (30-70) / RED (>70) based on outlet count, phrase novelty, post volume, geographic proximity
- [x] **CORR-04**: Evidence chain — each alert links to specific articles and posts that triggered it

### Dashboard (Lovable)

- [ ] **DASH-01**: Interactive map (Leaflet/Mapbox) centered on Taiwan Strait with movement markers, vessel icons, heatmap overlay, narrative focus regions
- [ ] **DASH-02**: Dual-axis correlation chart (Recharts) — narrative coordination score vs civilian movement count over time
- [ ] **DASH-03**: Narrative stream feed — real-time scrollable feed of state media articles with coordination signals highlighted
- [ ] **DASH-04**: Movement stream feed — real-time scrollable feed of classified posts with location and category tags
- [ ] **DASH-05**: Threat gauge (GREEN/AMBER/RED) with confidence score, auto-updates from alerts table
- [ ] **DASH-06**: Intelligence brief panel — formatted display of LLM-generated assessment with classification markings

### Demo & Integration

- [ ] **DEMO-01**: Demo playback engine steps through Taiwan Strait scenario at controlled speed, inserting time-sliced data into Supabase
- [ ] **DEMO-02**: Live data tab shows real GDELT + Telegram data flowing through the pipeline (separate from demo)
- [ ] **DEMO-03**: Offline/fallback mode — demo runs fully with pre-loaded data and cached LLM responses, no live API dependency
- [ ] **DEMO-04**: All dashboard panels update via Supabase realtime subscriptions (no polling)
- [ ] **DEMO-05**: Demo scenario plays GREEN → RED in ~5 minutes with ~24-48hr simulated advance warning

## v2 Requirements

### Notifications & Alerts

- **NOTF-01**: Email/SMS/webhook alerts on threat level escalation
- **NOTF-02**: Configurable alert thresholds per user
- **NOTF-03**: Alert history with acknowledgement tracking

### Multi-Region Support

- **REGION-01**: South China Sea monitoring region
- **REGION-02**: Korean Peninsula monitoring region
- **REGION-03**: User-configurable region definitions with custom media source lists

### Advanced Analytics

- **ANAL-01**: Historical playback of past escalation events
- **ANAL-02**: Statistical baseline calibration from 30-day rolling windows
- **ANAL-03**: Novelty scoring against historical phrase corpus
- **ANAL-04**: PDF export of intelligence briefs

### Authentication & Multi-User

- **AUTH-01**: User authentication via Supabase Auth
- **AUTH-02**: Role-based access (analyst, admin)
- **AUTH-03**: Audit log of analyst actions

## Out of Scope

| Feature | Reason |
|---------|--------|
| X/Twitter API integration | $200+/month, not justified for hackathon budget |
| TikTok Research API | Academic-only, weeks to approve |
| Weibo API | Requires Chinese SIM card |
| MarineTraffic API | No free tier |
| Custom LLM fine-tuning | No training data, inference-only approach faster |
| Dark web monitoring | Technical complexity, legal gray areas |
| Satellite imagery integration | API costs, complexity beyond 48-hour scope |
| Real-time global coverage | Scope explosion — demo focuses on Taiwan Strait |
| Conflict timing predictions | Impossible and ethically risky — system provides threat levels, not predictions |
| Mobile app | Web-first prototype, mobile later |
| Production deployment | Localhost demo sufficient for hackathon |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Complete |
| DATA-02 | Phase 1 | Complete |
| DATA-03 | Phase 1 | Complete |
| DATA-04 | Phase 1 | Complete |
| DATA-05 | Phase 1 | Complete |
| LLM-01 | Phase 2 | Pending |
| LLM-02 | Phase 2 | Pending |
| LLM-03 | Phase 2 | Pending |
| LLM-04 | Phase 2 | Pending |
| CORR-01 | Phase 3 | Complete |
| CORR-02 | Phase 3 | Complete |
| CORR-03 | Phase 3 | Complete |
| CORR-04 | Phase 3 | Complete |
| DASH-01 | Phase 4 | Pending |
| DASH-02 | Phase 4 | Pending |
| DASH-03 | Phase 4 | Pending |
| DASH-04 | Phase 4 | Pending |
| DASH-05 | Phase 4 | Pending |
| DASH-06 | Phase 4 | Pending |
| DEMO-01 | Phase 5 | Pending |
| DEMO-02 | Phase 5 | Pending |
| DEMO-03 | Phase 5 | Pending |
| DEMO-04 | Phase 5 | Pending |
| DEMO-05 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0

---
*Requirements defined: 2026-02-07*
*Last updated: 2026-02-07 (Phase 3 complete)*

# Project Research Summary

**Project:** Dragon Watch OSINT Pre-Conflict Early Warning System
**Domain:** Intelligence data fusion and real-time threat detection
**Researched:** 2026-02-07
**Confidence:** MEDIUM-HIGH

## Executive Summary

Dragon Watch is a dual-stream OSINT correlation system that detects pre-conflict warning signs by connecting state media narrative coordination with civilian-sourced military movement detection. Experts in this space build intelligence fusion platforms using independent stream processing architectures, LLM-powered pattern detection, and real-time data visualization. The system's core innovation is automated correlation between narrative signals (coordinated propaganda across Chinese state media) and movement signals (civilian reports of military activity), providing 24-48 hour advance warning before official announcements.

The recommended approach uses Python with FastAPI for async data pipelines, Supabase for Postgres + realtime subscriptions, and tiered LLM usage (GPT-4o Mini for bulk classification, Claude Sonnet for complex analysis). The architecture follows independent stream processing patterns where GDELT-sourced narrative analysis and Telegram/simulated civilian post classification operate as parallel pipelines, converging only at the correlation engine. This isolation prevents cascade failures and enables parallel development. The system must be designed for demo reliability from day one: pre-cached LLM responses, pre-scraped Telegram data, and synthetic demo scenarios are essential to survive the 48-hour hackathon constraint.

Key risks center on external API dependencies (LLM rate limits, Telegram FloodWait, GDELT data quality), correlation false positives from noisy baseline data, and frontend-backend integration complexity when using AI-generated React code (Lovable). Mitigation requires aggressive caching strategies, statistical baseline calibration instead of hardcoded thresholds, and early schema definition as a formal contract between backend and frontend teams. The demo narrative must be compelling — technical capability without operational context loses judges.

## Key Findings

### Recommended Stack

Python 3.11+ with FastAPI provides the async foundation required for concurrent data ingestion from multiple sources. Supabase handles both persistence and real-time subscriptions, eliminating the need for custom WebSocket infrastructure. The stack emphasizes cost-optimized LLM usage: Gemini/GPT for classification (cheap), Claude for analysis (expensive but necessary for complex reasoning).

**Core technologies:**
- **Python 3.11+ with FastAPI**: Async/await for concurrent data pipeline operations, WebSocket support for real-time feeds
- **Supabase (Postgres + Realtime)**: Free-tier friendly database with built-in pub/sub, eliminates custom WebSocket server overhead
- **Tiered LLM strategy**: GPT-4o Mini ($0.15/M tokens) for bulk classification, Claude Sonnet ($3/M) for narrative coordination detection
- **gdeltdoc + Telethon**: Purpose-built libraries for GDELT API and Telegram scraping, handle rate limiting and pagination
- **Lovable (React)**: AI-generated frontend for rapid UI development, pairs with Supabase realtime subscriptions

**Critical dependencies:**
- **Task orchestration**: APScheduler for MVP (in-process scheduling), Celery + Redis for production scaling
- **Data processing**: pandas for time-series correlation, spaCy for preprocessing to reduce LLM API costs
- **Dev tooling**: uv (fast package management), ruff (linting + formatting), pytest-asyncio (test async pipelines)

**Cost optimization patterns identified:**
1. Preprocessing layer (spaCy + langdetect) filters 70% of content before expensive LLM calls
2. LLM response caching prevents reprocessing identical inputs (critical for demos)
3. Batch processing (10-20 posts per LLM call) reduces per-request overhead
4. Token truncation (articles to 1K tokens, posts to 200 tokens) controls costs

**Version compatibility notes:** FastAPI 0.115+ requires Pydantic 2.x. Pandas 2.2 not yet compatible with NumPy 2.x. Telethon requires Python 3.11+ for native asyncio. All versions based on January 2025 training data — requires PyPI verification.

### Expected Features

Research identifies dual-stream correlation as the core differentiator: no existing vendor (Janes, Recorded Future, Dataminr) automatically correlates state narrative propaganda with civilian-sourced military movement. This is the product.

**Must have (table stakes):**
- **Dual-stream data ingestion**: GDELT for narrative, Telegram/simulated for movement — without both streams, correlation is impossible
- **Real-time visualization**: Map with event markers, timeline scrubber, traffic light threat gauge (GREEN/AMBER/RED) — users expect instant situation assessment
- **Source attribution**: Every detection links to originating article or social post — intelligence professionals require provenance
- **Threat level calculation**: Correlation algorithm with 72-hour window, geographic matching, produces actionable threat levels
- **Intelligence brief generation**: LLM-synthesized executive summary in realistic intelligence format

**Should have (competitive advantages):**
- **Centralized directive detection**: LLM analyzes state media for synchronized phrasing across outlets (the narrative signal)
- **Geolocation extraction from text**: LLM converts "near Xiamen" to lat/lon for map visualization
- **Temporal clustering**: 72-hour correlation window detects coordinated activity across time
- **Explainable AI scoring**: Shows why threat level changed (which signals triggered it) — transparency for analysts
- **Preemptive warning timeline**: Quantifiable metric: 24-48 hours before CNN/official sources

**Defer (v2+):**
- **Real Twitter/X ingestion**: Cost and rate limits prohibitive for MVP, assess after funding
- **Historical training corpus**: 20 years of GDELT for pattern learning requires infrastructure investment
- **Multi-region support**: Validate Taiwan Strait first, then expand to South China Sea, Korean Peninsula
- **Custom LLM fine-tuning**: Requires classified training data partnerships

**Anti-features (commonly requested but problematic):**
- Predicting exact conflict timing (creates false precision, legal/ethical risk)
- 100% automation without human review (false positives could trigger panic)
- Social media firehose ingestion (cost, noise, 48-hour timeline insufficient)
- Blockchain/dark web monitoring (tangential to core value)

### Architecture Approach

The system follows independent stream processing patterns where ingestion, analysis, and correlation are fully decoupled through the database. Each stream writes to Supabase independently; correlation engine reads from both. No shared state between streams prevents cascade failures and enables parallel development.

**Major components:**

1. **Ingestion Layer** (independent modules): GDELT fetcher polls DOC 2.0 API every 15 minutes, writes to `articles` table. Telegram scraper uses Telethon async iterator, writes to `social_posts` table. AIS listener receives WebSocket vessel positions, writes to `vessel_positions`. Simulated data loader pre-inserts demo scenarios. All write-only, no inter-dependencies.

2. **Processing Layer** (LLM-powered analysis): Narrative detector reads `articles`, uses Claude to identify coordinated phrasing, writes `narrative_events`. Post classifier reads `social_posts`, uses GPT-4o Mini for military relevance, writes `movement_events`. Entity extractor pulls structured data (locations, equipment, units) from text. All modules operate on database reads/writes only.

3. **Correlation Engine** (time-series analysis): Periodic job (every 6 hours) queries `narrative_events` and `movement_events` with 72-hour window and <500km geographic proximity. Statistical baseline comparison (current vs. 30-day mean + 2σ) determines anomaly. Writes `alerts` and triggers brief generation. This is the only cross-stream integration point.

4. **Realtime Middleware** (Supabase): Postgres tables with realtime subscriptions enabled. Backend writes trigger automatic WebSocket push to frontend. Database acts as both persistence and pub/sub event bus. Eliminates custom WebSocket server complexity.

5. **Presentation Layer** (Lovable React): Components subscribe to Supabase realtime channels. Map component (Leaflet), chart component (Recharts), feed components, threat gauge, intelligence brief display. All read-only from backend perspective — frontend never triggers backend operations directly.

**Key architectural patterns validated:**
- **LLM-First Analysis with Fallback Cache**: All complex pattern detection delegated to LLMs, but responses pre-cached for demo reliability and cost savings
- **Realtime Database as Event Bus**: Supabase realtime subscriptions replace custom WebSocket infrastructure
- **Time-Window Correlation with Sliding Baseline**: Rolling 30-day baseline adapts to changing normal activity levels
- **Demo Playback via Controlled Data Injection**: Pre-generated datasets with relative timestamps, rewritten to "now + offset" during playback

**Critical build order dependencies:**
1. Supabase schema definition blocks everything (all components need contract)
2. LLM wrapper with caching blocks all processing modules
3. Correlation engine blocks demo scenario design (can't script demo without knowing algorithm)
4. Frontend realtime connection blocks all UI components

### Critical Pitfalls

Research identified 10 major pitfalls, prioritizing by impact and recovery cost:

1. **LLM API Dependency for Live Demo (CRITICAL)**: Demo fails mid-presentation due to rate limits, API downtime, or slow responses. Cache ALL demo scenario LLM responses in Phase 3.4. Implement fallback layer serving cached responses keyed by input hash. Never call live APIs during judge presentation. Add `--offline` flag to demo playback engine.

2. **Correlation False Positives from Noisy Data (CRITICAL)**: System cries wolf constantly, RED alert has no impact. Use statistical anomaly detection (2+ standard deviations above rolling 7-day baseline), not hardcoded thresholds. Implement phrase novelty scoring in narrative detector ("restoration of necessary order" scores higher than routine "one China principle"). Test against 7 days of real data before demo.

3. **Supabase Realtime Race Conditions (MODERATE)**: Dashboard updates out of sequence — brief appears before correlation event that generated it. Demo playback should insert records with 200-500ms delays. Use sequence numbers, frontend sorts by sequence before rendering. Test at multiple playback speeds (1x, 5x, 10x).

4. **GDELT Data Quality Assumptions (CRITICAL)**: Article URLs 404'd, timestamps malformed, Chinese outlets missing from results. Pre-download 7 days of data during Phase 0, store in Supabase. Demo uses hand-crafted synthetic articles, NOT live GDELT. Add field validation (check for required fields, discard incomplete). Live GDELT is separate "technical proof" tab.

5. **Telegram FloodWait Rate Limiting (CRITICAL)**: Hits `FloodWaitError: wait 3600 seconds` during data collection, blocks pipeline. Implement exponential backoff wrapper catching FloodWaitError. Pre-scrape target channels in Phase 0 (first 6 hours). Demo uses pre-scraped messages, never live scraping. Have 2-3 Telegram accounts as backup.

6. **LLM Prompt Output Format Drift (MODERATE)**: LLM returns markdown table instead of expected JSON, parser breaks. Use structured output with exact JSON schema example in prompt ("respond ONLY with valid JSON"). Add validation after every LLM call with fallback to regex extraction. Cache all demo responses (known good outputs). If parsing fails, return safe defaults rather than crashing.

7. **Lovable React Integration Bugs (HIGH)**: Generated code doesn't correctly integrate with Supabase realtime, frontend dev spends 6+ hours debugging unfamiliar code. Define Supabase schema in Phase 0.6 BEFORE Lovable development. Start integration early (Phase 2.1, hour 16), test each panel immediately. Ensure team has React/TypeScript expertise.

8. **Demo Scenario Narrative Not Compelling (MODERATE)**: Technical demo works but judges don't care — "interesting tech, unclear value." Write demo scenario script in Phase 3.1 BEFORE building playback. Frame around analyst's problem. Use concrete details ("8 posts from Fujian fishing forums" not "movement indicators increased"). Intelligence brief should read like actual intelligence with specific evidence and actionable recommendations.

9. **Backend/Frontend Schema Mismatch (HIGH)**: Backend writes `article_count`, frontend expects `articleCount`. Chart shows blank. Define schema as formal contract in Phase 0.6, BOTH teams review. Document exact column names, types, examples in `.planning/SUPABASE_SCHEMA.md`. Schedule integration checkpoint at hour 20. Use TypeScript interfaces generated from Supabase schema.

10. **Map Geolocation Data Quality (MODERATE)**: 40% of posts have no location data, map nearly empty. LLM prompt should return structured location with lat/lon and confidence. Use geocoding service (Nominatim, Mapbox) to convert place names. Demo dataset includes explicit lat/lon in synthetic posts. Add location confidence filtering (only show "high confidence" on map).

**Pitfall prevention strategies embedded in roadmap:**
- Phase 0.6 (schema definition) prevents mismatch pitfall
- Phase 1.4 (correlation engine) addresses false positive pitfall with baseline calibration
- Phase 3.4 (testing) discovers all integration issues before Phase 4 demo
- Phase 3.5 (offline mode) eliminates API dependency risks

## Implications for Roadmap

Research findings dictate a four-phase structure optimized for 48-hour hackathon constraints. Phase boundaries align with architectural integration points and risk mitigation requirements.

### Phase 0: Foundation (Hours 0-8)
**Rationale:** Schema definition is the blocking dependency for all parallel work. Once database contract exists, backend ingestion and frontend development can proceed independently without coordination overhead.

**Delivers:**
- Supabase project with complete schema (articles, social_posts, vessel_positions, narrative_events, movement_events, alerts, briefs)
- Dev environment setup (Python 3.11+, uv, API keys in .env)
- GDELT ingestion pipeline with field validation
- Telegram scraper with FloodWait handling (pre-scrape data NOW)
- Simulated demo dataset generator
- Initial data collection (7 days of GDELT + Telegram for baseline)

**Addresses features:**
- Multi-source aggregation (table stakes)
- Source attribution (articles and posts with URLs)

**Avoids pitfalls:**
- #4 GDELT data quality (validation + synthetic fallback)
- #5 Telegram FloodWait (pre-scraping in Phase 0)
- #9 Schema mismatch (formal contract before parallel work)

**Research flag:** GDELT API behavior may vary — monitor data freshness and completeness during this phase.

### Phase 1: Intelligence Layer (Hours 8-20)
**Rationale:** Processing modules depend on ingestion completing but can be built in parallel. LLM wrapper must be completed first as all analysis modules depend on it. Correlation engine comes last as it reads outputs from both narrative and movement streams.

**Delivers:**
- LLM client wrapper with caching and fallback logic
- Narrative coordination detector (Claude Sonnet, identifies synchronized phrasing across outlets)
- Civilian post classifier (GPT-4o Mini, military relevance + geolocation extraction)
- Entity extractor (structured data from unstructured text)
- Correlation engine with statistical baseline calibration (72-hour window, geographic matching)
- Intelligence brief generator (LLM synthesis into executive format)
- Pipeline integration test (end-to-end data flow validation)

**Uses stack:**
- FastAPI for async LLM calls
- Anthropic SDK (Claude Sonnet 4.5) for narrative analysis
- OpenAI SDK (GPT-4o Mini) for bulk classification
- pandas for time-series correlation
- litellm for unified LLM interface (cost tracking)

**Implements architecture:**
- Processing Layer (all LLM analysis modules)
- Correlation Engine (cross-stream integration point)

**Addresses features:**
- Centralized directive detection (differentiator)
- Civilian OSINT for movement (differentiator)
- Geolocation extraction (differentiator)
- Temporal clustering (differentiator)
- Intelligence brief auto-generation (table stakes)

**Avoids pitfalls:**
- #1 LLM API dependency (caching infrastructure built here)
- #2 Correlation false positives (baseline calibration implemented)
- #6 LLM output format drift (structured prompts + validation)

**Research flag:** LLM prompt engineering for directive detection is novel — may require iteration. Budget 2-3 hours for prompt tuning.

### Phase 2: Visualization (Hours 20-32)
**Rationale:** Frontend development can start once schema is defined (Phase 0.6) but realtime integration should be tested early (hour 20) to catch Lovable-generated code issues before final integration. Dashboard layout blocks all specific components.

**Delivers:**
- Lovable project initialization with Supabase connection
- Dashboard layout with realtime subscription hooks
- Interactive map panel (Leaflet, movement markers + vessel positions)
- Correlation chart panel (Recharts, dual-axis timeline)
- Narrative feed panel (article stream with source attribution)
- Movement feed panel (social post stream with classification scores)
- Threat level gauge (GREEN/AMBER/RED with animated transitions)
- Intelligence brief display component (formatted markdown)

**Uses stack:**
- Lovable (React code generation)
- Supabase JavaScript client with realtime subscriptions
- Leaflet (map component)
- Recharts (chart component)

**Implements architecture:**
- Presentation Layer (all UI components)
- Realtime Middleware integration (Supabase subscriptions)

**Addresses features:**
- Real-time visualization (table stakes)
- Map with event markers (table stakes)
- Temporal filtering (timeline scrubber, table stakes)
- Threat level visualization (table stakes)

**Avoids pitfalls:**
- #3 Realtime race conditions (sequence-based rendering)
- #7 Lovable integration bugs (early testing at hour 20)
- #9 Schema mismatch (catch integration issues early)
- #10 Map geolocation quality (location confidence filtering)

**Research flag:** Lovable code quality for Supabase realtime is unknown — allocate buffer time for debugging generated code.

### Phase 3: Demo Integration (Hours 32-44)
**Rationale:** Technical system is complete after Phase 2, but demo reliability requires three additional layers: compelling scenario narrative, playback engine for controlled timing, and offline fallback mode. Scenario script must be written BEFORE playback engine (story drives implementation).

**Delivers:**
- Demo scenario script (Taiwan Strait 72-hour escalation with narrative arc)
- Demo playback engine (time-sliced data insertion with sequence control)
- Live data integration (separate "Technical Proof" tab, optional)
- End-to-end testing with multiple playback speeds
- Fallback/offline mode (cached LLM responses, no live API dependency)
- Intelligence brief editorial review (ensure realistic intelligence format)

**Uses stack:**
- Python script with controlled timing (demo playback)
- Supabase bulk inserts with sequence numbers
- LLM response cache (pre-computed, deterministic)

**Implements architecture:**
- Demo Playback Engine (controlled data injection)
- All pipelines tested end-to-end

**Addresses features:**
- Historical playback (differentiator, time-compressed for demo)
- Preemptive warning timeline (show 24-48 hour advantage)

**Avoids pitfalls:**
- #1 LLM API dependency (offline mode with cached responses)
- #3 Realtime race conditions (controlled playback with delays)
- #4 GDELT data quality (synthetic demo data)
- #8 Demo narrative not compelling (scenario script written first)

**Research flag:** None — standard demo engineering patterns.

### Phase 4: Presentation (Hours 44-48)
**Rationale:** Technical work complete, focus shifts to presentation clarity and rehearsal. Backup plan essential for demo day contingencies.

**Delivers:**
- Presentation slides (architecture diagram, value proposition, technical approach)
- Demo rehearsal (3+ run-throughs, timing optimization)
- Backup plan (screen recording, localhost fallback, manual narrative)
- API cost validation (confirm <$25 total spend)

**Addresses:** Hackathon judging criteria (clear value prop, working demo, novel approach, scalability story)

### Phase Ordering Rationale

**Why this sequence:**
1. **Schema first** (Phase 0.6): Blocks everything. Backend and frontend need contract before parallel work.
2. **Processing before visualization** (Phase 1 before Phase 2): Frontend can't display intelligence until processing modules generate it. But ingestion can run during Phase 1 (parallel).
3. **Core system before demo polish** (Phases 0-2 before Phase 3): Must have working technical foundation before demo scenario engineering.
4. **Presentation last** (Phase 4): Can't rehearse until demo playback works.

**Parallelization opportunities:**
- Phase 0: All ingestion modules (GDELT, Telegram, AIS, simulated) after schema defined
- Phase 1: Narrative detector + post classifier (independent streams)
- Phase 2: All dashboard UI components after realtime connection validated
- Phase 3: Live data integration + offline mode implementation (independent paths)

**Critical path:**
```
Schema (0.6) → LLM Wrapper (1.1) → Correlation Engine (1.4) →
Dashboard Realtime (2.1) → Demo Playback (3.2) → Rehearsal (4.3)
```

**Bottleneck tasks** (cannot be parallelized):
- Phase 0.6: Schema definition (6 tables, relationships, realtime config) — 2 hours
- Phase 1.1: LLM wrapper with caching — 2 hours
- Phase 1.4: Correlation engine with baseline calibration — 3 hours
- Phase 3.2: Demo playback engine with sequencing — 3 hours

Total critical path: ~10 hours. Remaining 38 hours available for parallelized work and buffer.

### Research Flags

**Phases likely needing deeper research:**
- **Phase 1.1 (Narrative coordination detector):** Novel prompt engineering for detecting synchronized propaganda phrasing. Sparse examples in public domain. May require `/gsd:research-phase` if initial prompts fail to detect coordination patterns.
- **Phase 1.4 (Correlation engine):** Statistical baseline calibration approach is standard in anomaly detection, but application to dual-stream intelligence fusion is domain-specific. Research time-series correlation patterns if false positive rate >10% during testing.

**Phases with standard patterns (skip research-phase):**
- **Phase 0 (Foundation):** GDELT and Telegram APIs well-documented. Supabase schema design is standard database work.
- **Phase 2 (Visualization):** Leaflet and Recharts have extensive documentation and examples. Supabase realtime patterns documented in official guides.
- **Phase 3 (Demo Integration):** Demo playback is standard hackathon engineering. No novel patterns.

**Validation checkpoints:**
- Hour 8 (end of Phase 0): Validate GDELT data completeness, Telegram scraping functional
- Hour 20 (end of Phase 1): Validate LLM analysis produces expected JSON outputs, correlation algorithm tested against real data
- Hour 32 (end of Phase 2): Validate dashboard receives realtime updates, all panels functional
- Hour 40 (end of Phase 3): Validate demo runs offline without API dependencies, scenario narrative compelling

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Python/FastAPI/Supabase are proven technologies. Versions based on January 2025 training data require PyPI verification. LLM SDK versions change frequently. Telethon and gdeltdoc are niche libraries — verify maintenance status. |
| Features | HIGH | Feature analysis based on established intelligence platform patterns (Janes, Recorded Future, Dataminr) and OSINT methodology (Bellingcat). Dual-stream correlation differentiator validated through competitor analysis showing no existing vendor automates this. |
| Architecture | HIGH | Independent stream processing, realtime database as event bus, LLM-first analysis with caching are all proven patterns in data fusion systems. Build order dependencies and critical path validated through architectural analysis. |
| Pitfalls | HIGH | Pitfalls derived from known failure modes in: data pipelines (GDELT quality, Telegram rate limits), LLM integrations (API dependency, output format drift), real-time systems (Supabase race conditions), and hackathon constraints (demo narrative, integration timing). |

**Overall confidence:** MEDIUM-HIGH

Research is comprehensive for architectural patterns, feature requirements, and risk mitigation strategies. Primary uncertainty is package version currency (training cutoff January 2025, researched February 2026) and niche library maintenance status (gdeltdoc, gdeltPyR).

### Gaps to Address

1. **Package version validation:** All Python library versions based on training data. CRITICAL: Verify on PyPI before Phase 0 setup:
   - gdeltdoc: Check GitHub last commit date, open issues for API breakage
   - Telethon: Confirm Python 3.11+ compatibility, FloodWait handling in latest version
   - Supabase Python client: Verify realtime subscription support (may be less mature than JavaScript client)
   - litellm: Confirm compatibility with Claude Sonnet 4.5, GPT-4o Mini, Gemini 2.5 Flash

2. **LLM API rate limits:** Research cites "50 req/min for Claude Sonnet" but actual limits depend on account tier. Validate rate limits during Phase 0 with test API calls. Monitor usage during Phase 1 development to avoid hitting limits before demo.

3. **GDELT Chinese state media coverage:** Research assumes GDELT indexes Xinhua, Global Times, CCTV, People's Daily. Verify during Phase 0.3 that GDELT DOC 2.0 actually returns articles from these domains. If coverage is sparse, may need RSS scraping as fallback.

4. **Telegram channel availability:** Demo assumes access to OSINT Telegram channels with military movement reports. If channels are private or require verification, fallback to simulated data is mandatory (already planned in Phase 0.5).

5. **Geocoding API choice:** Research mentions Nominatim (free) and Mapbox Geocoding. Decision needed in Phase 1.2: Nominatim sufficient for MVP but rate limits strict (1 req/sec). Mapbox free tier (100k requests/month) likely better for development.

**How to handle during planning:**
- Schedule 30-minute "verification sprint" at start of Phase 0 to check package versions and API access
- Add task to Phase 0.3: "Validate GDELT coverage of Chinese state media domains"
- Add task to Phase 1.2: "Select geocoding service (Nominatim vs. Mapbox) based on rate limits"
- Add task to Phase 3.4: "Measure actual API costs during end-to-end test, confirm <$25"

## Sources

### Primary (HIGH confidence)
- **STACK.md:** Python/FastAPI/Supabase stack research with package versions
- **FEATURES.md:** Feature landscape analysis with MVP definition and anti-features
- **ARCHITECTURE.md:** System architecture patterns and build order dependencies
- **PITFALLS.md:** Domain-specific pitfall analysis with prevention strategies
- Supabase documentation (realtime subscriptions, Python client patterns)
- Anthropic API documentation (structured output, rate limits, timeout handling)
- OpenAI API documentation (GPT-4o Mini pricing, batch processing)
- GDELT DOC 2.0 API documentation (query patterns, data format)
- Telethon documentation (FloodWait handling, channel message iteration)

### Secondary (MEDIUM confidence)
- Competitor analysis (Janes Intelligence, Recorded Future, Dataminr) — based on public information and domain knowledge, not verified via direct access
- Hackathon judging criteria — inferred from typical technical competition patterns
- LLM prompt engineering patterns — community best practices, not official guidance
- Demo playback engineering patterns — standard hackathon practices

### Tertiary (LOW confidence, needs validation)
- Package versions (January 2025 training cutoff, February 2026 research date) — PyPI verification required
- GDELT Chinese state media coverage — assumes indexing, requires validation
- Lovable-generated code quality for Supabase realtime — unknown, requires testing
- LLM API cost estimates — based on published pricing but actual usage may vary

---
*Research completed: 2026-02-07*
*Ready for roadmap: Yes*

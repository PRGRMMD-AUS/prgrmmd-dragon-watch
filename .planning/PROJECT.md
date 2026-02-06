# Dragon Watch

## What This Is

Dragon Watch is a pre-conflict early warning system that correlates state media narrative coordination with civilian social media movement indicators to detect military operations before they're publicly announced. Built as a 48-hour hackathon prototype (Team Panop), it runs two independent detection streams in parallel — propaganda synchronisation and civilian movement anomalies — and alerts when they converge. The demo scenario covers a simulated Taiwan Strait escalation.

## Core Value

The correlation of two independent signal streams (state media coordination + civilian movement reports) provides pre-conflict warning hours before official announcements — a capability no existing OSINT vendor offers.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] GDELT ingestion pipeline fetches Chinese state media articles (Xinhua, Global Times, CCTV, People's Daily) into Supabase
- [ ] Telegram scraper pulls messages from public OSINT/military channels into Supabase
- [ ] LLM-powered narrative coordination detector scores synchronisation across state media outlets
- [ ] LLM-powered civilian post classifier identifies military-relevant movement indicators
- [ ] Entity extraction pulls structured data (units, equipment, locations, timestamps) from text
- [ ] Correlation engine cross-references narrative spikes with movement clusters within 72-hour windows
- [ ] Intelligence brief generator produces formatted threat assessments (GREEN/AMBER/RED)
- [ ] Simulated Taiwan Strait demo dataset (50+ articles, 100+ civilian posts, AIS data) loaded in Supabase
- [ ] Demo playback engine steps through the scenario at controlled speed, writing time-sliced data to Supabase
- [ ] Supabase schema with realtime enabled on all tables (articles, social_posts, vessel_positions, alerts, correlation_events, briefs)
- [ ] React dashboard (Lovable) with map, dual-axis chart, narrative feed, movement feed, threat gauge, intel brief panel
- [ ] All dashboard panels update via Supabase realtime subscriptions
- [ ] Live data tab showing real GDELT/Telegram data flowing through the system
- [ ] Offline/fallback mode with pre-loaded data (no live API dependency for core demo)
- [ ] Demo runs GREEN → RED in ~5 minutes without crashes

### Out of Scope

- X/Twitter API — $200+/month, not justified for hackathon
- TikTok Research API — academic-only, weeks to approve
- Weibo API — requires Chinese SIM card
- MarineTraffic API — no free tier
- Real-time chat features — not core to the detection mission
- Mobile app — web-first prototype
- OAuth/social login — email/password or no auth for hackathon
- Production deployment — localhost demo is sufficient
- Multi-language UI — English only

## Context

**Hackathon prototype** — 48-hour build window, February 2026. Team Panop. UNCLASSIFIED // FOR EXERCISE USE ONLY.

**Architecture**: Python backend scripts process data and write to Supabase Postgres. React frontend (built in Lovable) reads from Supabase via realtime subscriptions. Backend and frontend are fully decoupled — Supabase tables are the contract.

**Two detection streams**:
- **Stream 1 (Narrative)**: Monitor Chinese state media via GDELT. LLM detects when multiple outlets simultaneously adopt identical unusual phrasing (synchronisation = centralised directive). Score by outlet count, phrase novelty, temporal clustering, topic severity.
- **Stream 2 (Movement)**: Monitor Telegram channels + simulated social feeds for civilian posts revealing military activity (convoys, naval sightings, flight activity, restricted zones). LLM classifies relevance, extracts geolocation, clusters by region/time.
- **Correlation**: Narrative spike within 72hrs + movement cluster in same geographic region = threat escalation.

**Demo scenario**: Taiwan Strait escalation over simulated 72 hours. GREEN → AMBER → RED. System provides ~24-48 hours advance warning before official PLA announcement.

**Key building block repos**:
- `gdeltdoc` — GDELT DOC 2.0 API wrapper (article-level queries, tone scoring)
- `gdeltPyR` — GDELT v1/v2 into Pandas DataFrames
- `aisstream/aisstream` — AISstream.io WebSocket examples (free real-time vessel positions)
- `followthemoney/vessel_research` — Bellingcat maritime OSINT + Global Fishing Watch API
- `Telethon` — Telegram API (pip installable, working scraper in <1 hour)
- GDELT sentiment analysis project — pipeline pattern reference
- GDELT news dashboard — ETL + dashboard reference architecture

**Data approach**: Simulated/seeded data first for demo reliability. Live GDELT + Telegram feeds wired in separately as technical proof. Demo must work offline with pre-loaded Supabase data.

**API keys**: Some ready, others still needed. Supabase (free tier), Anthropic API (Claude Sonnet 4.5), AISstream.io (free), Telegram (my.telegram.org), GDELT (no key needed), ACLED (free after registration).

**LLM strategy**: Claude Sonnet 4.5 for narrative analysis + brief generation (~$3/M input). GPT-4o Mini or Gemini 2.5 Flash for bulk post classification (~$0.15-0.60/M input). Total API cost <$25.

## Constraints

- **Timeline**: 48-hour hackathon build window — every decision optimises for speed
- **Budget**: <$25 total API costs, free-tier services only
- **Frontend**: Built in Lovable (separate from this repo) — this repo is Python backend + Supabase schema
- **Data**: No access to Weibo, X/Twitter, or TikTok — using GDELT, Telegram, AISstream, and simulated data
- **Classification**: UNCLASSIFIED // FOR EXERCISE USE ONLY — all data is open source or simulated
- **Demo**: Must work reliably on localhost with pre-loaded data — live feeds are bonus, not dependency
- **Stack**: Python 3.11+, FastAPI, Supabase (Postgres + Realtime), Claude/GPT APIs, Pandas/NumPy

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Lovable for frontend, not Streamlit | Better visual quality, proper React app, decoupled from backend via Supabase realtime | — Pending |
| Supabase as middleware layer | Managed Postgres + built-in realtime subscriptions. Backend writes, frontend reads. Free tier sufficient. | — Pending |
| Simulated data first, live feeds second | Demo reliability is paramount. Live feeds are technical proof, not demo dependency. | — Pending |
| Claude for narrative analysis, GPT-4o Mini for bulk classification | Cost optimisation: expensive model for complex analysis, cheap model for high-volume classification | — Pending |
| GDELT over direct media scraping | Free, no auth, 15-min updates, tone scoring built in. Good enough for hackathon. | — Pending |

---
*Last updated: 2026-02-07 after initialization*

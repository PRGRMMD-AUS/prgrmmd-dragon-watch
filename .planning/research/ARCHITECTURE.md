# Architecture Research

**Domain:** OSINT Data Fusion and Correlation Systems
**Researched:** 2026-02-07
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   Map    │  │  Chart   │  │  Feeds   │  │  Brief   │            │
│  │ Component│  │Component │  │ Component│  │Component │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │             │              │             │                  │
│       └─────────────┴──────────────┴─────────────┘                  │
│                          │                                           │
│                    (realtime subscriptions)                          │
└──────────────────────────┼───────────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────────┐
│                   REALTIME MIDDLEWARE                                │
│              (Supabase Postgres + Realtime)                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ articles │  │  posts   │  │ vessels  │  │  alerts  │            │
│  └────▲─────┘  └────▲─────┘  └────▲─────┘  └────▲─────┘            │
│       │             │              │             │                  │
└───────┼─────────────┼──────────────┼─────────────┼───────────────────┘
        │             │              │             │
        │             │              │             │ (write)
┌───────┼─────────────┼──────────────┼─────────────┼───────────────────┐
│                     PROCESSING LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌──────────────────┐                  │
│  │ Stream 1:        │         │ Stream 2:        │                  │
│  │ Narrative        │         │ Movement         │                  │
│  │ Detection        │         │ Detection        │                  │
│  └────────┬─────────┘         └────────┬─────────┘                  │
│           │                            │                            │
│           └────────────┬───────────────┘                            │
│                        │                                            │
│              ┌─────────▼──────────┐                                 │
│              │  Correlation       │                                 │
│              │  Engine            │                                 │
│              └─────────┬──────────┘                                 │
│                        │                                            │
│              ┌─────────▼──────────┐                                 │
│              │  Brief Generator   │                                 │
│              └────────────────────┘                                 │
├─────────────────────────────────────────────────────────────────────┤
│                     INGESTION LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  GDELT   │  │ Telegram │  │   AIS    │  │ Simulated│            │
│  │ Fetcher  │  │ Scraper  │  │ Stream   │  │   Data   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │             │              │             │                  │
└───────┼─────────────┼──────────────┼─────────────┼───────────────────┘
        │             │              │             │
   ┌────▼─────┐  ┌───▼────┐    ┌────▼─────┐  ┌───▼────┐
   │  GDELT   │  │Telegram│    │AISstream │  │ Manual │
   │  DOC 2.0 │  │  API   │    │.io WS    │  │ Load   │
   └──────────┘  └────────┘    └──────────┘  └────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Ingestion Layer** | Pull raw data from external sources, normalize, write to database | Python scripts with source-specific API clients (gdeltdoc, Telethon, WebSocket), scheduled via cron/while loops |
| **Processing Layer** | Analyze ingested data for patterns, correlate across streams, generate alerts | Python modules with LLM API calls (Claude/GPT), rule-based correlation logic, pandas for time-series analysis |
| **Realtime Middleware** | Store processed data, broadcast updates to frontend, handle queries | Postgres with realtime pub/sub (Supabase), row-level subscriptions, WebSocket transport |
| **Presentation Layer** | Display data streams, visualize correlations, show generated intelligence | React SPA with map (Leaflet/Mapbox), charts (Recharts), realtime hooks (Supabase client) |
| **Demo Playback Engine** | Insert time-sliced data to simulate scenario progression | Python script with controlled timing, writes to same database tables as live pipeline |

## Recommended Project Structure

```
dragon-watch/
├── backend/
│   ├── ingest/                 # Data ingestion modules
│   │   ├── gdelt_fetcher.py    # GDELT DOC 2.0 queries → articles table
│   │   ├── telegram_scraper.py # Telethon → social_posts table
│   │   ├── ais_listener.py     # AISstream WebSocket → vessel_positions
│   │   └── simulated_loader.py # Load demo dataset → all tables
│   ├── process/                # Analysis and correlation
│   │   ├── narrative_detector.py  # LLM: detect media coordination
│   │   ├── post_classifier.py     # LLM: classify military relevance
│   │   ├── entity_extractor.py    # LLM: extract structured entities
│   │   ├── correlation_engine.py  # Time-window + geo matching
│   │   └── brief_generator.py     # LLM: formatted intelligence output
│   ├── api/                    # Optional FastAPI endpoints
│   │   ├── main.py             # FastAPI app entry
│   │   └── routes.py           # REST endpoints (if needed)
│   ├── demo/                   # Demo scenario management
│   │   ├── playback_engine.py  # Time-sliced data insertion
│   │   ├── scenario_data/      # Pre-generated demo datasets
│   │   └── fallback_cache/     # Cached LLM responses for offline
│   ├── db/                     # Database utilities
│   │   ├── supabase_client.py  # Supabase connection wrapper
│   │   └── schema.sql          # Table definitions + realtime config
│   ├── config/                 # Configuration management
│   │   ├── settings.py         # Environment-based config (from .env)
│   │   └── prompts.py          # LLM prompt templates
│   └── utils/                  # Shared utilities
│       ├── llm_client.py       # Anthropic/OpenAI API wrappers
│       ├── retry.py            # Exponential backoff logic
│       └── geo.py              # Geospatial helpers
├── frontend/                   # Lovable-generated React app (separate repo)
│   └── [managed in Lovable]    # See frontend structure below
├── .planning/                  # GSD project management
│   ├── PROJECT.md              # Project definition
│   ├── research/               # Research artifacts
│   └── roadmap/                # Phase definitions
├── .env.example                # Template for API keys
├── requirements.txt            # Python dependencies
├── README.md                   # Setup + architecture overview
└── docker-compose.yml          # Optional: local Postgres for dev
```

### Frontend Structure (Lovable-generated)

```
lovable-dragon-watch/           # Separate Lovable project
├── src/
│   ├── components/
│   │   ├── Map/               # Leaflet/Mapbox integration
│   │   │   ├── BaseMap.tsx    # Map container
│   │   │   ├── MovementLayer.tsx # Civilian post markers
│   │   │   └── VesselLayer.tsx   # AIS ship icons
│   │   ├── Charts/
│   │   │   └── CorrelationChart.tsx # Recharts dual-axis
│   │   ├── Feeds/
│   │   │   ├── NarrativeFeed.tsx    # Article stream
│   │   │   └── MovementFeed.tsx     # Post stream
│   │   └── Brief/
│   │       ├── ThreatGauge.tsx      # GREEN/AMBER/RED indicator
│   │       └── IntelBrief.tsx       # Formatted brief display
│   ├── hooks/
│   │   └── useSupabaseRealtime.ts   # Realtime subscription logic
│   ├── lib/
│   │   └── supabase.ts              # Supabase client config
│   ├── pages/
│   │   ├── Dashboard.tsx            # Main view
│   │   └── LiveData.tsx             # Real feed monitoring
│   └── App.tsx
└── .env.local                       # Supabase URL + anon key
```

### Structure Rationale

- **backend/ingest/**: Each data source gets its own module. These run independently (different schedules/triggers). Write directly to Supabase, no inter-dependencies.
- **backend/process/**: Analysis modules read from Supabase, call LLM APIs, write results back. Can run as scheduled jobs or triggered by new data events.
- **backend/demo/**: Completely separate from live pipeline. Writes to same tables but from pre-generated datasets. Ensures demo reliability without live API dependency.
- **db/**: Centralized Supabase client prevents connection duplication. Schema as code for reproducibility.
- **config/**: All environment variables and prompt templates centralized. Makes prompt iteration faster during LLM tuning.
- **Frontend separation**: Lovable manages its own repo. Contract = Supabase table schemas. Backend team never touches React. Frontend team never touches Python.

## Architectural Patterns

### Pattern 1: Independent Stream Processing

**What:** Each detection stream (narrative, movement) operates as a completely independent pipeline from ingestion through analysis. No shared state, no direct communication. Correlation happens only at the final stage by reading completed outputs from the database.

**When to use:** Multi-source intelligence fusion where sources have different latencies, update frequencies, and failure modes.

**Trade-offs:**
- **Pro:** Isolation prevents cascade failures. GDELT downtime doesn't break Telegram processing.
- **Pro:** Parallel development. Two backend devs can build streams simultaneously without merge conflicts.
- **Pro:** Easy to add new streams (e.g., satellite imagery, flight tracking) without modifying existing pipelines.
- **Con:** Database becomes the bottleneck. All inter-stream communication is write → read.
- **Con:** Harder to implement backpressure if one stream overwhelms correlation engine.

**Example:**
```python
# backend/ingest/gdelt_fetcher.py
def main():
    while True:
        articles = fetch_gdelt_articles(domains=CHINESE_STATE_MEDIA)
        supabase.table('articles').insert(articles).execute()
        time.sleep(900)  # 15-min polling

# backend/ingest/telegram_scraper.py
def main():
    async with TelegramClient(...) as client:
        for channel in OSINT_CHANNELS:
            messages = await client.get_messages(channel, limit=100)
            supabase.table('social_posts').insert(messages).execute()

# No communication between these two scripts. Both write to database independently.
```

### Pattern 2: LLM-First Analysis with Fallback Cache

**What:** All complex pattern detection (narrative coordination, post classification, entity extraction) is delegated to LLM APIs. But for reliability, all LLM responses for the demo scenario are pre-cached. If API fails, system falls back to cached responses.

**When to use:** Hackathon/demo environments where live API calls are desired for "wow factor" but unreliable network/rate limits are a risk.

**Trade-offs:**
- **Pro:** Demo never fails due to API downtime. Pre-cached responses are deterministic.
- **Pro:** Massive cost savings during development (don't re-analyze same demo data 50 times).
- **Pro:** Faster iteration (LLM tuning happens on cached data, then tested live).
- **Con:** Cache invalidation complexity if demo scenario changes.
- **Con:** Cached responses may diverge from current LLM behavior (model updates).

**Example:**
```python
# backend/utils/llm_client.py
import hashlib
import json

CACHE_DIR = "backend/demo/fallback_cache/"

def cached_llm_call(prompt: str, system: str, model: str) -> str:
    cache_key = hashlib.md5(f"{model}:{system}:{prompt}".encode()).hexdigest()
    cache_file = f"{CACHE_DIR}/{cache_key}.json"

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)['response']

    # Live API call
    response = anthropic.messages.create(
        model=model,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.content[0].text

    # Cache for future
    with open(cache_file, 'w') as f:
        json.dump({'prompt': prompt, 'response': result}, f)

    return result
```

### Pattern 3: Realtime Database as Event Bus

**What:** Instead of building a custom WebSocket server or message queue, use Supabase Postgres with realtime subscriptions. Backend writes rows, frontend receives push notifications automatically. Database acts as both persistence and pub/sub.

**When to use:** Rapid prototyping where you want realtime updates but don't want to manage WebSocket infrastructure or Redis Pub/Sub.

**Trade-offs:**
- **Pro:** Zero boilerplate. Supabase handles WebSocket lifecycle, reconnection, auth.
- **Pro:** Frontend gets data + updates through same client library. No separate Socket.io code.
- **Pro:** Realtime subscriptions can filter by row conditions (e.g., only RED alerts).
- **Con:** Not suitable for high-frequency updates (>1Hz). Postgres replication slot has overhead.
- **Con:** Vendor lock-in to Supabase (though migration to self-hosted Realtime Server is possible).
- **Con:** Limited transformation logic on the realtime path. Backend must write presentation-ready data.

**Example:**
```python
# backend/process/correlation_engine.py
def write_alert(alert_data: dict):
    supabase.table('alerts').insert(alert_data).execute()
    # That's it. Frontend auto-receives via realtime subscription.
```

```typescript
// frontend/src/hooks/useSupabaseRealtime.ts
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

export function useAlerts() {
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    const channel = supabase
      .channel('alerts-changes')
      .on('postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'alerts' },
          (payload) => setAlerts(prev => [payload.new, ...prev])
      )
      .subscribe()

    return () => { channel.unsubscribe() }
  }, [])

  return alerts
}
// Now any component can call useAlerts() and get live updates
```

### Pattern 4: Time-Window Correlation with Sliding Baseline

**What:** Correlation engine maintains a rolling baseline of "normal" activity for each stream. Anomaly detection compares current window (e.g., last 6 hours) to historical baseline (e.g., last 30 days). Alerts fire when both streams spike above baseline simultaneously within a geographic region.

**When to use:** Any multi-stream anomaly detection system where "normal" varies over time (news cycles, seasonal patterns).

**Trade-offs:**
- **Pro:** Adapts to changing baselines (e.g., routine military exercises don't trigger false positives after first occurrence).
- **Pro:** No manual threshold tuning. System learns what "normal" looks like from historical data.
- **Con:** Cold start problem. System needs historical data before baselines are meaningful.
- **Con:** Can be gamed if adversary slowly ramps activity over weeks (boiling frog).

**Example:**
```python
# backend/process/correlation_engine.py
import pandas as pd
from datetime import datetime, timedelta

def detect_narrative_spike(articles_df: pd.DataFrame) -> dict:
    # Current window: last 6 hours
    now = datetime.utcnow()
    current_window = articles_df[articles_df['timestamp'] > now - timedelta(hours=6)]

    # Baseline: last 30 days, excluding current 6 hours
    baseline = articles_df[
        (articles_df['timestamp'] > now - timedelta(days=30)) &
        (articles_df['timestamp'] < now - timedelta(hours=6))
    ]

    # Metric: number of outlets coordinating on same phrase
    current_coordination = detect_coordinated_phrases(current_window)
    baseline_avg_coordination = baseline.groupby('phrase')['outlet'].nunique().mean()

    # Spike = current > 2x baseline
    is_spike = current_coordination['outlet_count'] > 2 * baseline_avg_coordination

    return {
        'is_spike': is_spike,
        'current': current_coordination,
        'baseline': baseline_avg_coordination,
        'timestamp': now
    }
```

### Pattern 5: Demo Playback via Controlled Data Injection

**What:** Demo scenarios are pre-generated datasets with timestamps relative to "demo start time". Playback engine rewrites timestamps to "now + offset" and inserts data in chunks, simulating live data flow. Frontend doesn't know it's demo data — it just sees new rows appearing via realtime.

**When to use:** Hackathon demos, sales presentations, training environments where you need deterministic, repeatable scenarios.

**Trade-offs:**
- **Pro:** Demo always works. No dependency on live APIs or external data sources.
- **Pro:** Perfect for time-compressed storytelling (72-hour scenario in 5 minutes).
- **Pro:** Easy to script multiple scenarios (Taiwan Strait, South China Sea, East China Sea).
- **Con:** Demo data must be manually curated and kept up-to-date with schema changes.
- **Con:** Doesn't exercise actual ingestion/processing code paths (bugs may hide until live deployment).

**Example:**
```python
# backend/demo/playback_engine.py
import time
from datetime import datetime, timedelta

def play_scenario(scenario_name: str, speed_multiplier: float = 1.0):
    """Insert demo data with controlled timing.

    Args:
        scenario_name: e.g., 'taiwan_strait_escalation'
        speed_multiplier: 1.0 = real-time, 60.0 = 1 hour per minute
    """
    scenario_data = load_scenario(scenario_name)
    demo_start_time = datetime.utcnow()

    for event in scenario_data:
        # event['offset_seconds'] is relative to demo start (e.g., 3600 = 1 hour in)
        wait_seconds = event['offset_seconds'] / speed_multiplier
        time.sleep(wait_seconds)

        # Rewrite timestamp to now
        event['timestamp'] = demo_start_time + timedelta(seconds=event['offset_seconds'])

        # Insert into appropriate table
        if event['type'] == 'article':
            supabase.table('articles').insert(event['data']).execute()
        elif event['type'] == 'post':
            supabase.table('social_posts').insert(event['data']).execute()

        print(f"[DEMO] Inserted {event['type']} at T+{event['offset_seconds']}s")
```

## Data Flow

### Request Flow (Live Pipeline)

```
[External API: GDELT DOC 2.0]
    ↓ (15-min poll)
[GDELT Fetcher] → normalize → [articles table write]
    ↓ (trigger: new rows)
[Narrative Detector] → LLM analysis → [narrative_events table write]
    ↓
[Correlation Engine reads narrative_events + movement_events]
    ↓ (if correlation detected)
[alerts table write + briefs table write]
    ↓ (Supabase realtime)
[Frontend receives push notification]
    ↓
[React components re-render with new data]
```

### State Management (Frontend)

```
[Supabase Realtime Client]
    ↓ (WebSocket connection)
[useSupabaseRealtime hook]
    ↓ (state update)
[React Context or local state]
    ↓ (subscribe)
[Dashboard Components: Map, Chart, Feeds, Gauge, Brief]
```

### Key Data Flows

1. **Ingestion → Storage → Processing:** Raw data flows from external APIs through ingestion modules into Supabase. Processing modules read from Supabase, analyze, write results back to different tables. No direct ingestion-to-processing communication.

2. **Processing → Frontend:** All analysis results write to Supabase tables with realtime enabled. Frontend subscribes to INSERT events on those tables. Push-based updates, no polling.

3. **Demo Playback → Frontend:** Demo playback engine writes to same tables as live pipeline. Frontend can't distinguish demo data from live data (both arrive via realtime). This means demo exercises the exact same rendering code paths as production.

4. **LLM Analysis → Cache → Fallback:** LLM prompts check local cache first. Cache miss = live API call + cache write. Demo mode uses only cached responses. This ensures deterministic output and zero API cost for repeated demo runs.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **Hackathon prototype (48 hours)** | Current architecture is optimal. Everything in Python scripts. Supabase free tier. No optimization needed. Run on localhost. |
| **Pilot deployment (100 analysts, 50 channels)** | (1) Move ingestion scripts to scheduled jobs (cron or Celery). (2) Add rate limiting to LLM calls (queue via Redis). (3) Upgrade Supabase to Pro for more database connections. (4) Add basic auth (Supabase auth + RLS). Still monolithic Python, single server is fine. |
| **Production (1000 analysts, 500 channels, 24/7 uptime)** | (1) Separate ingestion, processing, and API into distinct services (Docker Compose or K8s). (2) Add message queue (RabbitMQ or AWS SQS) between ingestion and processing to handle backpressure. (3) Implement circuit breakers for LLM APIs (fallback to cached models or rule-based heuristics). (4) Self-host Postgres + Realtime Server (or migrate to managed Postgres + custom WebSocket server). (5) Add horizontal scaling for processing workers (autoscale based on queue depth). (6) Implement proper logging/monitoring (Prometheus + Grafana or Datadog). (7) CDN for frontend assets. (8) Multi-region deployment for low-latency global access. |

### Scaling Priorities

1. **First bottleneck:** LLM API rate limits. As channel count grows, post classification volume overwhelms API quota.
   - **Fix:** Implement request queuing with Redis. Add exponential backoff. Use cheaper models (Gemini 2.5 Flash) for bulk classification. Cache repeated content (many posts are forwards/reposts).

2. **Second bottleneck:** Supabase realtime connection limits (free tier = 100 concurrent, Pro = 500).
   - **Fix:** Upgrade to Supabase Pro. Implement connection pooling on frontend (share realtime client across tabs). Add pagination to historical data queries (don't load all history on page load).

3. **Third bottleneck:** Single-threaded Python processing. As streams multiply, processing lag increases.
   - **Fix:** Parallelize processing with multiprocessing or move to async event-driven architecture (FastAPI background tasks or Celery workers). Add queue-based task distribution.

## Anti-Patterns

### Anti-Pattern 1: Shared State Between Streams

**What people do:** Create a global "analysis context" object that both narrative and movement detection modules read/write to during processing.

**Why it's wrong:** Creates tight coupling. Now both streams must run in same process, on same schedule. If one stream crashes, it can corrupt shared state and crash the other. Impossible to scale independently (can't add more movement processing workers without also scaling narrative processing).

**Do this instead:** Each stream writes its completed analysis to the database. Correlation engine reads from database as the only point of integration. Streams never communicate directly.

### Anti-Pattern 2: Polling the Database from Frontend

**What people do:** React components use setInterval to query Supabase every few seconds for new data.

**Why it's wrong:** Wastes database connections. Introduces 1-5 second latency (users see stale data). Scales poorly (100 users = 100 simultaneous polling queries). Doesn't feel "real-time" (choppy updates).

**Do this instead:** Use Supabase realtime subscriptions. Database pushes updates to frontend via WebSocket. Sub-second latency. Zero polling overhead. Scales to thousands of concurrent users (they all share same replication stream).

### Anti-Pattern 3: Complex Prompts Without Structured Output

**What people do:** Send LLM a wall of text and ask it to "extract all military-relevant entities" with no output format specified. Parse the freeform response with regex or string splitting.

**Why it's wrong:** LLM returns inconsistent formats (sometimes bullet points, sometimes JSON-ish, sometimes prose). Parsing breaks constantly. No validation. Half the processing code is brittle string manipulation.

**Do this instead:** Use LLM structured output (Anthropic's `response_format` or OpenAI's function calling). Define exact JSON schema for response. LLM is constrained to return valid JSON. Parsing is `json.loads()`. Add Pydantic validation for type safety.

**Example:**
```python
# Bad
prompt = "Extract all military units, equipment, and locations from this text."
response = llm.generate(prompt)
# Now parse freeform text... nightmare

# Good
response = anthropic.messages.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": prompt}],
    tools=[{
        "name": "extract_entities",
        "description": "Extract structured military entities",
        "input_schema": {
            "type": "object",
            "properties": {
                "units": {"type": "array", "items": {"type": "string"}},
                "equipment": {"type": "array", "items": {"type": "string"}},
                "locations": {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "lat": {"type": "number"},
                        "lon": {"type": "number"}
                    }
                }}
            }
        }
    }]
)
entities = response.content[0].input  # Guaranteed valid JSON
```

### Anti-Pattern 4: Storing Unprocessed Raw Data

**What people do:** Store every Telegram message's raw JSON in the database, including media metadata, reactions, forwarding chain, etc. Processing modules read this 10KB blob for each post analysis.

**Why it's wrong:** Database bloat. Most fields are never used. Query performance degrades (scanning large text fields). Processing is slow (deserialize JSON, extract relevant fields, every time).

**Do this instead:** Normalize during ingestion. Extract only fields you'll actually use (text, timestamp, channel_id, location mentions). Store as proper columns, not JSON blob. Raw data can be archived to object storage (S3) if you ever need it later.

### Anti-Pattern 5: Hardcoded Prompts in Processing Code

**What people do:** LLM prompts embedded as f-strings scattered throughout processing modules. To tune a prompt, you must find it in the code, edit, restart the process.

**Why it's wrong:** Slow iteration cycle for prompt engineering. Can't A/B test prompts without code changes. No version control for prompts. Risk of breaking code when editing prompts (syntax errors, quote escaping).

**Do this instead:** Store all prompts in `config/prompts.py` or external files. Processing code loads prompts by name. Prompt tuning = edit config file, no code changes, no restart required (reload config or use environment variables). Prompts can be versioned independently from code.

```python
# backend/config/prompts.py
NARRATIVE_COORDINATION_SYSTEM = """
You are an intelligence analyst specializing in state media propaganda patterns.
Analyze batches of articles from Chinese state media outlets for signs of coordination.
"""

NARRATIVE_COORDINATION_PROMPT = """
Analyze these {count} articles published within the last {window_hours} hours:

{articles}

Identify:
1. Repeated unusual phrases across multiple outlets
2. Synchronized theme adoption
3. Doctrinal language shifts

Output JSON:
{{
  "is_coordinated": bool,
  "coordination_score": 0-100,
  "coordinated_phrases": [str],
  "participating_outlets": [str],
  "themes": [str]
}}
"""

# backend/process/narrative_detector.py
from config.prompts import NARRATIVE_COORDINATION_SYSTEM, NARRATIVE_COORDINATION_PROMPT

def analyze_coordination(articles: list) -> dict:
    prompt = NARRATIVE_COORDINATION_PROMPT.format(
        count=len(articles),
        window_hours=6,
        articles=format_articles(articles)
    )
    return llm_call(system=NARRATIVE_COORDINATION_SYSTEM, prompt=prompt)
```

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **GDELT DOC 2.0** | REST API polling (15-min interval) | No auth required. Use `gdeltdoc` Python library. Filter by domain for Chinese state media. Returns JSON with article metadata + tone scores. |
| **Telegram** | Async API via Telethon library | Requires api_id/api_hash from my.telegram.org. Rate limit: ~20 req/sec. Use `get_messages()` for channel history. Handles FloodWait automatically with exponential backoff. |
| **AISstream.io** | WebSocket streaming | Free tier. Connect to wss://stream.aisstream.io/v0/stream. Send bounding box filter (SCS: 0-25°N, 100-125°E). Receive JSON vessel position messages in real-time. Reconnect on disconnect. |
| **Anthropic API** | REST API (Claude models) | Use official `anthropic` Python SDK. API key in env var. $3/$15 per M tokens I/O for Sonnet 4.5. Supports streaming responses. Has structured output via `tools` parameter. |
| **OpenAI API** | REST API (GPT models) | Use official `openai` Python SDK. API key in env var. $0.15/$0.60 per M tokens for GPT-4o Mini. Use for bulk classification (cheaper than Claude). |
| **Supabase** | REST API + Realtime WebSocket | Use `supabase-py` for backend (inserts/queries), `@supabase/supabase-js` for frontend (queries + realtime). Anon key for client, service_role key for backend admin operations. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **Ingestion ↔ Processing** | Via database (write → read) | Ingestion writes to `articles`, `social_posts`, `vessel_positions`. Processing reads from these tables. No direct calls. |
| **Processing ↔ Correlation** | Via database (write → read) | Processing writes to `narrative_events`, `movement_events`. Correlation engine reads both, writes to `alerts`. |
| **Backend ↔ Frontend** | Via database (write → read via realtime) | Backend writes to all tables. Frontend subscribes via Supabase realtime. Bi-directional communication only if frontend needs to trigger actions (e.g., manual refresh button → backend API endpoint). |
| **Demo Playback ↔ Live Pipeline** | Shared database tables | Both write to same schema. Demo uses separate scenario data files. Frontend can't distinguish (both arrive via realtime). Consider adding `is_demo` boolean column if you need to filter. |
| **LLM Modules ↔ LLM APIs** | Via `llm_client.py` wrapper | All LLM calls go through central wrapper. Handles: retry logic, cache lookup, fallback to cached responses in offline mode, token counting, cost tracking. Never call LLM APIs directly from processing code. |

## Build Order and Dependencies

### Phase 0: Foundation (Hours 0-6)
**Goal:** Dev environment + data contracts established

1. **First:** Supabase project + schema definition → This is the contract between all other components
2. **Then parallel:**
   - GDELT fetcher (writes to `articles`)
   - Telegram scraper (writes to `social_posts`)
   - Simulated data loader (writes to all tables)
   - Lovable project init (reads from all tables)

**Why this order:** Schema must exist before anything can write to it. Once schema is live, all ingestion and frontend work can proceed in parallel.

### Phase 1: Processing (Hours 6-16)
**Goal:** Intelligence analysis working end-to-end

1. **First:** LLM client wrapper with cache → All subsequent modules depend on this
2. **Then parallel:**
   - Narrative detector (reads `articles`)
   - Post classifier (reads `social_posts`)
   - Entity extractor (reads either table)
3. **Then:** Correlation engine (reads narrative_events + movement_events)
4. **Finally:** Brief generator (reads `alerts`)

**Why this order:** Can't correlate until both streams produce events. Can't generate briefs until correlation exists. LLM wrapper must be tested first (all modules depend on it).

### Phase 2: Visualization (Hours 16-28)
**Goal:** Dashboard displays everything

1. **First:** Dashboard layout + Supabase realtime connection → Framework for all other components
2. **Then parallel:**
   - Map component
   - Chart component
   - Feed components
   - Gauge component
   - Brief display component

**Why this order:** All visual components need the realtime connection. Once that's working, UI components are independent (different React components, no dependencies).

### Phase 3: Demo Integration (Hours 28-40)
**Goal:** Reliable, repeatable demo

1. **First:** Demo scenario script (defines the story)
2. **Then:** Demo playback engine (implements the script)
3. **Then:** Live data integration (separate tab in UI)
4. **Then:** End-to-end testing + fallback mode

**Why this order:** Can't build playback until scenario is defined. Can't test end-to-end until playback works. Live data is bonus feature (add last).

### Critical Path
```
Schema → LLM Wrapper → Stream Processing → Correlation → Frontend Realtime → Demo Playback
```

**Bottleneck tasks:**
- Schema design (blocks everything)
- LLM wrapper (blocks all processing)
- Correlation engine (blocks demo scenario design)
- Demo playback engine (blocks final presentation rehearsal)

**Parallelizable tasks:**
- All ingestion modules (GDELT, Telegram, AIS, simulated data)
- Narrative detector + post classifier (independent streams)
- All frontend UI components (after realtime connection works)

## Recommended Technology Substitutions

If the recommended stack doesn't work out, here are equivalent alternatives:

| Component | Recommended | Alternative 1 | Alternative 2 | Notes |
|-----------|-------------|---------------|---------------|-------|
| **Database + Realtime** | Supabase | Firebase Realtime DB + Cloud Functions | Self-hosted Postgres + Hasura | Supabase is easiest for hackathon. Firebase is faster to set up but more expensive. Hasura is most flexible but requires DevOps. |
| **Frontend framework** | Lovable (React) | Streamlit (Python) | Next.js (manual React) | Lovable = fastest to polished UI. Streamlit = fastest to working prototype (but ugly). Next.js = most control (but slowest). |
| **LLM for analysis** | Claude Sonnet 4.5 | GPT-4 Turbo | Gemini 1.5 Pro | Claude best for long context + reasoning. GPT-4 more familiar to most devs. Gemini cheapest for similar quality. |
| **LLM for classification** | GPT-4o Mini | Gemini 2.5 Flash | Claude Haiku 3.5 | All optimized for speed + cost. GPT-4o Mini most tested. Gemini Flash cheapest. Haiku best reasoning for price. |
| **Map library** | Leaflet (open source) | Mapbox GL JS | Google Maps | Leaflet = free, good enough. Mapbox = best performance + visuals (free tier 50k loads/mo). Google Maps = overkill + expensive. |
| **Chart library** | Recharts | Chart.js | D3.js | Recharts = native React, declarative. Chart.js = most popular, imperative. D3 = maximum flexibility, steep learning curve. |
| **Telegram client** | Telethon | python-telegram-bot | pyrogram | Telethon = most mature, best docs. python-telegram-bot = for bots (not scraping). pyrogram = faster but less stable. |

## Sources

**Architecture patterns:**
- Domain knowledge: OSINT data fusion systems (intelligence community tradecraft)
- Domain knowledge: Real-time analytics architectures (Lambda/Kappa architecture patterns)
- Dragon Watch dev report (provided in project context)

**Technology choices:**
- Supabase documentation (https://supabase.com/docs)
- Anthropic API documentation (https://docs.anthropic.com)
- GDELT project documentation (https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)
- Telethon documentation (https://docs.telethon.dev/)

**OSINT pipelines:**
- Bellingcat's open source investigation methodology
- GDELT sentiment analysis project (github.com/t4f1d/sentiment-analysis)
- Vessel research toolkit (github.com/followthemoney/vessel_research)

**Confidence:** HIGH for general architecture patterns (established patterns in intelligence systems). HIGH for technology-specific implementation (based on official documentation). MEDIUM for scaling considerations (based on domain knowledge, not verified at Dragon Watch's specific scale).

---
*Architecture research for: Dragon Watch OSINT pre-conflict detection system*
*Researched: 2026-02-07*

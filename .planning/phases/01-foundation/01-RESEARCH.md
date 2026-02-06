# Phase 1: Foundation - Research

**Researched:** 2026-02-07
**Domain:** Python data pipeline (ETL) with Supabase, GDELT, Telegram, AIS WebSocket
**Confidence:** MEDIUM

## Summary

Phase 1 builds a Python-based ETL pipeline that ingests data from three live sources (GDELT articles, Telegram messages, AIS vessel positions) into Supabase with realtime subscriptions enabled. The standard approach uses async Python for concurrent data collection, FastAPI BackgroundTasks for lightweight scheduling, Supabase Python client v2+ with async realtime, and direct SQL migrations via Supabase CLI.

Key technical constraints: All data sources require async/await patterns (Telethon, websockets, Supabase realtime). Rate limiting is critical for Telegram (FloodWaitError) and GDELT (undocumented quotas). Supabase realtime requires async client initialization via `acreate_client()` and manual replication enabling for database change subscriptions.

The hackathon context demands pragmatic shortcuts: SQL migrations without ORM, manual schema creation over migration generators, simulated data priority over live feed robustness, and FastAPI BackgroundTasks instead of Celery/Airflow. This trades production scalability for 48-hour delivery speed.

**Primary recommendation:** Use Supabase CLI for schema setup, async Python with FastAPI BackgroundTasks for data collection, and prioritize simulated dataset creation before debugging live API integrations.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| supabase-py | 2.27.3+ | Supabase client with realtime | Official Python client, async support added v2+, active development |
| fastapi | Latest | API framework with background tasks | Native BackgroundTasks for lightweight scheduling, async-first |
| gdeltdoc | 1.12.0 | GDELT DOC 2.0 API wrapper | Article-level queries with pandas output, simpler than gdeltPyR for small-scale analysis |
| Telethon | 1.42.0 | Telegram MTProto client | Asyncio-native, pip installable, handles rate limiting automatically |
| websockets | 16.0+ | WebSocket client library | Built-in reconnection support, asyncio integration, Python standard for WS |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | 2.x | Data validation | Validate API responses before Supabase insert, type safety |
| asyncio | stdlib | Async runtime | Required for Telethon, websockets, Supabase realtime |
| pandas | Latest | Data transformation | GDELT returns DataFrames, useful for bulk processing |
| supabase-pydantic | Latest | Generate models from schema | Optional: Auto-generate Pydantic models from Supabase tables |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FastAPI BackgroundTasks | Celery/Airflow | Celery adds Redis dependency, overkill for 48hr hackathon. Use for production multi-worker pipelines |
| Supabase CLI migrations | Alembic + SQLAlchemy | Alembic better for ORM-first workflows, but adds complexity when Supabase Studio provides schema UI |
| gdeltdoc | gdeltPyR | gdeltPyR handles v1/v2 GDELT but more complex API. gdeltdoc simpler for DOC 2.0 article queries |
| Telethon | python-telegram-bot | python-telegram-bot is for bots, Telethon for user/scraper accounts |

**Installation:**
```bash
pip install supabase==2.27.3 fastapi uvicorn[standard] gdeltdoc==1.12.0 Telethon==1.42.0 websockets pydantic pandas
```

## Architecture Patterns

### Recommended Project Structure
```
dragon-watch/
├── src/
│   ├── fetchers/           # Data collection modules
│   │   ├── gdelt.py        # GDELT article fetcher
│   │   ├── telegram.py     # Telegram scraper
│   │   └── ais.py          # AIS WebSocket client
│   ├── models/             # Pydantic validation models
│   ├── database/           # Supabase client + helpers
│   │   └── client.py       # Async Supabase singleton
│   └── main.py             # FastAPI app with background tasks
├── supabase/
│   ├── migrations/         # SQL migration files
│   └── seed.sql            # Simulated demo dataset
├── scripts/
│   └── load_demo_data.py   # One-time demo data loader
└── .env                    # API keys (not committed)
```

### Pattern 1: Async Supabase Client Singleton
**What:** Single async Supabase client shared across all fetchers, initialized once at startup.
**When to use:** All Supabase operations, especially realtime subscriptions (requires async client).
**Example:**
```python
# src/database/client.py
# Source: https://github.com/supabase/supabase-py (v2.27.3 docs)
from supabase import acreate_client, AsyncClient
import os

_supabase_client: AsyncClient | None = None

async def get_supabase() -> AsyncClient:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = await acreate_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    return _supabase_client
```

### Pattern 2: FastAPI Background Task Data Fetchers
**What:** Lightweight background tasks that run after API response, ideal for periodic data collection.
**When to use:** Fetchers that run on-demand or simple scheduling (not complex DAGs).
**Example:**
```python
# src/main.py
# Source: https://fastapi.tiangolo.com/tutorial/background-tasks/
from fastapi import FastAPI, BackgroundTasks
from src.fetchers.gdelt import fetch_gdelt_articles

app = FastAPI()

async def run_gdelt_fetcher():
    """Background task to fetch GDELT articles"""
    supabase = await get_supabase()
    articles = await fetch_gdelt_articles()
    await supabase.table("articles").insert(articles).execute()

@app.post("/fetch/gdelt")
async def trigger_gdelt(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_gdelt_fetcher)
    return {"status": "started"}
```

### Pattern 3: WebSocket Reconnection Loop
**What:** Infinite async iterator with automatic reconnection on network errors.
**When to use:** AIS WebSocket stream that must maintain 24/7 connection.
**Example:**
```python
# src/fetchers/ais.py
# Source: https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html
import asyncio
import websockets
import json

async def ais_stream():
    """Connect to AISstream.io with auto-reconnect"""
    url = "wss://stream.aisstream.io/v0/stream"

    async for websocket in websockets.connect(url):
        try:
            # Subscribe within 3 seconds or connection closes
            subscribe_msg = {
                "APIKey": os.getenv("AISSTREAM_API_KEY"),
                "BoundingBoxes": [[[23.0, 118.0], [26.0, 122.0]]],  # Taiwan Strait
                "FilterMessageTypes": ["PositionReport"]
            }
            await websocket.send(json.dumps(subscribe_msg))

            async for message in websocket:
                data = json.loads(message)
                # Process and insert to Supabase
                await handle_ais_message(data)

        except websockets.ConnectionClosed:
            continue  # Auto-reconnect on next iteration
```

### Pattern 4: Telethon Rate Limit Handling
**What:** Telethon auto-sleeps on FloodWaitError < 60s, manual handling for longer waits.
**When to use:** All Telegram channel scraping operations.
**Example:**
```python
# src/fetchers/telegram.py
# Source: https://docs.telethon.dev/en/stable/ + https://tech-champion.com/database/solving-telethon-telegram-timeouts-and-floodwaiterror-on-servers/
from telethon import TelegramClient, errors
import asyncio

client = TelegramClient('session', api_id, api_hash)

async def scrape_channel(channel_username: str):
    """Scrape channel with automatic rate limit handling"""
    try:
        async for message in client.iter_messages(channel_username, limit=100):
            # Process message
            await store_message(message)

    except errors.FloodWaitError as e:
        # Auto-handled if < 60s, manual if > 60s
        if e.seconds > 60:
            print(f"FloodWait {e.seconds}s, sleeping...")
            await asyncio.sleep(e.seconds)
```

### Pattern 5: GDELT Domain Filtering
**What:** Use `domain_exact` parameter for precise domain matching (avoid partial matches).
**When to use:** Querying specific Chinese state media outlets.
**Example:**
```python
# src/fetchers/gdelt.py
# Source: https://github.com/alex9smith/gdelt-doc-api (v1.12.0)
from gdeltdoc import GdeltDoc, Filters

gd = GdeltDoc()

# Query Chinese state media domains
filters = Filters(
    start_date="2026-02-07",
    end_date="2026-02-07",
    domain_exact=["xinhuanet.com", "globaltimes.cn", "cctv.com", "people.com.cn"]
)

articles = gd.article_search(filters)
# Returns pandas DataFrame with columns: url, title, seendate, domain, language, sourcecountry
```

### Anti-Patterns to Avoid
- **Sync Supabase client for realtime:** Realtime only works with `acreate_client()`, not `create_client()`. Sync client will fail silently.
- **Not enabling replication:** By default, Supabase disables database change subscriptions. Must enable via Dashboard → Replication settings.
- **Forgetting WebSocket subscription timeout:** AISstream.io closes connection if no subscription message within 3 seconds of connecting.
- **Using `domain` instead of `domain_exact`:** GDELT's `domain` parameter does partial matching ("times" matches nytimes.com AND globaltimes.cn). Always use `domain_exact` for precision.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Database migrations | Manual SQL file tracking | Supabase CLI migrations | Built-in versioning, automatic apply on `db reset`, integrates with remote push |
| WebSocket reconnection | Try/except + while loop | `websockets.connect()` as async iterator | Built-in exponential backoff, retries 500/502/503/504 errors automatically |
| Pydantic models from schema | Hand-write dataclasses | `supabase-pydantic` CLI | Auto-generates Insert/Update models with field validators from Supabase schema |
| Telegram rate limiting | Sleep timers + retry logic | Telethon's `flood_sleep_threshold` | Auto-sleeps on FloodWaitError < 60s, exposes `.seconds` for manual handling |
| Async task scheduling | Custom thread pools | FastAPI BackgroundTasks | Native FastAPI integration, handles async/sync functions, runs after response |

**Key insight:** Data pipeline libraries (Telethon, websockets, gdeltdoc) already handle the hard parts (auth, rate limits, reconnection). Hand-rolling these creates bugs that only appear under production load. Use library defaults, override only when measured as bottleneck.

## Common Pitfalls

### Pitfall 1: Supabase Realtime Not Enabled on Tables
**What goes wrong:** Supabase realtime subscriptions silently fail. Python client connects but receives no events when database changes.
**Why it happens:** New Supabase projects disable realtime by default for performance. Must manually enable replication per table.
**How to avoid:**
1. In Supabase Dashboard → Database → Replication
2. Enable replication for each table (articles, social_posts, vessel_positions, etc.)
3. For UPDATE/DELETE events, set table REPLICA IDENTITY to FULL
**Warning signs:** Realtime subscription connects without errors but callback never fires on inserts.

### Pitfall 2: GDELT Chinese Media Domain Coverage Gaps
**What goes wrong:** GDELT query returns zero results for valid Chinese state media domains.
**Why it happens:** GDELT indexes vary by outlet. "xinhuanet.com" may be indexed, "xinhua.com" may not. English vs Chinese language sites have different domain patterns.
**How to avoid:**
1. Test each domain with GDELT Analysis Service first (https://analysis.gdeltproject.org/)
2. Use GDELT Summary (https://summary.gdeltproject.org/) to verify recent indexing
3. Validate during Phase 1 setup, document working domains
**Warning signs:** Empty DataFrame from `gd.article_search()` despite knowing articles exist. Check GDELT coverage, not your code.

### Pitfall 3: Telethon Session File Conflicts
**What goes wrong:** `ValueError: Can't send requests while disconnected` or authentication loops.
**Why it happens:** Telethon stores session state in `.session` file. Multiple concurrent clients or corrupted session causes conflicts.
**How to avoid:**
1. Use unique session names per deployment: `TelegramClient('dragon-watch-prod', ...)`
2. Don't commit `.session` files to git (add to `.gitignore`)
3. On session errors, delete `.session` file and re-authenticate
**Warning signs:** Scraper works locally but fails on server, or fails after code deployment.

### Pitfall 4: AISstream.io Message Queue Overflow
**What goes wrong:** WebSocket connection closes unexpectedly with no error message.
**Why it happens:** If client can't process messages fast enough (~300 msg/sec globally), AISstream.io closes connection when queue exceeds limit.
**How to avoid:**
1. Use narrow bounding boxes (Taiwan Strait only, not global)
2. Filter MessageTypes: `["PositionReport"]` only, exclude `["ShipStaticData", "StandardClassBPositionReport"]`
3. Batch Supabase inserts (bulk insert 100 positions vs 100 individual inserts)
4. If processing lags, add `asyncio.Queue` buffer between websocket and database
**Warning signs:** WebSocket disconnects after 1-2 minutes of high message volume.

### Pitfall 5: Async Context Mixing in Supabase Realtime Callbacks
**What goes wrong:** `RuntimeError: cannot call await from sync context` in realtime subscription callbacks.
**Why it happens:** Supabase realtime callbacks may execute in sync context, but need to call async database operations.
**How to avoid:** Use `asyncio.create_task()` to schedule async operations from sync callbacks.
```python
def on_postgres_changes(payload):
    # Don't: await supabase.table("other").insert(...)  # RuntimeError
    # Do:
    asyncio.create_task(handle_change(payload))

async def handle_change(payload):
    await supabase.table("other").insert(...)  # Safe
```
**Warning signs:** `RuntimeError` when realtime event fires, works fine in direct async calls.

### Pitfall 6: GDELT API Undocumented Rate Limits
**What goes wrong:** GDELT API returns HTTP 429 or empty results after initial queries succeed.
**Why it happens:** GDELT has rate limits ("fractions of a QPS" per blog posts) but no official documented quotas. Rapid consecutive queries trigger throttling.
**How to avoid:**
1. Add delays between queries: `await asyncio.sleep(2)` between article fetches
2. Use `maxrecords` parameter to reduce response size: `&maxrecords=250` (default is lower)
3. For development, cache GDELT responses to avoid re-querying
4. If hit limits, wait 60+ seconds before retry
**Warning signs:** First 5-10 queries work, then sudden empty DataFrames or timeouts.

## Code Examples

Verified patterns from official sources:

### Supabase Async Client Initialization
```python
# Source: https://github.com/supabase/supabase-py (v2.27.3)
from supabase import acreate_client, AsyncClient
import os

async def init_supabase() -> AsyncClient:
    """Initialize async Supabase client (required for realtime)"""
    supabase: AsyncClient = await acreate_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    return supabase

# Usage in FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize client
    app.state.supabase = await init_supabase()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(lifespan=lifespan)
```

### GDELT Chinese State Media Query
```python
# Source: https://github.com/alex9smith/gdelt-doc-api (v1.12.0)
from gdeltdoc import GdeltDoc, Filters
from datetime import datetime, timedelta

gd = GdeltDoc()

# Query last 24 hours from Chinese state media
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")

filters = Filters(
    start_date=yesterday,
    end_date=today,
    domain_exact=["xinhuanet.com", "globaltimes.cn", "cctv.com", "people.com.cn"],
    num_records=250  # Max results per query
)

articles_df = gd.article_search(filters)

# DataFrame columns: url, url_mobile, title, seendate, socialimage, domain, language, sourcecountry
# Convert to dict for Supabase insert
articles = articles_df.to_dict('records')
```

### Telethon Channel Scraper Setup
```python
# Source: https://docs.telethon.dev/en/stable/
from telethon import TelegramClient
import os

# Get API credentials from https://my.telegram.org/apps
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

# Session name (creates .session file)
client = TelegramClient('dragon-watch', api_id, api_hash)

async def scrape_osint_channels():
    """Scrape messages from OSINT/military channels"""
    await client.start()

    channels = [
        "@osinttechnical",
        "@IntelDoge",
        # Add 8-10 more OSINT channels
    ]

    for channel in channels:
        async for message in client.iter_messages(channel, limit=100):
            # Extract message data
            post = {
                "telegram_id": message.id,
                "channel": channel,
                "text": message.text,
                "timestamp": message.date.isoformat(),
                "views": message.views
            }

            # Insert to Supabase
            await supabase.table("social_posts").insert(post).execute()
```

### AISstream.io Taiwan Strait Tracker
```python
# Source: https://github.com/aisstream/aisstream + https://aisstream.io/documentation
import asyncio
import websockets
import json
import os

async def track_taiwan_strait():
    """Stream AIS positions for Taiwan Strait bounding box"""
    url = "wss://stream.aisstream.io/v0/stream"

    # Taiwan Strait bounding box (approximate)
    # Center: 24.8°N, 119.9°E
    # Box: 23-26°N, 118-122°E
    subscription = {
        "APIKey": os.getenv("AISSTREAM_API_KEY"),
        "BoundingBoxes": [
            [[23.0, 118.0], [26.0, 122.0]]  # [[lat1, lon1], [lat2, lon2]]
        ],
        "FilterMessageTypes": ["PositionReport"]  # Only position updates
    }

    async for websocket in websockets.connect(url):
        try:
            # Must subscribe within 3 seconds
            await websocket.send(json.dumps(subscription))

            async for message_str in websocket:
                message = json.loads(message_str)

                # Extract position data
                ais_data = message["Message"]["PositionReport"]
                position = {
                    "mmsi": message["MetaData"]["MMSI"],
                    "ship_name": message["MetaData"].get("ShipName"),
                    "latitude": ais_data["Latitude"],
                    "longitude": ais_data["Longitude"],
                    "speed": ais_data.get("Sog"),  # Speed over ground
                    "course": ais_data.get("Cog"),  # Course over ground
                    "timestamp": message["MetaData"]["time_utc"]
                }

                # Insert to Supabase
                await supabase.table("vessel_positions").insert(position).execute()

        except websockets.ConnectionClosed:
            print("AIS connection closed, reconnecting...")
            await asyncio.sleep(5)
            continue  # Auto-reconnect
```

### Supabase Migration Creation
```bash
# Source: https://supabase.com/docs/guides/deployment/database-migrations

# Initialize Supabase project (if not done)
supabase init

# Create new migration file
supabase migration new create_foundation_tables

# Edit supabase/migrations/YYYYMMDDHHMMSS_create_foundation_tables.sql
# Add table creation SQL:
```

```sql
-- Source: Dragon Watch requirements DATA-05
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  url TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  domain TEXT NOT NULL,
  published_at TIMESTAMPTZ NOT NULL,
  tone_score FLOAT,
  language TEXT,
  source_country TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE social_posts (
  id BIGSERIAL PRIMARY KEY,
  telegram_id BIGINT,
  channel TEXT NOT NULL,
  text TEXT,
  timestamp TIMESTAMPTZ NOT NULL,
  views INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE vessel_positions (
  id BIGSERIAL PRIMARY KEY,
  mmsi INTEGER NOT NULL,
  ship_name TEXT,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  speed FLOAT,
  course FLOAT,
  timestamp TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE narrative_events (
  id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  summary TEXT NOT NULL,
  confidence FLOAT,
  source_ids JSONB,
  detected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE movement_events (
  id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  vessel_mmsi INTEGER,
  location_lat FLOAT,
  location_lon FLOAT,
  description TEXT,
  detected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE alerts (
  id BIGSERIAL PRIMARY KEY,
  severity TEXT NOT NULL,  -- 'low', 'medium', 'high', 'critical'
  title TEXT NOT NULL,
  description TEXT,
  event_ids JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);

CREATE TABLE briefs (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  key_developments JSONB,
  generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable realtime for all tables (CRITICAL: must enable replication in Dashboard)
-- This just prepares tables, actual replication enabled via UI
ALTER PUBLICATION supabase_realtime ADD TABLE articles;
ALTER PUBLICATION supabase_realtime ADD TABLE social_posts;
ALTER PUBLICATION supabase_realtime ADD TABLE vessel_positions;
ALTER PUBLICATION supabase_realtime ADD TABLE narrative_events;
ALTER PUBLICATION supabase_realtime ADD TABLE movement_events;
ALTER PUBLICATION supabase_realtime ADD TABLE alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE briefs;
```

```bash
# Apply migration locally
supabase db reset  # Recreates DB + applies all migrations + seeds

# Deploy to remote
supabase db push
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sync Supabase client | Async client via `acreate_client()` | v2.0 (2024) | Realtime only works with async, breaking change for realtime users |
| Manual replication setup | UI toggle in Dashboard | 2023 | Easier to enable, but still disabled by default (performance) |
| Celery for background tasks | FastAPI BackgroundTasks | FastAPI 0.63+ (2021) | Lighter weight for simple tasks, Celery still better for multi-worker |
| gdeltPyR for all GDELT | gdeltdoc for DOC 2.0 | 2020+ | gdeltdoc simpler API for article queries, gdeltPyR still active for v1/v2 |
| Telegram bot libraries | Telethon for scraping | N/A | Different use cases: bots vs user/scraper accounts |

**Deprecated/outdated:**
- **Supabase-realtime-py separate package:** Now bundled in supabase-py v2+. Don't install `supabase-realtime` independently.
- **GDELT v1 Event Database for articles:** Use DOC 2.0 API (gdeltdoc) for article-level data. V1 is event-level, different schema.
- **Manual WebSocket reconnection with while/try/except:** Use `websockets.connect()` as async iterator (v10+), handles reconnection automatically.

## Open Questions

Things that couldn't be fully resolved:

1. **GDELT Chinese state media domain exact URLs**
   - What we know: GDELT indexes "xinhuanet.com", "globaltimes.cn", "people.com.cn", "cctv.com" (from web mentions)
   - What's unclear: Exact working domain strings (e.g., "en.people.cn" vs "people.com.cn"), coverage reliability
   - Recommendation: TEST FIRST in Phase 1 setup. Use GDELT Analysis Service to validate each domain returns recent articles. Document working domains in code comments. If coverage gaps, supplement with RSS feeds.

2. **AISstream.io free tier message volume limits**
   - What we know: Taiwan Strait bounding box will be ~1-5% of global traffic (~15 msg/sec estimate), free tier exists but no explicit quota
   - What's unclear: Whether free tier can handle 24/7 Taiwan Strait stream, or needs paid tier
   - Recommendation: START with free tier, monitor for disconnections. If rate-limited, narrow bounding box further or add message throttling (skip every Nth position update).

3. **Telegram OSINT channel access restrictions**
   - What we know: Public channels don't require joining, Telethon can scrape without membership
   - What's unclear: Some OSINT channels may be private/invite-only, or block API access
   - Recommendation: VALIDATE during Phase 1. Manually verify each target channel allows public access. Have 10-15 backup channels in case 5-10 are inaccessible.

4. **Supabase realtime subscription limits per project**
   - What we know: Realtime has connection limits per pricing tier, free tier supports "up to 200 concurrent connections"
   - What's unclear: Whether this includes server-side subscriptions (Python client) or just browser clients, and whether 7 table subscriptions count as 7 connections
   - Recommendation: ASSUME subscriptions count as connections. For hackathon, server-side subscriptions will be 1-3 (not 200). Fine for free tier. For production, use Postgres LISTEN/NOTIFY or dedicated message queue.

5. **Python 3.11+ compatibility for all libraries**
   - What we know: Telethon supports "Python >=3.5", supabase-py uses modern async (likely 3.8+), gdeltdoc not explicitly versioned
   - What's unclear: Whether gdeltdoc/websockets have Python 3.11+ compatibility issues
   - Recommendation: TEST in Phase 1 setup. Run `pip install` and import tests for all libraries. If conflicts, pin Python 3.10 in Dockerfile/environment.

## Sources

### Primary (HIGH confidence)
- Supabase Python Client v2.27.3 - https://github.com/supabase/supabase-py
- Telethon v1.42.0 - https://docs.telethon.dev/en/stable/ + https://pypi.org/project/Telethon/
- FastAPI Background Tasks - https://fastapi.tiangolo.com/tutorial/background-tasks/
- websockets library - https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html
- gdeltdoc v1.12.0 - https://github.com/alex9smith/gdelt-doc-api + https://pypi.org/project/gdeltdoc/
- AISstream.io documentation - https://aisstream.io/documentation
- Supabase CLI migrations - https://supabase.com/docs/guides/deployment/database-migrations

### Secondary (MEDIUM confidence)
- Supabase Realtime Python API reference - https://supabase.com/docs/reference/python/realtime-api (verified with GitHub repo)
- GDELT rate limiting blog post - https://blog.gdeltproject.org/behind-the-scenes-api-quotas-the-impact-of-a-fraction-of-a-qps/ (official GDELT blog)
- Telethon FloodWaitError handling - https://tech-champion.com/database/solving-telethon-telegram-timeouts-and-floodwaiterror-on-servers/ (verified with docs)
- Taiwan Strait coordinates - https://latitude.to/articles-by-country/general/10083/taiwan-strait (verified with maps)
- supabase-pydantic tool - https://github.com/kmbhm1/supabase-pydantic (active repo, recent 2026 activity)

### Tertiary (LOW confidence - marked for validation)
- GDELT Chinese state media coverage examples - WebSearch results mention "Xinhua", "Global Times" in GDELT blog posts, but no direct verification of current indexing
- Supabase realtime best practices - https://www.leanware.co/insights/supabase-best-practices (third-party blog, not official docs)
- FastAPI ETL project structure - Multiple Medium articles (https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f), not official standard

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified on PyPI with recent versions, official docs fetched
- Architecture: MEDIUM - Patterns verified from official docs, but project structure is inferred best practice (not prescribed standard)
- Pitfalls: MEDIUM - Realtime replication and FloodWaitError confirmed from official sources, GDELT rate limits from blog (not API docs), AIS queue overflow from docs

**Research date:** 2026-02-07
**Valid until:** 2026-03-09 (30 days) - Libraries stable, but check for Supabase Python client updates (active development)

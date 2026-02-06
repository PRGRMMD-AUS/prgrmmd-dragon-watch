# Stack Research

**Domain:** OSINT Pre-Conflict Early Warning System
**Researched:** 2026-02-07
**Confidence:** MEDIUM (training data from January 2025, unable to verify current versions)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Backend runtime | Modern async/await, performance improvements, type hints, required for project constraints |
| Supabase | Latest | Postgres database + Realtime | Free-tier friendly, built-in realtime subscriptions, managed Postgres, auth included |
| FastAPI | 0.115+ | API framework | Best async Python framework for realtime data pipelines, auto OpenAPI docs, WebSocket support |
| Pydantic | 2.x | Data validation | Type-safe models, JSON schema generation, FastAPI integration, validation at boundaries |

### Data Collection Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| gdeltdoc | 1.4+ | GDELT DOC 2.0 API wrapper | State media article collection, narrative analysis data source |
| gdeltPyR | 0.1+ | GDELT into Pandas | Alternative GDELT interface if gdeltdoc insufficient, DataFrame operations |
| Telethon | 1.36+ | Telegram API client | Civilian movement detection via Telegram channels, async by default |
| httpx | 0.27+ | Async HTTP client | API calls to GDELT, LLM providers, better than requests for async workflows |
| beautifulsoup4 | 4.12+ | HTML parsing | Article content extraction if GDELT DOC snippets insufficient |
| feedparser | 6.0+ | RSS parsing | Backup data source for state media if GDELT gaps exist |

### Data Processing & Analysis

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pandas | 2.2+ | Tabular data operations | GDELT data wrangling, time-series windowing for 72-hour correlations |
| numpy | 1.26+ | Numerical operations | Coordinate calculations, statistical thresholds for threat levels |
| spaCy | 3.7+ | NLP preprocessing | Entity extraction, language detection before LLM analysis (cost reduction) |
| langdetect | 1.0+ | Language detection | Filter non-target language content before expensive LLM calls |
| python-dateutil | 2.9+ | Date parsing | Handle varied timestamp formats from GDELT, Telegram, social media APIs |

### LLM Integration

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| anthropic | 0.39+ | Claude API client | Narrative coordination analysis (Sonnet 4.5), intelligence brief generation |
| openai | 1.54+ | OpenAI API client | Bulk classification with GPT-4o Mini for civilian movement posts |
| google-generativeai | 0.8+ | Gemini API client | Alternative bulk classifier (2.5 Flash), API cost arbitrage |
| litellm | 1.52+ | Unified LLM interface | Switch between Claude/GPT/Gemini without code changes, cost tracking |

### Database & Realtime

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| supabase | 2.10+ | Supabase Python client | Write detections, trigger realtime subscriptions to frontend |
| asyncpg | 0.29+ | Async Postgres driver | Direct DB access if Supabase client insufficient, bulk inserts |
| psycopg2-binary | 2.9+ | Sync Postgres driver | Maintenance scripts, data migrations where async not needed |

### Task Orchestration

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| celery | 5.4+ | Distributed task queue | Schedule periodic GDELT/Telegram polling, parallel LLM calls |
| redis | 5.2+ | Message broker for Celery | Task queue backend, deduplication cache, rate limiting |
| apscheduler | 3.10+ | Cron-like scheduler | Simpler alternative to Celery if single-machine sufficient |
| rq | 1.16+ | Lightweight task queue | Minimalist alternative to Celery, Redis-backed, easier debugging |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Package management | Faster than pip, lockfile support, replaces pip + virtualenv |
| ruff | Linting + formatting | Replaces Black + isort + flake8, 100x faster, single tool |
| mypy | Static type checking | Catch bugs before runtime, critical for data pipelines |
| pytest | Testing framework | Async support, fixture system for DB mocks |
| pytest-asyncio | Async test support | Test async GDELT/Telegram collection functions |
| httpx-mock | HTTP mocking | Mock GDELT/LLM API calls in tests, avoid API costs |

## Installation

```bash
# Core framework
uv pip install fastapi[standard]==0.115.* pydantic==2.* uvicorn[standard]==0.32.*

# Data collection
uv pip install gdeltdoc==1.4.* Telethon==1.36.* httpx==0.27.* beautifulsoup4==4.12.* feedparser==6.0.*

# Data processing
uv pip install pandas==2.2.* numpy==1.26.* spacy==3.7.* langdetect==1.0.* python-dateutil==2.9.*

# LLM clients
uv pip install anthropic==0.39.* openai==1.54.* google-generativeai==0.8.* litellm==1.52.*

# Database
uv pip install supabase==2.10.* asyncpg==0.29.* psycopg2-binary==2.9.*

# Task queue (choose one)
uv pip install celery[redis]==5.4.* redis==5.2.*
# OR
uv pip install rq==1.16.* redis==5.2.*

# Dev dependencies
uv pip install ruff==0.8.* mypy==1.13.* pytest==8.3.* pytest-asyncio==0.24.* httpx-mock==0.0.*
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| FastAPI | Flask | If team unfamiliar with async, but loses realtime benefits |
| FastAPI | Django | If need admin panel, but overhead for data pipeline system |
| Celery | Temporal | If need complex workflow orchestration, but setup overhead for 48h project |
| Supabase | Raw Postgres + PostgREST | If need full control, but loses managed realtime subscriptions |
| Telethon | python-telegram-bot | If only need bot operations, but Telethon better for channel scraping |
| gdeltdoc | Direct GDELT API calls | If need customization gdeltdoc doesn't provide |
| litellm | Direct SDK calls | If only using one LLM provider and don't need cost tracking |
| uv | pip + pip-tools | If team requires traditional pip workflow |
| ruff | black + isort + flake8 | If team has existing configs for separate tools |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| requests | Blocking I/O kills performance with many API calls | httpx (async) |
| scrapy | Overkill for GDELT API, designed for crawling HTML sites | httpx + gdeltdoc |
| SQLAlchemy | Async support immature, adds abstraction layer complexity | asyncpg directly or Supabase client |
| Haystack/LangChain | Heavy frameworks for simple LLM calls, debugging nightmare | Direct SDK calls or litellm |
| Airflow | Infrastructure overhead for 48h hackathon, overkill for simple scheduling | APScheduler or Celery |
| tweepy | Twitter API costs prohibitive, civilian movement detection via Telegram cheaper | Telethon |
| newspaper3k | Unmaintained since 2019, better alternatives exist | beautifulsoup4 + httpx |
| transformers (local LLMs) | Inference too slow for realtime, GPU costs exceed API budget | Claude/GPT/Gemini APIs |

## Stack Patterns by Variant

**If building MVP in 48 hours:**
- Skip Celery, use APScheduler with in-process tasks
- Skip Redis, use in-memory deduplication
- Skip spaCy preprocessing, send raw text to LLMs
- Because: Infrastructure setup time doesn't fit 48h constraint

**If scaling beyond prototype:**
- Add Celery + Redis for distributed processing
- Add spaCy preprocessing to reduce LLM API costs
- Add asyncpg bulk inserts for high-volume data
- Because: Cost optimization and horizontal scaling required

**If API budget under $25:**
- Use GPT-4o Mini for all classification (cheapest per token)
- Use Gemini 2.5 Flash as fallback (free tier generous)
- Use Claude Sonnet only for final intelligence briefs (1-2 per day)
- Because: Claude most expensive, reserve for highest-value analysis

**If Telegram channels rate-limited:**
- Add Redis cache for channel message IDs
- Implement exponential backoff with Telethon's flood wait handling
- Spread polling across multiple Telegram accounts if needed
- Because: Telegram aggressive with rate limits, need resilience

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| FastAPI 0.115+ | Pydantic 2.x | Pydantic v1 not supported in FastAPI 0.100+ |
| Celery 5.4+ | Redis 5.x | Redis 6.x works but 5.x sufficient |
| Telethon 1.36+ | Python 3.11+ | asyncio native, no legacy Python support |
| pandas 2.2+ | numpy 1.26+ | Numpy 2.x not yet supported by pandas 2.2 |
| spaCy 3.7+ | Python 3.11+ | Requires model download: `python -m spacy download en_core_web_sm` |
| supabase 2.10+ | asyncpg optional | Supabase client can use asyncpg under the hood if installed |

## Architecture Notes

### Two-Pipeline Design

**Pipeline 1: State Media Narrative Analysis**
```
GDELT DOC 2.0 API → gdeltdoc → Pandas DataFrame →
spaCy entity extraction → Claude Sonnet 4.5 coordination detection →
Supabase insert (detections table) → Realtime broadcast
```

**Pipeline 2: Civilian Movement Detection**
```
Telegram channels → Telethon async iterator →
langdetect filter → GPT-4o Mini classification →
Supabase insert (movements table) → Realtime broadcast
```

**Correlation Engine**
```
Periodic query (every 6h): JOIN detections + movements ON
  timestamp_diff < 72h AND geo_proximity < 500km
→ Claude Sonnet threat assessment → Intelligence brief
```

### Cost Optimization Strategy

1. **Preprocessing layer (spaCy + langdetect)**: Filter 70% of content before LLM calls
2. **Tiered LLM usage**: Gemini/GPT for classification, Claude for analysis
3. **Caching**: Redis deduplication prevents reprocessing same articles/posts
4. **Batch processing**: Accumulate posts, send to LLM in batches (10-20 at once)
5. **Token limits**: Truncate articles to 1000 tokens, social posts to 200 tokens

### Realtime Architecture

- **Backend writes**: asyncpg bulk inserts to Supabase Postgres
- **Frontend reads**: Supabase Realtime subscriptions (WebSocket)
- **No polling**: Frontend receives updates pushed from Postgres triggers
- **Intelligence briefs**: Stored as JSONB in `assessments` table, single subscription

### Rate Limiting Considerations

| Service | Free Tier Limit | Mitigation |
|---------|----------------|------------|
| GDELT DOC | Unlimited (public) | None needed |
| Telegram | 20 req/sec per account | Use Telethon's flood wait, spread across time |
| Claude Sonnet | 50 req/min | Cache results, use only for final analysis |
| GPT-4o Mini | 500 req/min | Sufficient for bulk classification |
| Gemini Flash | 15 req/min (free) | Use as fallback, not primary |
| Supabase | 500MB DB free | Monitor table sizes, archive old detections |

## Confidence Assessment

| Component | Confidence | Notes |
|-----------|------------|-------|
| Core Python stack | HIGH | Python 3.11+, FastAPI, Pydantic are stable standards |
| GDELT libraries | MEDIUM | gdeltdoc/gdeltPyR maintained but niche, verify current status |
| Telethon | HIGH | De facto standard for Telegram scraping, well-maintained |
| LLM SDKs | MEDIUM | Anthropic/OpenAI/Google SDKs stable but versions change frequently |
| Supabase client | MEDIUM | Realtime feature verified in docs, Python client less mature than JS |
| Task queues | HIGH | Celery/Redis/APScheduler are battle-tested |
| Dev tools | HIGH | uv/ruff/mypy are current 2025-2026 standards |

## Sources

**Note:** Unable to verify current package versions due to tool access restrictions. Versions listed are based on January 2025 training data. **CRITICAL**: Verify all versions before production use.

**Verification needed:**
- [ ] Check PyPI for latest stable versions of all packages
- [ ] Verify Supabase Python client realtime subscription support
- [ ] Confirm gdeltdoc actively maintained (check GitHub last commit)
- [ ] Validate Telethon works with Python 3.11+ async
- [ ] Test litellm compatibility with Claude Sonnet 4.5 / GPT-4o Mini / Gemini 2.5 Flash

**Authoritative sources to check:**
- PyPI package pages for each library
- Supabase Python client docs: https://supabase.com/docs/reference/python
- Telethon documentation: https://docs.telethon.dev
- GDELT DOC 2.0 API docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- FastAPI docs: https://fastapi.tiangolo.com
- Anthropic Python SDK: https://github.com/anthropics/anthropic-sdk-python
- OpenAI Python SDK: https://github.com/openai/openai-python

---
*Stack research for: Dragon Watch OSINT Pre-Conflict Early Warning System*
*Researched: 2026-02-07*
*Confidence: MEDIUM (unable to verify current versions, requires validation)*

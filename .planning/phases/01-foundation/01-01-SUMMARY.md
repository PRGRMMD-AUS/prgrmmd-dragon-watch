---
phase: 01-foundation
plan: 01
subsystem: infrastructure
tags: [python, supabase, database, pydantic, async]
dependencies:
  requires: []
  provides: [project-scaffold, database-schema, data-models, db-client]
  affects: [01-02, 01-03, 02-01, 03-01]
tech-stack:
  added: [supabase-py>=2.27.3, pydantic>=2.0, fastapi, gdeltdoc>=1.12.0, Telethon>=1.42.0, websockets>=16.0]
  patterns: [async-singleton, pydantic-validation, realtime-enabled-schema]
file-tracking:
  created:
    - pyproject.toml
    - .env.example
    - .gitignore
    - src/__init__.py
    - src/models/__init__.py
    - src/models/schemas.py
    - src/database/__init__.py
    - src/database/client.py
    - src/fetchers/__init__.py
    - supabase/migrations/00001_create_foundation_tables.sql
  modified: []
decisions:
  - what: Use acreate_client() for async Supabase client
    why: Sync create_client() does not support realtime subscriptions
    impact: All database operations must use async/await pattern
    alternatives: Sync client (rejected - no realtime support)
  - what: Separate Create and Row models for each table
    why: Insert operations don't have id/timestamps, read operations do
    impact: Clear separation between data being written vs data from DB
    alternatives: Single model with Optional fields (rejected - less type safety)
  - what: REPLICA IDENTITY FULL deferred to user setup
    why: Requires SQL Editor access after migration
    impact: User must manually enable in Supabase dashboard
    alternatives: Include in migration (rejected - requires superuser privileges)
metrics:
  duration: 2 minutes
  completed: 2026-02-06
  commits: 2
  files-changed: 10
---

# Phase 1 Plan 01: Foundation Scaffold Summary

**One-liner:** Python project with 7-table Supabase schema, 14 Pydantic models, and async client using acreate_client() for realtime support.

## What Was Built

Created the complete foundation for Dragon Watch:

1. **Project Structure**
   - Python 3.11+ project with pyproject.toml
   - All core dependencies: supabase, fastapi, gdeltdoc, Telethon, websockets
   - Directory structure: src/models, src/database, src/fetchers
   - .env.example with all required API key placeholders
   - .gitignore covering Python, Telethon sessions, env files

2. **Database Schema**
   - SQL migration file with all 7 tables:
     - `articles`: GDELT news articles with tone scoring
     - `social_posts`: Telegram channel posts
     - `vessel_positions`: AIS maritime tracking data
     - `narrative_events`: LLM-detected coordination patterns
     - `movement_events`: Anomalous vessel movements
     - `alerts`: High-priority warnings with severity levels
     - `briefs`: Periodic intelligence summaries
   - Realtime publication enabled for all tables
   - Indexes for common query patterns (domain/published_at, channel/timestamp, mmsi/timestamp, severity/created_at)

3. **Data Models**
   - 14 Pydantic v2 models (7 Create + 7 Row variants)
   - All models match SQL schema with proper types
   - Row models use ConfigDict(from_attributes=True) for ORM compatibility
   - Literal types for severity enum in alerts

4. **Database Client**
   - Async Supabase client singleton using acreate_client()
   - Module-level singleton pattern with get_supabase() accessor
   - Error handling for missing environment variables
   - Clean shutdown with close_supabase()

## Key Technical Patterns

**Async-First Architecture**
- All database operations use async/await
- Client created with acreate_client() for realtime support
- Singleton pattern ensures single connection pool

**Type Safety**
- Pydantic validation on all data entering system
- Separate Create/Row models prevent id/timestamp confusion
- Literal types for enums (alert severity)

**Realtime-Enabled Schema**
- All tables added to supabase_realtime publication
- Frontend will receive live updates via subscriptions
- No polling required for data freshness

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

**Blockers:** None

**Concerns:**
- User must manually set REPLICA IDENTITY FULL on tables after running migration (requires SQL Editor access)
- Supabase credentials must be obtained before Phase 1 Plan 02 (GDELT fetcher)

**Dependencies Ready:**
- ✅ Project structure exists for fetcher modules
- ✅ Database schema defined for all data types
- ✅ Pydantic models ready for validation
- ✅ Async client ready for database operations

## Task Breakdown

| Task | Name                                      | Commit  | Status |
| ---- | ----------------------------------------- | ------- | ------ |
| 1    | Project scaffolding and Supabase schema   | 8e72cae | ✅      |
| 2    | Pydantic models and async Supabase client | 9d96598 | ✅      |

## Files Created

**Configuration:**
- `pyproject.toml` - Project metadata and dependencies
- `.env.example` - API key placeholders
- `.gitignore` - Python + Telethon + env exclusions

**Database:**
- `supabase/migrations/00001_create_foundation_tables.sql` - All 7 tables with realtime

**Models:**
- `src/models/schemas.py` - 14 Pydantic models (Create + Row variants)

**Client:**
- `src/database/client.py` - Async Supabase singleton

**Structure:**
- `src/__init__.py`, `src/models/__init__.py`, `src/database/__init__.py`, `src/fetchers/__init__.py`

## Verification Results

✅ pyproject.toml validates with tomllib
✅ All 7 tables present in SQL migration
✅ Realtime publication configured for all tables
✅ All directories exist (models, database, fetchers)
✅ All 14 Pydantic models import without errors
✅ Async client module imports successfully
✅ Dependencies install via pip3

## Links & References

**Key patterns established:**
- Async Supabase client: `src/database/client.py` → `acreate_client()`
- Pydantic validation: `src/models/schemas.py` → SQL column matching
- Realtime: SQL migration → ALTER PUBLICATION supabase_realtime

**Next plan dependencies:**
- Plan 01-02 (GDELT Fetcher) will import ArticleCreate from src.models.schemas
- Plan 01-02 will use get_supabase() from src.database.client
- Plan 01-03 (Telegram Fetcher) will import SocialPostCreate from src.models.schemas
- All future phases depend on this database schema

---

**Summary generated:** 2026-02-06
**Execution time:** 2 minutes
**Result:** ✅ Complete - all success criteria met

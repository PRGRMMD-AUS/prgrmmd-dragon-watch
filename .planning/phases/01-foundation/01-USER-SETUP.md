# Phase 1: User Setup Required

**Generated:** 2026-02-06
**Phase:** 01-foundation
**Status:** Incomplete

Complete these items for the integration to function.

## Service: Supabase

**Purpose:** Managed Postgres with realtime subscriptions

### Environment Variables

| Status | Variable | Source | Add to |
|--------|----------|--------|--------|
| [ ] | `SUPABASE_URL` | Supabase Dashboard -> Settings -> API -> Project URL | `.env` |
| [ ] | `SUPABASE_KEY` | Supabase Dashboard -> Settings -> API -> anon/public key | `.env` |

### Account Setup

- [ ] **Create a new Supabase project**
  - URL: https://supabase.com/dashboard -> New Project

### Dashboard Configuration

- [ ] **Enable realtime replication for all tables after migration**
  - Location: Supabase Dashboard -> Database -> Replication -> Enable for each table

- [ ] **Set REPLICA IDENTITY FULL on all tables**
  - Location: Run in SQL Editor:
    ```sql
    ALTER TABLE articles REPLICA IDENTITY FULL;
    ALTER TABLE social_posts REPLICA IDENTITY FULL;
    ALTER TABLE vessel_positions REPLICA IDENTITY FULL;
    ALTER TABLE narrative_events REPLICA IDENTITY FULL;
    ALTER TABLE movement_events REPLICA IDENTITY FULL;
    ALTER TABLE alerts REPLICA IDENTITY FULL;
    ALTER TABLE briefs REPLICA IDENTITY FULL;
    ```

## Verification

After completing setup:

1. Copy `.env.example` to `.env` and fill in your credentials
2. Run the migration SQL in Supabase SQL Editor: `supabase/migrations/00001_create_foundation_tables.sql`
3. Verify all 7 tables exist in Database -> Tables
4. Enable replication and set REPLICA IDENTITY FULL as described above
5. Test connection: `python3 -c "import asyncio; from src.database.client import get_supabase; asyncio.run(get_supabase())"`

---
**Once all items complete:** Mark status as "Complete" at top of file.

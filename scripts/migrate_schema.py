#!/usr/bin/env python3
"""Apply schema migration to extend alerts and briefs tables.

This migration adds columns that the correlation engine and brief generator
write to but were missing from the initial schema.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

MIGRATION_SQL = """
-- Migration: extend_alerts_and_briefs_for_frontend
-- Adds columns that the correlation engine and brief generator write to

-- Extend alerts table
ALTER TABLE public.alerts
  ADD COLUMN IF NOT EXISTS region TEXT DEFAULT 'Taiwan Strait',
  ADD COLUMN IF NOT EXISTS threat_level TEXT DEFAULT 'GREEN',
  ADD COLUMN IF NOT EXISTS threat_score DOUBLE PRECISION DEFAULT 0,
  ADD COLUMN IF NOT EXISTS confidence INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS sub_scores JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS correlation_metadata JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- Add constraint for threat_level
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'alerts_threat_level_check') THEN
    ALTER TABLE public.alerts DROP CONSTRAINT alerts_threat_level_check;
  END IF;
END $$;

ALTER TABLE public.alerts
  ADD CONSTRAINT alerts_threat_level_check CHECK (threat_level IN ('GREEN', 'AMBER', 'RED'));

-- Extend briefs table
ALTER TABLE public.briefs
  ADD COLUMN IF NOT EXISTS threat_level TEXT DEFAULT 'GREEN',
  ADD COLUMN IF NOT EXISTS confidence INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS evidence_chain TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS timeline TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS information_gaps TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS collection_priorities TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS narrative_event_ids JSONB DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS movement_event_ids JSONB DEFAULT '[]';

-- Add constraint for threat_level
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'briefs_threat_level_check') THEN
    ALTER TABLE public.briefs DROP CONSTRAINT briefs_threat_level_check;
  END IF;
END $$;

ALTER TABLE public.briefs
  ADD CONSTRAINT briefs_threat_level_check CHECK (threat_level IN ('GREEN', 'AMBER', 'RED'));
"""


def get_connection_string():
    """Build Postgres connection string from environment."""
    # Supabase format: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
    project_ref = "czyqiqgssvebgatxprey"
    db_password = os.getenv("SUPABASE_DB_PASSWORD", os.getenv("SUPABASE_PASSWORD", ""))

    if not db_password:
        # Try to get service role key for REST API
        print("WARNING: No SUPABASE_DB_PASSWORD found. Using alternative method...")
        return None

    return f"postgresql://postgres.{project_ref}:{db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"


def main():
    """Apply the migration."""
    conn_string = get_connection_string()

    if not conn_string:
        print("\n" + "="*70)
        print("MANUAL MIGRATION REQUIRED")
        print("="*70)
        print("\nThe Supabase database password is not set in .env file.")
        print("Please run the following SQL in the Supabase SQL Editor:")
        print("\nhttps://supabase.com/dashboard/project/czyqiqgssvebgatxprey/sql/new")
        print("\n" + "-"*70)
        print(MIGRATION_SQL)
        print("-"*70)
        print("\nAfter running the SQL, the migration will be complete.")
        print("="*70 + "\n")
        return 1

    try:
        print("Connecting to Supabase database...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        print("Applying migration: extend_alerts_and_briefs_for_frontend")
        cursor.execute(MIGRATION_SQL)
        conn.commit()

        print("✓ Migration applied successfully!")

        # Verify alerts columns
        print("\nVerifying alerts table columns...")
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'alerts' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        alerts_cols = [row[0] for row in cursor.fetchall()]
        print(f"✓ Alerts columns ({len(alerts_cols)}): {', '.join(alerts_cols)}")

        # Check for required columns
        required_alerts = ['region', 'threat_level', 'threat_score', 'confidence', 'sub_scores', 'correlation_metadata', 'updated_at']
        missing = [col for col in required_alerts if col not in alerts_cols]
        if missing:
            print(f"✗ WARNING: Missing alerts columns: {missing}")
        else:
            print(f"✓ All required alerts columns present")

        # Verify briefs columns
        print("\nVerifying briefs table columns...")
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'briefs' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        briefs_cols = [row[0] for row in cursor.fetchall()]
        print(f"✓ Briefs columns ({len(briefs_cols)}): {', '.join(briefs_cols)}")

        # Check for required columns
        required_briefs = ['threat_level', 'confidence', 'evidence_chain', 'timeline', 'information_gaps', 'collection_priorities', 'narrative_event_ids', 'movement_event_ids']
        missing = [col for col in required_briefs if col not in briefs_cols]
        if missing:
            print(f"✗ WARNING: Missing briefs columns: {missing}")
        else:
            print(f"✓ All required briefs columns present")

        cursor.close()
        conn.close()

        print("\n✓ Migration complete!\n")
        return 0

    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        print("Fallback: Please run the SQL manually in Supabase SQL Editor.")
        print("\n" + "-"*70)
        print(MIGRATION_SQL)
        print("-"*70 + "\n")
        return 1


if __name__ == "__main__":
    exit(main())

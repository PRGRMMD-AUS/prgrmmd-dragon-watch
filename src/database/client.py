"""Async Supabase client singleton.

CRITICAL: Uses acreate_client() for async support and realtime subscriptions.
DO NOT use create_client() - it's sync-only and doesn't support realtime.
"""

import os

from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client

# Load environment variables
load_dotenv()

# Module-level singleton
_client: AsyncClient | None = None


async def get_supabase() -> AsyncClient:
    """Get or create the async Supabase client singleton.

    Returns:
        AsyncClient: Configured Supabase client with realtime support

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing
    """
    global _client

    if _client is not None:
        return _client

    # Get credentials from environment
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            "Missing required environment variables: SUPABASE_URL and SUPABASE_KEY must be set. "
            "Copy .env.example to .env and fill in your credentials."
        )

    # Create async client with realtime support
    _client = await acreate_client(url, key)
    return _client


async def close_supabase() -> None:
    """Close the Supabase client and reset singleton.

    Call this during application shutdown for clean resource cleanup.
    """
    global _client
    _client = None

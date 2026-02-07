"""FastAPI application for Dragon Watch data ingestion.

Main API server that coordinates:
- GDELT article fetching
- Telegram channel scraping
- AIS vessel tracking (WebSocket stream)
- Demo data loading for testing
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI

from scripts.load_demo_data import load_demo_data
from src.database.client import close_supabase, get_supabase
from src.fetchers.ais import connect_ais_stream, stop_ais_stream
from src.fetchers.gdelt import fetch_and_store_articles
from src.fetchers.telegram import close_telegram, scrape_and_store_channels
from src.processors.correlate_events import correlate_events_batch


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown.

    Startup:
        - Initialize Supabase client singleton via get_supabase()

    Shutdown:
        - Close Supabase connection via close_supabase()
        - Close Telegram client via close_telegram()
        - Stop AIS stream if running
    """
    # Startup
    try:
        await get_supabase()
        print("Supabase client initialized")
    except Exception as e:
        print(f"Warning: Supabase initialization failed: {e}")

    yield

    # Shutdown
    print("Shutting down Dragon Watch...")
    await close_supabase()
    await close_telegram()
    await stop_ais_stream()
    print("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Dragon Watch",
    description="Pre-conflict early warning system",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Status message and Supabase connection verification
    """
    # Verify Supabase connection
    try:
        supabase = await get_supabase()
        # Simple query to verify connection
        await supabase.table("articles").select("id").limit(1).execute()
        supabase_status = "connected"
    except Exception as e:
        supabase_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "service": "dragon-watch",
        "supabase": supabase_status,
    }


@app.post("/fetch/gdelt")
async def fetch_gdelt(background_tasks: BackgroundTasks, lookback_hours: int = 24):
    """Fetch GDELT articles in background.

    Args:
        lookback_hours: How many hours back to search (default: 24)

    Returns:
        dict: Task status message
    """
    background_tasks.add_task(fetch_and_store_articles, lookback_hours=lookback_hours)
    return {
        "status": "started",
        "task": "gdelt_fetch",
        "lookback_hours": lookback_hours,
    }


@app.post("/fetch/telegram")
async def fetch_telegram(
    background_tasks: BackgroundTasks, limit_per_channel: int = 100
):
    """Fetch Telegram channel messages in background.

    Args:
        limit_per_channel: Maximum messages per channel (default: 100)

    Returns:
        dict: Task status message
    """
    background_tasks.add_task(
        scrape_and_store_channels, channels=None, limit_per_channel=limit_per_channel
    )
    return {
        "status": "started",
        "task": "telegram_fetch",
        "limit_per_channel": limit_per_channel,
    }


@app.post("/fetch/ais/start")
async def start_ais_stream():
    """Start AIS WebSocket stream as long-running task.

    Uses asyncio.create_task (not BackgroundTasks) because WebSocket is long-running.
    Stores task reference on app.state for later cancellation.

    Returns:
        dict: Task status message
    """
    # Check if already running
    if hasattr(app.state, "ais_task") and app.state.ais_task is not None:
        if not app.state.ais_task.done():
            return {
                "status": "already_running",
                "message": "AIS stream is already active",
            }

    # Start AIS stream as asyncio task
    app.state.ais_task = asyncio.create_task(connect_ais_stream())

    return {
        "status": "started",
        "task": "ais_stream",
        "message": "AIS WebSocket stream started",
    }


@app.post("/fetch/ais/stop")
async def stop_ais():
    """Stop AIS WebSocket stream.

    Cancels the running asyncio task and signals graceful shutdown.

    Returns:
        dict: Task status message
    """
    # Signal graceful shutdown
    await stop_ais_stream()

    # Cancel task if it exists
    if hasattr(app.state, "ais_task") and app.state.ais_task is not None:
        if not app.state.ais_task.done():
            app.state.ais_task.cancel()
            try:
                await app.state.ais_task
            except asyncio.CancelledError:
                pass

        app.state.ais_task = None

    return {
        "status": "stopped",
        "task": "ais_stream",
        "message": "AIS WebSocket stream stopped",
    }


@app.post("/demo/load")
async def load_demo():
    """Load demo dataset into Supabase.

    Loads 72-hour Taiwan Strait escalation scenario:
    - Articles: GREEN/AMBER/RED narrative progression
    - Posts: Civilian movement signals
    - Positions: Vessel pattern changes

    Returns:
        dict: Counts of loaded records
    """
    try:
        counts = await load_demo_data()
        return {
            "status": "success",
            "message": "Demo data loaded",
            "counts": counts,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load demo data: {str(e)}",
        }


@app.post("/fetch/all")
async def fetch_all(background_tasks: BackgroundTasks):
    """Trigger all data fetchers (GDELT + Telegram) in background.

    Does NOT start AIS stream (requires explicit start/stop control).

    Returns:
        dict: Task status message
    """
    # Add both tasks to background queue
    background_tasks.add_task(fetch_and_store_articles, lookback_hours=24)
    background_tasks.add_task(
        scrape_and_store_channels, channels=None, limit_per_channel=100
    )

    return {
        "status": "started",
        "tasks": ["gdelt_fetch", "telegram_fetch"],
        "message": "GDELT and Telegram fetchers started",
    }


@app.post("/api/correlate")
async def correlate_events():
    """Run correlation engine to match narrative and movement events.

    Analyzes time-window matching, geographic proximity, and calculates
    composite threat scores. Upserts alert with monotonic escalation enforcement.

    Returns:
        dict: Correlation result with status, correlations_found, highest_score,
              threat_level, and confidence
    """
    result = await correlate_events_batch()
    return result


@app.get("/api/alerts/current")
async def get_current_alert():
    """Get the current active Taiwan Strait alert.

    Returns the most recent unresolved alert with threat level, scores,
    and correlation metadata.

    Returns:
        dict: Alert data or 404 if no active alert exists
    """
    try:
        client = await get_supabase()

        # Query for active Taiwan Strait alert
        response = (
            await client.table("alerts")
            .select("*")
            .eq("region", "Taiwan Strait")
            .is_("resolved_at", "null")
            .execute()
        )

        if not response.data:
            return {"status": "no_active_alert", "message": "No active Taiwan Strait alert found"}

        return response.data[0]

    except Exception as e:
        return {"status": "error", "error": str(e)}

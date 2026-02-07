"""FastAPI application for Dragon Watch data ingestion.

Main API server that coordinates:
- GDELT article fetching
- Telegram channel scraping
- AIS vessel tracking (WebSocket stream)
- Demo data loading for testing
- Demo playback control (start/pause/reset/speed)
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scripts.load_demo_data import load_demo_data
from src.database.client import close_supabase, get_supabase
from src.demo.engine import demo_engine

# Note: fetchers module temporarily removed from repository
# from src.fetchers.ais import connect_ais_stream, stop_ais_stream
# from src.fetchers.gdelt import fetch_and_store_articles
# from src.fetchers.telegram import close_telegram, scrape_and_store_channels

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
    # Note: fetchers temporarily removed
    # await close_telegram()
    # await stop_ais_stream()
    print("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Dragon Watch",
    description="Pre-conflict early warning system",
    lifespan=lifespan,
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Note: Fetcher endpoints temporarily disabled (fetchers module removed)
# @app.post("/fetch/gdelt")
# async def fetch_gdelt(background_tasks: BackgroundTasks, lookback_hours: int = 24):
#     """Fetch GDELT articles in background."""
#     background_tasks.add_task(fetch_and_store_articles, lookback_hours=lookback_hours)
#     return {"status": "started", "task": "gdelt_fetch", "lookback_hours": lookback_hours}
#
# @app.post("/fetch/telegram")
# async def fetch_telegram(background_tasks: BackgroundTasks, limit_per_channel: int = 100):
#     """Fetch Telegram channel messages in background."""
#     background_tasks.add_task(scrape_and_store_channels, channels=None, limit_per_channel=limit_per_channel)
#     return {"status": "started", "task": "telegram_fetch", "limit_per_channel": limit_per_channel}
#
# @app.post("/fetch/ais/start")
# async def start_ais_stream():
#     """Start AIS WebSocket stream as long-running task."""
#     if hasattr(app.state, "ais_task") and app.state.ais_task is not None:
#         if not app.state.ais_task.done():
#             return {"status": "already_running", "message": "AIS stream is already active"}
#     app.state.ais_task = asyncio.create_task(connect_ais_stream())
#     return {"status": "started", "task": "ais_stream", "message": "AIS WebSocket stream started"}
#
# @app.post("/fetch/ais/stop")
# async def stop_ais():
#     """Stop AIS WebSocket stream."""
#     await stop_ais_stream()
#     if hasattr(app.state, "ais_task") and app.state.ais_task is not None:
#         if not app.state.ais_task.done():
#             app.state.ais_task.cancel()
#             try:
#                 await app.state.ais_task
#             except asyncio.CancelledError:
#                 pass
#         app.state.ais_task = None
#     return {"status": "stopped", "task": "ais_stream", "message": "AIS WebSocket stream stopped"}


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


# Note: Fetcher endpoints temporarily disabled (fetchers module removed)
# @app.post("/fetch/all")
# async def fetch_all(background_tasks: BackgroundTasks):
#     """Trigger all data fetchers (GDELT + Telegram) in background."""
#     background_tasks.add_task(fetch_and_store_articles, lookback_hours=24)
#     background_tasks.add_task(scrape_and_store_channels, channels=None, limit_per_channel=100)
#     return {"status": "started", "tasks": ["gdelt_fetch", "telegram_fetch"], "message": "GDELT and Telegram fetchers started"}


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


# Demo Control Router
demo_router = APIRouter(prefix="/api/demo", tags=["demo"])


@demo_router.post("/start")
async def demo_start(clear_first: bool = True):
    """Start demo playback.

    Args:
        clear_first: If True, clear all tables before starting (default: True)

    Returns:
        dict: Current demo status
    """
    await demo_engine.start(clear_first=clear_first)
    return demo_engine.get_status()


@demo_router.post("/pause")
async def demo_pause():
    """Pause demo playback at current position.

    Returns:
        dict: Current demo status
    """
    await demo_engine.pause()
    return demo_engine.get_status()


@demo_router.post("/reset")
async def demo_reset():
    """Reset demo playback to beginning and clear tables.

    Returns:
        dict: Current demo status
    """
    await demo_engine.reset()
    return demo_engine.get_status()


@demo_router.post("/speed")
async def demo_speed(preset: str = None, multiplier: float = None):
    """Change demo playback speed.

    Args:
        preset: Speed preset name ("slow" | "normal" | "fast")
        multiplier: Custom speed multiplier (e.g. 1.0, 2.0, 5.0, 10.0, 25.0)

    Returns:
        dict: Current demo status
    """
    if multiplier is not None:
        demo_engine.set_speed(multiplier)
    else:
        speed_map = {"slow": 0.5, "normal": 1.0, "fast": 2.5}
        speed = speed_map.get(preset, 1.0)
        demo_engine.set_speed(speed)
    return demo_engine.get_status()


@demo_router.get("/status")
async def demo_status():
    """Get current demo playback status.

    Returns:
        dict: Status with state, speed, progress, simulated_time, etc.
    """
    return demo_engine.get_status()


# Include demo router
app.include_router(demo_router)

"""AIS WebSocket vessel tracker for Taiwan Strait.

Streams real-time vessel positions from AISstream.io WebSocket API.
Focuses on Taiwan Strait region (23-26N, 118-122E).
Batch inserts positions to Supabase for efficient database writes.
"""

import asyncio
import json
import os
from collections.abc import Callable
from datetime import datetime

import websockets
from dotenv import load_dotenv

from src.database.client import get_supabase
from src.models.schemas import VesselPositionCreate

# Load environment variables
load_dotenv()

# AIS WebSocket connection
AIS_WS_URL = "wss://stream.aisstream.io/v0/stream"

# Taiwan Strait bounding box (approximately 23-26N, 118-122E)
# This narrow region focuses on the critical transit zone
TAIWAN_STRAIT_BBOX = [[23.0, 118.0], [26.0, 122.0]]

# Control flag for graceful shutdown
_running = True


async def flush_positions(positions: list[dict]) -> int:
    """Bulk insert vessel positions to Supabase.

    Args:
        positions: List of position dictionaries ready for insertion

    Returns:
        Number of positions successfully inserted

    Raises:
        Exception: On database errors (logged but not raised)
    """
    if not positions:
        return 0

    try:
        supabase = await get_supabase()
        response = await supabase.table("vessel_positions").insert(positions).execute()
        return len(response.data) if response.data else 0
    except Exception as e:
        print(f"Error flushing positions to database: {e}")
        return 0


async def connect_ais_stream(
    on_position: Callable | None = None, batch_size: int = 50
) -> None:
    """Connect to AIS WebSocket stream and process vessel positions.

    Subscribes to Taiwan Strait region with PositionReport messages only.
    Automatically reconnects on connection failures.
    Batch inserts positions to Supabase for efficiency.

    Args:
        on_position: Optional callback called with each validated position dict
        batch_size: Number of positions to batch before flushing to database

    Raises:
        ValueError: If AISSTREAM_API_KEY environment variable is missing

    Note:
        CRITICAL: Must subscribe within 3 seconds of connection or server disconnects.
        Reconnection is automatic via websockets.connect() retry logic.
    """
    global _running

    # Validate API key exists
    api_key = os.getenv("AISSTREAM_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing AISSTREAM_API_KEY environment variable. "
            "Get your API key from https://aisstream.io/dashboard"
        )

    # Build subscription message (must be sent within 3 seconds)
    subscription = {
        "APIKey": api_key,
        "BoundingBoxes": [TAIWAN_STRAIT_BBOX],
        "FilterMessageTypes": ["PositionReport"],
    }

    position_batch = []

    # Auto-reconnecting WebSocket loop
    async for websocket in websockets.connect(AIS_WS_URL):
        try:
            # CRITICAL: Send subscription immediately (server requires < 3 seconds)
            await websocket.send(json.dumps(subscription))
            print(f"Subscribed to Taiwan Strait AIS stream ({TAIWAN_STRAIT_BBOX})")

            # Process incoming messages
            async for message_raw in websocket:
                if not _running:
                    print("Shutdown requested, closing AIS stream...")
                    await websocket.close()
                    break

                try:
                    # Parse JSON message
                    message = json.loads(message_raw)

                    # Extract position data from PositionReport
                    position_report = message.get("Message", {}).get("PositionReport")
                    metadata = message.get("MetaData", {})

                    if not position_report or not metadata:
                        continue  # Skip malformed messages

                    # Build validated position dict
                    position_data = {
                        "mmsi": metadata.get("MMSI"),
                        "ship_name": metadata.get("ShipName"),
                        "latitude": position_report.get("Latitude"),
                        "longitude": position_report.get("Longitude"),
                        "speed": position_report.get("Sog"),  # Speed over ground
                        "course": position_report.get("Cog"),  # Course over ground
                        "timestamp": datetime.fromisoformat(
                            metadata.get("time_utc").replace("Z", "+00:00")
                        ),
                    }

                    # Validate through Pydantic model
                    validated = VesselPositionCreate(**position_data)

                    # Call optional callback
                    if on_position:
                        on_position(validated.model_dump())

                    # Add to batch
                    position_batch.append(validated.model_dump())

                    # Flush batch when size reached
                    if len(position_batch) >= batch_size:
                        count = await flush_positions(position_batch)
                        print(f"Flushed {count} positions to database")
                        position_batch.clear()

                except json.JSONDecodeError:
                    # Skip invalid JSON
                    continue
                except KeyError as e:
                    # Skip messages missing expected fields
                    print(f"Missing field in AIS message: {e}")
                    continue
                except ValueError as e:
                    # Skip messages that fail Pydantic validation
                    print(f"Validation error: {e}")
                    continue

        except websockets.ConnectionClosed:
            # Connection lost - auto-reconnect after brief delay
            print("AIS connection closed, reconnecting in 5 seconds...")
            await asyncio.sleep(5)
            continue

    # Flush any remaining positions before exit
    if position_batch:
        count = await flush_positions(position_batch)
        print(f"Flushed final {count} positions to database")


async def stop_ais_stream() -> None:
    """Signal graceful shutdown of AIS stream.

    Sets the global _running flag to False, causing the stream loop to exit.
    """
    global _running
    _running = False

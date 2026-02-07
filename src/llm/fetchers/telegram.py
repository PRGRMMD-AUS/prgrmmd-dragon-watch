"""Telegram OSINT channel scraper.

Scrapes messages from public military/OSINT Telegram channels and stores in Supabase.
Handles rate limiting and channel access errors gracefully.
"""

import logging
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import ChannelInvalidError, ChannelPrivateError, FloodWaitError
from telethon.tl.types import Message

from src.database.client import get_supabase
from src.models.schemas import SocialPostCreate

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OSINT/military channels to scrape
# NOTE: Validate channel accessibility during setup
OSINT_CHANNELS = [
    "@osinttechnical",
    "@IntelDoge",
    "@militarymap",
    "@Lobaev_Z",
    "@ukraine_map",
]

# Module-level TelegramClient (lazy initialization)
# Telethon auto-handles FloodWaitError < 60s, only manually handle > 60s
_client: TelegramClient | None = None


def _get_client() -> TelegramClient:
    """Get or create the Telegram client singleton.

    Returns:
        TelegramClient: Configured Telegram client

    Raises:
        ValueError: If TELEGRAM_API_ID or TELEGRAM_API_HASH are missing/invalid
    """
    global _client

    if _client is not None:
        return _client

    # Get credentials from environment
    api_id_str = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id_str or not api_hash:
        raise ValueError(
            "Missing required environment variables: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set. "
            "Get credentials from https://my.telegram.org/apps"
        )

    try:
        api_id = int(api_id_str)
    except ValueError:
        raise ValueError(f"TELEGRAM_API_ID must be an integer, got: {api_id_str}")

    # Create client with flood wait handling
    _client = TelegramClient(
        "dragon-watch",
        api_id,
        api_hash,
        flood_sleep_threshold=60,  # Auto-sleep for waits < 60s
    )

    return _client


async def scrape_channel(channel: str, limit: int = 100) -> list[dict]:
    """Scrape messages from a single Telegram channel.

    Args:
        channel: Channel username (e.g., "@osinttechnical")
        limit: Maximum number of messages to fetch (default: 100)

    Returns:
        List of message dicts validated through SocialPostCreate model
    """
    client = _get_client()
    messages = []

    try:
        logger.info(f"Scraping channel: {channel} (limit={limit})")

        async for message in client.iter_messages(channel, limit=limit):
            # Skip messages without text
            if not message.text:
                continue

            try:
                # Create SocialPostCreate model
                post_data = {
                    "telegram_id": message.id,
                    "channel": channel,
                    "text": message.text,
                    "timestamp": message.date,
                    "views": message.views,
                    "raw_data": {
                        "message_id": message.id,
                        "date": message.date.isoformat(),
                        "views": message.views,
                        "forwards": message.forwards,
                        "replies": message.replies.replies if message.replies else 0,
                    },
                }

                # Validate through Pydantic model
                post = SocialPostCreate(**post_data)
                messages.append(post.model_dump())

            except Exception as e:
                logger.warning(f"Failed to process message {message.id}: {e}")
                continue

        logger.info(f"Scraped {len(messages)} messages from {channel}")
        return messages

    except ChannelPrivateError:
        logger.error(f"Channel {channel} is private or requires authentication")
        return []
    except ChannelInvalidError:
        logger.error(f"Channel {channel} is invalid or does not exist")
        return []
    except FloodWaitError as e:
        # Only manually handle waits > 60s (under threshold handled automatically)
        logger.error(
            f"FloodWaitError for {channel}: must wait {e.seconds} seconds (exceeds threshold)"
        )
        return []
    except Exception as e:
        logger.error(f"Error scraping channel {channel}: {e}")
        return []


async def scrape_and_store_channels(
    channels: list[str] | None = None, limit_per_channel: int = 100
) -> int:
    """Scrape multiple Telegram channels and store in Supabase.

    Args:
        channels: List of channel usernames (default: OSINT_CHANNELS)
        limit_per_channel: Maximum messages per channel (default: 100)

    Returns:
        Total number of messages inserted/updated
    """
    if channels is None:
        channels = OSINT_CHANNELS

    client = _get_client()

    # Ensure client is started
    if not client.is_connected():
        await client.start()

    total_count = 0

    for channel in channels:
        # Scrape channel
        messages = await scrape_channel(channel, limit=limit_per_channel)

        if not messages:
            logger.info(f"No messages to store from {channel}")
            continue

        try:
            # Get Supabase client
            supabase = await get_supabase()

            # Insert messages to Supabase
            response = await supabase.table("social_posts").insert(messages).execute()

            count = len(response.data) if response.data else 0
            total_count += count
            logger.info(f"Stored {count} messages from {channel}")

        except Exception as e:
            logger.error(f"Supabase insert error for {channel}: {e}")
            continue

    logger.info(f"Total messages stored: {total_count}")
    return total_count


async def close_telegram() -> None:
    """Disconnect Telegram client.

    Call this during application shutdown for clean resource cleanup.
    """
    global _client

    if _client is not None and _client.is_connected():
        await _client.disconnect()
        logger.info("Telegram client disconnected")
        _client = None

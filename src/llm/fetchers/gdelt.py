"""GDELT article fetcher for Chinese state media.

Queries GDELT for articles from Chinese state media domains and stores in Supabase.
Uses domain_exact parameter for precise domain matching (NOT domain - partial matching causes false positives).
"""

import asyncio
import logging
from datetime import datetime, timedelta

import gdeltdoc
from gdeltdoc import Filters

from src.database.client import get_supabase
from src.models.schemas import ArticleCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chinese state media domains to query
# NOTE: These domains need validation against GDELT during setup
# See research open question #1: Verify Xinhua, Global Times, CCTV, People's Daily are indexed
STATE_MEDIA_DOMAINS = [
    "xinhuanet.com",
    "globaltimes.cn",
    "cctv.com",
    "people.com.cn",
]


async def fetch_gdelt_articles(
    lookback_hours: int = 24, max_records: int = 250
) -> list[dict]:
    """Fetch articles from GDELT for Chinese state media domains.

    Args:
        lookback_hours: How many hours back to search (default: 24)
        max_records: Maximum number of records to fetch (default: 250)

    Returns:
        List of article dicts validated through ArticleCreate model
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=lookback_hours)

    # Format dates as YYYY-MM-DD
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    logger.info(
        f"Fetching GDELT articles: domains={STATE_MEDIA_DOMAINS}, "
        f"date_range={start_str} to {end_str}, max_records={max_records}"
    )

    try:
        # Create GDELT filters with domain_exact for precise matching
        filters = Filters(
            domain_exact=STATE_MEDIA_DOMAINS,
            start_date=start_str,
            end_date=end_str,
            num_records=max_records,
        )

        # gdeltdoc is synchronous, so wrap in asyncio.to_thread()
        gd = gdeltdoc.GdeltDoc()
        df = await asyncio.to_thread(gd.article_search, filters)

        # Handle empty DataFrame
        if df is None or df.empty:
            logger.info("No articles found for specified criteria")
            return []

        # Convert DataFrame rows to ArticleCreate models
        articles = []
        for _, row in df.iterrows():
            try:
                # Map GDELT columns to ArticleCreate fields
                article_data = {
                    "url": row.get("url"),
                    "title": row.get("title"),
                    "domain": row.get("domain"),
                    "published_at": datetime.strptime(
                        str(row.get("seendate")), "%Y%m%d%H%M%S"
                    ),
                    "language": row.get("language"),
                    "source_country": row.get("sourcecountry"),
                    # TODO: gdeltdoc does NOT return tone directly - need to fetch separately or use GKG
                    "tone_score": None,
                    "raw_data": row.to_dict(),
                }

                # Validate through Pydantic model
                article = ArticleCreate(**article_data)
                articles.append(article.model_dump())

            except Exception as e:
                logger.warning(f"Failed to process article: {e}")
                continue

        logger.info(f"Successfully fetched {len(articles)} articles")
        return articles

    except Exception as e:
        logger.error(f"GDELT API error: {e}")
        return []


async def fetch_and_store_articles(lookback_hours: int = 24) -> int:
    """Fetch GDELT articles and store in Supabase.

    Args:
        lookback_hours: How many hours back to search (default: 24)

    Returns:
        Number of articles inserted/updated
    """
    # Fetch articles from GDELT
    articles = await fetch_gdelt_articles(lookback_hours=lookback_hours)

    if not articles:
        logger.info("No articles to store")
        return 0

    try:
        # Get Supabase client
        supabase = await get_supabase()

        # Batch insert with upsert on URL conflict
        response = (
            await supabase.table("articles")
            .upsert(articles, on_conflict="url")
            .execute()
        )

        count = len(response.data) if response.data else 0
        logger.info(f"Stored {count} articles in Supabase")
        return count

    except Exception as e:
        logger.error(f"Supabase insert error: {e}")
        return 0

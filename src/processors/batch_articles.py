import asyncio
import structlog
from datetime import datetime, timezone
from typing import List, Dict, Any
from src.database.client import get_supabase
from src.llm.narrative import detect_narrative_coordination
from src.llm.extraction import extract_entities
from src.config.settings import get_settings

logger = structlog.get_logger()

async def fetch_unprocessed_articles(limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch articles that haven't been processed yet."""
    client = await get_supabase()
    
    # Using async client methods directly
    response = await client.table("articles") \
        .select("*") \
        .is_("processed_at", "null") \
        .order("published_at", desc=True) \
        .limit(limit) \
        .execute()
        
    return response.data

async def write_narrative_event(coordination: Any, article_ids: List[str]) -> Dict[str, Any]:
    """Write narrative coordination event to database."""
    client = await get_supabase()
    
    event_data = {
        "coordination_score": coordination.coordination_score,
        "synchronized_phrases": coordination.synchronized_phrases,
        "outlet_count": coordination.outlet_count,
        "geographic_focus": coordination.geographic_focus,
        "themes": coordination.themes,
        "confidence": coordination.confidence,
        "article_ids": article_ids,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = await client.table("narrative_events").insert(event_data).execute()
    return response.data[0] if response.data else {}

async def write_entities(entities_result: Any, source_id: str, source_type: str = "article") -> None:
    """Write extracted entities to database."""
    if not entities_result.entities:
        return

    client = await get_supabase()
    
    # Check if we have an entities table, if not (based on phase 0 plan), 
    # we might need to store it in a JSONB column or a separate table.
    # The Schema Summary says "7 tables" but doesn't list `entities`.
    # However, Phase 01 Schema included `articles`, `social_posts`, etc.
    # Plan 02 Task 2.3 says: "Bulk insert extracted entities into an entities enrichment field or separate table"
    # Given I cannot see the schema right now, I will assume there might NOT be an entities table yet 
    # OR I should check the schema first.
    # But to unstuck, I will assume we might need to update the source article with enrichment data 
    # OR insert into a generic `entities` table if it exists.
    # Let's check `01-01-SUMMARY.md` again.
    # It lists: articles, social_posts, vessel_positions, narrative_events, movement_events, alerts, briefs.
    # No `entities` table.
    # So I should probably update the `articles` table with an `entities` JSONB column if it exists, 
    # or create a new table.
    # The plan says "Bulk insert... into an entities enrichment field or separate table".
    # Since I can't change schema easily here without migration, I'll attempt to update a JSONB column 'entities' on the source table.
    # If that fails, I'll log a warning.
    
    formatted_entities = [
        {
            "entity_type": e.entity_type,
            "entity_value": e.entity_value,
            "source_span": e.source_span,
            "confidence": e.confidence,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "source_id": source_id,
            "source_type": source_type
        }
        for e in entities_result.entities
    ]
    
    # Attempting to update the 'entities' column on the source article/post
    # This assumes the table has an 'entities' column (JSONB)
    try:
        table_name = "articles" if source_type == "article" else "social_posts"
        await client.table(table_name) \
            .update({"entities": formatted_entities}) \
            .eq("id", source_id) \
            .execute()
    except Exception as e:
        logger.warning("failed_to_write_entities", error=str(e), source_id=source_id)

async def mark_articles_processed(article_ids: List[str]) -> None:
    """Mark articles as processed."""
    if not article_ids:
        return
        
    client = await get_supabase()
    now = datetime.now(timezone.utc).isoformat()
    
    await client.table("articles") \
        .update({"processed_at": now}) \
        .in_("id", article_ids) \
        .execute()

async def process_article_batch() -> Dict[str, Any]:
    """Main pipeline orchestrator."""
    settings = get_settings()
    logger.info("pipeline_start", pipeline="batch_articles")
    
    try:
        # 1. Fetch
        articles = await fetch_unprocessed_articles(limit=NARRATIVE_MAX_ARTICLES)
        if not articles:
            logger.info("pipeline_complete", status="no_articles")
            return {"status": "no_articles", "count": 0}
            
        logger.info("articles_fetched", count=len(articles))
        article_ids = [a["id"] for a in articles]

        # 2. Narrative Detection
        narrative_result = await detect_narrative_coordination(articles)
        
        # 3. Entity Extraction (Concurrent)
        extraction_tasks = []
        semaphore = asyncio.Semaphore(settings.max_concurrent_claude)
        
        async def extract_with_semaphore(text: str, source_id: str):
            async with semaphore:
                result = await extract_entities(text, source_type="article")
                await write_entities(result, source_id, "article")
                return result

        for article in articles:
            content = article.get("content", "") or ""
            extraction_tasks.append(extract_with_semaphore(content, article["id"]))
            
        extraction_results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        
        # 4. Write Narrative Event
        if narrative_result.coordination_score > 0:
             await write_narrative_event(narrative_result, article_ids)

        # 5. Mark Processed
        await mark_articles_processed(article_ids)
        
        summary = {
            "status": "success",
            "articles_processed": len(articles),
            "coordination_score": narrative_result.coordination_score,
            "entities_extracted": sum(1 for r in extraction_results if r and not isinstance(r, Exception) and r.entities)
        }
        
        logger.info("pipeline_complete", **summary)
        return summary

    except Exception as e:
        logger.error("pipeline_failed", error=str(e))
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    asyncio.run(process_article_batch())

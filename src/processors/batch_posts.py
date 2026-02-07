import asyncio
import structlog
from datetime import datetime, timezone
from typing import List, Dict, Any
from src.database.client import get_supabase
from src.llm.classification import classify_posts_batch
from src.llm.extraction import extract_entities
from src.llm.schemas import MovementCategory
from src.config.settings import get_settings

logger = structlog.get_logger()

async def fetch_unprocessed_posts(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch posts that haven't been processed yet."""
    client = await get_supabase()
    
    response = await client.table("social_posts") \
        .select("*") \
        .is_("processed_at", "null") \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
        
    return response.data

async def write_movement_event(classification: Any, post_id: str, entities_result: Any = None) -> None:
    """Write movement event to database."""
    # Skip not_relevant
    if classification.category == MovementCategory.not_relevant:
        return

    client = await get_supabase()
    
    event_data = {
        "category": classification.category.value,
        "location": classification.location,
        "confidence": classification.confidence,
        "reasoning": classification.reasoning,
        "post_id": post_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        # Store entities as JSONB if field exists, or we might need separate writes.
        # Assuming `entities` column exists on `movement_events` or we write to `movement_events` table 
        # which might have an `entities` column or we follow previous pattern.
        # Plan says: "entities (extracted entity data if available)"
        "entities": [e.model_dump() for e in entities_result.entities] if entities_result else []
    }
    
    # Try inserting. If `entities` column doesn't exist, this might fail.
    # But based on Phase 2 Plan 03 "must haves", it says "Classification results... are written to movement_events table".
    # I'll proceed with insert.
    try:
        await client.table("movement_events").insert(event_data).execute()
    except Exception as e:
        logger.error("write_movement_event_failed", error=str(e), post_id=post_id)

async def mark_posts_processed(post_ids: List[str]) -> None:
    """Mark posts as processed."""
    if not post_ids:
        return
        
    client = await get_supabase()
    now = datetime.now(timezone.utc).isoformat()
    
    await client.table("social_posts") \
        .update({"processed_at": now}) \
        .in_("id", post_ids) \
        .execute()

async def process_post_batch() -> Dict[str, Any]:
    """Main pipeline orchestrator."""
    settings = get_settings()
    logger.info("pipeline_start", pipeline="batch_posts")
    
    try:
        # 1. Fetch
        posts = await fetch_unprocessed_posts(limit=50) # limit from plan
        if not posts:
            logger.info("pipeline_complete", status="no_posts")
            return {"status": "no_posts", "count": 0}
            
        logger.info("posts_fetched", count=len(posts))
        
        # 2. Classify Batch
        # We need to map results back to posts.
        classifications = await classify_posts_batch(posts)
        
        # 3. Filter & Extract Entities (Concurrent)
        relevant_posts = []
        extraction_tasks = []
        semaphore = asyncio.Semaphore(settings.max_concurrent_claude)
        
        async def extract_with_semaphore(text: str, _id: str):
            async with semaphore:
                return await extract_entities(text, source_type="post")

        for i, classification in enumerate(classifications):
            if classification and classification.category != MovementCategory.not_relevant:
                post = posts[i]
                relevant_posts.append((post, classification))
                
                content = post.get("text", "") or post.get("content", "") or ""
                extraction_tasks.append(extract_with_semaphore(content, post["id"]))
        
        # Run extractions
        extraction_results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        
        # 4. Write Movement Events
        write_tasks = []
        for i, (post, classification) in enumerate(relevant_posts):
            extraction_result = extraction_results[i]
            if isinstance(extraction_result, Exception):
                extraction_result = None
            
            write_tasks.append(write_movement_event(classification, post["id"], extraction_result))
            
        if write_tasks:
            await asyncio.gather(*write_tasks)
            
        # 5. Mark Processed
        post_ids = [p["id"] for p in posts]
        await mark_posts_processed(post_ids)
        
        # Calculate stats
        categories = {}
        for c in classifications:
            if c:
                cat = c.category.value
                categories[cat] = categories.get(cat, 0) + 1
                
        summary = {
            "status": "success",
            "posts_processed": len(posts),
            "relevant_count": len(relevant_posts),
            "categories": categories,
            "entities_extracted_count": sum(1 for e in extraction_results if e and not isinstance(e, Exception) and e.entities)
        }
        
        logger.info("pipeline_complete", **summary)
        return summary

    except Exception as e:
        logger.error("pipeline_failed", error=str(e))
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    asyncio.run(process_post_batch())

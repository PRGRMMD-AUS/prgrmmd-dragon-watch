import asyncio
import structlog
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from src.database.client import get_supabase
from src.llm.briefs import generate_intelligence_brief
from src.llm.schemas import IntelligenceBrief
from src.config.settings import get_settings

logger = structlog.get_logger()

async def fetch_recent_narrative_events(hours: int = 72) -> List[Dict[str, Any]]:
    """Fetch narrative events within the last N hours."""
    client = await get_supabase()
    time_threshold = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    response = await client.table("narrative_events") \
        .select("*") \
        .gte("created_at", time_threshold) \
        .order("created_at", desc=True) \
        .execute()
        
    return response.data

async def fetch_recent_movement_events(hours: int = 72) -> List[Dict[str, Any]]:
    """Fetch movement events within the last N hours."""
    client = await get_supabase()
    time_threshold = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    response = await client.table("movement_events") \
        .select("*") \
        .gte("created_at", time_threshold) \
        .order("created_at", desc=True) \
        .execute()
        
    return response.data

async def write_brief(
    brief: IntelligenceBrief, 
    narrative_event_ids: List[str], 
    movement_event_ids: List[str]
) -> Dict[str, Any]:
    """Write generated brief to database."""
    client = await get_supabase()
    
    brief_data = {
        "threat_level": brief.threat_level.value,
        "confidence": brief.confidence,
        "summary": brief.summary,
        "evidence_chain": brief.evidence_chain,
        "timeline": brief.timeline,
        "information_gaps": brief.information_gaps,
        "collection_priorities": brief.collection_priorities,
        "narrative_event_ids": narrative_event_ids,
        "movement_event_ids": movement_event_ids,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = await client.table("briefs").insert(brief_data).execute()
    return response.data[0] if response.data else {}

async def generate_brief(time_window_hours: int = 72) -> Dict[str, Any]:
    """Main pipeline orchestrator."""
    logger.info("pipeline_start", pipeline="brief_generator", window_hours=time_window_hours)
    
    try:
        # 1. Fetch Streams concurrently
        narrative_task = fetch_recent_narrative_events(hours=time_window_hours)
        movement_task = fetch_recent_movement_events(hours=time_window_hours)
        
        narrative_events, movement_events = await asyncio.gather(narrative_task, movement_task)
        
        logger.info("events_fetched", narrative_count=len(narrative_events), movement_count=len(movement_events))
        
        # 2. Check overlap logic
        # If both empty, maybe skip?
        if not narrative_events and not movement_events:
            logger.info("pipeline_complete", status="no_events")
            return {"status": "no_events"}
            
        # 3. Generate Brief
        brief = await generate_intelligence_brief(
            narrative_events, 
            movement_events, 
            time_window_hours
        )
        
        # 4. Write Brief
        narrative_ids = [e["id"] for e in narrative_events if "id" in e]
        movement_ids = [e["id"] for e in movement_events if "id" in e]
        
        saved_brief = await write_brief(brief, narrative_ids, movement_ids)
        
        summary = {
            "status": "success",
            "brief_id": saved_brief.get("id"),
            "threat_level": brief.threat_level.value,
            "confidence": brief.confidence,
            "narrative_events_count": len(narrative_events),
            "movement_events_count": len(movement_events)
        }
        
        logger.info("pipeline_complete", **summary)
        return summary

    except Exception as e:
        logger.error("pipeline_failed", error=str(e))
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    asyncio.run(generate_brief())

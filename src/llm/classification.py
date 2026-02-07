import structlog
import time
import asyncio
from typing import List
from src.llm.clients import get_openai_client
from src.llm.schemas import PostClassification
from src.llm.utils import create_retry_decorator, log_llm_call, truncate_text, estimate_cost, create_semaphore
from src.config.settings import get_settings

logger = structlog.get_logger()
retry_decorator = create_retry_decorator()

@retry_decorator
async def classify_civilian_post(post_text: str) -> PostClassification:
    """Classify a single civilian post for military relevance."""
    settings = get_settings()
    
    # Truncate
    # Rough char approx (4 chars / token)
    max_chars = settings.max_post_tokens * 4
    truncated_text = truncate_text(post_text, max_chars)

    prompt = f"""
<instructions>
Classify this social media post for military-relevant movement indicators.

Categories:
- convoy: Road convoy, military vehicles in formation, troop transport
- naval: Ship/submarine activity, port movements, naval exercises
- flight: Military aircraft, unusual flight patterns, airspace restrictions
- restricted_zone: Access restrictions, roadblocks, evacuations, security cordons
- not_relevant: Civilian activity, no military indicators

Extract:
- Category (exactly one from above)
- Location mentioned (city, region, or coordinates if present; null if absent)
- Confidence 0-100 (how certain is this classification)
- Brief reasoning (1-2 sentences why this category)

Indicators to look for: vehicle types, movement patterns, uniform/equipment mentions,
restricted access, unusual military presence, security checkpoints, naval vessel sightings.
</instructions>

<post>
{truncated_text}
</post>
"""

    start_time = time.time()
    client = get_openai_client()
    
    try:
        response = await client.beta.chat.completions.parse(
            model=settings.openai_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=PostClassification,
            max_tokens=300
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Parse Response
        result = response.choices[0].message.parsed
        
        # Logging
        # OpenAI usage structure might differ slightly in `beta.chat.completions.parse` responses,
        # but usage object usually present.
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = estimate_cost(settings.openai_model, input_tokens, output_tokens)
        
        log_llm_call(
            model=settings.openai_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            cost_usd=cost
        )
        
        return result

    except Exception as e:
        logger.error("classification_failed", error=str(e))
        raise

async def classify_posts_batch(posts: List[dict], max_concurrent: int = None) -> List[PostClassification]:
    """Classify a batch of posts concurrently."""
    settings = get_settings()
    limit = max_concurrent or settings.max_concurrent_openai
    semaphore = create_semaphore(limit)
    
    async def classify_with_semaphore(post):
        async with semaphore:
            try:
                content = post.get("text", "") or post.get("content", "") or ""
                return await classify_civilian_post(content)
            except Exception as e:
                logger.error("batch_item_failed", error=str(e), post_id=post.get("id"))
                return None

    tasks = [classify_with_semaphore(p) for p in posts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions from gather if any remain (though we catch inside)
    clean_results = []
    for r in results:
        if isinstance(r, Exception) or r is None:
            clean_results.append(None) # Maintain index alignment if needed, or filter out?
            # Plan says "Return list of PostClassification results"
            # It implies successful ones. But to map back to inputs we might want to keep order.
            # However, simpler to just return the results and handle mapping in the caller if needed.
            # But wait, logic in batch processor needs to join classification with post_id.
            # So `classify_posts_batch` should probably return results in order or (post_id, result) tuples.
            # The plan signature `-> List[PostClassification]` implies strictly the objects.
            # I will return the list, maintaining index order (None for failures).
            pass
        else:
             pass
    
    return results

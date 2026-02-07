import structlog
import time
from src.llm.clients import get_anthropic_client
from src.llm.schemas import EntityExtraction
from src.llm.utils import create_retry_decorator, log_llm_call, truncate_text, estimate_cost
from src.config.settings import get_settings

logger = structlog.get_logger()
retry_decorator = create_retry_decorator()

@retry_decorator
async def extract_entities(text: str, source_type: str = "article") -> EntityExtraction:
    """
    Extracts military-relevant entities from text using Claude.
    """
    settings = get_settings()
    
    # Truncate based on source type
    max_tokens = settings.max_article_tokens if source_type == "article" else settings.max_post_tokens
    # Rough char approx (4 chars / token)
    max_chars = max_tokens * 4
    truncated_text = truncate_text(text, max_chars)

    prompt = f"""
<instructions>
Extract military-relevant entities from this text.

Entity types:
- military_unit: Unit names, designations (e.g., "PLA Eastern Theater Command", "Type 052D")
- equipment: Weapon systems, vehicles, platforms (e.g., "J-20 fighter", "DF-21D")
- location: Geographic locations with coordinates if available (e.g., "Taiwan Strait", "24.5N 118.2E")
- timestamp: Dates, times, temporal references (e.g., "Tuesday morning", "March 15")

Rules:
1. Extract ONLY entities explicitly present in text — do NOT infer or fabricate
2. Include exact source_span (verbatim text snippet containing the entity)
3. For locations, include latitude/longitude if coordinates present in text, null otherwise
4. Rate confidence 0-100 for each entity
5. Return empty entities list if no military-relevant entities found
</instructions>

<data>
{truncated_text}
</data>
"""

    start_time = time.time()
    client = get_anthropic_client()
    
    try:
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ],
            tools=[
                {
                    "name": "extract_entities",
                    "description": "Output structured extracted entities",
                    "input_schema": EntityExtraction.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "extract_entities"}
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Parse Tool Use
        tool_use = next(block for block in response.content if block.type == "tool_use")
        result = EntityExtraction(**tool_use.input)
        
        # Logging
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = estimate_cost(settings.claude_model, input_tokens, output_tokens)
        
        log_llm_call(
            model=settings.claude_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            cost_usd=cost
        )
        
        return result

    except Exception as e:
        logger.error("entity_extraction_failed", error=str(e))
        raise

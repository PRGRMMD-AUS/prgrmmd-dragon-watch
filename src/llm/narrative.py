import structlog
import time
from typing import List, Dict
from src.llm.clients import get_anthropic_client
from src.llm.schemas import NarrativeCoordination
from src.llm.utils import create_retry_decorator, log_llm_call, truncate_text, estimate_cost
from src.llm.config import NARRATIVE_ARTICLE_SNIPPET_LEN, NARRATIVE_MAX_ARTICLES
from src.config.settings import get_settings

logger = structlog.get_logger()
retry_decorator = create_retry_decorator()

@retry_decorator
async def detect_narrative_coordination(articles: List[Dict]) -> NarrativeCoordination:
    """
    Analyzes a batch of state media articles for narrative coordination.
    """
    settings = get_settings()
    
    # Pre-processing
    articles = articles[:NARRATIVE_MAX_ARTICLES]
    formatted_articles = ""
    total_input_chars = 0
    
    for art in articles:
        snippet = truncate_text(art.get("content", "") or "", NARRATIVE_ARTICLE_SNIPPET_LEN)
        formatted_articles += f"""
<article>
<outlet>{art.get("outlet", "unknown")}</outlet>
<title>{art.get("title", "no title")}</title>
<content>{snippet}</content>
<published_at>{art.get("published_at", "unknown")}</published_at>
</article>
"""
        total_input_chars += len(snippet)

    prompt = f"""
<instructions>
Analyze these state media articles for narrative coordination.
Look for:
1. Identical or near-identical phrases (3+ words) repeated across multiple outlets
2. Same geographic focus across outlets (e.g., Taiwan Strait, South China Sea)
3. Synchronized themes suggesting centralised directive

Score coordination 0-100:
- 0-30: Independent reporting (different topics, natural language variation)
- 30-70: Moderate coordination (shared themes, some phrasing overlap)
- 70-100: Strong coordination (synchronized phrasing across 3+ outlets, identical narratives)

Extract all synchronized phrases (exact 3+ word sequences appearing in 2+ outlets).
Identify the primary geographic region mentioned across outlets.
List narrative themes (1-3 words each).
Rate your confidence in the assessment (0-100).
</instructions>

<articles>
{formatted_articles}
</articles>
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
                    "name": "analyze_narrative",
                    "description": "Output structured narrative coordination analysis",
                    "input_schema": NarrativeCoordination.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "analyze_narrative"}
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Parse Tool Use
        tool_use = next(block for block in response.content if block.type == "tool_use")
        result = NarrativeCoordination(**tool_use.input)
        
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
        logger.error("narrative_detection_failed", error=str(e))
        raise

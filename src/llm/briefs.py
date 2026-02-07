import structlog
import time
from typing import List
from src.llm.clients import get_anthropic_client
from src.llm.schemas import IntelligenceBrief
from src.llm.utils import create_retry_decorator, log_llm_call, estimate_cost
from src.config.settings import get_settings

logger = structlog.get_logger()
retry_decorator = create_retry_decorator()

def format_narrative_events(events: List[dict]) -> str:
    """Format narrative events for prompt."""
    if not events:
        return "No narrative events found."
    
    formatted = []
    for e in events:
        # Assuming database columns match these keys
        # If created via write_narrative_event: coordination_score, synchronized_phrases, outlet_count, geographic_focus
        phrases = e.get("synchronized_phrases", [])
        if isinstance(phrases, list):
            phrases_str = ", ".join(phrases[:3])
        else:
            phrases_str = str(phrases)
            
        formatted.append(
            f"- {e.get('outlet_count')} outlets, score {e.get('coordination_score')}, "
            f"phrases: {phrases_str}, focus: {e.get('geographic_focus')}"
        )
    return "\n".join(formatted)

def format_movement_events(events: List[dict]) -> str:
    """Format movement events for prompt."""
    if not events:
        return "No movement events found."
        
    formatted = []
    for e in events:
        # Assuming database columns match keys
        formatted.append(
            f"- {e.get('category')}: {e.get('location')}, confidence {e.get('confidence')}, "
            f"post_id: {e.get('post_id')}"
        )
    return "\n".join(formatted)

@retry_decorator
async def generate_intelligence_brief(
    narrative_events: List[dict], 
    movement_events: List[dict], 
    time_window_hours: int = 72
) -> IntelligenceBrief:
    """Generate intelligence brief from analyzed events."""
    settings = get_settings()

    formatted_narrative = format_narrative_events(narrative_events)
    formatted_movement = format_movement_events(movement_events)

    prompt = f"""
<instructions>
Generate an intelligence assessment from the following dual-stream analysis data.

You are producing a UNCLASSIFIED // FOR EXERCISE USE ONLY intelligence brief for a pre-conflict early warning system monitoring the Taiwan Strait region.

Produce:
1. Threat Level: GREEN (routine, score <30) / AMBER (elevated, 30-70) / RED (critical, >70)
   Base on: narrative coordination strength, movement cluster size, geographic proximity, temporal alignment
2. Confidence (0-100): How certain is this threat assessment
3. Executive Summary: 2-3 sentences describing the current situation
4. Evidence Chain: List specific data points (articles, posts) supporting the assessment
5. Timeline: Chronological sequence of key events in the analysis window
6. Information Gaps: What information is missing or unclear
7. Collection Priorities: Recommended next collection targets (specific outlets, geographic areas, source types)

Intelligence analysis standards:
- Clearly separate confirmed facts from analytical assessments
- Hedge confidence based on source count and reliability
- Identify at least one alternative hypothesis
- Flag any single-source assessments
</instructions>

<narrative_stream>
Time window: {time_window_hours} hours
Events:
{formatted_narrative}
</narrative_stream>

<movement_stream>
Events:
{formatted_movement}
</movement_stream>
"""

    start_time = time.time()
    client = get_anthropic_client()
    
    try:
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=2048, # Increased context for full brief
            messages=[
                {"role": "user", "content": prompt}
            ],
            tools=[
                {
                    "name": "generate_brief",
                    "description": "Output structured intelligence brief",
                    "input_schema": IntelligenceBrief.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "generate_brief"}
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Parse Tool Use
        tool_use = next(block for block in response.content if block.type == "tool_use")
        result = IntelligenceBrief(**tool_use.input)
        
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
        logger.error("brief_generation_failed", error=str(e))
        raise

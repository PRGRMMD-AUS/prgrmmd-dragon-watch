import asyncio
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from anthropic import RateLimitError, APITimeoutError, InternalServerError
import openai

logger = structlog.get_logger()

def create_retry_decorator():
    return retry(
        retry=retry_if_exception_type((
            RateLimitError, APITimeoutError, InternalServerError,
            openai.RateLimitError, openai.APITimeoutError, openai.InternalServerError
        )),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60)
    )

def create_semaphore(max_concurrent: int) -> asyncio.Semaphore:
    return asyncio.Semaphore(max_concurrent)

def log_llm_call(model: str, input_tokens: int, output_tokens: int, duration_ms: int, cost_usd: float):
    logger.info("llm_call", model=model, input_tokens=input_tokens, output_tokens=output_tokens, duration_ms=duration_ms, cost_usd=cost_usd)

def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars-3] + "..."

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    # Prices per 1M tokens
    if "claude" in model.lower():
        input_price = 3.0
        output_price = 15.0
    elif "gpt-4o-mini" in model.lower():
        input_price = 0.15
        output_price = 0.60
    else:
        # Default fallback (safe overestimation or 0 to trigger manual check)
        return 0.0
        
    cost = (input_tokens / 1_000_000 * input_price) + (output_tokens / 1_000_000 * output_price)
    return cost

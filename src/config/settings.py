from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    anthropic_api_key: str = Field(..., description="API key for Anthropic Claude")
    openai_api_key: str = Field(..., description="API key for OpenAI GPT")
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase service role/anon key")
    
    # Model Configuration
    claude_model: str = "claude-3-5-sonnet-20241022" # Updated to latest Sonnet 3.5 ID
    openai_model: str = "gpt-4o-mini"
    
    # Concurrency Limits
    max_concurrent_claude: int = 5
    max_concurrent_openai: int = 20
    
    # Content Limits
    max_article_tokens: int = 1000
    max_post_tokens: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Configuration management"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    telegram_api_id: int = 12345678
    telegram_api_hash: str = "your_api_hash"
    telegram_bot_token: str = "your_bot_token"
    telegram_channel_id: str = "@ai_pulse_ai"
    
    database_url: str = "postgresql://ai_pulse:password@localhost:5432/ai_pulse"
    redis_url: str = "redis://localhost:6379/0"
    
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-70b-versatile"
    
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "ai-pulse-bot/1.0"
    
    app_env: str = "development"
    log_level: str = "INFO"
    debug: bool = False
    
    scout_interval_hours: int = 2
    daily_digest_hour: int = 9
    weekly_analytics_day: str = "fri"
    weekly_analytics_hour: int = 18
    
    min_score_for_publication: int = 60
    max_posts_per_day: int = 5
    language: str = "ru"


settings = Settings()

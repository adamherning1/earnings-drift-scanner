from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/earnings_db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Keys
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_")
    claude_api_key: str = os.getenv("CLAUDE_API_KEY", "")
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App Settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # Stripe Plans
    stripe_price_ids: dict = {
        "starter": os.getenv("STRIPE_STARTER_PRICE_ID", "price_starter"),
        "professional": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro"),
        "institution": os.getenv("STRIPE_INST_PRICE_ID", "price_inst")
    }
    
    # Rate Limits
    requests_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # App
    APP_NAME: str = "SwiftValuation AI"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/swiftval_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Feature flags / demo mode
    MOCK_MODE: bool = False
    ZOHO_MOCK_MODE: bool = False
    
    # APIs - Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-8b-8192"
    GROQ_VISION_MODEL: str = "llama-3.2-11b-vision-preview"
    
    # APIs - VIN Decoder
    VIN_DECODER_API_KEY: str = ""
    VIN_DECODER_URL: str = ""
    
    # APIs - Zoho CRM
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    ZOHO_REFRESH_TOKEN: str = ""
    ZOHO_BASE_URL: str = "https://www.zohoapis.com/crm/v2"
    ZOHO_CARS_MODULE: str = "Cars"
    
    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "swiftval-media"
    
    # Pricing
    DEFAULT_SPREAD_PERCENT: float = 15.0
    
@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

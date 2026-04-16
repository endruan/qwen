from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fitness_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # App
    APP_NAME: str = "Fitness & Nutrition API"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()

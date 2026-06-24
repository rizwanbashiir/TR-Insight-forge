####Updated settings.py 
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve path to .env file by traversing parent directories
env_file_path = ".env"
for parent in Path(__file__).resolve().parents:
    possible_env = parent / ".env"
    if possible_env.is_file():
        env_file_path = str(possible_env)
        break

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres@localhost:5432/analytics_db"
    
    # JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    #pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "trinsightforge"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Predefined Admin Settings
    PREDEFINED_ADMIN_EMAILS: str = "admin@example.com,admin@insightforge.com"

    # Grok Settings
    GROK_API_KEY: str = ""
    GROK_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROK_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = env_file_path
        extra = "ignore"

settings = Settings()
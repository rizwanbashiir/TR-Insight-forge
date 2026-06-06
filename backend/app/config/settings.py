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
    DATABASE_URL: str = "postgresql://postgres:yourpassword@localhost:5432/analytics_db"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    #pinecone
    PINECONE_API_KEY:str= "pcsk_4EtQAk_UDX8darV4qXEVigw2gAsQE8ibNMGZ98hpmzevz8TvmNoNhH1H9yk68sTvGqf6CR"
    PINECONE_INDEX_NAME:str = "trinsightforge"

    # Ollama
    OLLAMA_BASE_URL : str = "http://localhost:11434"
    OLLAMA_MODEL    : str = "llama3.2"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Predefined Admin Settings
    PREDEFINED_ADMIN_EMAILS: str = "admin@example.com,admin@insightforge.com"

    class Config:
        env_file = env_file_path

settings = Settings()
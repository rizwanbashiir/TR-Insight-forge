from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:yourpassword@localhost:5432/analytics_db"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    #pinecone
    PINECONE_API_KEY:str= "pcsk_4EtQAk_UDX8darV4qXEVigw2gAsQE8ibNMGZ98hpmzevz8TvmNoNhH1H9yk68sTvGqf6CR"
    PINECONE_INDEX_NAME:str = "trinsightforge"

    class Config:
        env_file = ".env"

settings = Settings()
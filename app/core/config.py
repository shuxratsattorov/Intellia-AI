from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Academic Assistant API"
    ENV: str = "local"
    DEBUG: bool = True

    # Security
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = 60

    # DB
    DATABASE_URL: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Optional
    REDIS_URL: str | None = None

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 1200

    # Email (optional)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None

    # Storage (optional)
    STORAGE_DRIVER: str = "local"
    STORAGE_LOCAL_DIR: str = "./storage"
    S3_BUCKET: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def cors_list(self) -> List[str]:
        # "a,b,c" => ["a","b","c"]
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

settings = Settings()

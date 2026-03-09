import pytz
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str
    ENV: str
    DEBUG: bool

    # CORS
    CORS_ORIGINS: list

    # JWT Security
    JWT_ALGORITHM: str
    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_ACCESS_TTL_MINUTES: int
    JWT_REFRESH_TTL_DAYS: int

    # Password Hash
    PASS_PEPPER: str
    TIME_COST: int
    MEMORY_COST: int
    PARALLELISM: int
    HASH_LEN: int
    SALT_LEN: int
    ENCODING: str

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    OPENAI_TEMPERATURE: float
    OPENAI_MAX_TOKENS: int

    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str

    # Storage
    STORAGE_DRIVER: str
    STORAGE_LOCAL_DIR: str
    S3_BUCKET: str
    S3_REGION: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str


    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parents[2] / ".env"), 
        extra="allow"
        )

    @property
    def cors_origins(self) -> list[str]:
        origins = self.CORS_ORIGINS

        if self.DEBUG:
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ])

        return origins

    @property
    def current_time(self):
        return pytz.timezone("Asia/Tashkent")


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
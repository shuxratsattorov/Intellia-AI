from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parents[2] / ".env"), 
        extra="allow",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # APP
    APP_NAME: str
    ENV: str
    DEBUG: bool
    DEFAULT_ROLE: str
    OTP_LENGTH: int

    # CORS
    CORS_ORIGINS: list

    # JWT (RSA256)
    JWT_ALGORITHM: str
    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str
    JWT_ISSUER: str
    JWT_ACCESS_TTL_MINUTES: int
    JWT_REFRESH_TTL_DAYS: int

    # PASSWORD HASH (Argon2)
    PEPPER: str
    TIME_COST: int
    MEMORY_COST: int
    PARALLELISM: int
    HASH_LEN: int
    SALT_LEN: int
    ENCODING: str

    # DATABASE (Posgtresql)
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # CACHE (Redis)
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int | None
    REDIS_PASSWORD: str | None
    DECODE_RESPONSES: bool

    # # OpenAI
    # OPENAI_API_KEY: str
    # OPENAI_MODEL: str
    # OPENAI_TEMPERATURE: float
    # OPENAI_MAX_TOKENS: int

    # EMAIL
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.POSTGRES_DB}"
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

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
import pytz
import datetime
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str
    ENV: str
    DEBUG: bool

    # CORS
    CORS_ORIGINS: list

    # Security
    JWT_SECRET: str
    JWT_ALG: str
    ACCESS_TOKEN_EXPIRE_MIN: int

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
    def current_time(time_zone=True):
        toshkent_tz = pytz.timezone('Asia/Tashkent')

        if time_zone:
            return datetime.datetime.now(tz=toshkent_tz)
        else:
            return datetime.datetime.now()    


settings = Settings()

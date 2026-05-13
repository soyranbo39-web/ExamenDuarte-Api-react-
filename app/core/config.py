from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AUTH_SECRET_KEY: SecretStr = Field(..., min_length=32)
    AUTH_ALGORITHM: str 
    AUTH_TOKEN_EXPIRE_MINUTES: int 
    AUTH_COOKIE_NAME: str 
    AUTH_COOKIE_SECURE: bool 
    AUTH_COOKIE_HTTPONLY: bool
    AUTH_COOKIE_SAMESITE: str
    SQLITE_DB_PATH: str 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()
SQLITE_DB_PATH = Path(settings.SQLITE_DB_PATH)
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")
    DEMO_MODE: bool = Field(default=True)
    APP_ENV: str = Field(default="development")
    DATA_DIR: str = Field(default=str(BASE_DIR / "backend" / "data"))
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR}/backend/data/northgate_kyc.db"
    )
    SIMULATED_DATE: str = Field(default="2026-11-12")
    PILOT_MODE: str = Field(default="assisted") # "shadow" | "assisted"
    CANARY_SHARE: float = Field(default=0.10)
    LOOKTHROUGH_THRESHOLD: float = Field(default=25.0)
    PORT: int = Field(default=8000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure DATA_DIR exists
os.makedirs(settings.DATA_DIR, exist_ok=True)

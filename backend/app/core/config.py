import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
os.makedirs(ROOT_DIR / "storage" / "uploads", exist_ok=True)
os.makedirs(ROOT_DIR / "storage" / "audio", exist_ok=True)

class Settings(BaseSettings):
    APP_NAME: str = "AI-Powered Dictation System"
    DATABASE_URL: str = "sqlite:///./storage/dictation.db"
    SECRET_KEY: str = "change-me-before-use"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "storage/uploads"
    AUDIO_DIR: str = "storage/audio"
    OCR_PROVIDER: str = "tesseract"
    OCR_MIN_CONFIDENCE: int = 45
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

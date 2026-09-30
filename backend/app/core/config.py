import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SignBridge AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "signbridge-secret-key-development-2026-secure-jwt-token")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./signbridge.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # ML & Inference settings
    CONFIDENCE_THRESHOLD: float = 0.65
    SEQUENCE_LENGTH: int = 20
    PREDICTION_DEBOUNCE_MS: int = 600
    ACTIVE_MODEL_TYPE: str = "demo_baseline"
    
    # Storage
    MODEL_DIR: str = os.getenv("MODEL_DIR", "../models")
    DATASET_DIR: str = os.getenv("DATASET_DIR", "../dataset")
    
    # Optional LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()

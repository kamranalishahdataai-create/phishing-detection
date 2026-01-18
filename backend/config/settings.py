"""
Settings and Configuration for Phishing Detection Backend
Uses Pydantic Settings for environment variable management
"""

import os
from pathlib import Path
from typing import Optional, List
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    APP_NAME: str = "Phishing Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Base Paths - auto-configured relative to project root
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODELS_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    # Model Paths (relative to BASE_DIR)
    ELECTRA_MODEL_PATH: str = "electra_url_model"
    BIFORMER_MODEL_PATH: str = "biformer_url_model"
    LGBM_MODEL_PATH: str = "phish_quick_run/lgbm_model.txt"
    CHAR2ID_PATH: str = "biformer_url_model/char2id.json"
    
    # Model Settings
    MAX_URL_LENGTH: int = 512
    BATCH_SIZE: int = 32
    MODEL_DEVICE: str = "cuda"  # Options: "cuda", "cpu", "auto"
    
    # Threshold Settings (from tuned_thresholds.json)
    PHISHING_THRESHOLD: float = 0.0863  # Precision-targeted threshold
    HIGH_CONFIDENCE_THRESHOLD: float = 0.95
    LOW_CONFIDENCE_THRESHOLD: float = 0.05
    
    # Ensemble Weights
    ELECTRA_WEIGHT: float = 0.40
    BIFORMER_WEIGHT: float = 0.35
    LGBM_WEIGHT: float = 0.25
    
    # Trust System Settings
    TRUST_SCORE_HIGH: float = 0.8
    TRUST_SCORE_MEDIUM: float = 0.5
    TRUST_SCORE_LOW: float = 0.2
    TRUST_SCORE_UNKNOWN: float = 0.0
    
    # Domain Intelligence
    MIN_DOMAIN_AGE_DAYS: int = 30  # Domains younger than this are suspicious
    SAFE_DOMAIN_AGE_DAYS: int = 365  # Domains older than this get trust bonus
    
    # External APIs (Optional)
    GOOGLE_SAFE_BROWSING_API_KEY: Optional[str] = None
    VIRUSTOTAL_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./phishing_detection.db"
    
    # Redis Cache (Optional)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour default cache
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/phishing_detection.log"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def electra_model_full_path(self) -> Path:
        return self.BASE_DIR / self.ELECTRA_MODEL_PATH
    
    @property
    def biformer_model_full_path(self) -> Path:
        return self.BASE_DIR / self.BIFORMER_MODEL_PATH
    
    @property
    def lgbm_model_full_path(self) -> Path:
        return self.BASE_DIR / self.LGBM_MODEL_PATH
    
    @property
    def char2id_full_path(self) -> Path:
        return self.BASE_DIR / self.CHAR2ID_PATH


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()

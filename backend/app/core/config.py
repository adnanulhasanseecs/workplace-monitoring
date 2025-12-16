"""
Application configuration management.
"""
from pydantic_settings import BaseSettings  # type: ignore
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Workflow Monitoring Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB_QUEUE: int = 0
    REDIS_DB_CACHE: int = 1
    REDIS_DB_COORDINATION: int = 2
    REDIS_PASSWORD: str = ""
    
    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3009", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # File Storage
    STORAGE_PATH: str = "./storage"
    EVENT_CLIPS_PATH: str = "./storage/clips"
    MAX_UPLOAD_SIZE_MB: int = 500
    
    # Video Processing
    DEFAULT_FPS: int = 5
    BURST_FPS: int = 30
    CHUNK_DURATION_SECONDS: int = 300
    VIDEO_CHUNK_DURATION_SECONDS: int = 300  # Alias for chunker
    VIDEO_STORAGE_PATH: str = "./storage"  # Base path for video storage
    FRAME_SAMPLE_RATE: int = 1
    
    # GPU Configuration
    CUDA_VISIBLE_DEVICES: str = "0"
    GPU_MEMORY_FRACTION: float = 0.8
    BATCH_SIZE: int = 16
    
    # YOLO11 Model Configuration
    YOLO_MODEL_PATH: str = "./models/yolo11n.pt"  # Options: yolo11n.pt, yolo11s.pt, yolo11m.pt, yolo11l.pt, yolo11x.pt
    YOLO_CONFIDENCE_THRESHOLD: float = 0.25
    YOLO_IOU_THRESHOLD: float = 0.45
    
    # Observability
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    PROMETHEUS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


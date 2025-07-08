"""
Global configuration settings
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_interviewer.db")
    
    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]
    
    # AI Services
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CLOUD_API_KEY: str = os.getenv("GOOGLE_CLOUD_API_KEY", "")
    
    # Google Cloud Settings
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    
    # External API Keys
    SPEECH_API_KEY: str = os.getenv("SPEECH_API_KEY", "")
    AZURE_FACE_API_KEY: str = os.getenv("AZURE_FACE_API_KEY", "")
    AZURE_FACE_ENDPOINT: str = os.getenv("AZURE_FACE_ENDPOINT", "")
    
    # AWS Storage
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "ai-interviewer-media")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Email/SMS Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "")
    ADMIN_EMAILS: List[str] = os.getenv("ADMIN_EMAILS", "").split(",") if os.getenv("ADMIN_EMAILS") else []
    
    # Twilio SMS
    TWILIO_SID: str = os.getenv("TWILIO_SID", "")
    TWILIO_TOKEN: str = os.getenv("TWILIO_TOKEN", "")
    TWILIO_PHONE: str = os.getenv("TWILIO_PHONE", "")
    
    # Other settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()

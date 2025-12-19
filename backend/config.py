"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Steam API Configuration
    steam_api_key: str = ""  # Required, but loaded from .env
    steam_id: Optional[str] = None
    
    # Database Configuration
    # Using postgresql+psycopg:// for psycopg3 (Python 3.13 compatible)
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/steam_rec_db"
    
    # Security & Authentication
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours
    jwt_algorithm: str = "HS256"
    
    # Application Configuration
    # CHANGE FOR PRODUCTION DEPLOYMENT
    environment: str = "development"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    
    # CORS Configuration
    allowed_origins: list[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Optional: Redis Cache
    redis_url: Optional[str] = None
    
    # Optional: Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60
    
    # API Settings
    api_v1_prefix: str = "/api"
    project_name: str = "Steam Game Recommendation API"
    debug: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Create global settings instance
settings = Settings()

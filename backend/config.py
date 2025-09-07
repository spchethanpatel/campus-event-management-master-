"""
Configuration settings for the Event Management System.
"""
from pathlib import Path
from typing import List


class Settings:
    """Application settings and configuration."""
    
    # Database configuration
    DATABASE_DIR: Path = Path(__file__).parent.parent / "database"
    DATABASE_NAME: str = "event_management_db.db"
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Event Management System"
    VERSION: str = "2.0.0"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000"
    ]
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    def __init__(self) -> None:
        """Initialize settings and ensure database directory exists."""
        self.DATABASE_DIR.mkdir(exist_ok=True)
    
    @property
    def database_path(self) -> str:
        """Get the full path to the database file."""
        return str(self.DATABASE_DIR / self.DATABASE_NAME)
    
    @property
    def database_url(self) -> str:
        """Get the SQLAlchemy database URL."""
        return f"sqlite:///{self.database_path}"


# Global settings instance
settings = Settings()

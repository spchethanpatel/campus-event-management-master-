"""
Database configuration and session management.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings


# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Only needed for SQLite
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_connection():
    """Get direct database connection for raw SQL queries."""
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

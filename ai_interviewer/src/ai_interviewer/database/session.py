"""
Database session management
"""

from typing import Generator
from sqlalchemy.orm import Session

from .base import SessionLocal

# This module provides a dependency for managing database sessions in the AI Interviewer application.
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields a database session.
    
    This function creates a new SQLAlchemy SessionLocal instance,
    yields it, and ensures it gets closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# This function can be used to create a new database session directly.
# It is useful for cases where you need to create a session outside of the dependency injection context
# provided by FastAPI or other frameworks.
def create_db_session() -> Session:
    """
    Create a new database session.
    
    Returns:
        Session: A new SQLAlchemy session
    """
    return SessionLocal()

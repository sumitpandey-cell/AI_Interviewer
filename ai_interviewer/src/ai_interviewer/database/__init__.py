"""
Database module initialization
"""
from .base import Base, engine, metadata, SessionLocal
from .session import get_db, create_db_session


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


__all__ = [
    'Base',
    'engine',
    'metadata',
    'SessionLocal',
    'get_db',
    'create_db_session',
    'create_tables',
]

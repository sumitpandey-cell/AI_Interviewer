"""
SQLAlchemy models for users (shared with auth)
"""

# Users model is defined in auth.models to avoid circular imports
from ai_interviewer.auth.models import User

__all__ = ["User"]

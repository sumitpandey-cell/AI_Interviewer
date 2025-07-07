"""
User-specific dependencies
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ai_interviewer.database.session import get_db
from ai_interviewer.users.service import UserService
from ai_interviewer.auth.dependencies import get_current_active_user
from ai_interviewer.auth.models import User


async def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get user service."""
    return UserService(db)


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user if they are admin."""
    # For now, we'll assume all users can perform admin actions
    # In a real application, you would check for admin role
    return current_user


async def validate_user_access(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
) -> bool:
    """Validate if current user can access the specified user."""
    # Users can only access their own data unless they're admin
    if current_user.id != user_id:
        # In a real application, check if current_user is admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return True

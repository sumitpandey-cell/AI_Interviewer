"""
User management business logic
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from ai_interviewer.auth.models import User
from ai_interviewer.users.schemas import UserUpdate, UserCreate
from ai_interviewer.utilities import hash_password
from ai_interviewer.exceptions import UserNotFoundException


class UserService:
    """User management service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users."""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")
        
        # Update fields if provided
        if user_update.email is not None:
            # Check if email is already taken by another user
            existing_user = await self.get_user_by_email(user_update.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already taken")
            user.email = user_update.email
        
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")
        
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        
        return user

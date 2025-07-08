"""
Authentication business logic
"""

from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session

from .models import User
from .schemas import UserRegister
from ...ai_interviewer.utils import hash_password, verify_password, create_access_token, decode_access_token
from ..config import settings
from ..exceptions import InvalidCredentialsException, UserAlreadyExistsException


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_data: UserRegister) -> str:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise UserAlreadyExistsException("User with this email already exists")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email}, 
            expires_delta=access_token_expires
        )
        
        return access_token
    
    async def authenticate_user(self, email: str, password: str) -> str:
        """Authenticate user and return access token."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            raise InvalidCredentialsException("Incorrect email or password")
            
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException("Incorrect email or password")
            
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return access_token
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        email: str = payload.get("email")
        if email is None:
            return None
        user = self.db.query(User).filter(User.email == email).first()
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

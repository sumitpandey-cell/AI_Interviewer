"""
Pydantic models for authentication
"""

from typing import Optional
from pydantic import BaseModel


class UserRegister(BaseModel):
    """User registration schema."""
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    """User login schema."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True

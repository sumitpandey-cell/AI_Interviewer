"""
Pydantic models for users
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True


class UserInDB(UserBase):
    """User in database schema."""
    id: int
    hashed_password: str
    is_active: bool
    
    class Config:
        orm_mode = True

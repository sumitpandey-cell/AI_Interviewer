"""
Authentication API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database.session import get_db
from .schemas import TokenResponse, UserRegister, UserResponse
from .service import AuthService
from .dependencies import get_current_active_user
from .models import User
from ..exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    invalid_credentials_exception,
    user_already_exists_exception
)


router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (will be hashed)
    - **full_name**: User's full name
    """
    auth_service = AuthService(db)
    try:
        token = await auth_service.register_user(user_data)
        return TokenResponse(access_token=token, token_type="bearer")
    except UserAlreadyExistsException as e:
        raise user_already_exists_exception(detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login user and get access token.
    
    - **username**: User's email address
    - **password**: User's password
    """
    auth_service = AuthService(db)
    try:
        token = await auth_service.authenticate_user(form_data.username, form_data.password)
        return TokenResponse(access_token=token, token_type="bearer")
    except (InvalidCredentialsException, UserNotFoundException):
        raise invalid_credentials_exception()


@router.post("/token", response_model=TokenResponse)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Get access token."""
    auth_service = AuthService(db)
    try:
        token = await auth_service.authenticate_user(form_data.username, form_data.password)
        return TokenResponse(access_token=token, token_type="bearer")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get information about the currently authenticated user.
    
    Returns:
        UserResponse: User details including id, email, full_name, and is_active
    """
    return current_user

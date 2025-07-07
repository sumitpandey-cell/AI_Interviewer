"""
Global custom exceptions
"""

from fastapi import HTTPException, status


class AIInterviewerException(Exception):
    """Base exception for AI Interviewer application."""
    pass


class UserNotFoundException(AIInterviewerException):
    """Exception raised when user is not found."""
    pass


class InterviewNotFoundException(AIInterviewerException):
    """Exception raised when interview is not found."""
    pass


class InvalidCredentialsException(AIInterviewerException):
    """Exception raised when credentials are invalid."""
    pass


class UserAlreadyExistsException(AIInterviewerException):
    """Exception raised when trying to create a user that already exists."""
    pass


class AIServiceException(AIInterviewerException):
    """Exception raised when AI service encounters an error."""
    pass


def user_not_found_exception():
    """HTTP exception for user not found."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


def interview_not_found_exception():
    """HTTP exception for interview not found."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Interview not found"
    )


def invalid_credentials_exception():
    """HTTP exception for invalid credentials."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"}
    )


def user_already_exists_exception(detail: str = "User with this email already exists"):
    """HTTP exception for when user already exists."""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )


def ai_service_exception():
    """HTTP exception for AI service errors."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="AI service error"
    )

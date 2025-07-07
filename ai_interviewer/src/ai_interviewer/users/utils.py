"""
User-specific utilities
"""

from typing import Dict, Any
import re


def validate_full_name(name: str) -> bool:
    """Validate full name format."""
    if not name or len(name.strip()) < 2:
        return False
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    pattern = r'^[a-zA-Z\s\-\'\.]+$'
    return re.match(pattern, name.strip()) is not None


def format_user_name(name: str) -> str:
    """Format user name (title case)."""
    return name.strip().title()


def get_user_initials(full_name: str) -> str:
    """Get user initials from full name."""
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    elif len(parts) == 1:
        return parts[0][0].upper()
    return ""


def sanitize_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize user input data."""
    sanitized = {}
    
    for key, value in user_data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    
    return sanitized


def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Check if password meets strength requirements.
    
    Returns:
        tuple: (is_strong, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets strength requirements"

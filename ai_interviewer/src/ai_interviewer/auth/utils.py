"""
Auth-specific utilities
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None


def sanitize_input(input_str: str) -> str:
    """Sanitize user input."""
    return input_str.strip()


def is_safe_redirect_url(url: str, allowed_hosts: list[str]) -> bool:
    """Check if redirect URL is safe."""
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    if not parsed.netloc:
        # Relative URLs are generally safe
        return True
    
    return parsed.netloc in allowed_hosts

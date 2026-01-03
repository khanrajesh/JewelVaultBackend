"""Authentication utilities."""

from functools import wraps
from typing import Optional

from django.http import JsonResponse

from backend.shared.exceptions import UnauthorizedException


def get_auth_token(request) -> Optional[str]:
    """Extract authorization token from request headers."""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def require_auth(func):
    """Decorator to require authentication."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = get_auth_token(request)
        if not token:
            raise UnauthorizedException("Missing authentication token")
        request.auth_token = token
        return func(request, *args, **kwargs)
    return wrapper


def verify_token(token: str) -> dict:
    """
    Verify authentication token.
    
    This is a placeholder. Implement with your actual token verification logic.
    """
    # TODO: Implement actual token verification (JWT, Firebase, etc.)
    if not token:
        raise UnauthorizedException("Invalid token")
    return {"token": token}

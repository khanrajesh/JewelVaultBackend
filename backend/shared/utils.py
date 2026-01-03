"""Utility functions."""

import uuid
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict

from django.http import JsonResponse


def generate_unique_id() -> str:
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())


def generate_timestamp() -> int:
    """Generate current timestamp in milliseconds."""
    return int(datetime.utcnow().timestamp() * 1000)


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JsonResponse:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        JsonResponse with standardized format
    """
    return JsonResponse({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


def error_response(message: str, data: Any = None, status_code: int = 400) -> JsonResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        data: Error details
        status_code: HTTP status code
        
    Returns:
        JsonResponse with standardized format
    """
    return JsonResponse({
        "success": False,
        "message": message,
        "data": data
    }, status=status_code)


def pagination_params(request) -> Dict[str, int]:
    """
    Extract pagination parameters from request.
    
    Args:
        request: Django request object
        
    Returns:
        Dictionary with 'page' and 'page_size' keys
    """
    from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
    
    page = max(1, int(request.GET.get('page', 1)))
    page_size = min(
        int(request.GET.get('page_size', DEFAULT_PAGE_SIZE)),
        MAX_PAGE_SIZE
    )
    
    return {
        'page': page,
        'page_size': page_size,
        'offset': (page - 1) * page_size
    }


def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to handle exceptions in views.
    
    Args:
        func: View function to decorate
        
    Returns:
        Decorated function with exception handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from .exceptions import ApplicationException
        
        try:
            return func(*args, **kwargs)
        except ApplicationException as e:
            return error_response(e.message, status_code=e.status_code)
        except Exception as e:
            return error_response(str(e), status_code=500)
    
    return wrapper

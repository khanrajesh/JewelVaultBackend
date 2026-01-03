"""Custom middleware for the application."""

import json
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ExceptionMiddleware:
    """Middleware to handle exceptions globally."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "message": "Internal Server Error",
                "data": None
            }, status=500)


class CORSMiddleware:
    """Simple CORS middleware."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response


class LoggingMiddleware:
    """Middleware to log incoming requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        logger.info(f"{request.method} {request.path}")
        response = self.get_response(request)
        logger.info(f"Response status: {response.status_code}")
        return response

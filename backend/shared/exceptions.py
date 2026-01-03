"""Custom exceptions for the application."""


class ApplicationException(Exception):
    """Base exception for the application."""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(ApplicationException):
    """Raised when validation fails."""
    def __init__(self, message, status_code=400):
        super().__init__(message, status_code)


class NotFoundException(ApplicationException):
    """Raised when a resource is not found."""
    def __init__(self, message, status_code=404):
        super().__init__(message, status_code)


class UnauthorizedException(ApplicationException):
    """Raised when user is not authenticated."""
    def __init__(self, message="Unauthorized", status_code=401):
        super().__init__(message, status_code)


class ForbiddenException(ApplicationException):
    """Raised when user doesn't have permission."""
    def __init__(self, message="Forbidden", status_code=403):
        super().__init__(message, status_code)


class ConflictException(ApplicationException):
    """Raised when there's a conflict (duplicate, etc.)."""
    def __init__(self, message, status_code=409):
        super().__init__(message, status_code)


class InternalServerException(ApplicationException):
    """Raised for internal server errors."""
    def __init__(self, message="Internal Server Error", status_code=500):
        super().__init__(message, status_code)

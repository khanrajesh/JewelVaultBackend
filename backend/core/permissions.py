"""Permission classes for authorization."""

from backend.shared.exceptions import ForbiddenException
from backend.shared.constants import ROLE_ADMIN


class Permission:
    """Base permission class."""
    
    @staticmethod
    def check(request, obj=None) -> bool:
        """Check if user has permission. Override in subclasses."""
        return True


class IsAuthenticated(Permission):
    """Check if user is authenticated."""
    
    @staticmethod
    def check(request, obj=None) -> bool:
        return hasattr(request, 'auth_token') and request.auth_token is not None


class IsAdmin(Permission):
    """Check if user is admin."""
    
    @staticmethod
    def check(request, obj=None) -> bool:
        user_role = getattr(request, 'user_role', None)
        return user_role == ROLE_ADMIN


class IsOwner(Permission):
    """Check if user owns the resource."""
    
    @staticmethod
    def check(request, obj=None) -> bool:
        if not obj:
            return False
        user_id = getattr(request, 'user_id', None)
        return obj.get('userId') == user_id or obj.get('user_id') == user_id


def require_permission(permission_class):
    """Decorator to require specific permission."""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not permission_class.check(request):
                raise ForbiddenException("You don't have permission to access this resource")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

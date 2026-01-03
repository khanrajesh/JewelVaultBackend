"""Input validators."""

import re
from typing import Optional

from .exceptions import ValidationException


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number (basic validation)."""
    phone_clean = re.sub(r'\D', '', phone)
    return 10 <= len(phone_clean) <= 15


def validate_required_fields(data: dict, required_fields: list) -> None:
    """
    Validate that all required fields are present.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValidationException: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        raise ValidationException(f"Missing required fields: {', '.join(missing_fields)}")


def validate_user_data(user_data: dict) -> None:
    """Validate user creation/update data."""
    required_fields = ['name', 'email', 'mobileNo', 'role']
    validate_required_fields(user_data, required_fields)
    
    if not validate_email(user_data['email']):
        raise ValidationException("Invalid email format")
    
    if not validate_phone(user_data['mobileNo']):
        raise ValidationException("Invalid phone number")


def validate_store_data(store_data: dict) -> None:
    """Validate store creation/update data."""
    required_fields = ['name', 'email', 'phone', 'address', 'proprietor']
    validate_required_fields(store_data, required_fields)
    
    if not validate_email(store_data['email']):
        raise ValidationException("Invalid email format")
    
    if not validate_phone(store_data['phone']):
        raise ValidationException("Invalid phone number")


def validate_pagination_params(page: Optional[int] = None, page_size: Optional[int] = None) -> None:
    """Validate pagination parameters."""
    if page is not None and page < 1:
        raise ValidationException("Page must be >= 1")
    
    if page_size is not None and page_size < 1:
        raise ValidationException("Page size must be >= 1")

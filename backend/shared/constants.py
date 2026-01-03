"""Application-wide constants."""

# User Roles
ROLE_ADMIN = "admin"
ROLE_STORE_OWNER = "store_owner"
ROLE_EMPLOYEE = "employee"
ROLE_CUSTOMER = "customer"

USER_ROLES = [
    ROLE_ADMIN,
    ROLE_STORE_OWNER,
    ROLE_EMPLOYEE,
    ROLE_CUSTOMER,
]

# HTTP Status Messages
SUCCESS_MESSAGE = "Success"
ERROR_MESSAGE = "Error"

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Firebase collections
FIREBASE_USERS_COLLECTION = "users"
FIREBASE_TEST_COLLECTION = "test"

# Database table names
TABLE_USERS = "users"
TABLE_USER_ADDITIONAL_INFO = "user_additional_info"
TABLE_STORE = "store"
TABLE_CATEGORY = "category"
TABLE_SUB_CATEGORY = "sub_category"
TABLE_ITEM = "item"

# Cache timeout (seconds)
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 1800  # 30 minutes
CACHE_TIMEOUT_LONG = 3600  # 1 hour

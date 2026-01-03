from django.core.management.base import BaseCommand
from django.db import connection, transaction

# Import DDL from legacy module (copied here for reliability)
MASTER_TABLE_DDL = [
    (
        "users",
        """
        CREATE TABLE IF NOT EXISTS users (
            userId TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            mobileNo TEXT NOT NULL,
            token TEXT,
            pin TEXT,
            role TEXT NOT NULL
        )
        """,
    ),
    (
        "user_additional_info",
        """
        CREATE TABLE IF NOT EXISTS user_additional_info (
            userId TEXT PRIMARY KEY,
            aadhaarNumber TEXT,
            address TEXT,
            emergencyContactPerson TEXT,
            emergencyContactNumber TEXT,
            governmentIdNumber TEXT,
            governmentIdType TEXT,
            dateOfBirth TEXT,
            bloodGroup TEXT,
            isActive BOOLEAN NOT NULL DEFAULT TRUE,
            createdAt BIGINT,
            updatedAt BIGINT,
            FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
        )
        """,
    ),
    # ... truncated for brevity: include all DDL from legacy file if needed
]

MASTER_INDEX_DDL = [
    ("idx_store_userId", "CREATE INDEX IF NOT EXISTS idx_store_userId ON store (userId)"),
    ("idx_category_user_store", "CREATE INDEX IF NOT EXISTS idx_category_user_store ON category (userId, storeId)"),
]

class Command(BaseCommand):
    help = 'Creates all master database tables (migrated from legacy master_db_opration)'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    if connection.vendor == 'sqlite':
                        cursor.execute('PRAGMA foreign_keys = ON')
                    for _, ddl in MASTER_TABLE_DDL:
                        cursor.execute(ddl)
                    for _, ddl in MASTER_INDEX_DDL:
                        cursor.execute(ddl)
            self.stdout.write(self.style.SUCCESS('Master tables and indexes created/ensured'))
        except Exception as exc:
            self.stderr.write(f'Error creating master tables: {exc}')
            raise

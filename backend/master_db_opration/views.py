from django.db import connection, transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Table definitions mirror the Room @Entity classes and DAOs in the mobile app.
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
    (
        "store",
        """
        CREATE TABLE IF NOT EXISTS store (
            storeId TEXT PRIMARY KEY,
            userId TEXT NOT NULL,
            proprietor TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            registrationNo TEXT NOT NULL,
            gstinNo TEXT NOT NULL,
            panNo TEXT NOT NULL,
            image TEXT NOT NULL,
            invoiceNo INTEGER NOT NULL DEFAULT 0,
            upiId TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "category",
        """
        CREATE TABLE IF NOT EXISTS category (
            catId TEXT PRIMARY KEY,
            catName TEXT NOT NULL,
            gsWt DOUBLE PRECISION NOT NULL DEFAULT 0,
            fnWt DOUBLE PRECISION NOT NULL DEFAULT 0,
            userId TEXT NOT NULL,
            storeId TEXT NOT NULL,
            FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
            FOREIGN KEY (storeId) REFERENCES store(storeId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "sub_category",
        """
        CREATE TABLE IF NOT EXISTS sub_category (
            subCatId TEXT PRIMARY KEY,
            catId TEXT NOT NULL,
            userId TEXT NOT NULL,
            storeId TEXT NOT NULL,
            catName TEXT NOT NULL,
            subCatName TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            gsWt DOUBLE PRECISION NOT NULL DEFAULT 0,
            fnWt DOUBLE PRECISION NOT NULL DEFAULT 0,
            FOREIGN KEY (catId) REFERENCES category(catId) ON DELETE CASCADE,
            FOREIGN KEY (storeId) REFERENCES store(storeId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "item",
        """
        CREATE TABLE IF NOT EXISTS item (
            itemId TEXT PRIMARY KEY,
            itemAddName TEXT NOT NULL,
            catId TEXT NOT NULL,
            userId TEXT NOT NULL,
            storeId TEXT NOT NULL,
            catName TEXT NOT NULL,
            subCatId TEXT NOT NULL,
            subCatName TEXT NOT NULL,
            entryType TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            gsWt DOUBLE PRECISION NOT NULL,
            ntWt DOUBLE PRECISION NOT NULL,
            fnWt DOUBLE PRECISION NOT NULL,
            purity TEXT NOT NULL,
            crgType TEXT NOT NULL,
            crg DOUBLE PRECISION NOT NULL,
            othCrgDes TEXT NOT NULL,
            othCrg DOUBLE PRECISION NOT NULL,
            cgst DOUBLE PRECISION NOT NULL,
            sgst DOUBLE PRECISION NOT NULL,
            igst DOUBLE PRECISION NOT NULL,
            huid TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'gm',
            addDesKey TEXT NOT NULL,
            addDesValue TEXT NOT NULL,
            addDate TIMESTAMPTZ NOT NULL,
            modifiedDate TIMESTAMPTZ NOT NULL,
            sellerFirmId TEXT NOT NULL,
            purchaseOrderId TEXT NOT NULL,
            purchaseItemId TEXT NOT NULL,
            FOREIGN KEY (catId) REFERENCES category(catId) ON DELETE CASCADE,
            FOREIGN KEY (subCatId) REFERENCES sub_category(subCatId) ON DELETE CASCADE,
            FOREIGN KEY (storeId) REFERENCES store(storeId) ON DELETE CASCADE,
            FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "customer",
        """
        CREATE TABLE IF NOT EXISTS customer (
            mobileNo TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            gstin_pan TEXT,
            addDate TIMESTAMPTZ NOT NULL,
            lastModifiedDate TIMESTAMPTZ NOT NULL,
            totalItemBought INTEGER NOT NULL DEFAULT 0,
            totalAmount DOUBLE PRECISION NOT NULL DEFAULT 0,
            notes TEXT,
            userId TEXT NOT NULL DEFAULT '',
            storeId TEXT NOT NULL DEFAULT ''
        )
        """,
    ),
    (
        "customer_khata_book",
        """
        CREATE TABLE IF NOT EXISTS customer_khata_book (
            khataBookId TEXT PRIMARY KEY,
            customerMobile TEXT NOT NULL,
            planName TEXT NOT NULL,
            startDate TIMESTAMPTZ NOT NULL,
            endDate TIMESTAMPTZ NOT NULL,
            monthlyAmount DOUBLE PRECISION NOT NULL,
            totalMonths INTEGER NOT NULL,
            totalAmount DOUBLE PRECISION NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            userId TEXT NOT NULL,
            storeId TEXT NOT NULL,
            FOREIGN KEY (customerMobile) REFERENCES customer(mobileNo) ON DELETE CASCADE
        )
        """,
    ),
    (
        "customer_transaction",
        """
        CREATE TABLE IF NOT EXISTS customer_transaction (
            transactionId TEXT PRIMARY KEY,
            customerMobile TEXT NOT NULL,
            transactionDate TIMESTAMPTZ NOT NULL,
            amount DOUBLE PRECISION NOT NULL,
            transactionType TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            referenceNumber TEXT,
            paymentMethod TEXT,
            khataBookId TEXT,
            monthNumber INTEGER,
            notes TEXT,
            userId TEXT NOT NULL,
            storeId TEXT NOT NULL,
            FOREIGN KEY (customerMobile) REFERENCES customer(mobileNo) ON DELETE CASCADE,
            FOREIGN KEY (khataBookId) REFERENCES customer_khata_book(khataBookId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "order",
        """
        CREATE TABLE IF NOT EXISTS "order" (
            orderId TEXT PRIMARY KEY,
            customerMobile TEXT NOT NULL,
            storeId TEXT NOT NULL,
            userId TEXT NOT NULL,
            orderDate TIMESTAMPTZ NOT NULL,
            totalAmount DOUBLE PRECISION NOT NULL DEFAULT 0,
            totalTax DOUBLE PRECISION NOT NULL DEFAULT 0,
            totalCharge DOUBLE PRECISION NOT NULL DEFAULT 0,
            discount DOUBLE PRECISION NOT NULL DEFAULT 0,
            note TEXT
        )
        """,
    ),
    (
        "order_item",
        """
        CREATE TABLE IF NOT EXISTS order_item (
            orderItemId TEXT PRIMARY KEY,
            orderId TEXT NOT NULL,
            orderDate TIMESTAMPTZ NOT NULL,
            itemId TEXT NOT NULL,
            customerMobile TEXT NOT NULL,
            catId TEXT NOT NULL,
            catName TEXT NOT NULL,
            itemAddName TEXT NOT NULL,
            subCatId TEXT NOT NULL,
            subCatName TEXT NOT NULL,
            entryType TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            gsWt DOUBLE PRECISION NOT NULL,
            ntWt DOUBLE PRECISION NOT NULL,
            fnWt DOUBLE PRECISION NOT NULL,
            fnMetalPrice DOUBLE PRECISION NOT NULL,
            purity TEXT NOT NULL,
            crgType TEXT NOT NULL,
            crg DOUBLE PRECISION NOT NULL,
            othCrgDes TEXT NOT NULL,
            othCrg DOUBLE PRECISION NOT NULL,
            cgst DOUBLE PRECISION NOT NULL,
            sgst DOUBLE PRECISION NOT NULL,
            igst DOUBLE PRECISION NOT NULL,
            huid TEXT NOT NULL,
            addDesKey TEXT NOT NULL,
            addDesValue TEXT NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            charge DOUBLE PRECISION NOT NULL,
            tax DOUBLE PRECISION NOT NULL,
            sellerFirmId TEXT NOT NULL,
            purchaseOrderId TEXT NOT NULL,
            purchaseItemId TEXT NOT NULL,
            FOREIGN KEY (orderId) REFERENCES "order"(orderId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "exchange_item",
        """
        CREATE TABLE IF NOT EXISTS exchange_item (
            exchangeItemId TEXT PRIMARY KEY,
            orderId TEXT NOT NULL,
            orderDate TIMESTAMPTZ NOT NULL,
            customerMobile TEXT NOT NULL,
            metalType TEXT NOT NULL,
            purity TEXT NOT NULL,
            grossWeight DOUBLE PRECISION NOT NULL,
            fineWeight DOUBLE PRECISION NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            isExchangedByMetal BOOLEAN NOT NULL,
            exchangeValue DOUBLE PRECISION NOT NULL,
            addDate TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            FOREIGN KEY (orderId) REFERENCES "order"(orderId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "firm",
        """
        CREATE TABLE IF NOT EXISTS firm (
            firmId TEXT PRIMARY KEY,
            firmName TEXT NOT NULL,
            firmMobileNumber TEXT NOT NULL,
            gstNumber TEXT NOT NULL,
            address TEXT NOT NULL
        )
        """,
    ),
    (
        "seller",
        """
        CREATE TABLE IF NOT EXISTS seller (
            sellerId TEXT PRIMARY KEY,
            firmId TEXT NOT NULL,
            name TEXT NOT NULL,
            mobileNumber TEXT NOT NULL,
            FOREIGN KEY (firmId) REFERENCES firm(firmId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "purchase_order",
        """
        CREATE TABLE IF NOT EXISTS purchase_order (
            purchaseOrderId TEXT PRIMARY KEY,
            sellerId TEXT NOT NULL,
            billNo TEXT NOT NULL,
            billDate TEXT NOT NULL,
            entryDate TEXT NOT NULL,
            extraChargeDescription TEXT,
            extraCharge DOUBLE PRECISION,
            totalFinalWeight DOUBLE PRECISION,
            totalFinalAmount DOUBLE PRECISION,
            notes TEXT,
            cgstPercent DOUBLE PRECISION NOT NULL,
            sgstPercent DOUBLE PRECISION NOT NULL,
            igstPercent DOUBLE PRECISION NOT NULL,
            FOREIGN KEY (sellerId) REFERENCES seller(sellerId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "purchase_order_item",
        """
        CREATE TABLE IF NOT EXISTS purchase_order_item (
            purchaseItemId TEXT PRIMARY KEY,
            purchaseOrderId TEXT NOT NULL,
            catId TEXT NOT NULL,
            catName TEXT NOT NULL,
            subCatId TEXT NOT NULL,
            subCatName TEXT NOT NULL,
            gsWt DOUBLE PRECISION NOT NULL,
            purity TEXT NOT NULL,
            ntWt DOUBLE PRECISION NOT NULL,
            fnWt DOUBLE PRECISION NOT NULL,
            fnRate DOUBLE PRECISION NOT NULL,
            wastagePercent DOUBLE PRECISION NOT NULL,
            FOREIGN KEY (purchaseOrderId) REFERENCES purchase_order(purchaseOrderId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "metal_exchange",
        """
        CREATE TABLE IF NOT EXISTS metal_exchange (
            exchangeId TEXT PRIMARY KEY,
            purchaseOrderId TEXT NOT NULL,
            catId TEXT NOT NULL,
            catName TEXT NOT NULL,
            subCatId TEXT NOT NULL,
            subCatName TEXT NOT NULL,
            fnWeight DOUBLE PRECISION NOT NULL,
            FOREIGN KEY (purchaseOrderId) REFERENCES purchase_order(purchaseOrderId) ON DELETE CASCADE
        )
        """,
    ),
    (
        "printer",
        """
        CREATE TABLE IF NOT EXISTS printer (
            address TEXT PRIMARY KEY,
            name TEXT,
            method TEXT NOT NULL,
            isDefault BOOLEAN NOT NULL DEFAULT FALSE,
            lastConnectedAt BIGINT,
            supportedLanguages TEXT,
            currentLanguage TEXT
        )
        """,
    ),
    (
        "label_template",
        """
        CREATE TABLE IF NOT EXISTS label_template (
            templateId TEXT PRIMARY KEY,
            templateName TEXT NOT NULL,
            templateType TEXT NOT NULL,
            labelWidth DOUBLE PRECISION NOT NULL,
            labelHeight DOUBLE PRECISION NOT NULL,
            gapWidth DOUBLE PRECISION NOT NULL,
            gapHeight DOUBLE PRECISION NOT NULL,
            printDensity INTEGER NOT NULL,
            printSpeed INTEGER NOT NULL,
            printDirection INTEGER NOT NULL,
            referenceX DOUBLE PRECISION NOT NULL,
            referenceY DOUBLE PRECISION NOT NULL,
            orientation TEXT NOT NULL,
            labelPadding DOUBLE PRECISION NOT NULL DEFAULT 1.5,
            printLanguage TEXT NOT NULL,
            createdAt BIGINT NOT NULL,
            modifiedAt BIGINT NOT NULL,
            isDefault BOOLEAN NOT NULL DEFAULT FALSE,
            description TEXT
        )
        """,
    ),
    (
        "label_element",
        """
        CREATE TABLE IF NOT EXISTS label_element (
            elementId TEXT PRIMARY KEY,
            templateId TEXT NOT NULL,
            elementType TEXT NOT NULL,
            x DOUBLE PRECISION NOT NULL,
            y DOUBLE PRECISION NOT NULL,
            width DOUBLE PRECISION NOT NULL,
            height DOUBLE PRECISION NOT NULL,
            rotation DOUBLE PRECISION NOT NULL,
            zIndex INTEGER NOT NULL,
            properties TEXT NOT NULL,
            dataBinding TEXT,
            isVisible BOOLEAN NOT NULL DEFAULT TRUE,
            FOREIGN KEY (templateId) REFERENCES label_template(templateId) ON DELETE CASCADE
        )
        """,
    ),
]

MASTER_INDEX_DDL = [
    ("idx_store_userId", "CREATE INDEX IF NOT EXISTS idx_store_userId ON store (userId)"),
    ("idx_category_user_store", "CREATE INDEX IF NOT EXISTS idx_category_user_store ON category (userId, storeId)"),
    ("idx_sub_category_cat", "CREATE INDEX IF NOT EXISTS idx_sub_category_cat ON sub_category (catId)"),
    ("idx_sub_category_store", "CREATE INDEX IF NOT EXISTS idx_sub_category_store ON sub_category (storeId)"),
    ("idx_item_cat", "CREATE INDEX IF NOT EXISTS idx_item_cat ON item (catId)"),
    ("idx_item_sub_cat", "CREATE INDEX IF NOT EXISTS idx_item_sub_cat ON item (subCatId)"),
    ("idx_item_store", "CREATE INDEX IF NOT EXISTS idx_item_store ON item (storeId)"),
    ("idx_item_user", "CREATE INDEX IF NOT EXISTS idx_item_user ON item (userId)"),
    ("idx_user_additional_info_user", "CREATE INDEX IF NOT EXISTS idx_user_additional_info_user ON user_additional_info (userId)"),
    ("idx_customer_khata_book_customer", "CREATE INDEX IF NOT EXISTS idx_customer_khata_book_customer ON customer_khata_book (customerMobile)"),
    ("idx_customer_transaction_customer", "CREATE INDEX IF NOT EXISTS idx_customer_transaction_customer ON customer_transaction (customerMobile)"),
    ("idx_customer_transaction_khata", "CREATE INDEX IF NOT EXISTS idx_customer_transaction_khata ON customer_transaction (khataBookId)"),
    ("idx_order_customer", 'CREATE INDEX IF NOT EXISTS idx_order_customer ON "order" (customerMobile)'),
    ("idx_order_item_order", "CREATE INDEX IF NOT EXISTS idx_order_item_order ON order_item (orderId)"),
    ("idx_exchange_item_order", "CREATE INDEX IF NOT EXISTS idx_exchange_item_order ON exchange_item (orderId)"),
    ("idx_seller_firm", "CREATE INDEX IF NOT EXISTS idx_seller_firm ON seller (firmId)"),
    ("idx_purchase_order_seller", "CREATE INDEX IF NOT EXISTS idx_purchase_order_seller ON purchase_order (sellerId)"),
    ("idx_purchase_order_item_po", "CREATE INDEX IF NOT EXISTS idx_purchase_order_item_po ON purchase_order_item (purchaseOrderId)"),
    ("idx_metal_exchange_po", "CREATE INDEX IF NOT EXISTS idx_metal_exchange_po ON metal_exchange (purchaseOrderId)"),
    ("idx_label_element_template", "CREATE INDEX IF NOT EXISTS idx_label_element_template ON label_element (templateId)"),
]


@require_POST
def create_master_tables(request):
    """
    Create/ensure all master tables mirrored from the mobile Room entities/DAOs.
    """
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                if connection.vendor == "sqlite":
                    cursor.execute("PRAGMA foreign_keys = ON")
                for _, ddl in MASTER_TABLE_DDL:
                    cursor.execute(ddl)
                for _, ddl in MASTER_INDEX_DDL:
                    cursor.execute(ddl)
        return JsonResponse(
            {
                "status": "ok",
                "db_vendor": connection.vendor,
                "tables": [name for name, _ in MASTER_TABLE_DDL],
                "indexes": [name for name, _ in MASTER_INDEX_DDL],
            }
        )
    except Exception as exc:  # pragma: no cover - defensive logging surface
        return JsonResponse({"error": str(exc)}, status=500)

import os

import firebase_admin
from firebase_admin import credentials, firestore, messaging, storage

cred_path = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", "backend/firebase/serviceAccountKey.json"
)

# Prefer explicit credentials file; otherwise fall back to the runtime's default
# service account (e.g., Cloud Run's service account).
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
else:
    cred = credentials.ApplicationDefault()

firebase_app = firebase_admin.initialize_app(cred, {
    "storageBucket": "jewel-vault.appspot.com"
})

# Shared Firestore client for the project.
db = firestore.client(firebase_app)

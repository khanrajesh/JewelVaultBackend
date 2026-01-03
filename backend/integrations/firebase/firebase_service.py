"""Firebase service integration."""

import os
import firebase_admin
from firebase_admin import credentials, firestore, messaging, storage
from typing import Any, Dict, List, Optional


class FirebaseService:
    """Service for Firebase operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase app and clients."""
        cred_path = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS",
            "backend/integrations/firebase/serviceAccountKey.json",
        )
        
        # Prefer explicit credentials file; otherwise fall back to default
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            cred = credentials.ApplicationDefault()
        
        self.app = firebase_admin.initialize_app(cred, {
            "storageBucket": "jewel-vault.appspot.com"
        })
        
        # Firestore client (accepts app)
        try:
            self.db = firestore.client(self.app)
        except Exception:
            # Fallback to default client
            self.db = firestore.client()

        # messaging does not expose a `client` factory in firebase-admin;
        # keep the module available and call send helpers when needed.
        try:
            self.messaging = messaging
        except Exception:
            self.messaging = None

        # Initialize storage bucket if available; guard against environment issues.
        try:
            # storage.bucket() will return the default bucket configured in the app
            self.storage = storage.bucket()
        except Exception:
            self.storage = None
    
    # Firestore operations
    def get_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """Fetch all documents from a collection."""
        docs = self.db.collection(collection_name).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific document."""
        doc = self.db.collection(collection_name).document(doc_id).get()
        if doc.exists:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    def create_document(self, collection_name: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """Create a new document."""
        if doc_id:
            self.db.collection(collection_name).document(doc_id).set(data)
            return doc_id
        else:
            ref = self.db.collection(collection_name).add(data)
            return ref[1].id
    
    def update_document(self, collection_name: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Update a document."""
        self.db.collection(collection_name).document(doc_id).update(data)
    
    def delete_document(self, collection_name: str, doc_id: str) -> None:
        """Delete a document."""
        self.db.collection(collection_name).document(doc_id).delete()
    
    def query_collection(self, collection_name: str, field: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """Query a collection."""
        query = self.db.collection(collection_name)
        query = query.where(field, operator, value)
        docs = query.stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    # Messaging operations
    def send_message(self, token: str, title: str, body: str, data: Optional[Dict] = None) -> str:
        """Send a message to a device."""
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token,
        )
        return self.messaging.send(message)
    
    def send_multicast(self, tokens: List[str], title: str, body: str, data: Optional[Dict] = None) -> Any:
        """Send a message to multiple devices."""
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            tokens=tokens,
        )
        return self.messaging.send_multicast(message)


# Singleton instance
firebase_service = FirebaseService()

from firebase_admin import auth, firestore
from app.config.firebase import get_firestore_client
from app.models.user import User
from typing import Optional


class UserRepository:
    """Repositório de persistência para Usuários no Firebase Auth e Cloud Firestore."""

    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def create_user_auth(self, email: str, password: str, display_name: str) -> str:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        return user_record.uid

    def save_user_data(self, uid: str, nome: str, email: str) -> None:
        self.db.collection('users').document(uid).set({
            'nome': nome,
            'email': email,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

    def get_user(self, uid: str) -> Optional[User]:
        doc = self.db.collection('users').document(uid).get()
        if doc.exists:
            data = doc.to_dict() or {}
            return User(
                uid=uid,
                nome=data.get('nome', ''),
                email=data.get('email', ''),
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            )
        return None
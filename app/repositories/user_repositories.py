from firebase_admin import auth, firestore
from app.models.user import User

class UserRepository:
    def create_user_auth(self, email: str, password: str, display_name: str) -> str:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        return user_record.uid  

    def save_user_data(self, uid: str, nome: str, email: str) -> None:
        db = firestore.client()
        db.collection('users').document(uid).set({
            'nome': nome,
            'email': email,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

    def get_user(self, uid: str) -> User:
        db = firestore.client()
        doc = db.collection('users').document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            return User(
                uid=uid,
                nome=data.get('nome'),
                email=data.get('email'),
                created_at=data.get('created_at'),
                update_at=data.get('updated_at')
            )
        return None
from firebase_admin import auth, firestore
from app.models.user import User

class UserRepository:
    def create_user_auth(self, email:str, password:str, display_name:str) -> str:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        return user_record.uid  

    def save_user_data (self, urid: str, nome: str, email: str) -> None:
        db = firestore.client()
        db collection('users').document(uid).set({
            'nome': nome,
            'email': email,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

        def get_user (self, uid: str) -> User:
            db = firestore.client()
            doc = db.collection('users').document(uid).get()
            if doc.exists:
                data = doc.to_dist()
                return User(
                    uid=uid,
                    nome=data['nome'],
                    email=data['email'],
                    created_at=data['created_at'],
                    update_at=data['updated_at']
                )

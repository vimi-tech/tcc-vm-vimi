import firebase_admin
from firebase_admin import firestore
from app.models.project import project

class projectrepositories:
    def get_all_projects(self) -> list[project]:
        db = firestore.client()
        docs = db.collection ('projects').stream()
        projects = []
        for doc in docs:
            data = doc.to_dict()
            projects.append(projects(id=doc.id,
                                     themes=data.get('themes'),
                                     description=data.get('description')
                                     images=data.get('images')
                                     video=data.get('video')
                                     room=data.get('room')
                                     evaluations=data.get('evaluations')
                                     criteria=data.get('criteria')
                                     average=data.get('average')
                                    ))

        return projects
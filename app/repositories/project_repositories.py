import firebase_admin
from firebase_admin import firestore
from app.models.project import project

class projectrepositories:
    def get_all_projects(self) -> list[Project]:
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
                                     criteria=data.get('criteria'),
                                     average=data.get('average')
                                    ))

        return projects

    def get_projects(self, project_id: str) -> Project:
        db = firestore.client()
        doc = db.collection('projects').document(project_id).get()
        if doc.exists:
            data = doc.to_dict()
            return Project (id=doc.id,
                                     themes=data.get('themes'),
                                     description=data.get('description')
                                     images=data.get('images')
                                     video=data.get('video')
                                     room=data.get('room')
                                     evaluations=data.get('evaluations')
                                     criteria=data.get('criteria'),
                                     average=data.get('average'))
        return None

    def add_projects(self, project: Project) -> str:
        db = firestore.client()
        doc = db.collection('projects').add({
            'themes': project.themes,
            'description': project.description,
            'images': project.images,
            'video': project.video,
            'room': project.room,
            'evaluations': project.evaluations,
            'criteria': project.criteria,
            'average': project.average
        })
        return doc.id

    def update_project(self, project_id: str, project: Project) -> bool:
        db = firestore.client()
        db.collection('projects').document(project_id).update({
            'themes': project.themes,
            'description': project.description,
            'images': project.images,
            'video': project.video,
            'room': project.room,
            'evaluations': project.evaluations,
            'criteria': project.criteria,
            'average': project.avarage
        })
       return True
                            
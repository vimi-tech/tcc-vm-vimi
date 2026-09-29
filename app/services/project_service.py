from app.repositories.project_repositories import ProjectRepositories
from app.models.project import Project 

class ProjectService:
    def __init__(self):
        self.project_repo = ProjectRepositories()
        
        def get_all_projects(self):
            return self.project_repo.get_all_projects()
        
        def get_project(self, data: dict):
            project = Project(
                id=None
                 themes=data.get('themes'),
                 description=data.get('description'),
                 images=data.get('images'),
                 video=data.get('video'),
                 room=data.get('room'),
                 evaluations=data.get('evaluations'),
                 criteria=data.get('criteria'),
                 average=float(data.get('average'0,0))
            )  
            return self.project_repo.add_project(project)
        
        def update_project(self, project_id:str, data: dict):
            project = project(
                 themes=data.get('themes'),
                 description=data.get('description'),
                 images=data.get('images'),
                 video=data.get('video'),
                 room=data.get('room'),
                 evaluations=data.get('evaluations'),
                 criteria=data.get('criteria'),
                 average=float(data.get('average'0,0))
            )    
            return self.project_repo.update_project(project_id, project)                   
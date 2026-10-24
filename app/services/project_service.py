from app.repositories.project_repositories import ProjectRepositories
from app.models.project import Project


def _para_float(valor, padrao=0.0):
    """Converte para número sem quebrar se vier vazio ou com texto."""
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


class ProjectService:
    def __init__(self):
        self.project_repo = ProjectRepositories()

    # Os métodos abaixo ficam no nível da classe (o recuo certo).
    # No seu código eles estavam DENTRO do __init__, por isso não existiam
    # em ProjectService e davam AttributeError.

    def get_all_projects(self):
        return self.project_repo.get_all_projects()

    def create_project(self, data: dict):
        """Cria um projeto novo (no seu código se chamava get_project)."""
        project = Project(
            id=None,
            themes=data.get('themes'),
            description=data.get('description'),
            images=data.get('images'),
            video=data.get('video'),
            room=data.get('room'),
            evaluations=data.get('evaluations'),
            criteria=data.get('criteria'),
            average=_para_float(data.get('average', 0)),
        )
        return self.project_repo.add_project(project)

    def update_project(self, project_id: str, data: dict):
        project = Project(
            id=project_id,
            themes=data.get('themes'),
            description=data.get('description'),
            images=data.get('images'),
            video=data.get('video'),
            room=data.get('room'),
            evaluations=data.get('evaluations'),
            criteria=data.get('criteria'),
            average=_para_float(data.get('average', 0)),
        )
        return self.project_repo.update_project(project_id, project)
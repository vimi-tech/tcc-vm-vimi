import uuid
from typing import List, Optional, Dict, Any
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from app.config.firebase import get_firestore_client
from app.models.project import Project


class ProjectRepository:
    """Repositório de persistência para Projetos / Estandes no Cloud Firestore."""

    COLLECTION_NAME = 'estandes'

    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def _get_collection(self):
        client = self.db
        if client is None:
            raise ConnectionError(
                "Não foi possível conectar ao Firestore. Verifique as credenciais do projeto 'tccfeirascore'."
            )
        return client.collection(self.COLLECTION_NAME)

    def get_all(self) -> List[Project]:
        """Recupera todos os projetos cadastrados, do mais recente para o mais antigo."""
        try:
            query = self._get_collection().order_by(
                'criadoEm', direction=firestore.Query.DESCENDING
            )
            docs = query.stream()
            projects = []
            for doc in docs:
                data = doc.to_dict() or {}
                projects.append(Project.from_dict(doc.id, data))
            return projects
        except Exception as e:
            # Fallback sem order_by caso o índice do Firestore ainda não tenha sido gerado
            try:
                docs = self._get_collection().stream()
                projects = []
                for doc in docs:
                    data = doc.to_dict() or {}
                    projects.append(Project.from_dict(doc.id, data))
                return projects
            except Exception as inner_err:
                raise RuntimeError(f"Erro ao listar projetos do Firestore: {inner_err}") from e

    def get_by_id(self, project_id: str) -> Optional[Project]:
        """Busca um projeto pelo ID do documento no Firestore."""
        if not project_id:
            return None
        doc = self._get_collection().document(project_id).get()
        if doc.exists:
            return Project.from_dict(doc.id, doc.to_dict() or {})
        return None

    def get_by_turma(self, turma: str) -> Optional[Project]:
        """Busca o projeto associado a uma turma específica."""
        if not turma:
            return None
        turma_normalizada = turma.strip().lower()
        try:
            query = self._get_collection().where(
                filter=FieldFilter('turma_busca', '==', turma_normalizada)
            ).limit(1).stream()
        except TypeError:
            query = self._get_collection().where(
                'turma_busca', '==', turma_normalizada
            ).limit(1).stream()

        for doc in query:
            return Project.from_dict(doc.id, doc.to_dict() or {})
        return None

    def turma_ja_cadastrada(self, turma: str, ignorar_id: Optional[str] = None) -> bool:
        """Verifica se já existe projeto registrado para a turma informada."""
        if not turma:
            return False
        turma_normalizada = turma.strip().lower()
        try:
            query = self._get_collection().where(
                filter=FieldFilter('turma_busca', '==', turma_normalizada)
            ).stream()
        except TypeError:
            query = self._get_collection().where(
                'turma_busca', '==', turma_normalizada
            ).stream()

        for doc in query:
            if doc.id != ignorar_id:
                return True
        return False

    def save(self, project: Project) -> Project:
        """Salva ou atualiza um projeto no Firestore."""
        doc_id = project.id or uuid.uuid4().hex
        project.id = doc_id

        data = project.to_dict()
        if 'criadoEm' not in data or not data['criadoEm']:
            data['criadoEm'] = firestore.SERVER_TIMESTAMP

        self._get_collection().document(doc_id).set(data)
        return project

    def update(self, project_id: str, fields: Dict[str, Any]) -> bool:
        """Atualiza campos específicos de um projeto."""
        if not project_id:
            return False
        if 'turma' in fields and 'turma_busca' not in fields:
            fields['turma_busca'] = fields['turma'].strip().lower()
        self._get_collection().document(project_id).update(fields)
        return True

    def delete(self, project_id: str) -> bool:
        """Remove o documento do projeto do Firestore."""
        if not project_id:
            return False
        self._get_collection().document(project_id).delete()
        return True


# Mantém compatibilidade com importações antigas
ProjectRepositories = ProjectRepository
projectrepositories = ProjectRepository
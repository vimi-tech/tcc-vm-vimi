from typing import List, Optional, Tuple, Dict, Any
from app.models.project import Project
from app.repositories.project_repositories import ProjectRepository
from app.services.media_service import MediaService


class ProjectService:
    """Regras de negócio para cadastro, vínculo com Turma e manipulação de Projetos."""

    def __init__(self, project_repo: Optional[ProjectRepository] = None, media_service: Optional[MediaService] = None):
        self.project_repo = project_repo or ProjectRepository()
        self.media_service = media_service or MediaService()

    def get_all_projects(self) -> List[Project]:
        """Lista todos os projetos/estandes cadastrados."""
        return self.project_repo.get_all()

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Busca um projeto pelo ID do documento."""
        return self.project_repo.get_by_id(project_id)

    def get_project_by_turma(self, turma: str) -> Optional[Project]:
        """Busca o projeto associado a uma determinada turma."""
        if not turma:
            return None
        return self.project_repo.get_by_turma(turma)

    def register_project(
        self,
        turma: str,
        nome: str,
        resumo: str,
        arquivos_midia: Optional[list] = None
    ) -> Tuple[Project, int]:
        """
        Cadastra um novo projeto e vincula-o obrigatoriamente a uma turma.
        Retorna (projeto_criado, qtd_midias_ignoradas).
        Lança ValueError em caso de dados inválidos ou turma já cadastrada.
        """
        if not turma or not turma.strip():
            raise ValueError("Por favor, informe a turma responsável pelo projeto!")

        if not nome or not nome.strip():
            raise ValueError("O nome do projeto é obrigatório!")

        if not resumo or not resumo.strip():
            raise ValueError("O resumo/descrição do projeto é obrigatório!")

        turma_limpa = turma.strip()
        nome_limpo = nome.strip()
        resumo_limpo = resumo.strip()

        # Validação da regra de negócio: cada turma só pode ter 1 projeto
        if self.project_repo.turma_ja_cadastrada(turma_limpa):
            raise ValueError(f'A turma "{turma_limpa}" já possui um projeto/estande cadastrado!')

        # Processamento e upload de mídias (fotos e vídeo)
        midias_salvas, ignoradas = [], 0
        if arquivos_midia:
            midias_salvas, ignoradas = self.media_service.salvar_midias(arquivos_midia)

        # Criação da entidade de domínio
        project = Project(
            turma=turma_limpa,
            nome=nome_limpo,
            resumo=resumo_limpo,
            midias=midias_salvas,
        )

        try:
            # Persistência no Firestore
            saved_project = self.project_repo.save(project)
            return saved_project, ignoradas
        except Exception as e:
            # Se ocorrer erro no banco, exclui as mídias para evitar arquivos órfãos
            for midia in midias_salvas:
                self.media_service.apagar_midia(midia)
            raise RuntimeError(f"Erro ao salvar o projeto no Firestore: {str(e)}") from e

    def update_project(self, project_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza os dados de um projeto existente com validação de turma."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Projeto não encontrado.")

        nova_turma = data.get('turma')
        if nova_turma and nova_turma.strip():
            nova_turma = nova_turma.strip()
            if self.project_repo.turma_ja_cadastrada(nova_turma, ignorar_id=project_id):
                raise ValueError(f'A turma "{nova_turma}" já possui outro projeto cadastrado!')
            data['turma'] = nova_turma
            data['turma_busca'] = nova_turma.lower()

        return self.project_repo.update(project_id, data)
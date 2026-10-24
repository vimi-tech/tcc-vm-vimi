from typing import Optional, Tuple, List
from app.models.turma import Turma
from app.repositories.turma_repository import TurmaRepository


class TurmaService:
    """Regras de negócio para autenticação de turmas via código e gerenciamento de turmas."""

    def __init__(self, turma_repo: Optional[TurmaRepository] = None):
        self.turma_repo = turma_repo or TurmaRepository()

    def autenticar_turma(self, usuario: str, codigo: str) -> Tuple[bool, Optional[Turma], str]:
        """
        Autentica uma turma a partir do código de acesso cadastrado no Firestore.
        Retorna (sucesso, turma_autenticada, mensagem).
        """
        if not usuario or not usuario.strip():
            return False, None, "Por favor, informe o seu nome de usuário!"

        if not codigo or not codigo.strip():
            return False, None, "Por favor, digite o código de acesso da turma!"

        codigo_limpo = codigo.strip()
        turma = self.turma_repo.get_by_codigo(codigo_limpo)

        if not turma:
            return False, None, "Código de turma inválido! Digite o código impresso no papel fornecido."

        if not turma.ativo:
            return False, None, "Este código de turma foi desativado pela organização."

        return True, turma, f"Acesso liberado para a {turma.nome}!"

    def cadastrar_turma(self, nome: str, codigo: str) -> Turma:
        """Permite à administração cadastrar uma nova turma com seu código no Firestore."""
        if not nome or not nome.strip():
            raise ValueError("O nome da turma é obrigatório.")
        if not codigo or not codigo.strip():
            raise ValueError("O código de acesso é obrigatório.")

        existente = self.turma_repo.get_by_codigo(codigo.strip())
        if existente:
            raise ValueError(f"O código '{codigo}' já está em uso pela {existente.nome}.")

        turma = Turma(
            nome=nome.strip(),
            codigo_acesso=codigo.strip(),
            ativo=True
        )
        return self.turma_repo.save(turma)

    def listar_todas(self) -> List[Turma]:
        """Lista todas as turmas disponíveis para administração."""
        return self.turma_repo.get_all()

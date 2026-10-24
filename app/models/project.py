from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Project:
    """Entidade de Domínio representando um Projeto / Estande vinculado a uma Turma."""
    turma: str
    nome: str
    resumo: str
    id: Optional[str] = None
    midias: List[str] = field(default_factory=list)
    turma_busca: Optional[str] = None
    criado_em: Optional[Any] = None
    criterios: List[str] = field(default_factory=list)
    media: float = 0.0

    def __post_init__(self):
        if not self.turma_busca and self.turma:
            self.turma_busca = self.turma.strip().lower()

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário pronto para gravação no Firestore."""
        data = {
            'turma': self.turma.strip() if self.turma else '',
            'turma_busca': (self.turma_busca or self.turma or '').strip().lower(),
            'nome': self.nome.strip() if self.nome else 'Projeto sem título',
            'resumo': self.resumo.strip() if self.resumo else '',
            'midias': self.midias,
            'criterios': self.criterios,
            'media': self.media,
        }
        if self.criado_em is not None:
            data['criadoEm'] = self.criado_em
        return data

    @classmethod
    def from_dict(cls, doc_id: str, data: Dict[str, Any]) -> 'Project':
        """Reconstitui a entidade a partir de um documento do Firestore."""
        return cls(
            id=doc_id,
            turma=data.get('turma', ''),
            turma_busca=data.get('turma_busca', (data.get('turma', '')).strip().lower()),
            nome=data.get('nome') or data.get('nome_projeto', 'Projeto sem título'),
            resumo=data.get('resumo') or data.get('descricao', ''),
            midias=data.get('midias') or [],
            criado_em=data.get('criadoEm') or data.get('criado_em'),
            criterios=data.get('criterios') or data.get('criteria') or [],
            media=float(data.get('media', 0.0) or data.get('average', 0.0) or 0.0),
        )

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Turma:
    """Entidade de Domínio representando uma Turma e suas credenciais de acesso."""
    nome: str
    codigo_acesso: str
    id: Optional[str] = None
    ativo: bool = True
    projeto_id: Optional[str] = None
    criado_em: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para gravação no Firestore."""
        data = {
            'nome': self.nome.strip(),
            'codigo_acesso': str(self.codigo_acesso).strip(),
            'ativo': self.ativo,
            'projeto_id': self.projeto_id,
        }
        if self.criado_em is not None:
            data['criado_em'] = self.criado_em
        return data

    @classmethod
    def from_dict(cls, doc_id: str, data: Dict[str, Any]) -> 'Turma':
        """Reconstitui a entidade a partir do Firestore."""
        return cls(
            id=doc_id,
            nome=data.get('nome', ''),
            codigo_acesso=str(data.get('codigo_acesso', '')).strip(),
            ativo=bool(data.get('ativo', True)),
            projeto_id=data.get('projeto_id'),
            criado_em=data.get('criado_em'),
        )

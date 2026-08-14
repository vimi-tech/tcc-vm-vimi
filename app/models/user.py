from dataclass import dataclass

@dataclass
class User:
    wid: str
    nome: str
    email: str
    created_at: str = None
    updated_at: str = None
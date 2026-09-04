from dataclass import dataclass
from datatime import datetime

@dataclass
class User:
    wid: str
    nome: str
    email: str
    created_at: datatime = field(default_factory=datatime.utcnow)
 
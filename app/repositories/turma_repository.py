import logging
from typing import List, Optional, Dict, Any
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from app.config.firebase import get_firestore_client
from app.models.turma import Turma

logger = logging.getLogger(__name__)

# Base inicial com as 58 turmas migradas do frontend para o Firestore
TURMAS_PADRAO = {
    "2176327": "Turma 01",
    "1489922": "Turma 02",
    "8163598": "Turma 03",
    "8629015": "Turma 04",
    "3908372": "Turma 05",
    "8077417": "Turma 06",
    "5337343": "Turma 07",
    "9884271": "Turma 08",
    "2339790": "Turma 09",
    "2427323": "Turma 10",
    "4928715": "Turma 11",
    "3304636": "Turma 12",
    "8016938": "Turma 13",
    "2886634": "Turma 14",
    "3228520": "Turma 15",
    "3828733": "Turma 16",
    "6740665": "Turma 17",
    "2270644": "Turma 18",
    "3599645": "Turma 19",
    "2823172": "Turma 20",
    "3702262": "Turma 21",
    "1903026": "Turma 22",
    "3978598": "Turma 23",
    "1420347": "Turma 24",
    "7451325": "Turma 25",
    "6159853": "Turma 26",
    "2136936": "Turma 27",
    "2703088": "Turma 28",
    "8689658": "Turma 29",
    "2775943": "Turma 30",
    "4532520": "Turma 31",
    "1940696": "Turma 32",
    "7637084": "Turma 33",
    "7969875": "Turma 34",
    "7597285": "Turma 35",
    "7483143": "Turma 36",
    "5888905": "Turma 37",
    "3562208": "Turma 38",
    "2338031": "Turma 39",
    "9281775": "Turma 40",
    "2550093": "Turma 41",
    "9508326": "Turma 42",
    "8564983": "Turma 43",
    "3362444": "Turma 44",
    "1925012": "Turma 45",
    "5703566": "Turma 46",
    "1780694": "Turma 47",
    "1513580": "Turma 48",
    "4344516": "Turma 49",
    "6860590": "Turma 50",
    "3439684": "Turma 51",
    "8418400": "Turma 52",
    "1786135": "Turma 53",
    "4742360": "Turma 54",
    "6880917": "Turma 55",
    "6066107": "Turma 56",
    "2866878": "Turma 57",
    "4802876": "Turma 58"
}


class TurmaRepository:
    """Repositório para persistência e validação de Turmas e Códigos de Acesso no Firestore."""

    COLLECTION_NAME = 'turmas'

    def __init__(self, db=None):
        self._db = db
        self._seeded = False

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def _get_collection(self):
        client = self.db
        if client is None:
            raise ConnectionError("Cliente do Firestore indisponível para TurmaRepository.")
        return client.collection(self.COLLECTION_NAME)

    def get_by_codigo(self, codigo: str) -> Optional[Turma]:
        """Busca uma turma pelo código de acesso no Firestore."""
        if not codigo:
            return None
        codigo_limpo = str(codigo).strip()

        # Garante inicialização das turmas padrão no Firestore se necessário
        self.garantir_seed()

        try:
            # 1. Tenta buscar pelo ID do documento sendo o próprio código
            doc = self._get_collection().document(codigo_limpo).get()
            if doc.exists:
                return Turma.from_dict(doc.id, doc.to_dict() or {})

            # 2. Busca pelo campo 'codigo_acesso'
            query = self._get_collection().where(
                filter=FieldFilter('codigo_acesso', '==', codigo_limpo)
            ).limit(1).stream()

            for d in query:
                return Turma.from_dict(d.id, d.to_dict() or {})
        except Exception as e:
            logger.warning(f"Aviso ao consultar Firestore por código '{codigo_limpo}': {e}")
            # Fallback seguro caso o Firestore esteja em modo offline/sem credencial
            if codigo_limpo in TURMAS_PADRAO:
                return Turma(
                    id=codigo_limpo,
                    nome=TURMAS_PADRAO[codigo_limpo],
                    codigo_acesso=codigo_limpo
                )

        return None

    def get_by_nome(self, nome: str) -> Optional[Turma]:
        """Busca uma turma pelo nome no Firestore."""
        if not nome:
            return None
        nome_limpo = nome.strip()

        try:
            query = self._get_collection().where(
                filter=FieldFilter('nome', '==', nome_limpo)
            ).limit(1).stream()

            for d in query:
                return Turma.from_dict(d.id, d.to_dict() or {})
        except Exception as e:
            logger.warning(f"Erro ao consultar turma por nome: {e}")

        return None

    def get_all(self) -> List[Turma]:
        """Retorna todas as turmas cadastradas no Firestore."""
        self.garantir_seed()
        turmas = []
        try:
            docs = self._get_collection().stream()
            for doc in docs:
                turmas.append(Turma.from_dict(doc.id, doc.to_dict() or {}))
        except Exception as e:
            logger.warning(f"Erro ao listar turmas do Firestore: {e}")
            for cod, nome in TURMAS_PADRAO.items():
                turmas.append(Turma(id=cod, nome=nome, codigo_acesso=cod))
        return turmas

    def save(self, turma: Turma) -> Turma:
        """Salva ou atualiza uma turma no Firestore."""
        doc_id = turma.id or turma.codigo_acesso
        turma.id = doc_id

        data = turma.to_dict()
        if 'criado_em' not in data or not data['criado_em']:
            data['criado_em'] = firestore.SERVER_TIMESTAMP

        self._get_collection().document(doc_id).set(data)
        return turma

    def garantir_seed(self) -> int:
        """Sincroniza as 58 turmas no Firestore caso a coleção esteja vazia."""
        if self._seeded:
            return 0

        try:
            col = self._get_collection()
            # Verifica se já existem documentos
            primeiro = next(col.limit(1).stream(), None)
            if primeiro is not None:
                self._seeded = True
                return 0

            # Coleção vazia: realiza o seed em batch
            batch = self.db.batch()
            count = 0
            for codigo, nome in TURMAS_PADRAO.items():
                ref = col.document(codigo)
                batch.set(ref, {
                    'nome': nome,
                    'codigo_acesso': codigo,
                    'ativo': True,
                    'criado_em': firestore.SERVER_TIMESTAMP
                })
                count += 1

            batch.commit()
            self._seeded = True
            logger.info(f"Seed concluído: {count} turmas cadastradas no Firestore.")
            return count
        except Exception as e:
            logger.warning(f"Não foi possível executar o seed automático de turmas no Firestore: {e}")
            return 0

import json
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', 'tccfeirascore')

_db = None
_app = None


def get_service_account_path() -> str | None:
    """Busca o caminho do arquivo de credenciais de serviço do Firebase."""
    candidatos = [
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
        os.environ.get('FIREBASE_CREDENTIALS'),
        '/etc/secrets/serviceAccountKey.json',
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'serviceAccountKey.json'),
        os.path.join(os.getcwd(), 'serviceAccountKey.json'),
    ]
    for caminho in candidatos:
        if caminho and os.path.isfile(caminho):
            return caminho
    return None


def init_firebase():
    """Inicializa o Firebase Admin SDK apontando para o projeto tccfeirascore."""
    global _app, _db

    if _app is not None and firebase_admin._apps:
        return _app

    # Se já existir um app padrão do Firebase inicializado
    if firebase_admin._apps:
        _app = firebase_admin.get_app()
        _db = firestore.client(app=_app)
        return _app

    caminho_chave = get_service_account_path()
    json_chave = os.environ.get('FIREBASE_CREDENTIALS_JSON') or os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')

    try:
        if json_chave:
            cred_dict = json.loads(json_chave)
            cred = credentials.Certificate(cred_dict)
            _app = firebase_admin.initialize_app(cred, {'projectId': FIREBASE_PROJECT_ID})
            logger.info("Firebase inicializado via variável de ambiente com JSON da chave.")
        elif caminho_chave:
            cred = credentials.Certificate(caminho_chave)
            _app = firebase_admin.initialize_app(cred, {'projectId': FIREBASE_PROJECT_ID})
            logger.info(f"Firebase inicializado via chave de arquivo: {caminho_chave}")
        else:
            # Tenta inicialização com ADC (Application Default Credentials) ou apenas com projectId
            try:
                cred = credentials.ApplicationDefault()
                _app = firebase_admin.initialize_app(cred, {'projectId': FIREBASE_PROJECT_ID})
                logger.info("Firebase inicializado com Application Default Credentials.")
            except Exception:
                _app = firebase_admin.initialize_app(options={'projectId': FIREBASE_PROJECT_ID})
                logger.info(f"Firebase inicializado com projectId={FIREBASE_PROJECT_ID}.")
    except Exception as e:
        logger.error(f"Erro ao inicializar Firebase Admin SDK: {e}")
        # Se falhar tudo, tenta fallback com projectId
        if not firebase_admin._apps:
            _app = firebase_admin.initialize_app(options={'projectId': FIREBASE_PROJECT_ID})

    try:
        _db = firestore.client(app=_app)
    except Exception as db_err:
        logger.error(f"Erro ao obter cliente Firestore: {db_err}")
        _db = None

    return _app


def get_firestore_client():
    """Retorna o cliente do Cloud Firestore conectado ao projeto tccfeirascore."""
    global _db
    if _db is None:
        init_firebase()
        if _db is None:
            try:
                _db = firestore.client()
            except Exception as e:
                logger.error(f"Não foi possível obter o Firestore client: {e}")
    return _db

import os
import firebase_admin
from firebase_admin import credentials
from flask import Flask

def create_app():
    # Caminhos absolutos garantem que o Render encontre os templates e arquivos estáticos
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '..', 'templates')
    static_dir = os.path.join(base_dir, '..', 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key')

    # Inicialização segura do Firebase sem quebrar o servidor no Render
    try:
        if not firebase_admin._apps:
            json_path = os.path.join(base_dir, '..', 'serviceAccountKey.json')
            if os.path.exists(json_path):
                cred = credentials.Certificate(json_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
    except Exception as e:
        print(f"Atenção: Firebase não foi inicializado corretamente. Erro: {e}")

    # Registro das rotas / Blueprints
    from app.controllers.home_controller import home_bp
    from app.controllers.auth_controller import auth_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)

    return app
from app.config.firebase import init_firebase, get_firestore_client
from app.controllers.auth_controller import auth_bp
from app.controllers.project_controller import project_bp
from app.controllers.home_controller import home_bp

__all__ = [
    'init_firebase',
    'get_firestore_client',
    'auth_bp',
    'project_bp',
    'home_bp'
]

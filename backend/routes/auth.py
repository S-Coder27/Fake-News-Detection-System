from flask import Blueprint
from controllers.authController import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    return AuthController.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    return AuthController.login()

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user"""
    return AuthController.get_current_user()

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    return AuthController.update_profile()
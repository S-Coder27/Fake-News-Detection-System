from flask import Blueprint, request
from controllers.adminController import AdminController

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    return AdminController.get_all_users()

@admin_bp.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    """Delete user"""
    return AdminController.delete_user()

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    return AdminController.get_stats()

@admin_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get prediction logs"""
    return AdminController.get_prediction_logs()
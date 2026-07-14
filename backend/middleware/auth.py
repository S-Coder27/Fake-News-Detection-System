from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from bson import ObjectId
from config.db import db
import logging

logger = logging.getLogger(__name__)


def token_required(f):
    """Decorator to protect routes with JWT authentication"""

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()

            # Get user id from token
            current_user_id = get_jwt_identity()

            print("JWT User ID:", current_user_id)

            users = db.get_collection('users')

            # Convert string id to ObjectId
            try:
                user = users.find_one({
                    '_id': ObjectId(current_user_id)
                })
            except Exception:
                user = users.find_one({
                    '_id': current_user_id
                })

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 401

            # Store current user in request
            request.current_user = user

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")

            return jsonify({
                'success': False,
                'message': 'Invalid or expired token',
                'error': str(e)
            }), 401

    return decorated


def admin_required(f):
    """Decorator to restrict access to admin users only"""

    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        try:
            if not request.current_user.get('isAdmin', False):
                return jsonify({
                    'success': False,
                    'message': 'Admin access required'
                }), 403

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Admin authorization error: {str(e)}")

            return jsonify({
                'success': False,
                'message': 'Authorization failed',
                'error': str(e)
            }), 403

    return decorated
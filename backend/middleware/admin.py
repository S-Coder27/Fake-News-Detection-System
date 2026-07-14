from functools import wraps
from flask import request, jsonify
from config.db import db
import logging

logger = logging.getLogger(__name__)


def admin_only(f):
    """Alternative admin check decorator"""

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            user = request.current_user

            if not user or not user.get('isAdmin'):
                return jsonify({
                    'success': False,
                    'message': 'Admin privileges required'
                }), 403

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Admin check failed: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Authorization failed'
            }), 403

    return decorated
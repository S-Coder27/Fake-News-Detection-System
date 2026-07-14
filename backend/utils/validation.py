import re
from flask import jsonify


def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, None


def validate_required_fields(data, required_fields):
    """Validate that all required fields are present"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            missing_fields.append(field)

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None


def validation_error(message, fields=None):
    """Return validation error response"""
    response = {
        'success': False,
        'message': message,
        'errors': fields if fields else []
    }
    return response, 400
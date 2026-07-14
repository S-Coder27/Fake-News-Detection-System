from flask import jsonify

class AppError(Exception):
    """Custom application error class"""
    def __init__(self, message, statusCode):
        self.message = message
        self.statusCode = statusCode
        super().__init__(self.message)

def error_handler(error):
    """Global error handler"""
    return jsonify({
        'success': False,
        'message': str(error),
        'error': error.__class__.__name__
    }), getattr(error, 'statusCode', 500)

def not_found(error):
    """404 error handler"""
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

def internal_server_error(error):
    """500 error handler"""
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'error': str(error)
    }), 500
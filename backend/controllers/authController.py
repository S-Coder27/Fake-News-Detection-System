from flask import request, jsonify
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import Config
from config.db import db
from utils.validation import validate_email, validate_password, validate_required_fields
from middleware.auth import token_required
import logging

logger = logging.getLogger(__name__)


class AuthController:
    """Authentication controller"""

    @staticmethod
    def register():
        """Register a new user"""
        try:
            data = request.get_json()

            # Validate required fields
            is_valid, message = validate_required_fields(data, ['email', 'password', 'name'])
            if not is_valid:
                return jsonify({'success': False, 'message': message}), 400

            email = data['email'].strip().lower()
            password = data['password']
            name = data['name'].strip()

            # Validate email
            if not validate_email(email):
                return jsonify({'success': False, 'message': 'Invalid email format'}), 400

            # Validate password
            is_valid, message = validate_password(password)
            if not is_valid:
                return jsonify({'success': False, 'message': message}), 400

            users = db.get_collection('users')

            # Check if user already exists
            if users.find_one({'email': email}):
                return jsonify({'success': False, 'message': 'User already exists'}), 409

            # Create new user
            user_doc = {
                'email': email,
                'password': generate_password_hash(password),
                'name': name,
                'isAdmin': False,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }

            # Create first user as admin
            if users.count_documents({}) == 0:
                user_doc['isAdmin'] = True

            result = users.insert_one(user_doc)

            # Create access token
            access_token = create_access_token(identity=str(result.inserted_id))

            logger.info(f"User registered: {email}")

            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'token': access_token,
                    'user': {
                        'id': str(result.inserted_id),
                        'email': user_doc['email'],
                        'name': user_doc['name'],
                        'isAdmin': user_doc['isAdmin']
                    }
                }
            }), 201

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Registration failed',
                'error': str(e)
            }), 500

    @staticmethod
    def login():
        """User login"""
        try:
            data = request.get_json()

            # Validate required fields
            is_valid, message = validate_required_fields(data, ['email', 'password'])
            if not is_valid:
                return jsonify({'success': False, 'message': message}), 400

            email = data['email'].strip().lower()
            password = data['password']

            users = db.get_collection('users')
            user = users.find_one({'email': email})

            if not user or not check_password_hash(user['password'], password):
                return jsonify({
                    'success': False,
                    'message': 'Invalid email or password'
                }), 401

            # Create access token
            access_token = create_access_token(identity=str(user['_id']))

            # Update last login
            users.update_one(
                {'_id': user['_id']},
                {'$set': {'lastLogin': datetime.utcnow()}}
            )

            logger.info(f"User logged in: {email}")

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'token': access_token,
                    'user': {
                        'id': str(user['_id']),
                        'email': user['email'],
                        'name': user['name'],
                        'isAdmin': user.get('isAdmin', False)
                    }
                }
            }), 200

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Login failed',
                'error': str(e)
            }), 500

    @staticmethod
    @token_required
    def get_current_user():
        """Get current logged in user"""
        try:
            user = request.current_user

            return jsonify({
                'success': True,
                'data': {
                    'user': {
                        'id': str(user['_id']),
                        'email': user['email'],
                        'name': user['name'],
                        'isAdmin': user.get('isAdmin', False),
                        'createdAt': user['createdAt'].isoformat()
                    }
                }
            }), 200

        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to get user info',
                'error': str(e)
            }), 500

    @staticmethod
    @token_required
    def update_profile():
        """Update user profile"""
        try:
            data = request.get_json()
            user = request.current_user
            users = db.get_collection('users')

            allowed_updates = ['name']
            update_data = {}

            for field in allowed_updates:
                if field in data and data[field].strip():
                    update_data[field] = data[field].strip()

            if update_data:
                update_data['updatedAt'] = datetime.utcnow()
                users.update_one(
                    {'_id': user['_id']},
                    {'$set': update_data}
                )

                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'No valid fields to update'
                }), 400

        except Exception as e:
            logger.error(f"Update profile error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to update profile',
                'error': str(e)
            }), 500
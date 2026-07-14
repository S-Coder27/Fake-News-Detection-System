from flask import jsonify
from datetime import datetime
from pymongo import ASCENDING
from pymongo.errors import PyMongoError
from config.db import db
from middleware.auth import admin_required
import logging

logger = logging.getLogger(__name__)


class AdminController:
    """Admin controller for system management"""

    @staticmethod
    @admin_required
    def get_all_users():
        """Get all registered users"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))

            users = db.get_collection('users')

            # Get total count
            total = users.count_documents({})
            pages = (total + limit - 1) // limit

            # Get users with pagination
            cursor = users.find().sort('createdAt', -1).skip((page - 1) * limit).limit(limit)
            users_list = list(cursor)

            # Format response (exclude passwords)
            formatted_users = []
            for user in users_list:
                formatted_users.append({
                    'id': str(user['_id']),
                    'email': user['email'],
                    'name': user['name'],
                    'isAdmin': user.get('isAdmin', False),
                    'createdAt': user['createdAt'].isoformat(),
                    'lastLogin': user.get('lastLogin', '').isoformat() if user.get('lastLogin') else None
                })

            return jsonify({
                'success': True,
                'data': {
                    'users': formatted_users,
                    'total': total,
                    'page': page,
                    'pages': pages
                }
            }), 200

        except Exception as e:
            logger.error(f"Get users error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to get users',
                'error': str(e)
            }), 500

    @staticmethod
    @admin_required
    def delete_user():
        """Delete a user by ID"""
        try:
            from bson.objectid import ObjectId, InvalidId

            user_id = request.view_args.get('id')

            try:
                obj_id = ObjectId(user_id)
            except InvalidId:
                return jsonify({
                    'success': False,
                    'message': 'Invalid user ID'
                }), 400

            users = db.get_collection('users')
            current_user = request.current_user

            # Prevent admin from deleting themselves
            if str(obj_id) == str(current_user['_id']):
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete your own account'
                }), 400

            # Check if user exists
            user = users.find_one({'_id': obj_id})
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404

            # Delete user
            result = users.delete_one({'_id': obj_id})

            if result.deleted_count == 0:
                return jsonify({
                    'success': False,
                    'message': 'Failed to delete user'
                }), 404

            # Also delete user's predictions
            predictions = db.get_collection('predictions')
            predictions.delete_one({'userId': obj_id})

            logger.info(f"User deleted: {user['email']}")

            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            }), 200

        except Exception as e:
            logger.error(f"Delete user error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to delete user',
                'error': str(e)
            }), 500

    @staticmethod
    @admin_required
    def get_stats():
        """Get system analytics and statistics"""
        try:
            users = db.get_collection('users')
            predictions = db.get_collection('predictions')

            # Basic counts
            total_users = users.count_documents({})
            total_predictions = predictions.count_documents({})

            # Fake vs Real ratio
            fake_count = predictions.count_documents({'isFake': True})
            real_count = predictions.count_documents({'isFake': False})

            # Recent predictions (last 7 days)
            from datetime import datetime, timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_predictions = predictions.count_documents({
                'timestamp': {'$gte': week_ago}
            })

            # Monthly predictions (last 12 months)
            monthly_data = []
            for i in range(11, -1, -1):
                month_start = datetime.utcnow() - timedelta(days=30 * (i + 1))
                month_end = datetime.utcnow() - timedelta(days=30 * i)

                count = predictions.count_documents({
                    'timestamp': {
                        '$gte': month_start,
                        '$lt': month_end
                    }
                })

                monthly_data.append({
                    'month': month_start.strftime('%b %Y'),
                    'count': count
                })

            # Average confidence
            pipeline = [
                {'$group': {'_id': None, 'avgConfidence': {'$avg': '$confidence'}}}
            ]
            avg_result = list(predictions.aggregate(pipeline))
            avg_confidence = avg_result[0]['avgConfidence'] if avg_result and avg_result[0]['avgConfidence'] else 0

            # Top suspicious keywords
            pipeline = [
                {'$unwind': '$suspiciousKeywords'},
                {'$group': {'_id': '$suspiciousKeywords', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            top_keywords = list(predictions.aggregate(pipeline))

            return jsonify({
                'success': True,
                'data': {
                    'overview': {
                        'totalUsers': total_users,
                        'totalPredictions': total_predictions,
                        'fakeNews': fake_count,
                        'realNews': real_count,
                        'recentPredictions': recent_predictions,
                        'avgConfidence': round(avg_confidence, 2)
                    },
                    'fakeRealRatio': {
                        'fake': fake_count,
                        'real': real_count,
                        'fakePercentage': round((fake_count / total_predictions * 100) if total_predictions > 0 else 0,
                                                2),
                        'realPercentage': round((real_count / total_predictions * 100) if total_predictions > 0 else 0,
                                                2)
                    },
                    'monthlyPredictions': monthly_data,
                    'topKeywords': [{'keyword': k['_id'], 'count': k['count']} for k in top_keywords]
                }
            }), 200

        except Exception as e:
            logger.error(f"Get stats error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to get statistics',
                'error': str(e)
            }), 500

    @staticmethod
    @admin_required
    def get_prediction_logs():
        """Get all prediction logs"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))

            predictions = db.get_collection('predictions')

            total = predictions.count_documents({})
            pages = (total + limit - 1) // limit

            cursor = predictions.find().sort('timestamp', -1).skip((page - 1) * limit).limit(limit)
            logs = list(cursor)

            formatted_logs = []
            for log in logs:
                formatted_logs.append({
                    'id': str(log['_id']),
                    'userId': str(log.get('userId')) if log.get('userId') else None,
                    'headline': log.get('headline', '')[:100],
                    'result': log['result'],
                    'confidence': log['confidence'],
                    'timestamp': log['timestamp'].isoformat()
                })

            return jsonify({
                'success': True,
                'data': {
                    'logs': formatted_logs,
                    'total': total,
                    'page': page,
                    'pages': pages
                }
            }), 200

        except Exception as e:
            logger.error(f"Get logs error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to get logs',
                'error': str(e)
            }), 500
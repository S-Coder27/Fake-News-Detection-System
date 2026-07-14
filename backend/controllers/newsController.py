from flask import request, jsonify
from datetime import datetime
from pymongo.errors import PyMongoError
from config.db import db
from middleware.auth import token_required
import joblib
import logging
import re
import os
logger = logging.getLogger(__name__)


class NewsController:
    """News prediction controller"""

    # Load ML model and vectorizer
    @staticmethod
    def load_model():
        """Load trained ML model and vectorizer"""
        try:
            import os

            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)

            model_path = os.path.join(
                backend_dir,
                'ml-model',
                'models',
                'model.pkl'
            )

            vectorizer_path = os.path.join(
                backend_dir,
                'ml-model',
                'models',
                'vectorizer.pkl'
            )

            logger.info(f"Loading model from: {model_path}")
            logger.info(f"Loading vectorizer from: {vectorizer_path}")

            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)

            return model, vectorizer

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise


    @staticmethod
    def preprocess_text(text):
        """Preprocess text for prediction"""
        # Convert to lowercase
        text = text.lower()

        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def predict_news():
        """Predict if news is fake or real"""
        try:
            data = request.get_json()

            # Validate input
            if not data or 'text' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Text is required'
                }), 400

            headline = data.get('headline', '')
            text = data.get('text', '')

            if not text.strip():
                return jsonify({
                    'success': False,
                    'message': 'Article text is required'
                }), 400

            # Combine headline and text
            combined_text = f"{headline} {text}" if headline else text

            # Preprocess
            processed_text = NewsController.preprocess_text(combined_text)

            # Load model
            model, vectorizer = NewsController.load_model()

            # Vectorize
            vectorized = vectorizer.transform([processed_text])

            prediction = model.predict(vectorized)[0]

            prediction = int(model.predict(vectorized)[0])

            # Confidence using decision_function
            decision_score = abs(model.decision_function(vectorized)[0])

            confidence = min(99.0, float(50 + decision_score * 10))

            # Determine fake/real
            is_fake = bool(prediction == 0)
            result = 'Fake' if is_fake else 'Real'

            probability_score = round(confidence / 100, 4)

            # Extract suspicious keywords (simple heuristic)
            suspicious_keywords = NewsController._extract_suspicious_keywords(text)

            # Calculate credibility score
            credibility_score = 100 - confidence if is_fake else confidence

            # Save prediction to database
            user_id = None
            if hasattr(request, 'current_user'):
                user_id = request.current_user['_id']

            prediction_doc = {
                'userId': user_id,
                'headline': headline,
                'text': combined_text,
                'result': result,
                'isFake': is_fake,
                'confidence': round(confidence, 2),
                'probabilityScore': round(probability_score, 4),
                'credibilityScore': round(credibility_score, 2),
                'suspiciousKeywords': suspicious_keywords,
                'timestamp': datetime.utcnow()
            }

            predictions = db.get_collection('predictions')
            result_id = predictions.insert_one(prediction_doc).inserted_id

            logger.info(f"Prediction made: {result} with {confidence:.2f}% confidence")

            return jsonify({
                'success': True,
                'message': 'Prediction completed successfully',
                'data': {
                    'id': str(result_id),
                    'result': result,
                    'isFake': bool(is_fake),
                    'confidence': round(confidence, 2),
                    'probabilityScore': round(probability_score, 4),
                    'credibilityScore': round(credibility_score, 2),
                    'suspiciousKeywords': suspicious_keywords,
                    'explanation': NewsController._generate_explanation(result, confidence, suspicious_keywords)
                }
            }), 200

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Prediction failed',
                'error': str(e)
            }), 500

    @staticmethod
    def _extract_suspicious_keywords(text):
        """Extract potentially suspicious keywords from text"""
        suspicious_words = [
            'shocking', 'breaking', 'exclusive', 'miracle', 'secret',
            'hidden', 'revealed', 'truth', 'conspiracy', 'cover-up', 'scandal', 'outrageous', 'incredible', 'unbelievable',
            'minus signs', 'censored', 'they dont want you to know'
        ]

        text_lower = text.lower()
        found_keywords = [word for word in suspicious_words if word in text_lower]

        return found_keywords[:5]  # Return top 5

    @staticmethod
    def _generate_explanation(result, confidence, keywords):
        """Generate explanation for prediction"""
        if result == 'Fake':
            explanation = f"This article is predicted as FAKE with {confidence:.1f}% confidence. "
            if keywords:
                explanation += f"Suspicious keywords detected: {', '.join(keywords)}. "
            explanation += "The writing style, tone, and content patterns are consistent with known fake news characteristics."
        else:
            explanation = f"This article is predicted as REAL with {confidence:.1f}% confidence. "
            explanation += "The writing follows standard journalistic practices with verifiable information and neutral tone."

        return explanation

    @staticmethod
    @token_required
    def get_history():
        """Get prediction history for current user"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            search = request.args.get('search', '').lower()
            filter_result = request.args.get('filter', '')  # 'fake' or 'real'

            predictions = db.get_collection('predictions')
            user_id = request.current_user['_id']

            # Build query
            query = {}
            if user_id:
                query['userId'] = user_id
            else:
                # For non-authenticated users, return empty
                return jsonify({
                    'success': True,
                    'data': {
                        'predictions': [],
                        'total': 0,
                        'page': page,
                        'pages': 0
                    }
                }), 200

            if search:
                query['$or'] = [
                    {'headline': {'$regex': search, '$options': 'i'}},
                    {'text': {'$regex': search, '$options': 'i'}}
                ]

            if filter_result:
                query['result'] = filter_result.capitalize()

            # Get total count
            total = predictions.count_documents(query)
            pages = (total + limit - 1) // limit

            # Get predictions with pagination
            cursor = predictions.find(query).sort('timestamp', -1).skip((page - 1) * limit).limit(limit)
            predictions_list = list(cursor)

            # Format response
            formatted_predictions = []
            for pred in predictions_list:
                formatted_predictions.append({
                    'id': str(pred['_id']),
                    'headline': pred.get('headline', '')[:100],
                    'result': pred['result'],
                    'isFake': pred['isFake'],
                    'confidence': pred['confidence'],
                    'credibilityScore': pred['credibilityScore'],
                    'timestamp': pred['timestamp'].isoformat()
                })

            return jsonify({
                'success': True,
                'data': {
                    'predictions': formatted_predictions,
                    'total': total,
                    'page': page,
                    'pages': pages
                }
            }), 200

        except Exception as e:
            logger.error(f"Get history error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to get history',
                'error': str(e)
            }), 500

    @staticmethod
    @token_required
    def delete_prediction():
        """Delete a prediction by ID"""
        try:
            prediction_id = request.view_args.get('id')

            from bson.objectid import ObjectId, InvalidId

            try:
                obj_id = ObjectId(prediction_id)
            except InvalidId:
                return jsonify({
                    'success': False,
                    'message': 'Invalid prediction ID'
                }), 400

            predictions = db.get_collection('predictions')
            user_id = request.current_user['_id']

            # Find and delete (only if belongs to user)
            result = predictions.delete_one({
                '_id': obj_id,
                'userId': user_id
            })

            if result.deleted_count == 0:
                return jsonify({
                    'success': False,
                    'message': 'Prediction not found or unauthorized'
                }), 404

            logger.info(f"Prediction deleted: {prediction_id}")

            return jsonify({
                'success': True,
                'message': 'Prediction deleted successfully'
            }), 200

        except Exception as e:
            logger.error(f"Delete prediction error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to delete prediction',
                'error': str(e)
            }), 500
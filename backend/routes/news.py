from flask import Blueprint
from controllers.newsController import NewsController
from middleware.auth import token_required

news_bp = Blueprint(
    'news',
    __name__,
    url_prefix='/api/news'
)

# Predict News (Login Required)
@news_bp.route('/predict', methods=['POST'])
@token_required
def predict():
    return NewsController.predict_news()


# Get Prediction History
@news_bp.route('/history', methods=['GET'])
@token_required
def get_history():
    return NewsController.get_history()


# Delete Prediction
@news_bp.route('/delete/<id>', methods=['DELETE'])
@token_required
def delete_prediction(id):
    return NewsController.delete_prediction()
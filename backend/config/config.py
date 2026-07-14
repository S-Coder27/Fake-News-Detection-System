from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb://localhost:27017/fake-news-db'
    )

    JWT_SECRET = os.getenv(
        'JWT_SECRET',
        'your-super-secret-jwt-key-change-in-production'
    )

    # FIXED
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    PORT = int(os.getenv('PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    MODEL_PATH = os.getenv('MODEL_PATH', 'models/model.pkl')
    VECTORIZER_PATH = os.getenv('VECTORIZER_PATH', 'models/vectorizer.pkl')
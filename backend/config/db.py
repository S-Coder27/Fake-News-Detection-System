from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config.config import Config
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager"""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Establish database connection"""
        try:
            if self._client is None:
                self._client = MongoClient(
                    Config.MONGODB_URI,
                    serverSelectionTimeoutMS=5000,
                    connect=True
                )
                # Test connection
                self._client.admin.command('ping')
                self._db = self._client.get_database()
                logger.info("Successfully connected to MongoDB")
            return self._db
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionFailure(f"Database connection failed: {str(e)}")

    def get_collection(self, collection_name):
        """Get a collection from the database"""
        db = self.connect()
        return db[collection_name]

    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")


# Global database instance
db = Database()
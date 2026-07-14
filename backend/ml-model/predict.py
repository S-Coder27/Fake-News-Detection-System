#!/usr/bin/env python3
"""
Prediction script for trained model
"""

import joblib
import re
import sys
import os


class NewsPredictor:
    """Predict fake news using trained model"""

    def __init__(self, model_path='models/model.pkl', vectorizer_path='models/vectorizer.pkl'):
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)

    def preprocess_text(self, text):
        """Preprocess text"""
        text = text.lower()
        text = re.sub(r'http\S+|www.\S+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
        words = text.split()
        words = [w for w in words if w not in stopwords]

        return ' '.join(words)

    def predict(self, headline, text):
        """Predict if news is fake or real"""
        combined = f"{headline} {text}" if headline else text
        processed = self.preprocess_text(combined)

        vectorized = self.vectorizer.transform([processed])
        prediction = self.model.predict(vectorized)[0]
        probability = self.model.predict_proba(vectorized)[0]

        result = 'Fake' if prediction == 0 else 'Real'
        confidence = max(probability) * 100

        return {
            'result': result,
            'isFake': prediction == 0,
            'confidence': confidence,
            'probability': probability.tolist()
        }


def main():
    """Test prediction"""
    predictor = NewsPredictor()

    # Test case 1
    headline = "Breaking: Shocking Discovery Revealed"
    text = "This is a shocking exclusive story that they don't want you to know about."

    result = predictor.predict(headline, text)
    print(f"\nTest 1:")
    print(f"Result: {result['result']}")
    print(f"Confidence: {result['confidence']:.2f}%")

    # Test case 2
    headline = "Science Report: New Study Published"
    text = "Researchers published a peer-reviewed study in a scientific journal."

    result = predictor.predict(headline, text)
    print(f"\nTest 2:")
    print(f"Result: {result['result']}")
    print(f"Confidence: {result['confidence']:.2f}%")


if __name__ == '__main__':
    main()
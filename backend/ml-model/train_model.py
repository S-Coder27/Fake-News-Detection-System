#!/usr/bin/env python3
"""
Fake News Detection Model Training Script
Uses TF-IDF Vectorizer and PassiveAggressiveClassifier
"""

import pandas as pd
import numpy as np
import re
import joblib
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NewsPreprocessor:
    """Text preprocessing for news articles"""

    @staticmethod
    def clean_text(text):
        """Clean and preprocess text"""
        if pd.isna(text):
            return ""

        # Convert to string
        text = str(text).lower()

        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)

        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def remove_stopwords(text):
        """Remove common stopwords (simple implementation)"""
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'also'
        }

        words = text.split()
        filtered_words = [word for word in words if word not in stopwords]

        return ' '.join(filtered_words)


class FakeNewsTrainer:
    """Training pipeline for fake news detection"""

    def __init__(self, data_dir='dataset', model_dir='models'):
        self.data_dir = data_dir
        self.model_dir = model_dir

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)

        self.preprocessor = NewsPreprocessor()
        self.vectorizer = None
        self.model = None

    def load_datasets(self):
        """Load fake and true news datasets"""
        print("=" * 60)
        print("LOADING DATASETS")
        print("=" * 60)

        fake_path = os.path.join(self.data_dir, 'Fake.csv')
        true_path = os.path.join(self.data_dir, 'True.csv')

        try:
            # Load datasets
            fake_df = pd.read_csv(fake_path)
            true_df = pd.read_csv(true_path)

            print(f"✓ Loaded {len(fake_df)} fake news articles")
            print(f"✓ Loaded {len(true_df)} real news articles")

            # Add labels
            fake_df['label'] = 0  # 0 = Fake
            true_df['label'] = 1  # 1 = Real

            # Combine datasets
            df = pd.concat([fake_df, true_df], ignore_index=True)

            print(f"✓ Total articles: {len(df)}")
            print(f"✓ Label distribution: Fake={sum(df['label'] == 0)}, Real={sum(df['label'] == 1)}")

            return df

        except FileNotFoundError as e:
            print(f"✗ Error: Dataset file not found - {e}")
            print("\nPlease download datasets from Kaggle:")
            print("  - https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset")
            print("\nPlace Fake.csv and True.csv in the 'dataset/' folder")
            sys.exit(1)

    def preprocess_data(self, df):
        """Preprocess the data"""
        print("\n" + "=" * 60)
        print("PREPROCESSING DATA")
        print("=" * 60)

        # Clean text
        print("Cleaning text...")
        df['cleaned_text'] = df['text'].apply(self.preprocessor.clean_text)

        # Remove stopwords
        print("Removing stopwords...")
        df['cleaned_text'] = df['cleaned_text'].apply(self.preprocessor.remove_stopwords)

        # Combine title and text
        df['combined'] = df['title'].fillna('') + ' ' + df['cleaned_text']

        # Remove empty entries
        df = df[df['combined'].str.len() > 0]

        print(f"✓ Preprocessed {len(df)} articles")

        return df

    def train_model(self, df):
        """Train the ML model"""
        print("\n" + "=" * 60)
        print("TRAINING MODEL")
        print("=" * 60)

        # Split data
        X = df['combined']
        y = df['label']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"✓ Training set: {len(X_train)} articles")
        print(f"✓ Testing set: {len(X_test)} articles")

        # TF-IDF Vectorization
        print("\nApplying TF-IDF Vectorization...")
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_df=0.8,
            min_df=2,
            ngram_range=(1, 4),
            max_features=50000
        )

        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)

        print(f"✓ Vocab size: {len(self.vectorizer.vocabulary_)}")
        print(f"✓ TF-IDF shape: {X_train_tfidf.shape}")

        self.model = LogisticRegression(
            max_iter=5000,
            random_state=42
        )

        self.model.fit(X_train_tfidf, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)

        print("\n" + "=" * 60)
        print("MODEL EVALUATION")
        print("=" * 60)
        print(f"✓ Accuracy: {accuracy * 100:.2f}%")
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Fake', 'Real']))

        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)

        return cm, accuracy

    def save_model(self):
        """Save trained model and vectorizer"""
        print("\n" + "=" * 60)
        print("SAVING MODEL")
        print("=" * 60)

        model_path = os.path.join(self.model_dir, 'model.pkl')
        vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')

        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)

        print(f"✓ Model saved to: {model_path}")
        print(f"✓ Vectorizer saved to: {vectorizer_path}")

    def plot_confusion_matrix(self, cm):
        """Plot and save confusion matrix"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Fake', 'Real'],
                    yticklabels=['Fake', 'Real'])
        plt.title('Confusion Matrix')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
        print("✓ Confusion matrix saved to: confusion_matrix.png")

    def run_training(self):
        """Run complete training pipeline"""
        print("\n" + "=" * 60)
        print("FAKE NEWS DETECTION MODEL TRAINING")
        print("=" * 60)

        # Load data
        df = self.load_datasets()

        # Preprocess
        df = self.preprocess_data(df)

        # Train
        cm, accuracy = self.train_model(df)

        # Plot confusion matrix
        self.plot_confusion_matrix(cm)

        # Save model
        self.save_model()

        print("\n" + "=" * 60)
        print(f"TRAINING COMPLETE! Accuracy: {accuracy * 100:.2f}%")
        print("=" * 60)
        print("\nModel files saved to 'models/' directory")
        print("Copy these files to backend/models/ folder")


def main():
    """Main function"""
    trainer = FakeNewsTrainer()
    trainer.run_training()


if __name__ == '__main__':
    main()
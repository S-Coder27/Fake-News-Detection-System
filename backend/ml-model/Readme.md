# Machine Learning Model - Fake News Detection

## Overview
This module contains the ML training pipeline for detecting fake news using TF-IDF vectorization and PassiveAggressiveClassifier.

## Dataset
- **Source**: ISOT Fake News Dataset
- **Files**: `Fake.csv`, `True.csv`
- **Download**: https://www.kaggle.com/datasets/clmentbisaillon/fake-

news-dataset

## Training Pipeline

1. **Data Loading**: Load Fake.csv and True.csv
2. **Preprocessing**: Clean text, remove stopwords
3. **Vectorization**: TF-IDF (1-4 n-grams)
4. **Training**: PassiveAggressiveClassifier
5. **Evaluation**: Accuracy, Classification Report
6. **Saving**: Save model and vectorizer

## Usage

### Train Model
```bash
python train_model.py
```

### Make Predictions
```bash
python predict.py
```

## Output Files
- `models/model.pkl` - Trained model
- `models/vectorizer.pkl` - TF-IDF vectorizer
- `confusion_matrix.png` - Evaluation visualization

## Model Performance
- **Accuracy**: ~93%
- **Algorithm**: PassiveAggressiveClassifier
- **Vectorization**: TF-IDF (max_features=50000, ngram_range=(1,4))
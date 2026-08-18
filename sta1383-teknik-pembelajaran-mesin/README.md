# MyBCA Sentiment Analysis

A machine-learning project for classifying sentiment in Indonesian-language reviews of the MyBCA mobile-banking application.

## Objective

Compare text representations and KNN-based classifiers to determine which combination provides the strongest sentiment-classification performance.

## Methods

- Indonesian text preprocessing and normalization.
- TF-IDF feature extraction.
- FastText word embeddings.
- Hybrid FastText + TF-IDF representation.
- Chi-square feature selection.
- K-Nearest Neighbors (KNN).
- Fuzzy K-Nearest Neighbors (FKNN) variants.
- Stratified cross-validation for model evaluation.

## Key Result

The accompanying report found the best performance using **Hybrid FastText-TF-IDF with KNN**, reaching **93.56% accuracy** with cosine distance and **K = 17**. The hybrid representation consistently performed slightly better than standalone FastText.

## Files

| File | Description |
|---|---|
| [`mybca-sentiment-analysis.ipynb`](mybca-sentiment-analysis.ipynb) | Main preprocessing, feature extraction, model comparison, and optimization notebook. |
| [`mybca.xlsx`](mybca.xlsx) | Labeled MyBCA review dataset containing positive and negative sentiment classes. |
| [`mybca-sentiment-analysis-knn-fasttext-tfidf.pdf`](mybca-sentiment-analysis-knn-fasttext-tfidf.pdf) | Full project report. |

## Reproducibility Note

The notebook preserves the original Kaggle setup and contains Kaggle-specific dataset paths. Update the input path when running from a local clone.

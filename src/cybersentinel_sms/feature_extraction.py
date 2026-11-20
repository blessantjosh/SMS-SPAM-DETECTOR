"""
Feature Extraction for SMS Fraud Detection
Combines word-level and character-level TF-IDF features
"""
import numpy as np
import logging
from typing import Tuple, Optional
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSFeatureExtractor:
    """
    Extract TF-IDF features from SMS text
    Combines word-level and character-level features for robust representation
    """

    def __init__(self, use_char_features: bool = True):
        """
        Initialize feature extractor

        Args:
            use_char_features: Whether to include character-level features
        """
        self.use_char_features = use_char_features

        # Word-level TF-IDF vectorizer
        self.word_vectorizer = TfidfVectorizer(
            **Config.TFIDF_WORD_CONFIG
        )

        # Character-level TF-IDF vectorizer
        if self.use_char_features:
            self.char_vectorizer = TfidfVectorizer(
                **Config.TFIDF_CHAR_CONFIG
            )
        else:
            self.char_vectorizer = None

        self.is_fitted = False

    def fit(self, texts):
        """
        Fit vectorizers on training texts

        CRITICAL: Only call this on training data to prevent data leakage

        Args:
            texts: Array-like of text strings (training data only)

        Returns:
            self
        """
        logger.info("Fitting feature extractors on training data...")

        # Fit word-level vectorizer
        logger.info(f"  Fitting word-level TF-IDF (max_features={Config.TFIDF_WORD_CONFIG['max_features']})...")
        self.word_vectorizer.fit(texts)
        word_vocab_size = len(self.word_vectorizer.vocabulary_)
        logger.info(f"    Word vocabulary size: {word_vocab_size}")

        # Fit character-level vectorizer
        if self.use_char_features:
            logger.info(f"  Fitting char-level TF-IDF (max_features={Config.TFIDF_CHAR_CONFIG['max_features']})...")
            self.char_vectorizer.fit(texts)
            char_vocab_size = len(self.char_vectorizer.vocabulary_)
            logger.info(f"    Char vocabulary size: {char_vocab_size}")
            total_features = word_vocab_size + char_vocab_size
        else:
            total_features = word_vocab_size

        self.is_fitted = True
        logger.info(f"✓ Feature extraction ready: {total_features} total features")

        return self

    def transform(self, texts) -> csr_matrix:
        """
        Transform texts to feature vectors

        Args:
            texts: Array-like of text strings

        Returns:
            Sparse feature matrix

        Raises:
            ValueError: If called before fit()
        """
        if not self.is_fitted:
            raise ValueError("Feature extractor must be fitted before transform. Call fit() first.")

        # Word-level features
        word_features = self.word_vectorizer.transform(texts)

        # Character-level features
        if self.use_char_features:
            char_features = self.char_vectorizer.transform(texts)
            # Combine features
            combined_features = hstack([word_features, char_features])
        else:
            combined_features = word_features

        return combined_features

    def fit_transform(self, texts) -> csr_matrix:
        """
        Fit vectorizers and transform texts in one step

        CRITICAL: Only use on training data

        Args:
            texts: Array-like of text strings (training data only)

        Returns:
            Sparse feature matrix
        """
        self.fit(texts)
        return self.transform(texts)

    def get_feature_names(self) -> list:
        """
        Get list of all feature names

        Returns:
            List of feature names
        """
        if not self.is_fitted:
            raise ValueError("Feature extractor must be fitted first")

        word_features = self.word_vectorizer.get_feature_names_out().tolist()

        if self.use_char_features:
            char_features = [
                f"char_{feat}" for feat in self.char_vectorizer.get_feature_names_out()
            ]
            return word_features + char_features
        else:
            return word_features

    def get_feature_count(self) -> int:
        """
        Get total number of features

        Returns:
            Feature count
        """
        if not self.is_fitted:
            raise ValueError("Feature extractor must be fitted first")

        word_count = len(self.word_vectorizer.vocabulary_)

        if self.use_char_features:
            char_count = len(self.char_vectorizer.vocabulary_)
            return word_count + char_count
        else:
            return word_count

    def get_top_features_by_importance(self, feature_importance: np.ndarray,
                                       top_n: int = 20) -> list:
        """
        Get top N features by importance scores

        Args:
            feature_importance: Array of feature importance scores
            top_n: Number of top features to return

        Returns:
            List of (feature_name, importance) tuples
        """
        if not self.is_fitted:
            raise ValueError("Feature extractor must be fitted first")

        feature_names = self.get_feature_names()

        if len(feature_importance) != len(feature_names):
            raise ValueError(
                f"Feature importance length ({len(feature_importance)}) "
                f"doesn't match feature count ({len(feature_names)})"
            )

        # Get indices of top features
        top_indices = np.argsort(np.abs(feature_importance))[-top_n:][::-1]

        # Get feature names and importance
        top_features = [
            (feature_names[idx], feature_importance[idx])
            for idx in top_indices
        ]

        return top_features


class SimpleTfidfExtractor:
    """
    Simplified feature extractor using only word-level TF-IDF
    Useful for quick experiments or when character features aren't needed
    """

    def __init__(self, max_features: int = 3000, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize simple extractor

        Args:
            max_features: Maximum number of features
            ngram_range: N-gram range (default: unigrams and bigrams)
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=2,
            sublinear_tf=True,
            strip_accents=None,
            lowercase=True
        )
        self.is_fitted = False

    def fit(self, texts):
        """Fit vectorizer on texts"""
        self.vectorizer.fit(texts)
        self.is_fitted = True
        return self

    def transform(self, texts):
        """Transform texts to features"""
        if not self.is_fitted:
            raise ValueError("Must call fit() before transform()")
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts):
        """Fit and transform"""
        return self.vectorizer.fit_transform(texts)

    def get_feature_names(self):
        """Get feature names"""
        return self.vectorizer.get_feature_names_out().tolist()

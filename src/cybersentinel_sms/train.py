"""
Model Training Module
Train individual ML models for SMS fraud detection
"""
import logging
import time
from typing import Dict, Any
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
import lightgbm as lgb

from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and manage SMS fraud detection models"""

    @staticmethod
    def create_logistic_regression() -> LogisticRegression:
        """
        Create Logistic Regression model with balanced class weights

        Returns:
            Configured LogisticRegression model
        """
        return LogisticRegression(**Config.LOGISTIC_REGRESSION_CONFIG)

    @staticmethod
    def create_linear_svm() -> LinearSVC:
        """
        Create Linear SVM model with balanced class weights

        Returns:
            Configured LinearSVC model
        """
        return LinearSVC(**Config.LINEAR_SVM_CONFIG)

    @staticmethod
    def create_lightgbm() -> lgb.LGBMClassifier:
        """
        Create LightGBM model with balanced class weights

        Returns:
            Configured LGBMClassifier model
        """
        return lgb.LGBMClassifier(**Config.LIGHTGBM_CONFIG)

    @staticmethod
    def get_model_by_name(model_name: str):
        """
        Get model instance by name

        Args:
            model_name: One of ['logistic_regression', 'linear_svm', 'lightgbm']

        Returns:
            Configured model instance

        Raises:
            ValueError: If model_name is not recognized
        """
        models = {
            'logistic_regression': ModelTrainer.create_logistic_regression,
            'linear_svm': ModelTrainer.create_linear_svm,
            'lightgbm': ModelTrainer.create_lightgbm
        }

        if model_name not in models:
            raise ValueError(
                f"Unknown model name: {model_name}. "
                f"Valid options: {list(models.keys())}"
            )

        return models[model_name]()

    @staticmethod
    def train_model(model, X_train, y_train, model_name: str = "model") -> Dict[str, Any]:
        """
        Train a model and return training metadata

        Args:
            model: Sklearn-compatible model instance
            X_train: Training features
            y_train: Training labels
            model_name: Name for logging

        Returns:
            Dictionary with training metadata
        """
        logger.info(f"Training {model_name}...")
        start_time = time.time()

        try:
            model.fit(X_train, y_train)
            training_time = time.time() - start_time

            logger.info(f"✓ {model_name} trained in {training_time:.2f} seconds")

            metadata = {
                "model_name": model_name,
                "training_time": training_time,
                "n_training_samples": len(y_train),
                "training_success": True
            }

            return metadata

        except Exception as e:
            training_time = time.time() - start_time
            logger.error(f"✗ Failed to train {model_name}: {e}")

            metadata = {
                "model_name": model_name,
                "training_time": training_time,
                "training_success": False,
                "error": str(e)
            }

            raise

    @staticmethod
    def get_model_info(model) -> Dict[str, Any]:
        """
        Extract model information and parameters

        Args:
            model: Trained model

        Returns:
            Dictionary with model information
        """
        model_type = type(model).__name__

        info = {
            "model_type": model_type,
            "model_class": str(type(model)),
        }

        # Extract parameters
        if hasattr(model, 'get_params'):
            info["parameters"] = model.get_params()

        # Extract feature importance (if available)
        if hasattr(model, 'coef_'):
            info["has_coefficients"] = True
            info["n_features"] = model.coef_.shape[1] if len(model.coef_.shape) > 1 else len(model.coef_)
        elif hasattr(model, 'feature_importances_'):
            info["has_feature_importances"] = True
            info["n_features"] = len(model.feature_importances_)

        return info


def train_all_models(X_train, y_train) -> Dict[str, Any]:
    """
    Train all three candidate models

    Args:
        X_train: Training features
        y_train: Training labels

    Returns:
        Dictionary mapping model names to trained models
    """
    logger.info("=" * 70)
    logger.info("TRAINING ALL MODELS")
    logger.info("=" * 70)

    trainer = ModelTrainer()
    models = {}
    metadata = {}

    model_names = ['logistic_regression', 'linear_svm', 'lightgbm']

    for model_name in model_names:
        try:
            model = trainer.get_model_by_name(model_name)
            train_metadata = trainer.train_model(model, X_train, y_train, model_name)

            models[model_name] = model
            metadata[model_name] = train_metadata

        except Exception as e:
            logger.error(f"Failed to train {model_name}: {e}")
            models[model_name] = None
            metadata[model_name] = {"error": str(e)}

    logger.info(f"\n✓ Training complete: {len([m for m in models.values() if m is not None])}/{len(model_names)} models succeeded")

    return {"models": models, "metadata": metadata}

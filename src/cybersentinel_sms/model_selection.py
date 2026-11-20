"""
Model Selection Module
Select best model based on cross-validation results
"""
import pandas as pd
import numpy as np
import logging
import joblib
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelSelector:
    """Select and save best model"""

    @staticmethod
    def select_best_model(cv_results: Dict[str, Dict],
                         test_results: Optional[Dict[str, Dict]] = None,
                         selection_metric: str = 'val_macro_f1',
                         stability_weight: float = 0.3) -> Tuple[str, Dict]:
        """
        Select best model based on validation performance and stability

        Args:
            cv_results: Cross-validation results for each model
            test_results: Optional test results (not used for selection, only reporting)
            selection_metric: Primary metric for selection (default: val_macro_f1)
            stability_weight: Weight for stability (lower std = better)

        Returns:
            Tuple of (best_model_name, selection_details)
        """
        logger.info("\n" + "=" * 70)
        logger.info("MODEL SELECTION")
        logger.info("=" * 70)

        scores = {}

        for model_name, results in cv_results.items():
            val_mean = results['val_mean']
            val_std = results['val_std']

            # Primary metric
            if selection_metric == 'val_macro_f1':
                primary_score = val_mean['macro_f1']
                stability_penalty = val_std['macro_f1_std']
            elif selection_metric == 'val_f1_scam':
                primary_score = val_mean['f1_scam']
                stability_penalty = val_std['f1_scam_std']
            else:
                primary_score = val_mean.get(selection_metric.replace('val_', ''), 0)
                stability_penalty = 0

            # Combined score: primary - (stability_weight * std)
            combined_score = primary_score - (stability_weight * stability_penalty)

            scores[model_name] = {
                'primary_score': primary_score,
                'stability_penalty': stability_penalty,
                'combined_score': combined_score,
                'val_f1_scam': val_mean['f1_scam'],
                'val_recall_scam': val_mean['recall_scam'],
                'val_precision_scam': val_mean['precision_scam'],
                'val_f1_ham': val_mean['f1_ham'],
                'val_recall_ham': val_mean['recall_ham'],
                'val_macro_f1': val_mean['macro_f1'],
                'val_accuracy': val_mean['accuracy']
            }

        # Find best model
        best_model_name = max(scores.keys(), key=lambda k: scores[k]['combined_score'])
        best_scores = scores[best_model_name]

        logger.info(f"\nModel Scores ({selection_metric}):")
        for model_name, score_info in sorted(scores.items(),
                                             key=lambda x: x[1]['combined_score'],
                                             reverse=True):
            logger.info(
                f"  {model_name:20s}: "
                f"Primary={score_info['primary_score']:.3f}, "
                f"Stability={score_info['stability_penalty']:.3f}, "
                f"Combined={score_info['combined_score']:.3f}"
            )

        logger.info(f"\n{'=' * 70}")
        logger.info(f"SELECTED MODEL: {best_model_name.upper()}")
        logger.info(f"{'=' * 70}")
        logger.info(f"Selection Criteria:")
        logger.info(f"  Primary Metric ({selection_metric}): {best_scores['primary_score']:.3f}")
        logger.info(f"  Stability Penalty: {best_scores['stability_penalty']:.3f}")
        logger.info(f"  Combined Score: {best_scores['combined_score']:.3f}")

        logger.info(f"\nValidation Performance:")
        logger.info(f"  F1 (Scam): {best_scores['val_f1_scam']:.3f}")
        logger.info(f"  F1 (Ham): {best_scores['val_f1_ham']:.3f}")
        logger.info(f"  Macro F1: {best_scores['val_macro_f1']:.3f}")
        logger.info(f"  Accuracy: {best_scores['val_accuracy']:.3f}")

        # If test results available, show them (but don't use for selection)
        if test_results and best_model_name in test_results:
            test_metrics = test_results[best_model_name]['metrics']
            logger.info(f"\nTest Set Performance (reference only):")
            logger.info(f"  F1 (Scam): {test_metrics['f1_scam']:.3f}")
            logger.info(f"  F1 (Ham): {test_metrics['f1_ham']:.3f}")
            logger.info(f"  Macro F1: {test_metrics['macro_f1']:.3f}")
            logger.info(f"  Accuracy: {test_metrics['accuracy']:.3f}")

        selection_details = {
            'selected_model': best_model_name,
            'selection_metric': selection_metric,
            'stability_weight': stability_weight,
            'all_scores': scores,
            'best_scores': best_scores
        }

        return best_model_name, selection_details

    @staticmethod
    def save_model_bundle(model, feature_extractor, model_name: str,
                         metadata: Dict[str, Any],
                         output_dir: Path = None) -> Path:
        """
        Save complete model bundle

        Args:
            model: Trained model
            feature_extractor: Fitted feature extractor
            model_name: Name of the model
            metadata: Training and selection metadata
            output_dir: Output directory (default: Config.TRAINED_MODELS_DIR)

        Returns:
            Path to saved bundle
        """
        output_dir = output_dir or Config.TRAINED_MODELS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_filename = f"{model_name}_{timestamp}.joblib"
        bundle_path = output_dir / bundle_filename

        bundle = {
            'model': model,
            'feature_extractor': feature_extractor,
            'model_name': model_name,
            'metadata': metadata,
            'config': {
                'random_seed': Config.RANDOM_SEED,
                'tfidf_word_config': Config.TFIDF_WORD_CONFIG,
                'tfidf_char_config': Config.TFIDF_CHAR_CONFIG,
                'target_column': Config.TARGET_COLUMN,
                'text_column': Config.TEXT_COLUMN,
                'label_scam': Config.LABEL_SCAM,
                'label_ham': Config.LABEL_HAM
            },
            'saved_at': timestamp,
            'version': '1.0.0'
        }

        joblib.dump(bundle, bundle_path)
        logger.info(f"\n✓ Model bundle saved to: {bundle_path}")

        # Also save with a "latest" name for easy loading
        latest_path = output_dir / f"{model_name}_latest.joblib"
        joblib.dump(bundle, latest_path)
        logger.info(f"✓ Latest model saved to: {latest_path}")

        # Save metadata separately as JSON for easy inspection
        import json
        metadata_path = output_dir / f"{model_name}_{timestamp}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✓ Metadata saved to: {metadata_path}")

        return bundle_path

    @staticmethod
    def load_model_bundle(bundle_path: Path) -> Dict[str, Any]:
        """
        Load model bundle

        Args:
            bundle_path: Path to saved bundle

        Returns:
            Model bundle dictionary
        """
        if not bundle_path.exists():
            raise FileNotFoundError(f"Model bundle not found: {bundle_path}")

        bundle = joblib.load(bundle_path)
        logger.info(f"✓ Loaded model bundle from: {bundle_path}")
        logger.info(f"  Model: {bundle['model_name']}")
        logger.info(f"  Saved at: {bundle['saved_at']}")

        return bundle

    @staticmethod
    def load_latest_model(model_name: str, models_dir: Path = None) -> Dict[str, Any]:
        """
        Load the latest version of a model

        Args:
            model_name: Name of the model
            models_dir: Models directory (default: Config.TRAINED_MODELS_DIR)

        Returns:
            Model bundle dictionary
        """
        models_dir = models_dir or Config.TRAINED_MODELS_DIR
        latest_path = models_dir / f"{model_name}_latest.joblib"

        return ModelSelector.load_model_bundle(latest_path)

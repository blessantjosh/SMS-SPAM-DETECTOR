"""
Grouped Cross-Validation Module
Prevent template leakage using StratifiedGroupKFold
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)

from .config import Config
from .feature_extraction import SMSFeatureExtractor
from .train import ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroupedCrossValidator:
    """
    Perform grouped cross-validation to prevent template leakage
    """

    def __init__(self, n_splits: int = 4, random_state: int = 42):
        """
        Initialize cross-validator

        Args:
            n_splits: Number of CV folds
            random_state: Random seed for reproducibility
        """
        self.n_splits = n_splits
        self.random_state = random_state
        self.cv_splitter = StratifiedGroupKFold(
            n_splits=n_splits,
            shuffle=True,
            random_state=random_state
        )

    def calculate_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """
        Calculate comprehensive evaluation metrics

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary of metrics
        """
        # Accuracy
        accuracy = accuracy_score(y_true, y_pred)

        # Precision, Recall, F1 for each class
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average=None, labels=[Config.LABEL_SCAM, Config.LABEL_HAM]
        )

        # Macro and weighted averages
        macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='macro'
        )

        weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted'
        )

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=[Config.LABEL_SCAM, Config.LABEL_HAM])

        # False positive and false negative rates
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

        metrics = {
            'accuracy': accuracy,
            'precision_scam': precision[0],
            'recall_scam': recall[0],
            'f1_scam': f1[0],
            'precision_ham': precision[1],
            'recall_ham': recall[1],
            'f1_ham': f1[1],
            'macro_precision': macro_precision,
            'macro_recall': macro_recall,
            'macro_f1': macro_f1,
            'weighted_precision': weighted_precision,
            'weighted_recall': weighted_recall,
            'weighted_f1': weighted_f1,
            'false_positive_rate': fpr,
            'false_negative_rate': fnr,
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }

        return metrics

    def run_cv_fold(self, model, X_train_fold, y_train_fold, X_val_fold, y_val_fold,
                    fold_num: int, model_name: str) -> Dict[str, Any]:
        """
        Run a single CV fold

        Args:
            model: Model instance to train
            X_train_fold: Training features for this fold
            y_train_fold: Training labels for this fold
            X_val_fold: Validation features for this fold
            y_val_fold: Validation labels for this fold
            fold_num: Fold number (for logging)
            model_name: Model name (for logging)

        Returns:
            Dictionary with fold results
        """
        logger.info(f"  Fold {fold_num}: {len(y_train_fold)} train, {len(y_val_fold)} val")

        # Train model
        model.fit(X_train_fold, y_train_fold)

        # Predictions
        y_train_pred = model.predict(X_train_fold)
        y_val_pred = model.predict(X_val_fold)

        # Calculate metrics
        train_metrics = self.calculate_metrics(y_train_fold, y_train_pred)
        val_metrics = self.calculate_metrics(y_val_fold, y_val_pred)

        # Calculate training-validation gap
        gap_metrics = {
            f"gap_{metric}": train_metrics[metric] - val_metrics[metric]
            for metric in ['accuracy', 'f1_scam', 'macro_f1']
        }

        results = {
            'fold': fold_num,
            'model_name': model_name,
            'train_size': len(y_train_fold),
            'val_size': len(y_val_fold),
            'train_metrics': train_metrics,
            'val_metrics': val_metrics,
            'gap_metrics': gap_metrics
        }

        logger.info(
            f"    Train: Acc={train_metrics['accuracy']:.3f}, "
            f"F1(scam)={train_metrics['f1_scam']:.3f}"
        )
        logger.info(
            f"    Val:   Acc={val_metrics['accuracy']:.3f}, "
            f"F1(scam)={val_metrics['f1_scam']:.3f} "
            f"(gap={gap_metrics['gap_f1_scam']:+.3f})"
        )

        return results

    def run_grouped_cv(self, X, y, groups, model_name: str,
                       use_char_features: bool = True) -> Dict[str, Any]:
        """
        Run complete grouped cross-validation for a model

        Args:
            X: Text features (raw text)
            y: Labels
            groups: Group IDs for splitting
            model_name: Name of model to train
            use_char_features: Whether to use character-level features

        Returns:
            Dictionary with CV results
        """
        logger.info(f"\n{'=' * 70}")
        logger.info(f"GROUPED CROSS-VALIDATION: {model_name.upper()}")
        logger.info(f"{'=' * 70}")

        fold_results = []
        trainer = ModelTrainer()

        for fold_num, (train_idx, val_idx) in enumerate(
            self.cv_splitter.split(X, y, groups), start=1
        ):
            # Split data
            X_train_fold = X.iloc[train_idx]
            X_val_fold = X.iloc[val_idx]
            y_train_fold = y.iloc[train_idx]
            y_val_fold = y.iloc[val_idx]

            # CRITICAL: Fit feature extractor on fold training data only
            feature_extractor = SMSFeatureExtractor(use_char_features=use_char_features)
            X_train_features = feature_extractor.fit_transform(X_train_fold)
            X_val_features = feature_extractor.transform(X_val_fold)

            # Create fresh model for this fold
            model = trainer.get_model_by_name(model_name)

            # Run fold
            fold_result = self.run_cv_fold(
                model, X_train_features, y_train_fold,
                X_val_features, y_val_fold,
                fold_num, model_name
            )

            fold_results.append(fold_result)

        # Aggregate results across folds
        aggregated = self._aggregate_fold_results(fold_results, model_name)

        return aggregated

    def _aggregate_fold_results(self, fold_results: List[Dict], model_name: str) -> Dict[str, Any]:
        """
        Aggregate results across folds

        Args:
            fold_results: List of results from each fold
            model_name: Name of the model

        Returns:
            Aggregated results
        """
        logger.info(f"\n{'-' * 70}")
        logger.info(f"AGGREGATED RESULTS: {model_name.upper()}")
        logger.info(f"{'-' * 70}")

        # Extract metrics
        train_metrics_list = [fr['train_metrics'] for fr in fold_results]
        val_metrics_list = [fr['val_metrics'] for fr in fold_results]

        # Calculate means and stds
        metric_names = train_metrics_list[0].keys()

        train_mean = {
            metric: np.mean([m[metric] for m in train_metrics_list])
            for metric in metric_names if isinstance(train_metrics_list[0][metric], (int, float))
        }

        train_std = {
            f"{metric}_std": np.std([m[metric] for m in train_metrics_list])
            for metric in metric_names if isinstance(train_metrics_list[0][metric], (int, float))
        }

        val_mean = {
            metric: np.mean([m[metric] for m in val_metrics_list])
            for metric in metric_names if isinstance(val_metrics_list[0][metric], (int, float))
        }

        val_std = {
            f"{metric}_std": np.std([m[metric] for m in val_metrics_list])
            for metric in metric_names if isinstance(val_metrics_list[0][metric], (int, float))
        }

        # Log key metrics
        logger.info(f"Training Performance (mean ± std):")
        logger.info(f"  Accuracy: {train_mean['accuracy']:.3f} ± {train_std['accuracy_std']:.3f}")
        logger.info(f"  F1 (scam): {train_mean['f1_scam']:.3f} ± {train_std['f1_scam_std']:.3f}")
        logger.info(f"  Macro F1: {train_mean['macro_f1']:.3f} ± {train_std['macro_f1_std']:.3f}")

        logger.info(f"\nValidation Performance (mean ± std):")
        logger.info(f"  Accuracy: {val_mean['accuracy']:.3f} ± {val_std['accuracy_std']:.3f}")
        logger.info(f"  F1 (scam): {val_mean['f1_scam']:.3f} ± {val_std['f1_scam_std']:.3f}")
        logger.info(f"  Macro F1: {val_mean['macro_f1']:.3f} ± {val_std['macro_f1_std']:.3f}")

        # Calculate train-val gaps
        gap_f1 = train_mean['f1_scam'] - val_mean['f1_scam']
        logger.info(f"\nTrain-Val Gap (F1 scam): {gap_f1:+.3f}")

        if gap_f1 > 0.10:
            logger.warning(f"⚠ Possible overfitting detected (gap > 0.10)")
        elif gap_f1 < 0:
            logger.warning(f"⚠ Validation higher than training (unusual)")

        aggregated = {
            'model_name': model_name,
            'n_folds': len(fold_results),
            'train_mean': train_mean,
            'train_std': train_std,
            'val_mean': val_mean,
            'val_std': val_std,
            'fold_results': fold_results
        }

        return aggregated

    def compare_models(self, cv_results: Dict[str, Dict]) -> pd.DataFrame:
        """
        Compare multiple models' CV results

        Args:
            cv_results: Dictionary mapping model names to their CV results

        Returns:
            Comparison dataframe
        """
        comparison_data = []

        for model_name, results in cv_results.items():
            val_mean = results['val_mean']
            val_std = results['val_std']

            comparison_data.append({
                'model': model_name,
                'val_accuracy': val_mean['accuracy'],
                'val_accuracy_std': val_std['accuracy_std'],
                'val_f1_scam': val_mean['f1_scam'],
                'val_f1_scam_std': val_std['f1_scam_std'],
                'val_precision_scam': val_mean['precision_scam'],
                'val_recall_scam': val_mean['recall_scam'],
                'val_f1_ham': val_mean['f1_ham'],
                'val_precision_ham': val_mean['precision_ham'],
                'val_recall_ham': val_mean['recall_ham'],
                'val_macro_f1': val_mean['macro_f1'],
                'val_macro_f1_std': val_std['macro_f1_std']
            })

        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('val_macro_f1', ascending=False)

        return comparison_df

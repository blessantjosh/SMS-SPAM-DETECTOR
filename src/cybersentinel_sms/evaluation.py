"""
Model Evaluation Module
Evaluate models on held-out test set
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)

from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate SMS fraud detection models"""

    def __init__(self, output_dir: Path = None):
        """
        Initialize evaluator

        Args:
            output_dir: Directory for saving outputs (default: Config.MODEL_REPORTS_DIR)
        """
        self.output_dir = output_dir or Config.MODEL_REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def calculate_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """
        Calculate comprehensive metrics

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary of metrics
        """
        # Accuracy
        accuracy = accuracy_score(y_true, y_pred)

        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average=None,
            labels=[Config.LABEL_SCAM, Config.LABEL_HAM]
        )

        # Macro and weighted
        macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='macro'
        )

        weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted'
        )

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=[Config.LABEL_SCAM, Config.LABEL_HAM])
        tn, fp, fn, tp = cm.ravel()

        # Rates
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

        metrics = {
            'accuracy': accuracy,
            'precision_scam': precision[0],
            'recall_scam': recall[0],
            'f1_scam': f1[0],
            'support_scam': int(support[0]),
            'precision_ham': precision[1],
            'recall_ham': recall[1],
            'f1_ham': f1[1],
            'support_ham': int(support[1]),
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
            'false_negatives': int(fn),
            'confusion_matrix': cm.tolist()
        }

        return metrics

    def evaluate_model(self, model, X_test, y_test, model_name: str) -> Dict[str, Any]:
        """
        Evaluate a single model on test set

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            model_name: Name of the model

        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating {model_name} on test set...")

        # Predictions
        y_pred = model.predict(X_test)

        # Metrics
        metrics = self.calculate_metrics(y_test, y_pred)

        results = {
            'model_name': model_name,
            'test_size': len(y_test),
            'metrics': metrics
        }

        # Log key metrics
        logger.info(f"  Accuracy: {metrics['accuracy']:.3f}")
        logger.info(f"  F1 (scam): {metrics['f1_scam']:.3f}")
        logger.info(f"  F1 (ham): {metrics['f1_ham']:.3f}")
        logger.info(f"  Macro F1: {metrics['macro_f1']:.3f}")
        logger.info(f"  FPR: {metrics['false_positive_rate']:.3f}")
        logger.info(f"  FNR: {metrics['false_negative_rate']:.3f}")

        return results

    def plot_confusion_matrix(self, cm: np.ndarray, model_name: str,
                             save: bool = True) -> None:
        """
        Plot confusion matrix

        Args:
            cm: Confusion matrix
            model_name: Name of the model
            save: Whether to save the plot
        """
        plt.figure(figsize=(8, 6))

        # Convert to DataFrame for better labeling
        cm_df = pd.DataFrame(
            cm,
            index=[Config.LABEL_SCAM, Config.LABEL_HAM],
            columns=[Config.LABEL_SCAM, Config.LABEL_HAM]
        )

        sns.heatmap(cm_df, annot=True, fmt='d', cmap='Blues',
                   cbar_kws={'label': 'Count'})

        plt.title(f'Confusion Matrix: {model_name}', fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()

        if save:
            filepath = self.output_dir / f'confusion_matrix_{model_name}.png'
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"  Saved confusion matrix to: {filepath}")

        plt.close()

    def save_classification_report(self, y_true, y_pred, model_name: str) -> None:
        """
        Save detailed classification report

        Args:
            y_true: True labels
            y_pred: Predicted labels
            model_name: Name of the model
        """
        report = classification_report(
            y_true, y_pred,
            target_names=[Config.LABEL_SCAM, Config.LABEL_HAM]
        )

        filepath = self.output_dir / f'classification_report_{model_name}.txt'
        with open(filepath, 'w') as f:
            f.write(f"Classification Report: {model_name}\n")
            f.write("=" * 60 + "\n\n")
            f.write(report)

        logger.info(f"  Saved classification report to: {filepath}")

    def save_evaluation_summary(self, results: Dict[str, Any], model_name: str) -> None:
        """
        Save evaluation summary as JSON

        Args:
            results: Evaluation results
            model_name: Name of the model
        """
        filepath = self.output_dir / f'evaluation_summary_{model_name}.json'

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"  Saved evaluation summary to: {filepath}")

    def compare_models_test(self, test_results: Dict[str, Dict]) -> pd.DataFrame:
        """
        Compare multiple models on test set

        Args:
            test_results: Dictionary mapping model names to test results

        Returns:
            Comparison DataFrame
        """
        comparison_data = []

        for model_name, results in test_results.items():
            metrics = results['metrics']

            comparison_data.append({
                'model': model_name,
                'accuracy': metrics['accuracy'],
                'f1_scam': metrics['f1_scam'],
                'precision_scam': metrics['precision_scam'],
                'recall_scam': metrics['recall_scam'],
                'f1_ham': metrics['f1_ham'],
                'precision_ham': metrics['precision_ham'],
                'recall_ham': metrics['recall_ham'],
                'macro_f1': metrics['macro_f1'],
                'weighted_f1': metrics['weighted_f1'],
                'fpr': metrics['false_positive_rate'],
                'fnr': metrics['false_negative_rate']
            })

        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('macro_f1', ascending=False)

        return comparison_df

    def plot_model_comparison(self, comparison_df: pd.DataFrame, save: bool = True) -> None:
        """
        Plot comparison of models

        Args:
            comparison_df: Comparison dataframe
            save: Whether to save the plot
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot 1: F1 Scores
        ax1 = axes[0, 0]
        comparison_df[['model', 'f1_scam', 'f1_ham', 'macro_f1']].set_index('model').plot(
            kind='bar', ax=ax1
        )
        ax1.set_title('F1 Scores by Model', fontweight='bold')
        ax1.set_ylabel('F1 Score')
        ax1.set_xlabel('Model')
        ax1.legend(['F1 (Scam)', 'F1 (Ham)', 'Macro F1'])
        ax1.set_ylim([0, 1.0])
        ax1.grid(axis='y', alpha=0.3)

        # Plot 2: Precision and Recall (Scam)
        ax2 = axes[0, 1]
        comparison_df[['model', 'precision_scam', 'recall_scam']].set_index('model').plot(
            kind='bar', ax=ax2
        )
        ax2.set_title('Precision & Recall (Scam Class)', fontweight='bold')
        ax2.set_ylabel('Score')
        ax2.set_xlabel('Model')
        ax2.legend(['Precision', 'Recall'])
        ax2.set_ylim([0, 1.0])
        ax2.grid(axis='y', alpha=0.3)

        # Plot 3: Error Rates
        ax3 = axes[1, 0]
        comparison_df[['model', 'fpr', 'fnr']].set_index('model').plot(
            kind='bar', ax=ax3, color=['red', 'orange']
        )
        ax3.set_title('Error Rates', fontweight='bold')
        ax3.set_ylabel('Rate')
        ax3.set_xlabel('Model')
        ax3.legend(['False Positive Rate', 'False Negative Rate'])
        ax3.set_ylim([0, 0.5])
        ax3.grid(axis='y', alpha=0.3)

        # Plot 4: Overall Accuracy
        ax4 = axes[1, 1]
        comparison_df.set_index('model')['accuracy'].plot(
            kind='bar', ax=ax4, color='green'
        )
        ax4.set_title('Overall Accuracy', fontweight='bold')
        ax4.set_ylabel('Accuracy')
        ax4.set_xlabel('Model')
        ax4.set_ylim([0, 1.0])
        ax4.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save:
            filepath = self.output_dir / 'model_comparison.png'
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Saved model comparison plot to: {filepath}")

        plt.close()

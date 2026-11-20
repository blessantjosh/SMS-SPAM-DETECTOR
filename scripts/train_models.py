"""
Complete Model Training Pipeline
Trains all models with grouped cross-validation and evaluates on test set
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import numpy as np
import logging
from datetime import datetime

from cybersentinel_sms.config import Config
from cybersentinel_sms.data_loader import DataLoader
from cybersentinel_sms.data_validation import DataValidator
from cybersentinel_sms.preprocessing import SMSPreprocessor
from cybersentinel_sms.feature_extraction import SMSFeatureExtractor
from cybersentinel_sms.cross_validation import GroupedCrossValidator
from cybersentinel_sms.evaluation import ModelEvaluator
from cybersentinel_sms.model_selection import ModelSelector
from cybersentinel_sms.train import ModelTrainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run complete training pipeline"""

    logger.info("=" * 80)
    logger.info("CYBERSENTINEL AI - SMS FRAUD DETECTION MODEL TRAINING")
    logger.info("=" * 80)
    start_time = datetime.now()

    # Ensure output directories exist
    Config.ensure_output_dirs()

    # ===== STEP 1: Load Data =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 1: LOADING DATA")
    logger.info("=" * 80)

    try:
        master_df, train_df, test_df, fold_manifest_df = DataLoader.load_all_datasets()
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        sys.exit(1)

    # ===== STEP 2: Validate Data =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: VALIDATING DATA")
    logger.info("=" * 80)

    try:
        DataValidator.run_full_validation(train_df, test_df)
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        sys.exit(1)

    # ===== STEP 3: Preprocess Text =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: PREPROCESSING TEXT")
    logger.info("=" * 80)

    preprocessor = SMSPreprocessor()

    logger.info("Preprocessing training data...")
    train_df = preprocessor.preprocess_dataframe(train_df)

    logger.info("Preprocessing test data...")
    test_df = preprocessor.preprocess_dataframe(test_df)

    # Use processed text for training
    X_train_text = train_df['text_processed']
    y_train = train_df[Config.TARGET_COLUMN]

    X_test_text = test_df['text_processed']
    y_test = test_df[Config.TARGET_COLUMN]

    logger.info(f"✓ Preprocessing complete")
    logger.info(f"  Train: {len(X_train_text)} samples")
    logger.info(f"  Test: {len(X_test_text)} samples")

    # ===== STEP 4: Prepare Groups for CV =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: PREPARING GROUPS FOR CROSS-VALIDATION")
    logger.info("=" * 80)

    # Merge fold manifest to get template groups
    train_with_groups = train_df.merge(
        fold_manifest_df[['record_id', 'template_group_id', 'fold']],
        on='record_id',
        how='left'
    )

    # Filter to training folds only (fold != 0)
    train_with_groups = train_with_groups[train_with_groups['fold'] != 0].copy()

    logger.info(f"Training records with group info: {len(train_with_groups)}")
    logger.info(f"Unique template groups: {train_with_groups['template_group_id'].nunique()}")

    X_train_cv = train_with_groups['text_processed']
    y_train_cv = train_with_groups[Config.TARGET_COLUMN]
    groups_cv = train_with_groups['template_group_id']

    # ===== STEP 5: Grouped Cross-Validation =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: GROUPED CROSS-VALIDATION")
    logger.info("=" * 80)

    cv_validator = GroupedCrossValidator(n_splits=4, random_state=Config.RANDOM_SEED)

    model_names = ['logistic_regression', 'linear_svm', 'lightgbm']
    cv_results = {}

    for model_name in model_names:
        try:
            logger.info(f"\nRunning CV for: {model_name}")
            cv_result = cv_validator.run_grouped_cv(
                X_train_cv, y_train_cv, groups_cv,
                model_name=model_name,
                use_char_features=True
            )
            cv_results[model_name] = cv_result
        except Exception as e:
            logger.error(f"CV failed for {model_name}: {e}")
            continue

    # Save CV results
    comparison_df = cv_validator.compare_models(cv_results)
    cv_results_path = Config.MODEL_REPORTS_DIR / 'grouped_cv_results.csv'
    comparison_df.to_csv(cv_results_path, index=False)
    logger.info(f"\n✓ CV results saved to: {cv_results_path}")

    # Display comparison
    logger.info("\n" + "=" * 80)
    logger.info("CROSS-VALIDATION RESULTS COMPARISON")
    logger.info("=" * 80)
    print("\n", comparison_df.to_string(index=False))

    # ===== STEP 6: Train Final Models on Full Training Set =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 6: TRAINING FINAL MODELS ON COMPLETE TRAINING SET")
    logger.info("=" * 80)

    # Fit feature extractor on all training data
    logger.info("Fitting feature extractor on complete training set...")
    feature_extractor = SMSFeatureExtractor(use_char_features=True)
    X_train_features = feature_extractor.fit_transform(X_train_text)
    X_test_features = feature_extractor.transform(X_test_text)

    logger.info(f"Feature extraction complete:")
    logger.info(f"  Total features: {feature_extractor.get_feature_count()}")
    logger.info(f"  Train shape: {X_train_features.shape}")
    logger.info(f"  Test shape: {X_test_features.shape}")

    # Train all models
    trainer = ModelTrainer()
    final_models = {}

    for model_name in model_names:
        try:
            logger.info(f"\nTraining final {model_name}...")
            model = trainer.get_model_by_name(model_name)
            trainer.train_model(model, X_train_features, y_train, model_name)
            final_models[model_name] = model
        except Exception as e:
            logger.error(f"Failed to train final {model_name}: {e}")
            continue

    # ===== STEP 7: Evaluate on Test Set =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 7: EVALUATING ON HELD-OUT TEST SET")
    logger.info("=" * 80)

    evaluator = ModelEvaluator()
    test_results = {}

    for model_name, model in final_models.items():
        logger.info(f"\nEvaluating {model_name} on test set...")
        try:
            test_result = evaluator.evaluate_model(
                model, X_test_features, y_test, model_name
            )
            test_results[model_name] = test_result

            # Save detailed reports
            y_pred = model.predict(X_test_features)
            evaluator.save_classification_report(y_test, y_pred, model_name)
            evaluator.plot_confusion_matrix(
                np.array(test_result['metrics']['confusion_matrix']),
                model_name
            )
            evaluator.save_evaluation_summary(test_result, model_name)

        except Exception as e:
            logger.error(f"Evaluation failed for {model_name}: {e}")
            continue

    # Compare models on test set
    test_comparison_df = evaluator.compare_models_test(test_results)
    test_comparison_path = Config.MODEL_REPORTS_DIR / 'test_set_comparison.csv'
    test_comparison_df.to_csv(test_comparison_path, index=False)
    logger.info(f"\n✓ Test results saved to: {test_comparison_path}")

    # Display test comparison
    logger.info("\n" + "=" * 80)
    logger.info("TEST SET RESULTS COMPARISON")
    logger.info("=" * 80)
    print("\n", test_comparison_df.to_string(index=False))

    # Plot comparison
    evaluator.plot_model_comparison(test_comparison_df)

    # ===== STEP 8: Model Selection and Saving =====
    logger.info("\n" + "=" * 80)
    logger.info("STEP 8: MODEL SELECTION AND SAVING")
    logger.info("=" * 80)

    selector = ModelSelector()

    # Select best model based on CV performance
    best_model_name, selection_details = selector.select_best_model(
        cv_results,
        test_results=test_results,
        selection_metric='val_macro_f1',
        stability_weight=0.3
    )

    # Save best model
    best_model = final_models[best_model_name]

    metadata = {
        'model_name': best_model_name,
        'selection_details': selection_details,
        'cv_results': {
            'val_macro_f1': cv_results[best_model_name]['val_mean']['macro_f1'],
            'val_f1_scam': cv_results[best_model_name]['val_mean']['f1_scam'],
            'val_f1_ham': cv_results[best_model_name]['val_mean']['f1_ham']
        },
        'test_results': {
            'macro_f1': test_results[best_model_name]['metrics']['macro_f1'],
            'f1_scam': test_results[best_model_name]['metrics']['f1_scam'],
            'f1_ham': test_results[best_model_name]['metrics']['f1_ham'],
            'accuracy': test_results[best_model_name]['metrics']['accuracy']
        },
        'training_samples': len(X_train_text),
        'test_samples': len(X_test_text),
        'feature_count': feature_extractor.get_feature_count()
    }

    bundle_path = selector.save_model_bundle(
        best_model,
        feature_extractor,
        best_model_name,
        metadata
    )

    # ===== FINAL SUMMARY =====
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("\n" + "=" * 80)
    logger.info("TRAINING PIPELINE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info(f"\nBest Model: {best_model_name}")
    logger.info(f"Validation Macro F1: {metadata['cv_results']['val_macro_f1']:.3f}")
    logger.info(f"Test Macro F1: {metadata['test_results']['macro_f1']:.3f}")
    logger.info(f"\nModel saved to: {bundle_path}")
    logger.info(f"\nAll reports saved to: {Config.MODEL_REPORTS_DIR}")

    logger.info("\n" + "=" * 80)
    logger.info("IMPORTANT NOTES")
    logger.info("=" * 80)
    logger.info("• This model was trained on synthetic SMS data")
    logger.info("• Independent real-world testing is required before production deployment")
    logger.info("• Model predictions are not guarantees of fraud/legitimacy")
    logger.info("• Regular retraining with real data is recommended")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

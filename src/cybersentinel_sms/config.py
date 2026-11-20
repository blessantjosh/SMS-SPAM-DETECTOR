"""
Configuration settings for CyberSentinel SMS Fraud Detection
"""
from pathlib import Path
from typing import Dict, List

class Config:
    """Central configuration for the SMS fraud detection pipeline"""

    # Project Root
    PROJECT_ROOT = Path(__file__).parent.parent.parent

    # Data Paths
    DATA_DIR = PROJECT_ROOT / "data"
    DATA_INPUT = DATA_DIR / "input"
    DATA_PROCESSED = DATA_DIR / "processed"
    DATA_EXTERNAL = DATA_DIR / "external"

    # Required Input Files
    SMS_MASTER_FILE = DATA_INPUT / "sms_cleaned_master.csv"
    SMS_TRAIN_FILE = DATA_INPUT / "sms_train_group_aware.csv"
    SMS_TEST_FILE = DATA_INPUT / "sms_test_group_aware.csv"
    FIVE_FOLD_MANIFEST = DATA_INPUT / "five_fold_group_manifest.csv"
    SPLIT_SUMMARY = DATA_INPUT / "split_summary.csv"
    DATASET_AUDIT = DATA_INPUT / "DATASET_AUDIT_AND_GUIDE.txt"

    # Output Paths
    MODELS_DIR = PROJECT_ROOT / "models"
    TRAINED_MODELS_DIR = MODELS_DIR / "trained"
    EVALUATION_DIR = MODELS_DIR / "evaluation"

    REPORTS_DIR = PROJECT_ROOT / "reports"
    DATASET_REPORTS_DIR = REPORTS_DIR / "dataset"
    MODEL_REPORTS_DIR = REPORTS_DIR / "models"
    VISUALIZATIONS_DIR = REPORTS_DIR / "visualizations"

    # Required CSV Columns
    REQUIRED_COLUMNS = ["record_id", "text", "label", "category", "language", "source"]

    # Target and Feature Columns
    TARGET_COLUMN = "label"
    TEXT_COLUMN = "text"
    GROUP_COLUMN = "template_group_id"
    FOLD_COLUMN = "fold"

    # Columns that MUST NOT be used as model features (data leakage prevention)
    FORBIDDEN_FEATURES = [
        "label",           # Target variable
        "category",        # Directly reveals label
        "source",          # Metadata
        "record_id",       # Identifier
        "template_group_id",  # Grouping metadata
        "fold"             # Split metadata
    ]

    # Label Values
    LABEL_SCAM = "scam"
    LABEL_HAM = "ham"
    VALID_LABELS = [LABEL_SCAM, LABEL_HAM]

    # Model Training Settings
    RANDOM_SEED = 42
    N_CV_FOLDS = 4  # Use 4 folds for grouped cross-validation (train on folds 1-4)
    TEST_FOLD = 0   # Fold 0 is held-out test set

    # TF-IDF Parameters
    TFIDF_WORD_CONFIG = {
        "max_features": 3000,
        "ngram_range": (1, 2),  # unigrams and bigrams
        "min_df": 2,
        "sublinear_tf": True,
        "strip_accents": None,  # Preserve multilingual characters
        "lowercase": True,
        "stop_words": None  # Don't remove stopwords automatically
    }

    TFIDF_CHAR_CONFIG = {
        "max_features": 2000,
        "ngram_range": (2, 4),  # character n-grams
        "analyzer": "char",
        "min_df": 2,
        "sublinear_tf": True,
        "lowercase": True
    }

    # Model Configurations
    LOGISTIC_REGRESSION_CONFIG = {
        "max_iter": 1000,
        "class_weight": "balanced",
        "random_state": RANDOM_SEED,
        "solver": "lbfgs",
        "C": 1.0
    }

    LINEAR_SVM_CONFIG = {
        "max_iter": 1000,
        "class_weight": "balanced",
        "random_state": RANDOM_SEED,
        "C": 1.0,
        "dual": "auto"
    }

    LIGHTGBM_CONFIG = {
        "n_estimators": 100,
        "max_depth": 5,
        "num_leaves": 31,
        "learning_rate": 0.05,
        "class_weight": "balanced",
        "random_state": RANDOM_SEED,
        "verbose": -1,
        "force_col_wise": True
    }

    # Evaluation Metrics
    PRIMARY_METRIC = "f1_scam"  # F1 score for scam class
    METRICS_TO_TRACK = [
        "accuracy",
        "precision_scam", "recall_scam", "f1_scam",
        "precision_ham", "recall_ham", "f1_ham",
        "macro_f1", "weighted_f1"
    ]

    @classmethod
    def validate_paths(cls) -> Dict[str, bool]:
        """Verify that required input files exist"""
        required_files = {
            "sms_cleaned_master.csv": cls.SMS_MASTER_FILE,
            "sms_train_group_aware.csv": cls.SMS_TRAIN_FILE,
            "sms_test_group_aware.csv": cls.SMS_TEST_FILE,
            "five_fold_group_manifest.csv": cls.FIVE_FOLD_MANIFEST,
            "split_summary.csv": cls.SPLIT_SUMMARY,
            "DATASET_AUDIT_AND_GUIDE.txt": cls.DATASET_AUDIT
        }

        results = {}
        for name, path in required_files.items():
            results[name] = path.exists()

        return results

    @classmethod
    def ensure_output_dirs(cls) -> None:
        """Create output directories if they don't exist"""
        dirs = [
            cls.DATA_PROCESSED,
            cls.TRAINED_MODELS_DIR,
            cls.EVALUATION_DIR,
            cls.DATASET_REPORTS_DIR,
            cls.MODEL_REPORTS_DIR,
            cls.VISUALIZATIONS_DIR
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

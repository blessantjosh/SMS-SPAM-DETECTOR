"""
Data loading utilities for SMS fraud detection
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Tuple, Optional

from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and basic validation of SMS dataset files"""

    @staticmethod
    def load_csv(file_path: Path, description: str = "dataset") -> pd.DataFrame:
        """
        Load a CSV file with error handling

        Args:
            file_path: Path to CSV file
            description: Human-readable description for logging

        Returns:
            Loaded DataFrame

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required {description} file not found: {file_path}"
            )

        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"Loaded {description}: {len(df)} records from {file_path.name}")
            return df
        except Exception as e:
            raise ValueError(f"Failed to load {description} from {file_path}: {e}")

    @classmethod
    def load_master_dataset(cls) -> pd.DataFrame:
        """Load the complete master SMS dataset"""
        return cls.load_csv(Config.SMS_MASTER_FILE, "master dataset")

    @classmethod
    def load_train_dataset(cls) -> pd.DataFrame:
        """Load the training dataset (group-aware split)"""
        return cls.load_csv(Config.SMS_TRAIN_FILE, "training dataset")

    @classmethod
    def load_test_dataset(cls) -> pd.DataFrame:
        """Load the held-out test dataset"""
        return cls.load_csv(Config.SMS_TEST_FILE, "test dataset")

    @classmethod
    def load_fold_manifest(cls) -> pd.DataFrame:
        """Load the five-fold group manifest for cross-validation"""
        return cls.load_csv(Config.FIVE_FOLD_MANIFEST, "fold manifest")

    @classmethod
    def load_split_summary(cls) -> pd.DataFrame:
        """Load the train/test split summary"""
        return cls.load_csv(Config.SPLIT_SUMMARY, "split summary")

    @classmethod
    def load_all_datasets(cls) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load all required datasets

        Returns:
            Tuple of (master_df, train_df, test_df, fold_manifest_df)
        """
        logger.info("Loading all datasets...")

        master_df = cls.load_master_dataset()
        train_df = cls.load_train_dataset()
        test_df = cls.load_test_dataset()
        fold_manifest_df = cls.load_fold_manifest()

        logger.info("All datasets loaded successfully")

        return master_df, train_df, test_df, fold_manifest_df

    @staticmethod
    def get_X_y(df: pd.DataFrame, text_column: str = None, target_column: str = None) -> Tuple[pd.Series, pd.Series]:
        """
        Extract features (X) and target (y) from dataframe

        Args:
            df: Input dataframe
            text_column: Name of text feature column (default: Config.TEXT_COLUMN)
            target_column: Name of target column (default: Config.TARGET_COLUMN)

        Returns:
            Tuple of (X, y) where X is text series and y is label series
        """
        text_col = text_column or Config.TEXT_COLUMN
        target_col = target_column or Config.TARGET_COLUMN

        if text_col not in df.columns:
            raise ValueError(f"Text column '{text_col}' not found in dataframe")
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe")

        X = df[text_col]
        y = df[target_col]

        return X, y

"""
Data validation utilities to ensure dataset integrity
"""
import pandas as pd
import logging
from typing import Dict, List, Any

from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validate SMS dataset integrity and detect potential issues"""

    @staticmethod
    def validate_required_columns(df: pd.DataFrame, required_columns: List[str] = None) -> bool:
        """
        Check if all required columns exist in dataframe

        Args:
            df: DataFrame to validate
            required_columns: List of required column names

        Returns:
            True if valid, raises ValueError otherwise
        """
        req_cols = required_columns or Config.REQUIRED_COLUMNS
        missing_cols = [col for col in req_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        logger.info(f"✓ All required columns present: {req_cols}")
        return True

    @staticmethod
    def validate_labels(df: pd.DataFrame, label_column: str = None) -> Dict[str, Any]:
        """
        Validate that labels are correct and report distribution

        Args:
            df: DataFrame to validate
            label_column: Name of label column

        Returns:
            Dictionary with validation results
        """
        label_col = label_column or Config.TARGET_COLUMN

        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found")

        # Check for missing labels
        missing_labels = df[label_col].isna().sum()
        if missing_labels > 0:
            raise ValueError(f"Found {missing_labels} missing labels")

        # Check valid label values
        unique_labels = df[label_col].unique()
        invalid_labels = [lbl for lbl in unique_labels if lbl not in Config.VALID_LABELS]

        if invalid_labels:
            raise ValueError(f"Invalid label values found: {invalid_labels}")

        # Label distribution
        label_counts = df[label_col].value_counts()
        label_percentages = df[label_col].value_counts(normalize=True) * 100

        results = {
            "total_records": len(df),
            "label_counts": label_counts.to_dict(),
            "label_percentages": label_percentages.to_dict(),
            "valid": True
        }

        logger.info(f"✓ Label validation passed")
        logger.info(f"  Total records: {len(df)}")
        for label in Config.VALID_LABELS:
            count = label_counts.get(label, 0)
            pct = label_percentages.get(label, 0)
            logger.info(f"  {label}: {count} ({pct:.2f}%)")

        return results

    @staticmethod
    def check_missing_values(df: pd.DataFrame) -> Dict[str, int]:
        """
        Check for missing values in all columns

        Args:
            df: DataFrame to check

        Returns:
            Dictionary mapping column names to missing value counts
        """
        missing = df.isna().sum()
        missing_dict = missing[missing > 0].to_dict()

        if missing_dict:
            logger.warning(f"⚠ Missing values found: {missing_dict}")
        else:
            logger.info("✓ No missing values found")

        return missing_dict

    @staticmethod
    def check_empty_text(df: pd.DataFrame, text_column: str = None) -> int:
        """
        Check for empty or whitespace-only SMS messages

        Args:
            df: DataFrame to check
            text_column: Name of text column

        Returns:
            Count of empty messages
        """
        text_col = text_column or Config.TEXT_COLUMN

        if text_col not in df.columns:
            raise ValueError(f"Text column '{text_col}' not found")

        empty_count = df[text_col].str.strip().str.len().eq(0).sum()

        if empty_count > 0:
            logger.warning(f"⚠ Found {empty_count} empty SMS messages")
        else:
            logger.info("✓ No empty SMS messages")

        return empty_count

    @staticmethod
    def check_duplicates(df: pd.DataFrame, subset: List[str] = None) -> int:
        """
        Check for duplicate records

        Args:
            df: DataFrame to check
            subset: Columns to check for duplicates (None = all columns)

        Returns:
            Count of duplicate rows
        """
        dup_count = df.duplicated(subset=subset).sum()

        if dup_count > 0:
            logger.warning(f"⚠ Found {dup_count} duplicate records")
        else:
            logger.info("✓ No duplicate records")

        return dup_count

    @staticmethod
    def check_record_id_uniqueness(df: pd.DataFrame, id_column: str = "record_id") -> bool:
        """
        Verify that record IDs are unique

        Args:
            df: DataFrame to check
            id_column: Name of ID column

        Returns:
            True if all IDs are unique
        """
        if id_column not in df.columns:
            logger.warning(f"⚠ ID column '{id_column}' not found, skipping uniqueness check")
            return True

        duplicate_ids = df[id_column].duplicated().sum()

        if duplicate_ids > 0:
            raise ValueError(f"Found {duplicate_ids} duplicate record IDs")

        logger.info(f"✓ All {len(df)} record IDs are unique")
        return True

    @staticmethod
    def check_train_test_overlap(train_df: pd.DataFrame, test_df: pd.DataFrame,
                                  id_column: str = "record_id") -> int:
        """
        Check if training and test sets have overlapping records

        Args:
            train_df: Training dataframe
            test_df: Test dataframe
            id_column: Column to check for overlap

        Returns:
            Count of overlapping records
        """
        if id_column not in train_df.columns or id_column not in test_df.columns:
            logger.warning(f"⚠ Cannot check overlap: '{id_column}' column missing")
            return 0

        train_ids = set(train_df[id_column])
        test_ids = set(test_df[id_column])

        overlap = train_ids.intersection(test_ids)
        overlap_count = len(overlap)

        if overlap_count > 0:
            raise ValueError(f"Found {overlap_count} overlapping records between train and test sets")

        logger.info(f"✓ No record overlap between train ({len(train_df)}) and test ({len(test_df)}) sets")
        return overlap_count

    @staticmethod
    def check_group_overlap(train_df: pd.DataFrame, test_df: pd.DataFrame,
                           group_column: str = "template_group_id") -> Dict[str, Any]:
        """
        Check if template groups overlap between train and test sets

        Args:
            train_df: Training dataframe
            test_df: Test dataframe
            group_column: Name of group column

        Returns:
            Dictionary with overlap analysis
        """
        if group_column not in train_df.columns or group_column not in test_df.columns:
            logger.warning(f"⚠ Cannot check group overlap: '{group_column}' column missing")
            return {"group_overlap_count": 0, "valid": True}

        train_groups = set(train_df[group_column].dropna())
        test_groups = set(test_df[group_column].dropna())

        overlap_groups = train_groups.intersection(test_groups)
        overlap_count = len(overlap_groups)

        results = {
            "train_groups": len(train_groups),
            "test_groups": len(test_groups),
            "overlap_groups": overlap_count,
            "valid": overlap_count == 0
        }

        if overlap_count > 0:
            raise ValueError(
                f"Found {overlap_count} template groups appearing in both train and test sets. "
                f"This violates group-aware splitting and will cause data leakage."
            )

        logger.info(f"✓ No template group overlap: {len(train_groups)} train groups, {len(test_groups)} test groups")
        return results

    @classmethod
    def run_full_validation(cls, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run complete validation suite on train and test datasets

        Args:
            train_df: Training dataframe
            test_df: Test dataframe

        Returns:
            Dictionary with all validation results
        """
        logger.info("=" * 60)
        logger.info("RUNNING FULL DATASET VALIDATION")
        logger.info("=" * 60)

        results = {}

        try:
            # Validate structure
            logger.info("\n1. Validating dataset structure...")
            cls.validate_required_columns(train_df)
            cls.validate_required_columns(test_df)

            # Validate labels
            logger.info("\n2. Validating labels...")
            results["train_labels"] = cls.validate_labels(train_df)
            results["test_labels"] = cls.validate_labels(test_df)

            # Check missing values
            logger.info("\n3. Checking for missing values...")
            results["train_missing"] = cls.check_missing_values(train_df)
            results["test_missing"] = cls.check_missing_values(test_df)

            # Check empty text
            logger.info("\n4. Checking for empty SMS messages...")
            results["train_empty_text"] = cls.check_empty_text(train_df)
            results["test_empty_text"] = cls.check_empty_text(test_df)

            # Check duplicates
            logger.info("\n5. Checking for duplicate records...")
            results["train_duplicates"] = cls.check_duplicates(train_df)
            results["test_duplicates"] = cls.check_duplicates(test_df)

            # Check ID uniqueness
            logger.info("\n6. Validating record ID uniqueness...")
            cls.check_record_id_uniqueness(train_df)
            cls.check_record_id_uniqueness(test_df)

            # Check train-test overlap
            logger.info("\n7. Checking train-test record overlap...")
            results["record_overlap"] = cls.check_train_test_overlap(train_df, test_df)

            # Check template group overlap
            logger.info("\n8. Checking template group overlap...")
            results["group_overlap"] = cls.check_group_overlap(train_df, test_df)

            logger.info("\n" + "=" * 60)
            logger.info("✓ ALL VALIDATIONS PASSED")
            logger.info("=" * 60)

            results["validation_passed"] = True

        except Exception as e:
            logger.error(f"\n✗ VALIDATION FAILED: {e}")
            results["validation_passed"] = False
            results["error"] = str(e)
            raise

        return results

"""
Dataset Inspection Script
Validates dataset integrity and generates summary reports
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import logging
from cybersentinel_sms.config import Config
from cybersentinel_sms.data_loader import DataLoader
from cybersentinel_sms.data_validation import DataValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run complete dataset inspection and validation"""

    logger.info("=" * 70)
    logger.info("CYBERSENTINEL AI - DATASET INSPECTION")
    logger.info("=" * 70)

    # Ensure output directories exist
    Config.ensure_output_dirs()

    # Step 1: Check if required files exist
    logger.info("\nStep 1: Checking required files...")
    file_status = Config.validate_paths()

    all_files_exist = all(file_status.values())

    for filename, exists in file_status.items():
        status = "✓" if exists else "✗"
        logger.info(f"  {status} {filename}")

    if not all_files_exist:
        logger.error("\n✗ Some required files are missing!")
        logger.error("Please ensure all 6 dataset files are placed in data/input/")
        sys.exit(1)

    logger.info("\n✓ All required files present")

    # Step 2: Load datasets
    logger.info("\nStep 2: Loading datasets...")
    try:
        master_df, train_df, test_df, fold_manifest_df = DataLoader.load_all_datasets()
    except Exception as e:
        logger.error(f"✗ Failed to load datasets: {e}")
        sys.exit(1)

    # Step 3: Run validation
    logger.info("\nStep 3: Running validation checks...")
    try:
        validation_results = DataValidator.run_full_validation(train_df, test_df)
    except Exception as e:
        logger.error(f"✗ Validation failed: {e}")
        sys.exit(1)

    # Step 4: Generate dataset summary
    logger.info("\nStep 4: Generating dataset summary...")

    summary = {
        "total_records": len(master_df),
        "train_records": len(train_df),
        "test_records": len(test_df),
        "scam_records": len(master_df[master_df[Config.TARGET_COLUMN] == Config.LABEL_SCAM]),
        "ham_records": len(master_df[master_df[Config.TARGET_COLUMN] == Config.LABEL_HAM]),
        "languages": master_df["language"].value_counts().to_dict(),
        "categories": master_df["category"].value_counts().to_dict(),
    }

    # Calculate SMS length statistics
    master_df["text_length"] = master_df[Config.TEXT_COLUMN].str.len()
    summary["sms_length_min"] = int(master_df["text_length"].min())
    summary["sms_length_max"] = int(master_df["text_length"].max())
    summary["sms_length_mean"] = round(master_df["text_length"].mean(), 2)
    summary["sms_length_median"] = int(master_df["text_length"].median())

    # Count URLs and phone numbers (simple patterns)
    import re
    url_pattern = r'http[s]?://|www\.|bit\.ly|tinyurl'
    phone_pattern = r'\d{10}|\d{5}[-\s]\d{5}|\+91[-\s]?\d{10}'

    summary["sms_with_urls"] = master_df[Config.TEXT_COLUMN].str.contains(
        url_pattern, case=False, regex=True, na=False
    ).sum()

    summary["sms_with_phone_numbers"] = master_df[Config.TEXT_COLUMN].str.contains(
        phone_pattern, regex=True, na=False
    ).sum()

    # Check template groups
    if "template_group_id" in fold_manifest_df.columns:
        unique_groups = fold_manifest_df["template_group_id"].nunique()
        repeated_groups = fold_manifest_df["template_group_id"].value_counts()
        repeated_groups = repeated_groups[repeated_groups > 1]

        summary["unique_template_groups"] = unique_groups
        summary["repeated_template_groups"] = len(repeated_groups)

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("DATASET SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Records: {summary['total_records']}")
    logger.info(f"  Training: {summary['train_records']}")
    logger.info(f"  Test: {summary['test_records']}")
    logger.info(f"\nLabel Distribution:")
    logger.info(f"  Scam: {summary['scam_records']} ({summary['scam_records']/summary['total_records']*100:.1f}%)")
    logger.info(f"  Ham: {summary['ham_records']} ({summary['ham_records']/summary['total_records']*100:.1f}%)")
    logger.info(f"\nLanguage Distribution:")
    for lang, count in summary['languages'].items():
        logger.info(f"  {lang}: {count}")
    logger.info(f"\nSMS Length Statistics:")
    logger.info(f"  Min: {summary['sms_length_min']} characters")
    logger.info(f"  Max: {summary['sms_length_max']} characters")
    logger.info(f"  Mean: {summary['sms_length_mean']} characters")
    logger.info(f"  Median: {summary['sms_length_median']} characters")
    logger.info(f"\nContent Patterns:")
    logger.info(f"  SMS with URLs: {summary['sms_with_urls']}")
    logger.info(f"  SMS with Phone Numbers: {summary['sms_with_phone_numbers']}")

    if "unique_template_groups" in summary:
        logger.info(f"\nTemplate Groups:")
        logger.info(f"  Unique Groups: {summary['unique_template_groups']}")
        logger.info(f"  Repeated Groups: {summary['repeated_template_groups']}")

    # Save summary to CSV
    summary_df = pd.DataFrame([summary])
    summary_path = Config.DATASET_REPORTS_DIR / "dataset_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    logger.info(f"\n✓ Dataset summary saved to: {summary_path}")

    # Save detailed statistics
    stats_dict = {
        "metric": [],
        "value": []
    }

    for key, value in summary.items():
        if not isinstance(value, dict):
            stats_dict["metric"].append(key)
            stats_dict["value"].append(value)

    stats_df = pd.DataFrame(stats_dict)
    stats_path = Config.DATASET_REPORTS_DIR / "dataset_statistics.csv"
    stats_df.to_csv(stats_path, index=False)
    logger.info(f"✓ Detailed statistics saved to: {stats_path}")

    logger.info("\n" + "=" * 70)
    logger.info("✓ DATASET INSPECTION COMPLETE")
    logger.info("=" * 70)
    logger.info("\nDataset is valid and ready for preprocessing and model training.")


if __name__ == "__main__":
    main()

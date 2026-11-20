"""
SMS Fraud Prediction Script
Predict whether an SMS message is fraudulent
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import argparse
import logging

from cybersentinel_sms.prediction import SMSPredictor
from cybersentinel_sms.config import Config

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def predict_single_sms(predictor: SMSPredictor, message: str):
    """
    Predict a single SMS and display results

    Args:
        predictor: SMSPredictor instance
        message: SMS text to analyze
    """
    result = predictor.predict_single(message, return_details=True)
    output = predictor.format_prediction_output(result)
    print(output)


def main():
    parser = argparse.ArgumentParser(
        description='Predict whether an SMS message is fraudulent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Predict a single SMS
  python scripts/predict_sms.py --message "Your bank account will be blocked. Update KYC immediately."

  # Use a specific model
  python scripts/predict_sms.py --model lightgbm --message "Your package is ready for delivery"

  # Get detailed output
  python scripts/predict_sms.py --message "Win Rs 50000! Click here" --verbose
        """
    )

    parser.add_argument(
        '--message', '-m',
        type=str,
        required=True,
        help='SMS message to analyze'
    )

    parser.add_argument(
        '--model', '-n',
        type=str,
        default=None,
        help='Model name to use (default: auto-detect latest)'
    )

    parser.add_argument(
        '--model-path', '-p',
        type=Path,
        default=None,
        help='Path to specific model file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO, force=True)

    # Load predictor
    try:
        if args.model_path:
            print(f"Loading model from: {args.model_path}")
            predictor = SMSPredictor.from_model_file(args.model_path)
        elif args.model:
            print(f"Loading model: {args.model}")
            predictor = SMSPredictor.from_latest_model(args.model)
        else:
            # Try to find any latest model
            models_dir = Config.TRAINED_MODELS_DIR
            latest_files = list(models_dir.glob("*_latest.joblib"))

            if not latest_files:
                print("ERROR: No trained models found!")
                print(f"Please train a model first using: python scripts/train_models.py")
                sys.exit(1)

            # Use the first one found
            model_path = latest_files[0]
            print(f"Loading model from: {model_path}")
            predictor = SMSPredictor.from_model_file(model_path)

    except FileNotFoundError as e:
        print(f"ERROR: Model not found: {e}")
        print(f"\nAvailable models in {Config.TRAINED_MODELS_DIR}:")
        for model_file in Config.TRAINED_MODELS_DIR.glob("*_latest.joblib"):
            print(f"  - {model_file.stem.replace('_latest', '')}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}")
        sys.exit(1)

    # Make prediction
    try:
        predict_single_sms(predictor, args.message)
    except Exception as e:
        print(f"ERROR: Prediction failed: {e}")
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()

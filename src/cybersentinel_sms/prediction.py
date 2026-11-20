"""
SMS Prediction Module
Make predictions on new SMS messages
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
from pathlib import Path

from .config import Config
from .preprocessing import SMSPreprocessor
from .model_selection import ModelSelector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSPredictor:
    """Predict fraud for SMS messages"""

    def __init__(self, model_bundle: Dict[str, Any]):
        """
        Initialize predictor with a loaded model bundle

        Args:
            model_bundle: Dictionary containing model, feature_extractor, and metadata
        """
        self.model = model_bundle['model']
        self.feature_extractor = model_bundle['feature_extractor']
        self.model_name = model_bundle['model_name']
        self.metadata = model_bundle.get('metadata', {})
        self.config = model_bundle.get('config', {})

        self.preprocessor = SMSPreprocessor()

        logger.info(f"✓ Predictor initialized with model: {self.model_name}")

    @classmethod
    def from_model_file(cls, model_path: Path) -> 'SMSPredictor':
        """
        Create predictor from a saved model file

        Args:
            model_path: Path to model bundle

        Returns:
            SMSPredictor instance
        """
        bundle = ModelSelector.load_model_bundle(model_path)
        return cls(bundle)

    @classmethod
    def from_latest_model(cls, model_name: str) -> 'SMSPredictor':
        """
        Create predictor from the latest version of a model

        Args:
            model_name: Name of the model

        Returns:
            SMSPredictor instance
        """
        bundle = ModelSelector.load_latest_model(model_name)
        return cls(bundle)

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess a single SMS text

        Args:
            text: Raw SMS text

        Returns:
            Preprocessed text
        """
        return self.preprocessor.preprocess_text(text)

    def predict_single(self, sms_text: str, return_details: bool = False) -> Dict[str, Any]:
        """
        Predict fraud for a single SMS message

        Args:
            sms_text: Raw SMS text
            return_details: Whether to return detailed information

        Returns:
            Dictionary with prediction results
        """
        if not sms_text or not sms_text.strip():
            return {
                'sms': sms_text,
                'prediction': 'INVALID',
                'label': None,
                'error': 'Empty SMS text'
            }

        # Preprocess
        processed_text = self.preprocess_text(sms_text)

        # Extract features
        features = self.feature_extractor.transform([processed_text])

        # Predict
        prediction = self.model.predict(features)[0]

        result = {
            'sms': sms_text,
            'prediction': 'SCAM' if prediction == Config.LABEL_SCAM else 'LEGITIMATE',
            'label': prediction
        }

        # Add detailed info if requested
        if return_details:
            result['processed_text'] = processed_text
            result['model_name'] = self.model_name

            # Try to get prediction probability/score if available
            if hasattr(self.model, 'predict_proba'):
                try:
                    proba = self.model.predict_proba(features)[0]
                    # Map to class labels
                    classes = self.model.classes_
                    result['probabilities'] = {
                        cls: float(prob) for cls, prob in zip(classes, proba)
                    }
                    result['confidence'] = float(max(proba))
                except:
                    pass

            elif hasattr(self.model, 'decision_function'):
                try:
                    score = self.model.decision_function(features)[0]
                    result['decision_score'] = float(score)
                except:
                    pass

        return result

    def predict_batch(self, sms_list: List[str]) -> List[Dict[str, Any]]:
        """
        Predict fraud for multiple SMS messages

        Args:
            sms_list: List of raw SMS texts

        Returns:
            List of prediction dictionaries
        """
        logger.info(f"Predicting {len(sms_list)} SMS messages...")

        # Preprocess all
        processed_texts = [self.preprocess_text(sms) for sms in sms_list]

        # Extract features
        features = self.feature_extractor.transform(processed_texts)

        # Predict
        predictions = self.model.predict(features)

        results = []
        for sms, prediction in zip(sms_list, predictions):
            results.append({
                'sms': sms,
                'prediction': 'SCAM' if prediction == Config.LABEL_SCAM else 'LEGITIMATE',
                'label': prediction
            })

        scam_count = sum(1 for r in results if r['label'] == Config.LABEL_SCAM)
        logger.info(f"✓ Predictions complete: {scam_count} scam, {len(results) - scam_count} legitimate")

        return results

    def predict_from_dataframe(self, df: pd.DataFrame,
                               text_column: str = 'text') -> pd.DataFrame:
        """
        Predict fraud for SMS messages in a DataFrame

        Args:
            df: DataFrame containing SMS texts
            text_column: Name of column with SMS text

        Returns:
            DataFrame with added prediction columns
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")

        logger.info(f"Predicting {len(df)} SMS messages from DataFrame...")

        df = df.copy()

        # Get predictions
        sms_list = df[text_column].tolist()
        predictions = self.predict_batch(sms_list)

        # Add to dataframe
        df['predicted_label'] = [p['label'] for p in predictions]
        df['predicted_class'] = [p['prediction'] for p in predictions]

        return df

    def get_recommendation(self, prediction_result: Dict[str, Any]) -> str:
        """
        Get user-friendly recommendation based on prediction

        Args:
            prediction_result: Result from predict_single()

        Returns:
            Recommendation text
        """
        if prediction_result['prediction'] == 'SCAM':
            return (
                "WARNING: This message shows characteristics of a scam.\n"
                "Recommendations:\n"
                "- Do NOT click any links in this message\n"
                "- Do NOT share personal information or OTPs\n"
                "- Do NOT make any payments requested in this message\n"
                "- Verify directly with the organization through official channels\n"
                "- Report this message to your mobile carrier"
            )
        else:
            return (
                "INFO: This message appears legitimate.\n"
                "Note: This is a machine prediction and not a guarantee of safety.\n"
                "Always exercise caution with:\n"
                "- Unsolicited requests for personal information\n"
                "- Urgent payment demands\n"
                "- Links from unknown senders"
            )

    def format_prediction_output(self, prediction_result: Dict[str, Any]) -> str:
        """
        Format prediction result for display

        Args:
            prediction_result: Result from predict_single()

        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 70)
        output.append("SMS FRAUD DETECTION ANALYSIS")
        output.append("=" * 70)
        output.append(f"\nMessage:")
        output.append(f"{prediction_result['sms']}")
        output.append(f"\nPrediction: {prediction_result['prediction']}")
        output.append(f"Model: {self.model_name}")

        # Add probability if available
        if 'probabilities' in prediction_result:
            probs = prediction_result['probabilities']
            output.append(f"\nProbabilities:")
            for label, prob in probs.items():
                output.append(f"  {label}: {prob:.3f}")

        # Add recommendation
        output.append(f"\n{self.get_recommendation(prediction_result)}")
        output.append("=" * 70)

        return "\n".join(output)

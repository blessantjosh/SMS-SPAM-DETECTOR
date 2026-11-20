"""
SMS Text Preprocessing Module
Handles multilingual SMS text normalization while preserving important fraud signals
"""
import re
import logging
from typing import List
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSPreprocessor:
    """
    Preprocess SMS text for fraud detection

    Important principles:
    - Preserve original meaning
    - Handle English, Hinglish, and Tanglish
    - Don't destroy URLs or phone numbers
    - Keep fraud-relevant words like 'urgent', 'blocked', 'verify'
    - Maintain consistent preprocessing for train and test
    """

    def __init__(self):
        """Initialize preprocessor"""
        pass

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize excessive whitespace while preserving structure

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace
        """
        if pd.isna(text) or text is None:
            return ""

        # Convert to string
        text = str(text)

        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)

        # Trim leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def preserve_urls(text: str) -> str:
        """
        Normalize URLs without destroying them
        URLs are important fraud signals

        Args:
            text: Input text

        Returns:
            Text with normalized URLs
        """
        if pd.isna(text) or text is None:
            return ""

        # Don't remove URLs, but normalize common patterns
        # bit.ly/xyz -> URL_TOKEN could destroy information
        # Instead, just ensure consistent spacing around URLs

        # Add space before URLs if not present
        text = re.sub(r'([^\s])(http[s]?://)', r'\1 \2', text)
        text = re.sub(r'([^\s])(www\.)', r'\1 \2', text)

        return text

    @staticmethod
    def preserve_phone_numbers(text: str) -> str:
        """
        Normalize phone number formats without removing them
        Phone numbers are important fraud signals

        Args:
            text: Input text

        Returns:
            Text with normalized phone numbers
        """
        if pd.isna(text) or text is None:
            return ""

        # Normalize Indian phone number patterns
        # +91-9876543210 -> +91 9876543210
        # +919876543210 -> +91 9876543210
        text = re.sub(r'\+91-(\d{10})', r'+91 \1', text)
        text = re.sub(r'\+91(\d{10})', r'+91 \1', text)

        # Normalize hyphenated numbers: 98765-43210 -> 98765 43210
        text = re.sub(r'(\d{5})-(\d{5})', r'\1 \2', text)

        return text

    @staticmethod
    def normalize_punctuation(text: str) -> str:
        """
        Handle punctuation carefully
        Don't blindly remove all punctuation

        Args:
            text: Input text

        Returns:
            Text with normalized punctuation
        """
        if pd.isna(text) or text is None:
            return ""

        # Add space after punctuation if not present
        text = re.sub(r'([.,!?:;])([^\s\d])', r'\1 \2', text)

        # Remove excessive punctuation (more than 2 repeated)
        text = re.sub(r'([.,!?:;]){3,}', r'\1\1', text)

        return text

    @staticmethod
    def normalize_case(text: str) -> str:
        """
        Convert to lowercase for consistency

        Args:
            text: Input text

        Returns:
            Lowercase text
        """
        if pd.isna(text) or text is None:
            return ""

        return text.lower()

    @staticmethod
    def handle_special_characters(text: str) -> str:
        """
        Handle special characters while preserving multilingual text

        Args:
            text: Input text

        Returns:
            Text with handled special characters
        """
        if pd.isna(text) or text is None:
            return ""

        # Remove or normalize problematic characters
        # But preserve Tamil, Hindi, and other Unicode characters

        # Remove zero-width characters
        text = re.sub(r'[​‌‍﻿]', '', text)

        # Normalize currency symbols
        text = text.replace('₹', 'Rs ')
        text = text.replace('$', 'USD ')

        return text

    def preprocess_text(self, text: str, preserve_original: bool = False) -> str:
        """
        Complete preprocessing pipeline for a single SMS

        Args:
            text: Input SMS text
            preserve_original: If True, return original on empty result

        Returns:
            Preprocessed text
        """
        if pd.isna(text) or text is None:
            return ""

        original_text = str(text)

        # Apply preprocessing steps in order
        text = self.handle_special_characters(original_text)
        text = self.normalize_whitespace(text)
        text = self.preserve_urls(text)
        text = self.preserve_phone_numbers(text)
        text = self.normalize_punctuation(text)
        text = self.normalize_case(text)
        text = self.normalize_whitespace(text)  # Final whitespace cleanup

        # If preprocessing resulted in empty text, optionally preserve original
        if not text.strip() and preserve_original:
            return original_text.strip()

        return text

    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str = "text",
                            output_column: str = "text_processed") -> pd.DataFrame:
        """
        Preprocess all SMS texts in a dataframe

        Args:
            df: Input dataframe
            text_column: Name of column containing raw text
            output_column: Name of column for processed text

        Returns:
            Dataframe with added processed text column
        """
        logger.info(f"Preprocessing {len(df)} SMS messages...")

        # Create copy to avoid modifying original
        df = df.copy()

        # Apply preprocessing
        df[output_column] = df[text_column].apply(self.preprocess_text)

        # Check for any empty results
        empty_count = (df[output_column].str.strip() == "").sum()
        if empty_count > 0:
            logger.warning(f"⚠ {empty_count} messages became empty after preprocessing")

        logger.info(f"✓ Preprocessing complete")

        return df

    @staticmethod
    def get_text_statistics(texts: pd.Series) -> dict:
        """
        Calculate statistics about text length and content

        Args:
            texts: Series of text strings

        Returns:
            Dictionary of statistics
        """
        lengths = texts.str.len()
        word_counts = texts.str.split().str.len()

        stats = {
            "total_texts": len(texts),
            "min_length": int(lengths.min()),
            "max_length": int(lengths.max()),
            "mean_length": round(lengths.mean(), 2),
            "median_length": int(lengths.median()),
            "min_words": int(word_counts.min()),
            "max_words": int(word_counts.max()),
            "mean_words": round(word_counts.mean(), 2)
        }

        return stats

# CyberSentinel AI - SMS Fraud Detection

**Stage 1: Complete Machine Learning Pipeline**

A machine learning-based SMS fraud detection system for the Bharat AI-SoC Challenge 2026-27.

## 🎯 Project Overview

CyberSentinel AI is an offline, on-device AI cybersecurity assistant designed to detect:
- Network intrusions
- Phishing URLs
- **Fraudulent SMS communications** ← Current Stage

This Stage 1 implementation focuses exclusively on SMS fraud detection using machine learning.

## 📊 Dataset

- **Total Records:** 912 SMS messages
- **Training Set:** 730 messages (80%)
- **Test Set:** 182 messages (20%)
- **Classes:** Scam (804) and Legitimate/Ham (108)
- **Languages:** English, Hinglish, Tanglish
- **Split Method:** Group-aware stratified splitting (prevents template leakage)

**⚠️ Important:** This dataset is synthetic and represents common Indian scam patterns. Independent real-world testing is required before production deployment.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or 3.12
- Windows 10/11
- 4GB+ RAM recommended

### Installation

1. **Clone or navigate to project directory:**
   ```bash
   cd D:\Cyber
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   # PowerShell
   .\venv\Scripts\Activate.ps1
   
   # Git Bash
   source venv/Scripts/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Dataset Setup

Place the following 6 files in `data/input/`:

1. `sms_cleaned_master.csv`
2. `sms_train_group_aware.csv`
3. `sms_test_group_aware.csv`
4. `five_fold_group_manifest.csv`
5. `split_summary.csv`
6. `DATASET_AUDIT_AND_GUIDE.txt`

## 📋 Usage

### 1. Inspect Dataset

Verify dataset integrity and generate summary reports:

```bash
python scripts/inspect_dataset.py
```

**Outputs:**
- `reports/dataset/dataset_summary.csv`
- `reports/dataset/dataset_statistics.csv`

### 2. Train Models

Run the complete training pipeline with grouped cross-validation:

```bash
python scripts/train_models.py
```

**This will:**
- Preprocess SMS text
- Train 3 models (Logistic Regression, Linear SVM, LightGBM)
- Perform 4-fold grouped cross-validation
- Evaluate on held-out test set
- Select and save the best model
- Generate comprehensive reports

**Training Duration:** ~5-10 minutes on CPU

**Outputs:**
- Trained models in `models/trained/`
- Evaluation reports in `reports/models/`
- Confusion matrices and comparison plots in `reports/visualizations/`

### 3. Predict SMS

Analyze a single SMS message:

```bash
python scripts/predict_sms.py --message "Your bank account will be blocked. Update KYC immediately."
```

**Example Output:**
```
======================================================================
SMS FRAUD DETECTION ANALYSIS
======================================================================

Message:
Your bank account will be blocked. Update KYC immediately.

Prediction: SCAM
Model: lightgbm

⚠️ This message shows characteristics of a scam.
Recommendations:
• Do NOT click any links in this message
• Do NOT share personal information or OTPs
• Do NOT make any payments requested in this message
• Verify directly with the organization through official channels
• Report this message to your mobile carrier
======================================================================
```

**Test with legitimate message:**
```bash
python scripts/predict_sms.py --message "Your mobile recharge of Rs 499 was successful. Thank you."
```

## 🏗️ Project Structure

```
cyber/
├── data/
│   ├── input/              # Original dataset files
│   ├── processed/          # Preprocessed data
│   └── external/           # External data sources
│
├── src/
│   └── cybersentinel_sms/  # Core ML modules
│       ├── config.py               # Configuration settings
│       ├── data_loader.py          # Load CSV files
│       ├── data_validation.py     # Data integrity checks
│       ├── preprocessing.py        # Text preprocessing
│       ├── feature_extraction.py   # TF-IDF features
│       ├── train.py                # Model training
│       ├── cross_validation.py     # Grouped CV
│       ├── evaluation.py           # Model evaluation
│       ├── model_selection.py      # Select best model
│       └── prediction.py           # SMS prediction
│
├── scripts/
│   ├── inspect_dataset.py     # Dataset validation
│   ├── train_models.py        # Complete training pipeline
│   └── predict_sms.py         # Predict single SMS
│
├── models/
│   ├── trained/        # Saved model bundles
│   └── evaluation/     # Evaluation artifacts
│
├── reports/
│   ├── dataset/        # Dataset analysis reports
│   ├── models/         # Model performance reports
│   └── visualizations/ # Charts and plots
│
├── notebooks/          # Jupyter notebooks for EDA
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🤖 Models

### Implemented Models

1. **Logistic Regression**
   - Linear model with L2 regularization
   - Balanced class weights
   - Fast training and inference

2. **Linear SVM**
   - LinearSVC with balanced classes
   - Effective for text classification
   - Good generalization

3. **LightGBM**
   - Gradient boosting decision trees
   - Handles sparse TF-IDF features
   - Conservative hyperparameters to reduce overfitting

### Feature Engineering

- **Word-level TF-IDF:** Unigrams and bigrams (max 3000 features)
- **Character-level TF-IDF:** 2-4 character n-grams (max 2000 features)
- **Total Features:** ~5000 combined features

### Data Leakage Prevention

**Critical:** The following columns are NEVER used as model features:
- `label` (target variable)
- `category` (directly reveals label)
- `source`, `record_id` (metadata)
- `template_group_id`, `fold` (grouping info)

Only the `text` column is used for predictions.

## 📊 Evaluation Metrics

Models are evaluated using:

- **Accuracy:** Overall correctness
- **Precision (Scam):** How many predicted scams are actually scams
- **Recall (Scam):** How many actual scams are detected
- **F1-Score (Scam):** Harmonic mean of precision and recall
- **Precision/Recall/F1 (Ham):** Metrics for legitimate messages
- **Macro F1:** Average F1 across both classes
- **False Positive Rate:** Legitimate messages incorrectly flagged as scam
- **False Negative Rate:** Scams incorrectly marked as legitimate
- **Confusion Matrix:** Detailed breakdown of predictions

**Primary Selection Metric:** Validation Macro F1 (balanced performance across both classes)

## 🔬 Cross-Validation Strategy

**Grouped 4-Fold Cross-Validation** using `StratifiedGroupKFold`:

- Keeps SMS with similar templates in the same fold
- Prevents template leakage between train/validation splits
- Maintains class distribution across folds
- Random seed: 42 (reproducible)

**Why Grouped CV?**
If the same SMS template appears in both training and validation, the model can memorize patterns instead of learning generalizable fraud signals. Grouped CV ensures robust evaluation.

## ⚠️ Known Limitations

1. **Synthetic Data:** Model trained on synthetic Indian SMS data, not real-world messages
2. **Class Imbalance:** 88% scam, 12% legitimate (handled via class weighting)
3. **Small Dataset:** 912 total records limits model capacity
4. **Language Coverage:** English, Hinglish, Tanglish only
5. **Offline Only:** No internet required, but also no real-time threat intelligence
6. **No URL Verification:** Only text patterns analyzed, not actual URL safety
7. **Evolving Threats:** Scammers adapt; model requires regular retraining

## 🛠️ Development Notes

### Text Preprocessing

The preprocessing pipeline:
- Normalizes whitespace
- Preserves URLs and phone numbers (fraud signals)
- Maintains multilingual characters (Tamil, transliterated Hindi)
- Converts to lowercase
- Does NOT remove stopwords like "urgent", "blocked", "verify" (carry fraud meaning)

### Model Training Best Practices

✅ **DO:**
- Fit vectorizers on training data only
- Use grouped cross-validation
- Apply class weighting for imbalance
- Regularize to prevent overfitting
- Monitor train-validation gaps

❌ **DON'T:**
- Fit on entire dataset before splitting
- Use category or metadata as features
- Blindly remove all stopwords
- Ignore legitimate message recall
- Select models based on accuracy alone

## 🧪 Testing

Run unit tests (when implemented):

```bash
pytest tests/
```

## 📈 Future Work (Not in Stage 1)

- Network intrusion detection module
- Phishing URL detection module
- Llama LLM integration for explanations
- Android application
- Real-time on-device inference
- Model quantization for edge deployment
- Integration with Arm-based hardware

## 📝 Citation

Developed for **Bharat AI-SoC Challenge 2026-27, Problem Statement 3**

## 📄 License

[Add your license here]

## 🤝 Contributing

This is a competition project. External contributions are not accepted during the challenge period.

## 📞 Troubleshooting

### "Model not found" error
```bash
# Train a model first
python scripts/train_models.py
```

### Virtual environment activation fails
```powershell
# PowerShell execution policy issue
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Import errors
```bash
# Ensure you're in the virtual environment
source venv/Scripts/activate  # Git Bash
# or
.\venv\Scripts\Activate.ps1   # PowerShell

# Reinstall dependencies
pip install -r requirements.txt
```

### Low memory during training
- Close unnecessary applications
- Use simpler features (disable character-level TF-IDF in config)
- Reduce max_features in config.py

## 📚 Documentation

- **Dataset Audit:** See `data/input/DATASET_AUDIT_AND_GUIDE.txt`
- **Model Reports:** See `reports/models/` after training
- **API Documentation:** See module docstrings in `src/cybersentinel_sms/`

---

**Version:** 1.0.0  
**Status:** Stage 1 Complete  
**Last Updated:** November 2026

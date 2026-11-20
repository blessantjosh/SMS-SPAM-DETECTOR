"""
CyberSentinel AI - FastAPI Backend Server
Serves the SMS fraud detection ML model via REST API
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import time
from datetime import datetime

from cybersentinel_sms.prediction import SMSPredictor
from cybersentinel_sms.config import Config

# Initialize FastAPI app
app = FastAPI(
    title="CyberSentinel AI API",
    description="REST API for SMS fraud detection and cybersecurity analytics",
    version="1.0.0"
)

# CORS middleware - allow requests from Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:4201", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global predictor instance
predictor: Optional[SMSPredictor] = None


# Request/Response Models
class SMSAnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="SMS message to analyze")


class SMSAnalyzeResponse(BaseModel):
    sms: str
    prediction: str
    label: str
    model_name: str
    inference_time_ms: float
    probabilities: Optional[Dict[str, float]] = None
    confidence: Optional[float] = None
    risk_category: str
    recommendation: str
    timestamp: str


class SystemStatusResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: Optional[str] = None
    model_path: Optional[str] = None
    backend_version: str
    timestamp: str


class ModelPerformanceResponse(BaseModel):
    model_name: str
    test_accuracy: float
    f1_scam: float
    f1_ham: float
    macro_f1: float
    precision_scam: float
    recall_scam: float
    false_positive_rate: float
    false_negative_rate: float


class DashboardStatsResponse(BaseModel):
    total_analyzed: int
    scam_detected: int
    legitimate_detected: int
    suspicious_detected: int
    model_name: str
    last_updated: str


@app.on_event("startup")
async def startup_event():
    """Load ML model on startup"""
    global predictor
    try:
        print("Loading SMS fraud detection model...")
        predictor = SMSPredictor.from_latest_model("logistic_regression")
        print(f"[OK] Model loaded successfully: {predictor.model_name}")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        predictor = None


@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "message": "CyberSentinel AI API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "system_status": "/api/system/status",
            "analyze_sms": "/api/sms/analyze",
            "model_performance": "/api/model/performance",
            "dashboard_stats": "/api/dashboard/stats"
        }
    }


@app.get("/api/system/status", response_model=SystemStatusResponse, tags=["System"])
async def get_system_status():
    """Get system status and model information"""
    model_loaded = predictor is not None
    model_name = predictor.model_name if model_loaded else None

    model_path = None
    if model_loaded:
        model_path = str(Config.TRAINED_MODELS_DIR / f"{model_name}_latest.joblib")

    return SystemStatusResponse(
        status="online",
        model_loaded=model_loaded,
        model_name=model_name,
        model_path=model_path,
        backend_version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/sms/analyze", response_model=SMSAnalyzeResponse, tags=["SMS Detection"])
async def analyze_sms(request: SMSAnalyzeRequest):
    """
    Analyze an SMS message for fraud detection

    Returns prediction, confidence, and recommendations
    """
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please restart the server."
        )

    try:
        # Measure inference time
        start_time = time.time()

        # Predict
        result = predictor.predict_single(request.message, return_details=True)

        inference_time_ms = (time.time() - start_time) * 1000

        # Determine risk category
        risk_category = "high" if result['prediction'] == 'SCAM' else "low"
        if 'confidence' in result and result['confidence'] < 0.7:
            risk_category = "medium"

        # Get recommendation
        recommendation = predictor.get_recommendation(result)

        return SMSAnalyzeResponse(
            sms=result['sms'],
            prediction=result['prediction'],
            label=result['label'],
            model_name=predictor.model_name,
            inference_time_ms=round(inference_time_ms, 2),
            probabilities=result.get('probabilities'),
            confidence=result.get('confidence'),
            risk_category=risk_category,
            recommendation=recommendation,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/api/model/performance", response_model=ModelPerformanceResponse, tags=["Model"])
async def get_model_performance():
    """Get model performance metrics from test evaluation"""
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded"
        )

    try:
        # Load test results from saved evaluation
        model_name = predictor.model_name
        eval_file = Config.MODEL_REPORTS_DIR / f"evaluation_summary_{model_name}.json"

        if not eval_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Evaluation results not found"
            )

        with open(eval_file, 'r') as f:
            eval_data = json.load(f)

        metrics = eval_data['metrics']

        return ModelPerformanceResponse(
            model_name=model_name,
            test_accuracy=round(metrics['accuracy'], 4),
            f1_scam=round(metrics['f1_scam'], 4),
            f1_ham=round(metrics['f1_ham'], 4),
            macro_f1=round(metrics['macro_f1'], 4),
            precision_scam=round(metrics['precision_scam'], 4),
            recall_scam=round(metrics['recall_scam'], 4),
            false_positive_rate=round(metrics['false_positive_rate'], 4),
            false_negative_rate=round(metrics['false_negative_rate'], 4)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load performance metrics: {str(e)}"
        )


@app.get("/api/dashboard/stats", response_model=DashboardStatsResponse, tags=["Dashboard"])
async def get_dashboard_stats():
    """
    Get dashboard statistics

    NOTE: Currently returns demo stats. In production, this would track
    actual usage through a database or analytics service.
    """
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded"
        )

    # In a real application, these would come from a database
    # For now, return test set statistics
    return DashboardStatsResponse(
        total_analyzed=182,  # Test set size
        scam_detected=161,   # From test results
        legitimate_detected=21,
        suspicious_detected=0,
        model_name=predictor.model_name,
        last_updated=datetime.now().isoformat()
    )


@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("CYBERSENTINEL AI - BACKEND SERVER")
    print("=" * 70)
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("=" * 70)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from model import predict_message, load_model
from rules import analyze_rules

app = FastAPI(title="Indian Scam SMS & Call Detector")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Attempt to load model at startup
    # (Forces reload of the newly trained massive dataset model)
    model, vectorizer = load_model()
    if not model or not vectorizer:
        print("WARNING: Model artifacts not found. Please run train.py first.")

class PredictionRequest(BaseModel):
    message: str

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    reasons: list[str]
    safe_signals: list[str]
    highlighted_words: list[str]

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    message = request.message
    
    # 1. ML Prediction
    scam_prob = predict_message(message)
    ml_confidence = scam_prob
    
    # 2. Rule-based triggers (Weighted Score)
    risk_score, rules_reasons, safe_signals, highlighted_words = analyze_rules(message)
    
    # 3. Hybrid Classification Logic
    final_reasons = []
    
    # Calculate final effective risk, boosting with ML intuition if score is borderline
    effective_risk = risk_score
    
    if ml_confidence > 0.8:
        effective_risk += 3
        final_reasons.append("ML Model flagged language as highly dangerous (+3)")
    elif ml_confidence > 0.5:
        effective_risk += 1
        final_reasons.append("ML Model flagged language as suspicious (+1)")
        
    final_reasons.extend(rules_reasons)

    # Classification logic based on effective risk
    if effective_risk <= 0:
        prediction = "Safe"
        if not final_reasons and not safe_signals:
            safe_signals.append("Message appears to be normal and safe.")
    elif 1 <= effective_risk <= 3:
        prediction = "Suspicious"
    else:  # effective_risk >= 4
        prediction = "Dangerous"

    # Normalize final confidence percentage to report to the user
    # Baseline is the ML confidence, but heavily tilted by the explicit rule score
    confidence = ml_confidence
    if prediction == "Safe":
        # Confidence the message is SAFE
        confidence = 1.0 - ml_confidence
        if effective_risk < 0:
            confidence = min(0.99, confidence + (abs(effective_risk) * 0.1))
    else:
        # Confidence the message is SCAM (Suspicious or Dangerous)
        if effective_risk >= 4:
            confidence = max(0.90, ml_confidence + 0.2)
        elif effective_risk > 0:
            confidence = max(0.60, ml_confidence + 0.1)

    return PredictionResponse(
        prediction=prediction,
        confidence=round(min(confidence, 0.99), 4),
        reasons=final_reasons,
        safe_signals=safe_signals,
        highlighted_words=highlighted_words
    )

# Mount frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

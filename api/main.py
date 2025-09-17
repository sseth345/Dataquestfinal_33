from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib

# ======================================================
# Load both models
# ======================================================
# 1. Simple Isolation Forest model
with open("dataq.pkl", "rb") as f:
    saved_data = joblib.load(f)
scaler_simple = saved_data["scaler"]
clf_simple = saved_data["model"]

# 2. Advanced XGBoost model
clf_advanced = joblib.load("insider_threat_model.pkl")

# ======================================================
# FastAPI app
# ======================================================
app = FastAPI(title="Insider Threat Detection API", version="3.0")

# ======================================================
# Request bodies
# ======================================================

# --- Simple Features (dataq.pkl) ---
class SimpleUserFeatures(BaseModel):
    empid: str
    name: str
    num_logins: int
    avg_login_hour: float
    unique_pcs: int
    num_files_accessed: int

# --- Advanced Features (insider_threat_model.pkl) ---
class AdvancedUserFeatures(BaseModel):
    empid: str
    name: str
    size: float
    attachments: int
    external_email: int
    hour_sin: float
    hour_cos: float
    day_sin: float
    day_cos: float
    is_weekend: int
    unusual_hour: int
    large_email: int
    has_attachments: int
    size_deviation: float
    hour_deviation: float
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

# ======================================================
# Endpoints
# ======================================================

@app.get("/")
def home():
    return {
        "message": "🚀 Insider Threat Detection API is running!",
        "endpoints": ["/predict_simple", "/predict_advanced"]
    }

# --- Simple model prediction ---
@app.post("/predict_simple")
def predict_simple(features: SimpleUserFeatures):
    data = np.array([[
        features.num_logins,
        features.avg_login_hour,
        features.unique_pcs,
        features.num_files_accessed
    ]])

    data_scaled = scaler_simple.transform(data)
    pred = clf_simple.predict(data_scaled)[0]   # -1 = anomaly, 1 = normal
    score = float(clf_simple.decision_function(data_scaled)[0])

    return {
        "empid": features.empid,
        "name": features.name,
        "prediction": int(pred),
        "status": "anomaly" if pred == -1 else "normal",
        "confidence_score": score
    }

# --- Advanced model prediction ---
@app.post("/predict_advanced")
def predict_advanced(features: AdvancedUserFeatures):
    input_df = pd.DataFrame([features.dict()])

    pred = int(clf_advanced.predict(input_df)[0])        # 0 = normal, 1 = anomaly
    prob = clf_advanced.predict_proba(input_df)[0][1]    # probability of anomaly

    return {
        "empid": features.empid,
        "name": features.name,
        "prediction": pred,
        "status": "anomaly" if pred == 1 else "normal",
        "probability": float(prob)
    }

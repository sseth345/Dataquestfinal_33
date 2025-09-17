# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib
import os

# ======================================================
# Wrapper class for advanced model
# ======================================================
class InsiderThreatModel:
    def __init__(self, model, scaler, feature_columns):
        self.model = model
        self.scaler = scaler
        self.feature_columns = feature_columns

    def predict(self, X_df):
        X = X_df[self.feature_columns].values
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X_df):
        X = X_df[self.feature_columns].values
        X_scaled = self.scaler.transform(X)
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X_scaled)
        else:
            preds = self.model.predict(X_scaled)
            return np.column_stack([1 - preds, preds])

# ======================================================
# Paths
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIMPLE_MODEL_PATH = os.path.join(BASE_DIR, "dataq.pkl")
ADVANCED_MODEL_PATH = os.path.join(BASE_DIR, "insider_threat_model.pkl")

# ======================================================
# Load models
# ======================================================
# 1. Simple Isolation Forest model
if not os.path.exists(SIMPLE_MODEL_PATH):
    raise RuntimeError(f"{SIMPLE_MODEL_PATH} not found!")
with open(SIMPLE_MODEL_PATH, "rb") as f:
    saved_data = joblib.load(f)
scaler_simple = saved_data["scaler"]
clf_simple = saved_data["model"]

# 2. Advanced model
if not os.path.exists(ADVANCED_MODEL_PATH):
    raise RuntimeError(f"{ADVANCED_MODEL_PATH} not found!")
with open(ADVANCED_MODEL_PATH, "rb") as f:
    adv_data = joblib.load(f)

feature_columns = [
    "size", "attachments", "external_email", "hour_sin", "hour_cos",
    "day_sin", "day_cos", "is_weekend", "unusual_hour", "large_email",
    "has_attachments", "size_deviation", "hour_deviation",
    "openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"
]

clf_advanced = InsiderThreatModel(
    model=adv_data["model"], 
    scaler=adv_data["scaler"], 
    feature_columns=feature_columns
)

# ======================================================
# FastAPI app
# ======================================================
app = FastAPI(title="Insider Threat Detection API", version="3.0")

# ======================================================
# Request bodies
# ======================================================
class SimpleUserFeatures(BaseModel):
    empid: str
    name: str
    num_logins: int
    avg_login_hour: float
    unique_pcs: int
    num_files_accessed: int

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

@app.post("/predict_simple")
def predict_simple(features: SimpleUserFeatures):
    try:
        data = np.array([[
            features.num_logins,
            features.avg_login_hour,
            features.unique_pcs,
            features.num_files_accessed
        ]])
        data_scaled = scaler_simple.transform(data)
        pred = int(clf_simple.predict(data_scaled)[0])
        score = float(clf_simple.decision_function(data_scaled)[0])
        return {
            "empid": features.empid,
            "name": features.name,
            "prediction": pred,
            "status": "anomaly" if pred == -1 else "normal",
            "confidence_score": score
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/predict_advanced")
def predict_advanced(features: AdvancedUserFeatures):
    try:
        input_df = pd.DataFrame([features.dict()])
        pred = int(clf_advanced.predict(input_df)[0])
        prob = float(clf_advanced.predict_proba(input_df)[0][1])
        return {
            "empid": features.empid,
            "name": features.name,
            "prediction": pred,
            "status": "anomaly" if pred == 1 else "normal",
            "probability": prob
        }
    except Exception as e:
        return {"error": str(e)}

from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

# --------------------------
# Load model + scaler + features from pickle
# --------------------------
with open("dataq.pkl", "rb") as f:
    saved_data = joblib.load(f)

scaler = saved_data["scaler"]
clf = saved_data["model"]

# --------------------------
# FastAPI app
# --------------------------
app = FastAPI(title="Insider Threat Detection API", version="1.0")

# Define request body
class UserFeatures(BaseModel):
    empid: str
    name: str
    num_logins: int
    avg_login_hour: float
    unique_pcs: int
    num_files_accessed: int

# Prediction endpoint
@app.post("/predict")
def predict(features: UserFeatures):
    # Convert input into array
    data = np.array([[
        features.num_logins,
        features.avg_login_hour,
        features.unique_pcs,
        features.num_files_accessed
    ]])

    # Scale + predict
    data_scaled = scaler.transform(data)
    pred = clf.predict(data_scaled)[0]   # -1 = anomaly, 1 = normal
    score = float(clf.decision_function(data_scaled)[0])

    # Response with extra details
    return {
        "empid": features.empid,
        "name": features.name,
        "prediction": int(pred),
        "status": "anomaly" if pred == -1 else "normal",
        "confidence_score": score
    }

# Health check
@app.get("/")
def home():
    return {"message": "🚀 Insider Threat Detection API is running!"}

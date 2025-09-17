from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

# --------------------------
# Load model + scaler from pickle
# --------------------------
with open("dataq.pkl", "rb") as f:
    saved_data = joblib.load(f)

scaler = saved_data["scaler"]
clf = saved_data["model"]

# --------------------------
# FastAPI app
# --------------------------
app = FastAPI(title="Insider Threat Detection API", version="1.0")

# --------------------------
# Define request body with all features
# --------------------------
class UserFeatures(BaseModel):
    empid: str
    name: str
    num_logins: int
    avg_login_hour: float
    unique_pcs: int
    num_files_accessed_file: int
    num_files_to_removable_file: int
    num_files_from_removable_file: int
    unique_files_file: int
    avg_content_length_file: float
    num_emails_sent_email: int
    avg_num_recipients_email: float
    pct_emails_with_attachment_email: float
    avg_content_length_email: float
    avg_size_email: float
    num_decoy_files_accessed_decoy: int
    pct_decoy_files_accessed_decoy: float
    num_device_events_decoy: int
    num_connects_decoy: int
    num_disconnects_decoy: int
    unique_pcs_device_decoy: int
    avg_filetree_length_decoy: float
    num_http_requests_decoy: int
    unique_urls_decoy: int
    unique_pcs_http_decoy: int
    avg_content_length_http_decoy: float

# --------------------------
# Prediction endpoint
# --------------------------
@app.post("/predict")
def predict(features: UserFeatures):
    # Convert input into array in the exact order your model expects
    data = np.array([[
        features.num_logins,
        features.avg_login_hour,
        features.unique_pcs,
        features.num_files_accessed_file,
        features.num_files_to_removable_file,
        features.num_files_from_removable_file,
        features.unique_files_file,
        features.avg_content_length_file,
        features.num_emails_sent_email,
        features.avg_num_recipients_email,
        features.pct_emails_with_attachment_email,
        features.avg_content_length_email,
        features.avg_size_email,
        features.num_decoy_files_accessed_decoy,
        features.pct_decoy_files_accessed_decoy,
        features.num_device_events_decoy,
        features.num_connects_decoy,
        features.num_disconnects_decoy,
        features.unique_pcs_device_decoy,
        features.avg_filetree_length_decoy,
        features.num_http_requests_decoy,
        features.unique_urls_decoy,
        features.unique_pcs_http_decoy,
        features.avg_content_length_http_decoy
    ]])

    # Scale + predict
    data_scaled = scaler.transform(data)
    pred = clf.predict(data_scaled)[0]   # -1 = anomaly, 1 = normal
    score = float(clf.decision_function(data_scaled)[0])

    # Response
    return {
        "empid": features.empid,
        "name": features.name,
        "prediction": int(pred),
        "status": "anomaly" if pred == -1 else "normal",
        "confidence_score": score
    }

# --------------------------
# Health check
# --------------------------
@app.get("/")
def home():
    return {"message": "🚀 Insider Threat Detection API is running!"}

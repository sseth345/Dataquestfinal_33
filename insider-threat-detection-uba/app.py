#!/usr/bin/env python3
"""
Minimal Insider Threat Detection System for Hackathon
Works with basic packages - Flask, scikit-learn, pandas, numpy
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import json
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)

class ThreatDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'login_frequency', 'data_access_volume', 'after_hours_activity',
            'failed_login_attempts', 'unusual_location', 'privilege_escalation'
        ]
        
    def generate_sample_data(self, n_samples=1000):
        """Generate sample data for demo purposes"""
        np.random.seed(42)
        
        # Normal user behavior
        normal_data = {
            'user_id': [f'user_{i}' for i in range(int(n_samples * 0.9))],
            'login_frequency': np.random.normal(8, 2, int(n_samples * 0.9)),
            'data_access_volume': np.random.normal(100, 30, int(n_samples * 0.9)),
            'after_hours_activity': np.random.normal(2, 1, int(n_samples * 0.9)),
            'failed_login_attempts': np.random.poisson(0.5, int(n_samples * 0.9)),
            'unusual_location': np.random.binomial(1, 0.1, int(n_samples * 0.9)),
            'privilege_escalation': np.random.binomial(1, 0.05, int(n_samples * 0.9))
        }
        
        # Anomalous user behavior (insider threats)
        anomaly_count = int(n_samples * 0.1)
        anomaly_data = {
            'user_id': [f'threat_{i}' for i in range(anomaly_count)],
            'login_frequency': np.random.normal(20, 5, anomaly_count),  # High login frequency
            'data_access_volume': np.random.normal(500, 100, anomaly_count),  # High data access
            'after_hours_activity': np.random.normal(10, 3, anomaly_count),  # High after hours
            'failed_login_attempts': np.random.poisson(3, anomaly_count),  # More failed attempts
            'unusual_location': np.random.binomial(1, 0.7, anomaly_count),  # Often from unusual locations
            'privilege_escalation': np.random.binomial(1, 0.4, anomaly_count)  # More privilege escalation
        }
        
        # Combine data
        all_data = {}
        for key in normal_data:
            all_data[key] = list(normal_data[key]) + list(anomaly_data[key])
        
        return pd.DataFrame(all_data)
    
    def train_model(self, df=None):
        """Train the isolation forest model"""
        if df is None:
            df = self.generate_sample_data()
        
        # Prepare features
        X = df[self.feature_columns].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        return {"status": "Model trained successfully", "samples": len(df)}
    
    def predict_threat(self, user_data):
        """Predict if user behavior indicates threat"""
        if not self.is_trained:
            self.train_model()
        
        # Convert to dataframe if needed
        if isinstance(user_data, dict):
            user_data = pd.DataFrame([user_data])
        
        # Prepare features
        X = user_data[self.feature_columns].values
        X_scaled = self.scaler.transform(X)
        
        # Predict (-1 = anomaly/threat, 1 = normal)
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        results = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            threat_level = "HIGH" if pred == -1 else "LOW"
            confidence = abs(score) * 100
            
            user_id = user_data.iloc[i]['user_id'] if 'user_id' in user_data.columns else f'user_{i}'
            results.append({
                "user_id": user_id,
                "threat_level": threat_level,
                "confidence": round(confidence, 2),
                "anomaly_score": round(score, 4),
                "is_threat": pred == -1
            })
        
        return results

# Initialize detector
detector = ThreatDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/train', methods=['POST'])
def train_model():
    """Train the threat detection model"""
    try:
        result = detector.train_model()
        return jsonify({"success": True, "message": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_threat():
    """Predict threat for given user data"""
    try:
        data = request.json
        
        # Sample data if none provided
        if not data:
            data = {
                'user_id': 'demo_user',
                'login_frequency': random.uniform(5, 25),
                'data_access_volume': random.uniform(50, 600),
                'after_hours_activity': random.uniform(0, 15),
                'failed_login_attempts': random.randint(0, 5),
                'unusual_location': random.randint(0, 1),
                'privilege_escalation': random.randint(0, 1)
            }
        
        results = detector.predict_threat(data)
        return jsonify({"success": True, "results": results})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-sample', methods=['GET'])
def generate_sample_data():
    """Generate sample user data for testing"""
    sample = {
        'user_id': f'user_{random.randint(1, 1000)}',
        'login_frequency': round(random.uniform(1, 30), 2),
        'data_access_volume': round(random.uniform(10, 1000), 2),
        'after_hours_activity': round(random.uniform(0, 20), 2),
        'failed_login_attempts': random.randint(0, 10),
        'unusual_location': random.randint(0, 1),
        'privilege_escalation': random.randint(0, 1)
    }
    return jsonify(sample)

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data for visualization"""
    # Generate some fake real-time data
    current_time = datetime.now()
    dashboard_data = {
        'total_users': random.randint(500, 1000),
        'threats_detected': random.randint(5, 25),
        'high_risk_users': random.randint(2, 8),
        'recent_alerts': [
            {
                'time': (current_time - timedelta(minutes=random.randint(1, 60))).strftime('%H:%M'),
                'user': f'user_{random.randint(1, 100)}',
                'threat_level': random.choice(['HIGH', 'MEDIUM', 'LOW']),
                'description': random.choice([
                    'Unusual data access pattern detected',
                    'After-hours login from unusual location',
                    'Multiple failed login attempts',
                    'Privilege escalation detected'
                ])
            } for _ in range(5)
        ],
        'threat_trends': [random.randint(0, 10) for _ in range(24)]
    }
    return jsonify(dashboard_data)

if __name__ == '__main__':
    print("🚀 Starting Insider Threat Detection System...")
    print("📊 Training model with sample data...")
    detector.train_model()
    print("✅ Model ready!")
    print("🌐 Access the app at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
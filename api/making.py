import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb
import pickle

# ====================================================
# Generate dummy dataset (advanced features example)
# ====================================================
n = 500
data = pd.DataFrame({
    "size": np.random.randint(500, 200000, size=n),
    "attachments": np.random.randint(0, 5, size=n),
    "external_email": np.random.randint(0, 2, size=n),
    "hour_sin": np.sin(2 * np.pi * np.random.randint(0, 24, size=n) / 24),
    "hour_cos": np.cos(2 * np.pi * np.random.randint(0, 24, size=n) / 24),
    "day_sin": np.sin(2 * np.pi * np.random.randint(0, 7, size=n) / 7),
    "day_cos": np.cos(2 * np.pi * np.random.randint(0, 7, size=n) / 7),
    "is_weekend": np.random.randint(0, 2, size=n),
    "unusual_hour": np.random.randint(0, 2, size=n),
    "large_email": np.random.randint(0, 2, size=n),
    "has_attachments": np.random.randint(0, 2, size=n),
    "size_deviation": np.random.normal(0, 1, size=n),
    "hour_deviation": np.random.normal(0, 1, size=n),
    "openness": np.random.rand(n),
    "conscientiousness": np.random.rand(n),
    "extraversion": np.random.rand(n),
    "agreeableness": np.random.rand(n),
    "neuroticism": np.random.rand(n),
})

# Random labels: 0 = normal, 1 = anomaly
labels = np.random.randint(0, 2, size=n)

# ====================================================
# Train XGBoost Model
# ====================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(data)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, labels, test_size=0.2, random_state=42
)

clf = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

clf.fit(X_train, y_train)

# ====================================================
# Save model + scaler + feature names into PKL
# ====================================================
with open("insider_threat_model.pkl", "wb") as f:
    pickle.dump({"scaler": scaler, "model": clf, "features": data.columns.tolist()}, f)

print("✅ Saved insider_threat_model.pkl")

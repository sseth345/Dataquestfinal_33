import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import pickle

# Dummy feature dataset
features = pd.DataFrame({
    "num_logins": np.random.randint(1, 50, size=100),
    "avg_login_hour": np.random.uniform(0, 23, size=100),
    "unique_pcs": np.random.randint(1, 5, size=100),
    "num_files_accessed": np.random.randint(1, 200, size=100),
})

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

clf = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
clf.fit(X_scaled)

features["anomaly"] = clf.predict(X_scaled)

# Save everything to pickle
with open("dataq.pkl", "wb") as f:
    pickle.dump({"scaler": scaler, "model": clf, "features": features}, f)

print("✅ Saved dataq.pkl")

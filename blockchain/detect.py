import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies():
    # Load your real dataset
    df = pd.read_csv("dataresult1.csv")

    # Features to use (exclude user ID and existing labels)
    features = [
        'num_logins',
        'avg_login_hour',
        'unique_pcs',
        'num_files_accessed_file',
        'num_files_to_removable_file',
        'num_files_from_removable_file',
        'unique_files_file',
        'avg_content_length_file',
        'num_emails_sent_email',
        'avg_num_recipients_email',
        'pct_emails_with_attachment_email',
        'avg_content_length_email',
        'avg_size_email',
        'num_decoy_files_accessed_decoy',
        'pct_decoy_files_accessed_decoy'
    ]

    X = df[features]

    # Train Isolation Forest
    model = IsolationForest(contamination=0.1, random_state=42)
    df['predicted_anomaly'] = model.fit_predict(X)

    # Keep only anomalies
    anomalies = df[df['predicted_anomaly'] == -1]

    # Convert to dictionary for blockchain & dashboard
    return anomalies[['user'] + features].to_dict(orient="records")

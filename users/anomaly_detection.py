
import numpy as np
from sklearn.ensemble import IsolationForest
from .data_preprocessing import preprocess_energy_data

def detect_anomalies(user):
    df = preprocess_energy_data(user)
    X = df['amount_kwh'].values.reshape(-1, 1)

    model = IsolationForest(contamination=0.05)
    model.fit(X)
    anomalies = model.predict(X)
    anomaly_dates = df.index[anomalies == -1]

    return anomaly_dates
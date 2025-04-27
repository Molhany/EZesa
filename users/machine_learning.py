from sklearn.linear_model import LinearRegression
import numpy as np

def train_energy_model(df):
    df['day_of_year'] = df.index.dayofyear
    X = df['day_of_year'].values.reshape(-1, 1)
    y = df['amount_kwh'].values

    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_energy_usage(model, future_days):
    future_days = np.array(future_days).reshape(-1, 1)
    predictions = model.predict(future_days)
    return predictions
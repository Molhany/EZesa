
import requests
from .data_preprocessing import preprocess_energy_data

def get_weather_data(location):
    weather_data = {'temperature': 20, 'humidity': 60}  # Mock data
    return weather_data

def generate_recommendations(user):
    df = preprocess_energy_data(user)
    avg_daily_usage = df.resample('D').sum()['amount_kwh'].mean()
    weather_data = get_weather_data(user.address)

    recommendations = []

    if avg_daily_usage > 30:
        recommendations.append("Consider using energy-efficient appliances to reduce your daily usage.")
    if weather_data['temperature'] > 25:
        recommendations.append("The weather is warm. Use fans instead of air conditioning to save energy.")
    return recommendations
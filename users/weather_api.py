import requests

def get_weather(location):
    api_key = 'YOUR_API_KEY'  # Replace with your actual API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "q=" + location + "&appid=" + api_key
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        temperature = main["temp"]
        humidity = main["humidity"]
        weather_desc = data["weather"][0]["description"]
        return {
            "temperature": temperature,
            "humidity": humidity,
            "description": weather_desc
        }
    else:
        return None
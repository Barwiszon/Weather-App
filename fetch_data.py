import requests
import json
import os

API_KEY = "cfae0d677936d38ace227e59b340bf16"
API_URL = "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
#API_URL = "http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={key}&units=metric&lang=pl"

def fetch_weather_data(city):
    response = requests.get(API_URL.format(city=city, key=API_KEY))
    if response.status_code == 200:
        return response.json()
    else:
        print("Błąd pobierania danych API")
        return None

def save_weather_data(data, filename="weather_data.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_weather_data(filename="weather_data.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return None

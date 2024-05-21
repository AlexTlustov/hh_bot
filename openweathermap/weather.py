import requests
from translate import Translator

from settings import KEY_WEATHER

def get_weather(city):
    api_key = KEY_WEATHER
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city.lower()}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()

    if data['cod'] == 200:
        weather_en = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        forecast = f'The weather forecast for today is {weather_en}'
        translator= Translator(to_lang="ru")
        weather_ru = translator.translate(forecast)

        weather_info = f"Погода в {city}:\n"
        weather_info += f"Описание: {weather_ru}\n"
        weather_info += f"Температура: {temperature}°C\n"
        weather_info += f"Влажность: {humidity}%\n"
        weather_info += f"Скорость ветра: {wind_speed} м/с"

        return weather_info
    else:
        return "Не удалось получить данные о погоде."
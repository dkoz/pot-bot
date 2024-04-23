import random

weather_probabilities = {
    "Wet": [("rain", 40), ("storm", 40), ("overcast", 10), ("fog", 5), ("cloudy", 5)],
    "Dry": [("overcast", 10), ("fog", 10), ("cloudy", 10), ("clearsky", 70)],
    "Temperate": [("rain", 5), ("storm", 5), ("overcast", 10), ("fog", 10), ("cloudy", 20), ("clearsky", 50)],
    "Cold": [("rain", 0), ("storm", 0), ("overcast", 10), ("fog", 10), ("cloudy", 20), ("clearsky", 0), ("snow", 60)]
}

message_details = {
    "rain": "Rain with {humidity}% humidity and {wind_speed} mph winds.",
    "storm": "Storm with {humidity}% humidity and {wind_speed} mph winds.",
    "clearsky": "Clear skies with minimal cloud cover.",
    "cloudy": "Cloudy with scattered clouds.",
    "overcast": "Overcast skies, dense with clouds.",
    "fog": "Foggy conditions reducing visibility significantly.",
    "snow": "Heavy snowfall with accumulation expected."
}

def get_weather_update(season):
    weather_options = weather_probabilities[season]
    weights = [weight for _, weight in weather_options]
    weather_types = [weather for weather, _ in weather_options]
    selected_weather = random.choices(weather_types, weights=weights, k=1)[0]

    humidity = random.randint(70, 100)
    wind_speed = random.randint(1, 40)

    return message_details[selected_weather].format(humidity=humidity, wind_speed=wind_speed), selected_weather

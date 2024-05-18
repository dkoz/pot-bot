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

weather_emojis = {
    "rain": "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-32-512.png",
    "storm": "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-23-512.png",
    "overcast": "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-02-512.png",
    "fog": "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-27-512.png",
    "cloudy": "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-22-512.png",
    "clearsky": "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-01-512.png",
    "snow": "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-24-512.png"
}

season_descriptions = {
    "wet": [
        "The heavens open up, drenching the landscape. Adapt to the wet conditions and witness the world transform into a vibrant, waterlogged haven! 🌧️🦕",
        "Rainfall breathes life into the rivers, creating a thriving ecosystem. Dive into the wet season's adventure! 💦🌿",
        "Mud puddles abound as rain showers paint the environment in shades of green. Embrace the challenge and beauty of the wet season! 🌧️🍃",
        "The rhythmic sound of raindrops fills the air. Explore the lush, wet world as the wet season unfolds! 🌧️🌳"
    ],
    "dry": [
        "Feel the scorching sun and witness the landscape shimmer in the heat. Stay cool and hydrated as the dry season challenges your survival! ☀️🏜️",
        "Dust clouds rise with each step in the arid heat. Seek shade and navigate the challenges of the dry season's relentless sun. 🌞🦴",
        "Under the blazing sun, the land transforms into a desert oasis. Adapt to the dry season's trials and embrace the arid beauty. 🌵☀️",
        "Waves of heat distort the horizon as the dry season takes hold. Conquer the challenges and discover the secrets of the parched landscape. 🌞🔥"
    ],
    "temperate": [
        "Mild temperatures create the perfect setting for exploration. Venture out and savor the tranquility of the temperate season! 🍃🌤️",
        "Gentle breezes carry whispers of adventure through the temperate landscape. Embark on a journey in this ideal season for exploration. 🌳🌞",
        "Under a sunlit sky, enjoy the beauty of the temperate season. Discover the wonders of nature as you traverse this harmonious environment. 🌞🌳",
        "Balmy temperatures invite you to explore the temperate wonderland. Revel in the calm and beauty of the season's embrace. 🍂🌤️"
    ],
    "cold": [
        "Snow blankets the ground, turning the world into a winter wonderland. Adapt to the cold and embrace the challenges of the snowy landscape. ❄️⛄",
        "Frosty air and falling snowflakes transform the world into a serene winter realm. Experience the magic of the cold season's snowy landscapes. 🌨️❄️",
        "The crunch of snow beneath your feet echoes through the tranquil cold season. Navigate the challenges and uncover the secrets of the frozen landscape. ❄️🦕",
        "Breathe in the crisp, wintry air as the cold season unfolds. Survive and thrive in the snowy wilderness of this prehistoric world. ☃️❄️"
    ]
}

def get_weather_update(season):
    weather_options = weather_probabilities[season]
    weights = [weight for _, weight in weather_options]
    weather_types = [weather for weather, _ in weather_options]
    selected_weather = random.choices(weather_types, weights=weights, k=1)[0]

    humidity = random.randint(70, 100)
    wind_speed = random.randint(1, 40)

    return message_details[selected_weather].format(humidity=humidity, wind_speed=wind_speed), selected_weather

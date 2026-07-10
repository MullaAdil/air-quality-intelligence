import requests
from config import OPENWEATHER_API_KEY


def _degrees_to_compass(degrees):
    """Convert wind direction in degrees to compass label."""
    if degrees is None:
        return None
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]


def fetch_weather(city):
    """Fetch current weather conditions from OpenWeatherMap."""
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city},IN&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        wind = data.get("wind", {})
        wind_deg = wind.get("deg")
        weather = data.get("weather", [{}])[0]

        # OpenWeather returns m/s; convert to km/h for downstream use
        wind_speed_ms = wind.get("speed")
        wind_speed = round(wind_speed_ms * 3.6, 1) if wind_speed_ms is not None else None

        return {
            "wind_speed": wind_speed,
            "wind_direction": wind_deg,
            "wind_direction_text": _degrees_to_compass(wind_deg),
            "humidity": data.get("main", {}).get("humidity"),
            "temperature": data.get("main", {}).get("temp"),
            "description": weather.get("description"),
        }
    except Exception:
        return None

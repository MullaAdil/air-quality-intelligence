import requests
from config import WAQI_API_KEY

# WAQI uses slightly different city slugs for some Indian cities
WAQI_CITY_MAP = {
    "bengaluru": "bangalore",
    "delhi": "delhi",
    "mumbai": "mumbai",
    "chennai": "chennai",
    "kolkata": "kolkata",
    "hyderabad": "hyderabad",
    "pune": "pune",
    "ahmedabad": "ahmedabad",
}


def _pollutant_value(iaqi, key):
    """Extract pollutant value from WAQI iaqi block."""
    block = iaqi.get(key, {})
    return block.get("v") if isinstance(block, dict) else None


def _dominant_pollutant(pm25, pm10, no2, so2, co, o3):
    """Return pollutant name with the highest reading."""
    readings = {
        "PM2.5": pm25,
        "PM10": pm10,
        "NO2": no2,
        "SO2": so2,
        "CO": co,
        "O3": o3,
    }
    valid = {k: v for k, v in readings.items() if v is not None}
    if not valid:
        return None
    return max(valid, key=valid.get)


def fetch_aqi(city):
    """Fetch real-time AQI and pollutant data from WAQI API."""
    try:
        slug = WAQI_CITY_MAP.get(city.lower(), city.lower())
        url = f"https://api.waqi.info/feed/{slug}/?token={WAQI_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()

        if payload.get("status") != "ok":
            return None

        data = payload.get("data", {})
        iaqi = data.get("iaqi", {})

        pm25 = _pollutant_value(iaqi, "pm25")
        pm10 = _pollutant_value(iaqi, "pm10")
        no2 = _pollutant_value(iaqi, "no2")
        so2 = _pollutant_value(iaqi, "so2")
        co = _pollutant_value(iaqi, "co")
        o3 = _pollutant_value(iaqi, "o3")

        forecast_tomorrow_pm25 = None
        forecast = data.get("forecast", {}).get("daily", {}).get("pm25", [])
        if len(forecast) > 1:
            forecast_tomorrow_pm25 = forecast[1].get("avg")

        return {
            "aqi": data.get("aqi"),
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "so2": so2,
            "co": co,
            "o3": o3,
            "dominant_pollutant": _dominant_pollutant(pm25, pm10, no2, so2, co, o3),
            "station_name": data.get("city", {}).get("name"),
            "timestamp": data.get("time", {}).get("s"),
            "forecast_tomorrow_pm25": forecast_tomorrow_pm25,
        }
    except Exception:
        return None

from datetime import datetime, timezone

from data_collectors.aqi_fetcher import fetch_aqi
from data_collectors.weather_fetcher import fetch_weather
from data_collectors.fire_fetcher import fetch_fires
from data_collectors.traffic_fetcher import fetch_traffic
from data_collectors.osm_fetcher import fetch_nearby_sources


def collect_all_data(city, lat, lon):
    """Call all data fetchers and merge results into one dict."""
    return {
        "city": city,
        "lat": lat,
        "lon": lon,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aqi": fetch_aqi(city),
        "weather": fetch_weather(city),
        "fires": fetch_fires(lat, lon),
        "traffic": fetch_traffic(lat, lon),
        "nearby_sources": fetch_nearby_sources(lat, lon),
    }

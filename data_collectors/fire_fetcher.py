import csv
import io
import requests
from config import NASA_FIRMS_KEY
from utils import haversine_km


def fetch_fires(lat, lon, radius_km=150):
    """Fetch fire hotspots from NASA FIRMS within radius_km of a point."""
    try:
        west, south, east, north = lon - 2, lat - 2, lon + 2, lat + 2
        url = (
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            f"{NASA_FIRMS_KEY}/VIIRS_SNPP_NRT/{west},{south},{east},{north}/1"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if not response.text.strip():
            return []

        reader = csv.DictReader(io.StringIO(response.text))
        fires = []
        for row in reader:
            fire_lat = float(row.get("latitude", 0))
            fire_lon = float(row.get("longitude", 0))
            distance = round(haversine_km(lat, lon, fire_lat, fire_lon), 1)

            if distance <= radius_km:
                fires.append(
                    {
                        "latitude": fire_lat,
                        "longitude": fire_lon,
                        "brightness": float(row.get("bright_ti4") or row.get("brightness") or 0),
                        "confidence": row.get("confidence"),
                        "date": row.get("acq_date") or row.get("date"),
                        "distance_km": distance,
                    }
                )

        return fires
    except Exception:
        return []

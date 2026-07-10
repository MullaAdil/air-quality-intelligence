import requests
from config import TOMTOM_API_KEY


def fetch_traffic(lat, lon):
    """Fetch traffic flow and congestion data from TomTom API."""
    try:
        url = (
            "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
            f"?point={lat},{lon}&key={TOMTOM_API_KEY}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        segment = data.get("flowSegmentData", {})
        current_speed = segment.get("currentSpeed")
        free_flow_speed = segment.get("freeFlowSpeed")

        congestion_percent = None
        if current_speed is not None and free_flow_speed and free_flow_speed > 0:
            congestion_percent = round(
                ((free_flow_speed - current_speed) / free_flow_speed) * 100, 1
            )

        return {
            "current_speed": current_speed,
            "free_flow_speed": free_flow_speed,
            "congestion_percent": congestion_percent,
            "road_closure": segment.get("roadClosure", False),
            "confidence": segment.get("confidence"),
        }
    except Exception:
        return None

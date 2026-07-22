from feature_engineering.pollution_scorer import calculate_scores

def _aqi_category(aqi):
    """Map AQI value to health category label."""
    if aqi is None:
        return None
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def build_features(raw_data):
    """Add derived boolean and summary fields on top of collected data."""
    features = dict(raw_data)

    aqi_data = raw_data.get("aqi") or {}
    weather = raw_data.get("weather") or {}
    fires = raw_data.get("fires") or []
    traffic = raw_data.get("traffic") or {}
    nearby = raw_data.get("nearby_sources") or {}
    industries = nearby.get("industries") or []

    aqi_value = aqi_data.get("aqi")
    wind_speed = weather.get("wind_speed")
    congestion = traffic.get("congestion_percent")

    nearest_fire_km = None
    if fires:
        nearest_fire_km = min((f.get("distance_km") or 9999) for f in fires)

    features["is_high_aqi"] = aqi_value is not None and aqi_value > 150
    features["wind_is_low"] = wind_speed is not None and wind_speed < 5
    features["has_nearby_fire"] = len(fires) > 0
    features["fires_count"] = len(fires)
    features["nearest_fire_km"] = nearest_fire_km
    features["has_nearby_industry"] = len(industries) > 0
    features["industry_count"] = len(industries)
    features["traffic_is_heavy"] = congestion is not None and congestion > 50
    features["dominant_pollutant"] = aqi_data.get("dominant_pollutant")
    features["aqi_category"] = _aqi_category(aqi_value)

    # Calculate evidence scores
    features["pollution_scores"] = calculate_scores(features)
    
    print("\n===== ENGINEERED FEATURES =====")
    print(features)

    return features



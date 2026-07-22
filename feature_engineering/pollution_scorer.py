"""
Deterministic Pollution Evidence Scorer

This module calculates objective attribution weights across major pollution sources
(Traffic, Industry, Fire, and Dust) using chemical markers, spatial proximity, and meteorology.
"""


def calculate_scores(features):
    """
    Calculate deterministic evidence scores for pollution sources.

    Returns normalized percentage scores that always sum to ~100.
    """

    scores = {
        "Dust": 0,
        "Traffic": 0,
        "Industry": 0,
        "Fire": 0
    }

    # ---------------------------------------------------
    # Extract Evidence
    # ---------------------------------------------------

    aqi = features.get("aqi") or {}

    pm25 = aqi.get("pm25") or 0
    pm10 = aqi.get("pm10") or 0
    no2 = aqi.get("no2") or 0
    so2 = aqi.get("so2") or 0
    co = aqi.get("co") or 0

    weather = features.get("weather") or {}
    wind_speed = weather.get("wind_speed") or 0
    humidity = weather.get("humidity") or 0

    traffic = features.get("traffic") or {}
    congestion = traffic.get("congestion_percent") or 0

    fires = features.get("fires_count") or 0

    industries = features.get("industry_count") or 0

    nearby_sources = features.get("nearby_sources") or {}
    construction = len(nearby_sources.get("construction") or [])

    print("\n========== EVIDENCE ==========")
    print(f"PM2.5        : {pm25}")
    print(f"PM10         : {pm10}")
    print(f"NO₂          : {no2}")
    print(f"SO₂          : {so2}")
    print(f"CO           : {co}")
    print(f"Wind Speed   : {wind_speed}")
    print(f"Humidity     : {humidity}")
    print(f"Traffic (%)  : {congestion}")
    print(f"Fire Count   : {fires}")
    print(f"Industries   : {industries}")
    print(f"Construction : {construction}")

    # ===================================================
    # Dust Scoring
    # ===================================================

    if pm10 >= 150:
        scores["Dust"] += 50
    elif pm10 >= 100:
        scores["Dust"] += 40
    elif pm10 >= 75:
        scores["Dust"] += 25

    if pm25 >= 100:
        scores["Dust"] += 10

    if humidity < 40:
        scores["Dust"] += 10

    if construction > 0:
        scores["Dust"] += min(construction * 10, 20)

    if 5 <= wind_speed <= 15:
        scores["Dust"] += 10

    # ===================================================
    # Traffic Scoring
    # ===================================================

    if congestion >= 70:
        scores["Traffic"] += 40
    elif congestion >= 50:
        scores["Traffic"] += 30
    elif congestion >= 30:
        scores["Traffic"] += 20
    elif congestion >= 10:
        scores["Traffic"] += 10

    if no2 >= 40:
        scores["Traffic"] += 25
    elif no2 >= 20:
        scores["Traffic"] += 15
    elif no2 >= 10:
        scores["Traffic"] += 5

    if co >= 20:
        scores["Traffic"] += 20
    elif co >= 10:
        scores["Traffic"] += 10
    elif co >= 5:
        scores["Traffic"] += 5

    # ===================================================
    # Industry Scoring
    # ===================================================

    if industries > 0:
        scores["Industry"] += min(industries * 15, 40)

    if so2 >= 30:
        scores["Industry"] += 30
    elif so2 >= 15:
        scores["Industry"] += 20
    elif so2 >= 5:
        scores["Industry"] += 10

    # ===================================================
    # Fire Scoring
    # ===================================================

    if fires > 0:
        scores["Fire"] += min(fires * 20, 60)

    if fires > 0 and pm25 >= 100:
        scores["Fire"] += 20

    if fires > 0 and wind_speed < 10:
        scores["Fire"] += 10

    # ===================================================
    # Raw Scores
    # ===================================================

    print("\n========== RAW SCORES ==========")
    print(scores)

    # ===================================================
    # Normalize Scores
    # ===================================================

    total = sum(scores.values())

    if total == 0:
        normalized_scores = {
            source: 0
            for source in scores
        }
    else:
        normalized_scores = {
            source: round(score / total * 100)
            for source, score in scores.items()
        }

        # Ensure total equals exactly 100
        difference = 100 - sum(normalized_scores.values())

        if difference != 0:
            largest = max(normalized_scores, key=normalized_scores.get)
            normalized_scores[largest] += difference

    print("\n========== NORMALIZED SCORES ==========")
    print(normalized_scores)

    return normalized_scores
'''def calculate_scores(features):
    """
    Calculate evidence scores for each pollution source.
    """

    scores = {
        "Dust": 0,
        "Traffic": 0,
        "Industry": 0,
        "Fire": 0
    }

    # ------------------------
    # Extract Evidence
    # ------------------------

    aqi = features.get("aqi", {})

    pm25 = aqi.get("pm25", 0)
    pm10 = aqi.get("pm10", 0)
    no2 = aqi.get("no2", 0)
    so2 = aqi.get("so2", 0)
    co = aqi.get("co", 0)

    weather = features.get("weather", {})
    wind_speed = weather.get("wind_speed", 0)
    humidity = weather.get("humidity", 0)

    traffic = features.get("traffic", {})
    congestion = traffic.get("congestion_percent", 0)

    fires = features.get("fires_count", 0)

    industries = features.get("industry_count", 0)

    construction = len(
        features.get("nearby_sources", {}).get("construction", [])
    )

    print("\n========== EVIDENCE ==========")
    print(f"PM2.5: {pm25}")
    print(f"PM10 : {pm10}")
    print(f"NO2  : {no2}")
    print(f"SO2  : {so2}")
    print(f"CO   : {co}")
    print(f"Wind : {wind_speed}")
    print(f"Humidity : {humidity}")
    print(f"Traffic : {congestion}")
    print(f"Fire : {fires}")
    print(f"Industries : {industries}")
    print(f"Construction : {construction}")
    # ------------------------
    # Dust Score
    # ------------------------

    # High PM10 indicates dust/resuspended particles
    if pm10 >= 150:
        scores["Dust"] += 50
    elif pm10 >= 100:
        scores["Dust"] += 40
    elif pm10 >= 75:
        scores["Dust"] += 25

    # Dry weather favors dust
    if humidity < 40:
        scores["Dust"] += 10

    # Construction nearby
    if construction > 0:
        scores["Dust"] += 20

    # Wind can lift road dust
    if 5 <= wind_speed <= 15:
        scores["Dust"] += 10
    
    print("\n========== SCORES ==========")
    print(scores)

    return scores'''


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

    aqi = features.get("aqi", {})

    pm25 = aqi.get("pm25", 0)
    pm10 = aqi.get("pm10", 0)
    no2 = aqi.get("no2", 0)
    so2 = aqi.get("so2", 0)
    co = aqi.get("co", 0)

    weather = features.get("weather", {})
    wind_speed = weather.get("wind_speed", 0)
    humidity = weather.get("humidity", 0)

    traffic = features.get("traffic", {})
    congestion = traffic.get("congestion_percent", 0)

    fires = features.get("fires_count", 0)

    industries = features.get("industry_count", 0)

    construction = len(
        features.get("nearby_sources", {}).get("construction", [])
    )

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
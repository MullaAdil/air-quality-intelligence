

import sys
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_collectors.areas import CITY_AREAS
from data_collectors.collector_manager import collect_all_data
from feature_engineering.feature_builder import build_features
from ai_engine.brain import analyze

app = Flask(__name__)
CORS(app)

CITIES = {
    city: {
        "lat": list(areas.values())[0][0],
        "lon": list(areas.values())[0][1],
    }
    for city, areas in CITY_AREAS.items()
}


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/cities", methods=["GET"])
def cities():
    result = [
        {
            "name": name,
            "lat": coords["lat"],
            "lon": coords["lon"],
        }
        for name, coords in CITIES.items()
    ]

    return jsonify({"cities": result})

@app.route("/api/areas", methods=["GET"])
def areas():
    city = request.args.get("city", "").strip()

    city_key = next(
        (k for k in CITY_AREAS if k.lower() == city.lower()),
        None,
    )

    if not city_key:
        return jsonify({"areas": []})

    result = [
        {
            "name": area,
            "lat": coords[0],
            "lon": coords[1],
        }
        for area, coords in CITY_AREAS[city_key].items()
    ]

    return jsonify({"areas": result})
@app.route("/api/analyze", methods=["GET"])
def analyze_city():

    city = request.args.get("city", "").strip()
    area = request.args.get("area", "").strip()

    if not city:
        return jsonify(
            {
                "success": False,
                "error": "city parameter is required",
            }
        ), 400

    city_key = next(
        (k for k in CITIES if k.lower() == city.lower()),
        None,
    )

    if not city_key:
        return jsonify(
            {
                "success": False,
                "error": f"City '{city}' not supported",
            }
        ), 404

    try:

        # Use selected area coordinates if provided
        if area:
            if area not in CITY_AREAS[city_key]:
                return jsonify(
                    {
                        "success": False,
                        "error": f"Area '{area}' not found in {city_key}",
                    }
                ), 404

            lat, lon = CITY_AREAS[city_key][area]

        else:
            # Default to the first area of the city
            lat = CITIES[city_key]["lat"]
            lon = CITIES[city_key]["lon"]

        print("\n========== START ANALYSIS ==========")

        raw_data = collect_all_data(
            city_key,
            lat,
            lon,
        )
        print("✅ 1. Raw data collected")

        features = build_features(raw_data)
        print("✅ 2. Features built")

        print("✅ 3. Calling AI...")
        ai_analysis = analyze(features)

        print("✅ 4. AI returned")
        print(ai_analysis)

        if ai_analysis is None:
            return jsonify(
                {
                    "success": False,
                    "error": "AI analysis failed",
                }
            ), 500

        nearby = raw_data.get("nearby_sources") or {}
        fires = raw_data.get("fires") or []

        return jsonify(
            {
                "success": True,
                "city": city_key,
                "area": area if area else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),

                "aqi_data": raw_data.get("aqi"),
                "weather": raw_data.get("weather"),
                "traffic": raw_data.get("traffic"),

                "fires_count": len(fires),
                "nearby_industries": len(
                    nearby.get("industries") or []
                ),

                "features": {
                    "is_high_aqi": features.get("is_high_aqi"),
                    "wind_is_low": features.get("wind_is_low"),
                    "has_nearby_fire": features.get("has_nearby_fire"),
                    "fires_count": features.get("fires_count"),
                    "nearest_fire_km": features.get("nearest_fire_km"),
                    "has_nearby_industry": features.get("has_nearby_industry"),
                    "industry_count": features.get("industry_count"),
                    "traffic_is_heavy": features.get("traffic_is_heavy"),
                    "dominant_pollutant": features.get("dominant_pollutant"),
                    "aqi_category": features.get("aqi_category"),
                },

                "ai_analysis": ai_analysis,
            }
        )

    except Exception as e:

        import traceback

        print("\n========== BACKEND ERROR ==========")
        print(type(e).__name__)
        print(e)
        traceback.print_exc()

        return jsonify(
            {
                "success": False,
                "error": str(e),
            }
        ), 500
    
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
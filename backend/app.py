import sys
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_collectors.collector_manager import collect_all_data
from feature_engineering.feature_builder import build_features
from ai_engine.brain import analyze

app = Flask(__name__)
CORS(app)

CITIES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
}


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/api/cities", methods=["GET"])
def cities():
    """Return list of supported cities with coordinates."""
    result = [
        {"name": name, "lat": coords["lat"], "lon": coords["lon"]}
        for name, coords in CITIES.items()
    ]
    return jsonify({"cities": result})


@app.route("/api/analyze", methods=["GET"])
def analyze_city():
    """Collect data, build features, run AI analysis for a city."""
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"success": False, "error": "city parameter is required"}), 400

    # Case-insensitive city lookup
    city_key = next((k for k in CITIES if k.lower() == city.lower()), None)
    if not city_key:
        return jsonify({"success": False, "error": f"City '{city}' not supported"}), 404

    coords = CITIES[city_key]
    raw_data = collect_all_data(city_key, coords["lat"], coords["lon"])
    features = build_features(raw_data)
    ai_analysis = analyze(features)

    if ai_analysis is None:
        return jsonify({"success": False, "error": "AI analysis failed"}), 500

    nearby = raw_data.get("nearby_sources") or {}
    fires = raw_data.get("fires") or []

    return jsonify(
        {
            "success": True,
            "city": city_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "aqi_data": raw_data.get("aqi"),
            "weather": raw_data.get("weather"),
            "traffic": raw_data.get("traffic"),
            "fires_count": len(fires),
            "nearby_industries": len(nearby.get("industries") or []),
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)

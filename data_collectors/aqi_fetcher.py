"""
aqi_fetcher.py

Purpose:
    Fetch real-time Air Quality data from the selected AQI provider.

Responsibilities:
    - Connect to AQI API
    - Fetch current AQI
    - Handle API errors
    - Return clean structured data

This module DOES NOT:
    - Analyze pollution
    - Generate recommendations
    - Call the AI model
    - Perform feature engineering
"""


# Expected Output Format
#
# {
#     "city": "Delhi",
#     "aqi": 182,
#     "category": "Moderate",
#     "pollutants": {
#         "pm25": 94,
#         "pm10": 130,
#         "no2": 42,
#         "so2": 10,
#         "co": 0.8,
#         "o3": 22
#     },
#     "timestamp": "2026-06-24T10:30:00Z"
# }


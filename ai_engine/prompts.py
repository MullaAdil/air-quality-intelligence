import json


def build_prompt(features):
    """Build a detailed prompt for the AI pollution analysis model."""
    prompt = f"""You are an urban air quality intelligence expert analyzing pollution in Indian cities.

Analyze the following real-time environmental data and identify the most likely primary cause of air pollution.

DATA:
{json.dumps(features, indent=2, default=str)}

Based on this data, determine:
1. Primary pollution source (Traffic, Industry, Fire, Dust, or Mixed)
2. Confidence score (0-100) for the primary source
3. Secondary contributing sources with confidence scores
4. Clear reasoning in 2-3 sentences
5. AQI health level
6. Three specific government actions
7. Citizen health advisories in English, Hindi, Telugu, and Kannada
8. A brief forecast advisory based on forecast_tomorrow_pm25 if available

Return ONLY valid JSON with this exact structure (no markdown, no extra text):
{{
  "primary_source": "Traffic or Industry or Fire or Dust or Mixed",
  "primary_confidence": 72,
  "secondary_sources": [{{"source": "Industry", "confidence": 18}}],
  "reasoning": "2-3 sentence explanation",
  "aqi_level": "Unhealthy",
  "government_actions": ["action1", "action2", "action3"],
  "citizen_alert_english": "What to do",
  "citizen_alert_hindi": "Hindi translation",
  "citizen_alert_telugu": "Telugu translation",
  "citizen_alert_kannada": "Kannada translation",
  "forecast_advisory": "Based on tomorrow forecast, brief advice"
}}"""
    return prompt

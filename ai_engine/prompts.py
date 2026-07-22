"""
AI Prompt Builder

This file defines how the AI reasons about urban air quality.

Design Principles:
- Never guess.
- Every conclusion must be supported by evidence.
- Explain why other pollution sources were ruled out.
- Provide actionable recommendations.
"""

import json


def build_prompt(features):
    """Build prompt for explainable AI pollution analysis."""

    pollution_scores = features.get("pollution_scores", {})

    prompt = f"""
You are an Environmental Intelligence Expert.

Your purpose is to EXPLAIN pollution evidence.

IMPORTANT:

The pollution source confidence scores below were calculated by a deterministic Python evidence engine.

THESE SCORES ARE FINAL.

DO NOT modify them.

DO NOT invent new confidence values.

DO NOT estimate percentages.

Your job is ONLY to explain WHY those scores make sense.

========================
POLLUTION SOURCE SCORES
========================

{json.dumps(pollution_scores, indent=2)}

========================
REAL-TIME ENVIRONMENT DATA
========================

{json.dumps(features, indent=2, default=str)}

========================
REASONING RULES
========================

Base every conclusion ONLY on the supplied data.

Never invent facts or hallucinate percentages.

Never exaggerate certainty.

Use cautious scientific language.

If evidence is missing, say:

"No nearby industries were detected in the available map data."

"No nearby fire hotspots were detected in the available satellite data."

"No construction sites were detected in the available map data."

Never state that something does not exist—only describe what the available data indicates.

Instead of

"There are no industries."

say

"No industries were detected in the available map data."

Likewise for

• construction
• fire
• traffic

Explain
Explain

• why the highest score became the primary source.

• Always prioritize the pollutant that most strongly indicates that source.

For example:

- Dust should primarily be explained using PM10, with PM2.5 mentioned only as supporting evidence when appropriate.

- Traffic should primarily be explained using traffic congestion, NO₂ and CO.

- Industry should primarily be explained using nearby industries and SO₂.

- Fire should primarily be explained using nearby fire hotspots together with elevated PM2.5.

Do not use weak indicators as the main justification when stronger evidence exists.

Explain why the remaining pollution sources received lower scores based on the supplied evidence.

Government recommendations must directly target the primary pollution source.

Citizen alerts should match the AQI category.

Forecast advice should use tomorrow's PM2.5 forecast.

Scientific Reasoning Guidelines

- PM10 is the strongest indicator for dust and resuspended road dust.

- PM2.5 alone does NOT necessarily indicate dust.

- PM2.5 may originate from traffic, industrial emissions, biomass burning, secondary aerosols, or fine dust.

- If PM10 is elevated alongside moderate wind, dust becomes more likely.

- If PM2.5 is elevated without elevated PM10, avoid concluding that dust is the primary source unless other evidence supports it.

Always base explanations on the strongest available evidence rather than the highest pollutant concentration alone.

========================
OUTPUT
========================

Return ONLY valid JSON.

{{
    "primary_source": "Dust",
    "primary_confidence": 67,
    "secondary_sources": [
        {{
            "source": "Traffic",
            "confidence": 22
        }},
        {{
            "source": "Industry",
            "confidence": 11
        }}
    ],
    "reasoning": "Explain the supplied evidence without inventing new confidence values.",
    "aqi_level": "",
    "government_actions": [],
    "citizen_alert_english": "",
    "citizen_alert_hindi": "",
    "citizen_alert_telugu": "",
    "citizen_alert_kannada": "",
    "forecast_advisory": ""
}}
"""

    return prompt
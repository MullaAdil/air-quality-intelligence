import json
import re
from openai import OpenAI
from config import OPENROUTER_API_KEY
from ai_engine.prompts import build_prompt


def _parse_json_response(text):
    """Extract and parse JSON from model response, stripping markdown if present."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def analyze(features):
    """Send features to OpenRouter AI and return structured pollution analysis."""
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        prompt = build_prompt(features)
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return _parse_json_response(content)
    except Exception:
        return None

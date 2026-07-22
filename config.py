import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys loaded securely from environment variables
WAQI_API_KEY = os.getenv("WAQI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "")
NASA_FIRMS_KEY = os.getenv("NASA_FIRMS_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
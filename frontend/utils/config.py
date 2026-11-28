
from pathlib import Path
import os
from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Load environment variables once
load_dotenv(BASE_DIR / ".env")

# API configuration
API_BASE_URL = os.getenv(
    "VOLT_SIGHT_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

# API endpoints
FORECAST_ENDPOINT = f"{API_BASE_URL}/api/v1/forecast/predict"
FREQUENCY_ENDPOINT = f"{API_BASE_URL}/api/v1/frequency/predict-from-db"
OUTAGE_ENDPOINT = f"{API_BASE_URL}/api/v1/outages/predict-from-db"

from pathlib import Path
import sys
import pandas as pd

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

from app.routers.forecast import load_artifact
from app.services.grid_forecaster_service import get_grid_forecaster

print("Loading legacy model...")
legacy = load_artifact()
print("Legacy model loaded:", isinstance(legacy, dict), "keys:", len(legacy) if isinstance(legacy, dict) else "n/a")

print("Loading new team's models...")
forecaster = get_grid_forecaster()
bundle = BACKEND / "app" / "model_bundle"

frequency = pd.read_csv(bundle / "examples" / "frequency_sample.csv")
outage = pd.read_csv(bundle / "examples" / "outage_sample.csv")

frequency_result = forecaster.predict_frequency(frequency.tail(97).copy())
outage_result = forecaster.predict_outages(outage.copy())

print("Frequency smoke test:", frequency_result)
print("Outage smoke test regions:", list(outage_result["forecasts"].keys()))
print("ALL MODEL SMOKE TESTS PASSED")

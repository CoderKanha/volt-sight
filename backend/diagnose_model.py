
from pathlib import Path
import sys
import joblib

import sklearn._loss._loss as sklearn_loss_extension

# Compatibility alias for the serialized model.
sys.modules["_loss"] = sklearn_loss_extension

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "app"
    / "model_bundle"
    / "artifacts"
    / "frequency"
    / "national_frequency_hgb.joblib"
)

print("Model path:", MODEL_PATH)
print("Model exists:", MODEL_PATH.exists())

if not MODEL_PATH.exists():
    raise FileNotFoundError(MODEL_PATH)

try:
    model = joblib.load(MODEL_PATH)

    print("\nSUCCESS: Frequency model loaded!")
    print("Model type:", type(model))

except Exception:
    import traceback
    traceback.print_exc()

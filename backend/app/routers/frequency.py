import os
import pandas as pd
from fastapi import APIRouter, HTTPException

from app.schemas.grid_forecast import FrequencyForecastRequest
from app.services.grid_forecaster_service import get_grid_forecaster
from app.services.grid_history_service import fetch_frequency_grid_history

router = APIRouter(prefix="/api/v1/frequency", tags=["Frequency"])

FREQUENCY_TABLE = os.getenv("FREQUENCY_TABLE", "raw_frequency_sample")
FREQUENCY_DB_LIMIT = int(os.getenv("FREQUENCY_DB_LIMIT", "120"))

def _run(records):
    try:
        df = pd.DataFrame(records)
        result = get_grid_forecaster().predict_frequency(df)
        return {"status": "success", **result}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Frequency prediction failed.", "error_type": type(exc).__name__, "error": str(exc)},
        )

# Will not take input from user, will fetch data from backend with below endpoint
# @router.post("/predict")
# def predict_frequency(request: FrequencyForecastRequest):
#     return _run(request.records)

@router.post("/predict-from-db")
def predict_frequency_from_db():
    try:
        df = fetch_frequency_grid_history(FREQUENCY_TABLE, FREQUENCY_DB_LIMIT)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No rows found in public.{FREQUENCY_TABLE}.")
        return _run(df.to_dict(orient="records"))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"message": "Could not fetch frequency history.", "error": str(exc)})

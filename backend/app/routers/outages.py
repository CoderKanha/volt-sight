import os
import pandas as pd
from fastapi import APIRouter, HTTPException

from app.schemas.grid_forecast import OutageForecastRequest, DatabaseOutageRequest
from app.services.grid_forecaster_service import get_grid_forecaster
from app.services.grid_history_service import fetch_daily_grid_history
from app.services.shortage_service import calculate_shortage

router = APIRouter(prefix="/api/v1/outages", tags=["Outages"])

OUTAGE_TABLE = os.getenv("OUTAGE_TABLE", "raw_outage_sample")
OUTAGE_DB_LIMIT = int(os.getenv("OUTAGE_DB_LIMIT", "120"))

def _run(records, shortage_inputs=None):
    try:
        df = pd.DataFrame(records)
        if "date" not in df.columns:
            raise ValueError("Outage history must contain a 'date' column.")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
        if df["date"].duplicated().any():
            raise ValueError("Duplicate daily dates detected. Keep one row per date.")
        if len(df) < 15:
            raise ValueError("The outage model requires at least 15 daily records.")

        result = get_grid_forecaster().predict_outages(df)
        result["shortage_calculations"] = {}
        shortage_inputs = shortage_inputs or {}

        for region_key, prediction in result["forecasts"].items():
            supplied = shortage_inputs.get(region_key)
            if supplied is None:
                result["shortage_calculations"][region_key] = {
                    "shortage_mw": None,
                    "shortage_percentage": None,
                    "outage_burden_percentage_of_demand": None,
                    "status": "demand_and_pre_outage_supply_required",
                }
                continue

            values = supplied.model_dump() if hasattr(supplied, "model_dump") else supplied
            result["shortage_calculations"][region_key] = calculate_shortage(
                demand_mw=float(values["demand_mw"]),
                available_supply_before_outages_mw=float(
                    values["available_supply_before_outages_mw"]
                ),
                predicted_outage_mw=float(prediction["predicted_outage_mw"]),
            )

        result["shortage_metric_note"] = (
            "The model predicts forced outage capacity, not unmet demand. "
            "Shortage percentage is calculated only when demand and supply "
            "before subtracting predicted outages are provided."
        )
        return {"status": "success", **result}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Outage prediction failed.", "error_type": type(exc).__name__, "error": str(exc)},
        )

# Will not take input from user, will fetch data from backend with below endpoint
# @router.post("/predict")
# def predict_outages(request: OutageForecastRequest):
#     return _run(request.records, request.shortage_inputs)

@router.post("/predict-from-db")
def predict_outages_from_db(request: DatabaseOutageRequest | None = None):
    try:
        df = fetch_daily_grid_history(OUTAGE_TABLE, OUTAGE_DB_LIMIT)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No rows found in public.{OUTAGE_TABLE}.")
        return _run(df.to_dict(orient="records"), request.shortage_inputs if request else None)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"message": "Could not fetch outage history.", "error": str(exc)})

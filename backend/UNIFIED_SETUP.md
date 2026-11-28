# VoltSight unified FastAPI application

Your original FastAPI app and both model families now run in ONE FastAPI application and ONE Python environment.

## What remains from your project
- Existing CSV upload and database retrieval APIs.
- Existing `/api/v1/forecast/*` endpoints.
- Existing `backend/models/india_grid_forecaster.pkl`.
- Existing Neon SQLAlchemy engine and data ingestion behavior.

## What was added
- Original handoff bundle under `backend/app/model_bundle/`.
- `POST /api/v1/outages/predict`
- `POST /api/v1/outages/predict-from-db`
- `POST /api/v1/frequency/predict`
- `POST /api/v1/frequency/predict-from-db`
- Shortage MW and shortage percentage calculation.

## One shared dependency environment
The common runtime is pinned to the existing backend's resolved Python 3.13 lock versions:
- Python 3.13
- NumPy 2.5.5
- Pandas 3.1.1
- Scikit-learn 1.9.1
- Joblib 1.6.0
- LightGBM 4.7.0

The old `uv.lock` was removed because its dependency resolution must be regenerated against the new exact pins.

The supplied handoff estimators were serialized with scikit-learn 1.6.1. A narrow compatibility shim in `app/services/grid_forecaster_service.py` maps the older `SimpleImputer._fit_dtype` pickle state to the `_fill_dtype` attribute expected by newer scikit-learn. This is based on the actual observed inference error and was tested locally against the supplied handoff artifacts on scikit-learn 1.8.0: all four artifacts loaded, the frequency sample predicted, and the outage sample predicted. Still run the included smoke test after installing the exact pinned 1.9.1 environment before production deployment.

The old model was previously unable to load under pandas 2.2.3 due to a pandas `StringDtype` pickle mismatch. The shared environment now uses the existing project's pandas 3.1.1 version, matching the old backend's lock. Do not downgrade pandas to the handoff's 2.2.3.

## Install
From `backend/`:
```bash
uv lock
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `/docs`. Both model families are loaded at application startup. If either artifact cannot load, startup fails rather than serving partial or misleading predictions.

## New model input requirements
- Outage model: at least 15 daily records, all required raw columns from `app/model_bundle/examples/outage_sample.csv`. The model class performs feature engineering internally.
- Frequency model: at least 97 consecutive 15-minute records; sample schema is `app/model_bundle/examples/frequency_sample.csv`.
- The DB endpoint defaults to tables `raw_outage_sample` and `raw_frequency_sample`. These names follow the existing upload API if files are uploaded as `outage_sample.csv` and `frequency_sample.csv`.
- Set `OUTAGE_TABLE` and `FREQUENCY_TABLE` if your actual table names differ.

## Shortage calculation
The outage model predicts forced outage capacity (MW), not unmet demand. Supply the following for a region:
- `demand_mw`
- `available_supply_before_outages_mw`

The API calculates:
`adjusted_supply = max(available_supply_before_outages_mw - predicted_outage_mw, 0)`
`shortage_mw = max(demand_mw - adjusted_supply, 0)`
`shortage_percentage = shortage_mw / demand_mw * 100`

Do not pass supply that has already had this predicted outage subtracted.

## Important
- The handoff manifest's training snapshot ends 2026-11-21. Validate on newer observations.
- `joblib`/pickle files can execute code while loading. Only use the model files supplied by your trusted team.
- Restrict CORS and add authentication before public deployment.


import os
import pickle
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import pandas as pd

import logging
from fastapi import APIRouter, HTTPException, Request

from datetime import date
from sqlalchemy import text


from app.core.database import engine
from app.schemas.forecast import ForecastRequest


router = APIRouter(prefix="/api/v1/forecast", tags=["Forecast"])

MODEL_PATH = Path(
    os.getenv(
        "FORECAST_MODEL_PATH",
        "models/india_grid_forecaster.pkl"
    )
)

CALENDAR_COLUMNS = {
    "is_post_2023",
    "target_month",
    "target_dayofweek",
    "target_is_weekend",
    "target_sin_doy",
    "target_cos_doy",
}

GENERATED_SUFFIXES = (
    "_lag1",
    "_lag6",
    "_roll7_mean",
    "_roll14_mean",
)


def load_artifact():
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")

    # Only load a pickle artifact that you trust.
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


@asynccontextmanager
async def lifespan(app):
    app.state.forecaster = load_artifact()
    yield
    app.state.forecaster = None


def build_latest_features(history: list[dict], artifact: dict):
    feature_cols = artifact["feature_cols"]
    targets = artifact["all_targets"]

    # Identify original columns from the stored feature list.
    base_cols = [
        c for c in feature_cols
        if c not in CALENDAR_COLUMNS
        and not c.endswith(GENERATED_SUFFIXES)
    ]

    raw = pd.DataFrame(history)

    if "date" not in raw.columns:
        raise ValueError("Every history record must contain 'date'.")

    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")

    if raw["date"].isna().any():
        raise ValueError("One or more dates are invalid.")

    raw = (
        raw.sort_values("date")
        .drop_duplicates("date", keep="last")
        .reset_index(drop=True)
    )

    missing = [c for c in base_cols if c not in raw.columns]
    if missing:
        raise ValueError(
            "Missing required input columns: " + ", ".join(missing)
        )

    # Match the notebook's continuous daily calendar.
    raw = raw[["date"] + base_cols]

    full_dates = pd.date_range(
        raw["date"].min(),
        raw["date"].max(),
        freq="D"
    )

    df = (
        raw.set_index("date")
        .reindex(full_dates)
        .rename_axis("date")
        .reset_index()
    )

    # The notebook treats these two wind targets as structural zeros.
    for col in ["wind_gen_er_mu", "wind_gen_ner_mu"]:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)

    target_date = df["date"] + pd.Timedelta(days=1)

    # Calendar features for the day being forecast.
    df["is_post_2023"] = (
        df["date"] >= pd.Timestamp("2023-01-01")
    ).astype(int)

    df["target_month"] = target_date.dt.month
    df["target_dayofweek"] = target_date.dt.dayofweek
    df["target_is_weekend"] = (
        target_date.dt.dayofweek >= 5
    ).astype(int)

    day_of_year = target_date.dt.dayofyear

    df["target_sin_doy"] = np.sin(
        2 * np.pi * day_of_year / 365.25
    )
    df["target_cos_doy"] = np.cos(
        2 * np.pi * day_of_year / 365.25
    )

    # Historical features: exactly as in the notebook.
    for col in targets:
        df[f"{col}_lag1"] = df[col].shift(1)
        df[f"{col}_lag6"] = df[col].shift(6)

        df[f"{col}_roll7_mean"] = (
            df[col].rolling(window=7, min_periods=1).mean()
        )

        df[f"{col}_roll14_mean"] = (
            df[col].rolling(window=14, min_periods=1).mean()
        )

    latest = df.iloc[[-1]].copy()

    if latest[feature_cols].isna().any().any():
        bad = latest[feature_cols].columns[
            latest[feature_cols].isna().any()
        ].tolist()

        raise ValueError(
            "Latest row contains missing model features: "
            + ", ".join(bad)
        )

    return latest, feature_cols


def reconcile_group(
    top_col,
    bottom_cols,
    predictions,
    intervals,
    covariance,
    allow_negative=False
):
    columns = [top_col] + bottom_cols

    y_hat = np.array(
        [predictions[c] for c in columns],
        dtype=float
    )

    k = len(bottom_cols)
    S = np.vstack([np.ones((1, k)), np.eye(k)])

    W_inv = np.linalg.pinv(covariance)

    P = (
        S
        @ np.linalg.pinv(S.T @ W_inv @ S)
        @ S.T
        @ W_inv
    )

    reconciled = P @ y_hat

    if not allow_negative:
        reconciled = np.clip(reconciled, 0, None)

    for col, value in zip(columns, reconciled):
        new_value = round(float(value), 2)
        delta = new_value - predictions[col]

        predictions[col] = new_value

        if col in intervals:
            for q in ("q10", "q90"):
                adjusted = intervals[col][q] + delta
                intervals[col][q] = round(
                    adjusted if allow_negative
                    else max(0.0, adjusted),
                    2
                )


def reconcile_hydro_children(
    children,
    predictions,
    intervals,
    covariance,
    total_value
):
    y = np.array([predictions[c] for c in children], dtype=float)
    one = np.ones(len(children))

    W = covariance

    adjusted = (
        y
        + W @ one * (total_value - y.sum())
        / (one @ W @ one)
    )

    for _ in range(10):
        adjusted = np.clip(adjusted, 0, None)
        gap = total_value - adjusted.sum()

        if abs(gap) < 1e-9:
            break

        free = adjusted > 0
        if not np.any(free):
            break

        weights = W[np.ix_(free, free)] @ np.ones(free.sum())

        if abs(weights.sum()) < 1e-12:
            break

        adjusted[free] += weights * gap / weights.sum()

    for col, value in zip(children, adjusted):
        new_value = round(float(value), 2)
        delta = new_value - predictions[col]
        predictions[col] = new_value

        if col in intervals:
            for q in ("q10", "q90"):
                intervals[col][q] = round(
                    max(0.0, intervals[col][q] + delta),
                    2
                )


def run_forecast(latest, feature_cols, artifact):
    predictions = {}
    intervals = {}

    targets = artifact["all_targets"]
    persistence_targets = set(artifact["persistence_targets"])
    models = artifact["fitted_models"]

    today = latest.iloc[0]
    forecast_date = (
        pd.Timestamp(today["date"]) + pd.Timedelta(days=1)
    ).strftime("%Y-%m-%d")

    X = latest[feature_cols]

    for target in targets:
        today_value = float(today[target])
        allow_negative = artifact["allow_neg_flags"].get(
            target, target.startswith("ie_actual_")
        )

        if target not in persistence_targets:
            target_models = models[target]

            values = {}

            for label in ("q10", "q50", "q90"):
                predicted_change = float(
                    target_models[label].predict(X)[0]
                )

                value = today_value + predicted_change

                if not allow_negative:
                    value = max(0.0, value)

                values[label] = value

            values["q10"] = min(values["q10"], values["q50"])
            values["q90"] = max(values["q90"], values["q50"])

            predictions[target] = round(values["q50"], 2)

            intervals[target] = {
                "q10": round(values["q10"], 2),
                "q90": round(values["q90"], 2)
            }

        else:
            # Same persistence approach used in the notebook.
            month = int(today["target_month"])

            d10, d90 = artifact[
                "persistence_seasonal_diffs"
            ][target][month]

            p50 = today_value
            p10 = today_value + d10
            p90 = today_value + d90

            if not allow_negative:
                p50 = max(0.0, p50)
                p10 = max(0.0, p10)
                p90 = max(0.0, p90)

            predictions[target] = round(p50, 2)

            intervals[target] = {
                "q10": round(min(p10, p50), 2),
                "q90": round(max(p90, p50), 2)
            }

    # Structural zeros.
    for col in ["wind_gen_er_mu", "wind_gen_ner_mu"]:
        predictions[col] = 0.0
        intervals[col] = {"q10": 0.0, "q90": 0.0}

    # Apply the same reconciliation hierarchy as the notebook.
    cov = artifact["cov_cache"]

    reconcile_group(
        "gen_total_mu",
        artifact["national_sources"],
        predictions,
        intervals,
        cov["gen_total_mu"]
    )

    hydro = artifact["reg_hydro"]

    reconcile_hydro_children(
        hydro,
        predictions,
        intervals,
        cov["__children__" + hydro[0]],
        predictions["gen_hydro_mu"]
    )

    for top_col, child_key in [
        ("solar_gen_total_mu", "reg_solar"),
        ("wind_gen_total_mu", "reg_wind"),
        ("energy_met_total_mu", "reg_energy_met"),
        ("ie_actual_total_mu", "reg_ie_actual")
    ]:
        reconcile_group(
            top_col,
            artifact[child_key],
            predictions,
            intervals,
            cov[top_col],
            allow_negative=(top_col == "ie_actual_total_mu")
        )

    # Calculate exchange-adjusted regional generation.
    regional_net = {}
    regional_gross = {}

    for region in artifact["regions"]:
        energy = predictions[f"energy_met_{region}_mu"]
        exchange = predictions[f"ie_actual_{region}_mu"]

        regional_net[region] = round(energy - exchange, 2)

    sum_net = sum(regional_net.values())

    if abs(sum_net) < 1e-12:
        raise ValueError(
            "Cannot calculate regional gross generation: "
            "sum of regional net generation is zero."
        )

    multiplier = predictions["gen_total_mu"] / sum_net

    for region in artifact["regions"]:
        regional_gross[region] = round(
            regional_net[region] * multiplier, 2
        )

    return {
        "forecast_date": forecast_date,
        "data_up_to_date": pd.Timestamp(today["date"]).strftime(
            "%Y-%m-%d"
        ),
        "unit": "MU",
        "national_forecast": {
            key: {
                "predicted_mu": predictions[key],
                "lower_80pct_mu": intervals[key]["q10"],
                "upper_80pct_mu": intervals[key]["q90"]
            }
            for key in (
                ["gen_total_mu"] + artifact["national_sources"]
                + artifact["national_totals"]
            )
        },
        "all_target_forecasts": {
            key: {
                "predicted_mu": predictions[key],
                "lower_80pct_mu": intervals[key]["q10"],
                "upper_80pct_mu": intervals[key]["q90"]
            }
            for key in targets
        },
        "regional_forecast": {
            region.upper(): {
                "energy_met_mu": predictions[
                    f"energy_met_{region}_mu"
                ],
                "net_exchange_mu": predictions[
                    f"ie_actual_{region}_mu"
                ],
                "net_generation_mu": regional_net[region],
                "gross_generation_mu": regional_gross[region],
                "hydro_mu": predictions[f"hydro_gen_{region}_mu"],
                "solar_mu": predictions[f"solar_gen_{region}_mu"],
                "wind_mu": predictions.get(
                    f"wind_gen_{region}_mu", 0.0
                )
            }
            for region in artifact["regions"]
        }
    }

def get_previous_records(before_date: date, limit: int = 13):
    """Return the latest unique daily rows before before_date, oldest first."""
    query = text("""
        SELECT *
        FROM (
            SELECT DISTINCT ON (date::DATE) *
            FROM raw_study1_daily
            WHERE date::DATE < CAST(:before_date AS DATE)
            ORDER BY date::DATE DESC, ctid DESC
        ) AS daily
        ORDER BY date::DATE DESC
        LIMIT :limit
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query, {"before_date": before_date, "limit": limit}
        ).mappings().all()

    records = [dict(row) for row in rows]
    records.reverse()
    return records


def _model_dump(model):
    """Support Pydantic v2 and v1."""
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_none=True)
    return model.dict(exclude_none=True)


def get_expected_base_columns(artifact: dict):
    """Recover raw columns required by the notebook's feature pipeline."""
    feature_cols = artifact["feature_cols"]
    return [
        col for col in feature_cols
        if col not in CALENDAR_COLUMNS
        and not col.endswith(GENERATED_SUFFIXES)
    ]


def debug_forecast_input(latest_record: dict, artifact: dict):
    """Return useful diagnostics without exposing credentials or row contents."""
    expected = get_expected_base_columns(artifact)
    received = set(latest_record.keys())
    missing = [col for col in expected if col not in received]
    null_fields = [
        col for col in expected
        if col in latest_record and latest_record[col] is None
    ]
    return {
        "date_received": str(latest_record.get("date")),
        "received_field_count": len(received),
        "expected_raw_field_count": len(expected),
        "missing_required_fields": missing,
        "null_required_fields": null_fields,
        "input_is_complete": not missing and not null_fields,
        "model_path": str(MODEL_PATH),
        "model_file_exists": MODEL_PATH.exists(),
    }


@router.get("/debug/model")
def debug_model(request: Request):
    """Check model loading and database connectivity/table visibility."""
    artifact = getattr(request.app.state, "forecaster", None)
    if artifact is None:
        raise HTTPException(status_code=503, detail="Forecast model is not loaded.")

    db_status = {"connected": False, "table_exists": False, "row_count": None}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            db_status["connected"] = True
            table_result = connection.execute(text("""
                SELECT to_regclass('public.raw_study1_daily')
            """)).scalar()
            db_status["table_exists"] = table_result is not None
            if db_status["table_exists"]:
                db_status["row_count"] = connection.execute(text(
                    "SELECT COUNT(*) FROM raw_study1_daily"
                )).scalar_one()
    except Exception as exc:
        db_status["error"] = str(exc)

    return {
        "model_loaded": True,
        "model_path": str(MODEL_PATH.resolve()),
        "feature_count": len(artifact.get("feature_cols", [])),
        "target_count": len(artifact.get("all_targets", [])),
        "expected_raw_columns": get_expected_base_columns(artifact),
        "database": db_status,
    }


@router.post("/debug/input")
def debug_input(payload: ForecastRequest, request: Request):
    """Check whether latest_record contains every raw model input column."""
    artifact = getattr(request.app.state, "forecaster", None)
    if artifact is None:
        raise HTTPException(status_code=503, detail="Forecast model is not loaded.")

    latest = _model_dump(payload.latest_record)
    diagnostics = debug_forecast_input(latest, artifact)
    return diagnostics


def get_latest_records(as_of_date: date | None = None, limit: int = 14):
    """Fetch the latest unique daily records from Neon, oldest first.

    If as_of_date is omitted, use the latest date available in the table.
    When duplicate rows exist for a date, the row with the greatest ctid is
    selected as a deterministic tie-breaker. Verify duplicates are identical
    or define a business rule for choosing the authoritative row.
    """
    query = text("""
        SELECT *
        FROM (
            SELECT DISTINCT ON (date::DATE) *
            FROM raw_study1_daily
            WHERE date::DATE <= COALESCE(
                CAST(:as_of_date AS DATE),
                (SELECT MAX(date::DATE) FROM raw_study1_daily)
            )
            ORDER BY date::DATE DESC, ctid DESC
        ) AS daily
        ORDER BY date::DATE DESC
        LIMIT :limit
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"as_of_date": as_of_date, "limit": limit},
        ).mappings().all()

    records = [dict(row) for row in rows]
    records.reverse()
    return records


@router.get("/debug/data")
def debug_database_data(request: Request, as_of_date: date | None = None):
    """Inspect the exact 14 database records that would feed the model."""
    artifact = getattr(request.app.state, "forecaster", None)
    if artifact is None:
        raise HTTPException(status_code=503, detail="Forecast model is not loaded.")

    try:
        records = get_latest_records(as_of_date=as_of_date, limit=14)
        if not records:
            return {"record_count": 0, "message": "No daily records found."}

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        expected = get_expected_base_columns(artifact)
        missing_columns = [col for col in expected if col not in df.columns]
        null_counts = {
            col: int(df[col].isna().sum())
            for col in expected
            if col in df.columns and df[col].isna().any()
        }
        dates = pd.DatetimeIndex(df["date"].dropna().sort_values())
        consecutive = (
            len(dates) == 14
            and dates.equals(pd.date_range(dates.min(), dates.max(), freq="D"))
        )

        return {
            "record_count": len(df),
            "date_range": [
                df["date"].min().strftime("%Y-%m-%d"),
                df["date"].max().strftime("%Y-%m-%d"),
            ],
            "dates": [d.strftime("%Y-%m-%d") for d in dates],
            "expected_raw_column_count": len(expected),
            "missing_columns": missing_columns,
            "null_counts": null_counts,
            "dates_are_14_consecutive_days": consecutive,
            "database_input_is_ready": (
                len(df) == 14 and not missing_columns
                and not null_counts and consecutive
            ),
        }
    except Exception as exc:
        logging.exception("VoltSight database input diagnostic failed")
        raise HTTPException(
            status_code=500,
            detail={"message": "Could not inspect database forecast input.",
                    "error_type": type(exc).__name__, "error": str(exc)},
        ) from exc


@router.post("/predict")
def predict_forecast(request: Request, as_of_date: date | None = None):
    """Forecast using the latest 14 complete daily records stored in Neon.

    No latest_record JSON body is required. Optionally pass as_of_date as a
    query parameter; the latest database date on or before it will be used.
    """
    try:
        artifact = getattr(request.app.state, "forecaster", None)
        if artifact is None:
            raise HTTPException(status_code=503, detail="Forecast model is not loaded.")

        history = get_latest_records(as_of_date=as_of_date, limit=14)
        if len(history) != 14:
            raise HTTPException(
                status_code=400,
                detail=f"Only {len(history)} unique daily records found in Neon; 14 are required.",
            )

        history_df = pd.DataFrame(history)
        history_df["date"] = pd.to_datetime(history_df["date"], errors="coerce")
        if history_df["date"].isna().any():
            raise HTTPException(status_code=422, detail="Neon contains an invalid date value.")

        history_df = history_df.sort_values("date").reset_index(drop=True)
        dates = pd.DatetimeIndex(history_df["date"])
        expected_dates = pd.date_range(dates.min(), dates.max(), freq="D")
        if len(dates) != 14 or not dates.equals(expected_dates):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "The latest 14 unique database records are not 14 consecutive calendar days.",
                    "dates_received": [d.strftime("%Y-%m-%d") for d in dates],
                    "unique_dates": len(dates),
                },
            )

        expected_columns = get_expected_base_columns(artifact)
        missing_columns = [c for c in expected_columns if c not in history_df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=422,
                detail={"message": "Database table is missing required model columns.",
                        "missing_columns": missing_columns},
            )

        null_counts = {
            c: int(history_df[c].isna().sum())
            for c in expected_columns
            if history_df[c].isna().any()
        }
        if null_counts:
            raise HTTPException(
                status_code=422,
                detail={"message": "Database history contains null required values.",
                        "null_counts": null_counts},
            )

        latest_features, feature_cols = build_latest_features(
            history_df.to_dict(orient="records"), artifact
        )
        forecast = run_forecast(latest_features, feature_cols, artifact)

        return {
            "status": "success",
            "historical_records_used": len(history_df),
            "data_up_to_date": dates[-1].strftime("%Y-%m-%d"),
            "forecast_date": forecast["forecast_date"],
            "forecast": forecast,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("VoltSight forecast prediction failed")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Forecast prediction failed. Check the backend terminal logs.",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        ) from exc

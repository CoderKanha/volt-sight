
import json
import joblib
import numpy as np
import pandas as pd

from pathlib import Path


BAD_DATES = {
    "2024-11-20",
    "2025-04-01",
    "2025-10-02"
}


class GridForecaster:

    def __init__(self, bundle_dir):

        self.bundle_dir = Path(bundle_dir)

        registry_path = (
            self.bundle_dir
            / "config"
            / "model_registry.json"
        )

        with open(registry_path, "r", encoding="utf-8") as file:
            self.registry = json.load(file)

        frequency_path = (
            self.bundle_dir
            / self.registry["frequency"]["artifact"]
        )

        self.frequency = joblib.load(
            frequency_path
        )

        self.outage_models = {}

        for target_key, config in self.registry[
            "interday"
        ]["regions"].items():

            if config["model_type"] == "estimator":

                artifact_path = (
                    self.bundle_dir
                    / config["artifact"]
                )

                self.outage_models[target_key] = joblib.load(
                    artifact_path
                )

    def predict_frequency(self, intraday_data):

        artifact = self.frequency

        feature_row, current_frequency, last_timestamp = (
            self._build_frequency_features(
                intraday_data,
                artifact
            )
        )

        predicted_delta = float(
            artifact["model"].predict(
                feature_row
            )[0]
        )

        predicted_frequency = (
            current_frequency + predicted_delta
        )

        return {
            "model_id": "national_frequency_hgb_v1",
            "forecast_horizon_minutes": 15,
            "data_timestamp": last_timestamp.isoformat(),
            "forecast_timestamp": (
                last_timestamp + pd.Timedelta(minutes=15)
            ).isoformat(),
            "current_frequency_hz": current_frequency,
            "predicted_delta_hz": predicted_delta,
            "predicted_frequency_hz": float(
                predicted_frequency
            ),
            "unit": "Hz"
        }

    def _build_frequency_features(
        self,
        raw,
        artifact
    ):

        df = raw.copy()

        required = [
            "timestamp",
            "freq_hz"
        ]

        missing = set(required) - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing frequency input columns: {sorted(missing)}"
            )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["timestamp"]
        ).sort_values("timestamp")

        if df["timestamp"].duplicated().any():
            raise ValueError(
                "Duplicate intraday timestamps detected."
            )

        if len(df) < 97:
            raise ValueError(
                "Frequency forecasting requires at least "
                "97 consecutive 15-minute observations."
            )

        last_timestamp = df["timestamp"].iloc[-1]

        if last_timestamp.minute % 15 != 0:
            raise ValueError(
                "Latest timestamp is not aligned to 15 minutes."
            )

        expected_index = pd.date_range(
            end=last_timestamp,
            periods=97,
            freq="15min"
        )

        history = (
            df.set_index("timestamp")
            .reindex(expected_index)
        )

        if any(
            str(date) in BAD_DATES
            for date in expected_index.date
        ):
            raise ValueError(
                "Input history contains a known corrupted SCADA date."
            )

        history["freq_hz"] = pd.to_numeric(
            history["freq_hz"],
            errors="coerce"
        )

        frequency_values = history[
            "freq_hz"
        ].to_numpy(dtype=float)

        if not np.isfinite(frequency_values).all():
            raise ValueError(
                "Missing frequency observations in the 24-hour input window."
            )

        feature_set = artifact["feature_set"]

        physical_features = artifact["physical_features"]

        lags = artifact["frequency_lags"]

        values = {}

        if feature_set in [
            "physical_only",
            "integrated"
        ]:

            for column in physical_features:

                if column not in history.columns:
                    raise ValueError(
                        f"Missing physical feature: {column}"
                    )

                series = pd.to_numeric(
                    history[column],
                    errors="coerce"
                )

                feature_values = series.to_numpy(
                    dtype=float
                )

                if not np.isfinite(
                    feature_values[-5:]
                ).all():
                    raise ValueError(
                        f"Insufficient recent values for {column}."
                    )

                values[f"{column}_current"] = feature_values[-1]

                values[f"{column}_delta_15m"] = (
                    feature_values[-1] - feature_values[-2]
                )

                values[f"{column}_delta_1h"] = (
                    feature_values[-1] - feature_values[-5]
                )

        if feature_set in [
            "frequency_history",
            "integrated"
        ]:

            for lag in lags:

                name = (
                    "freq_hz_current"
                    if lag == 0
                    else f"freq_hz_lag_{lag * 15}m"
                )

                values[name] = frequency_values[-1 - lag]

            values["freq_hz_1h_mean"] = np.mean(
                frequency_values[-4:]
            )

            values["freq_hz_1h_std"] = np.std(
                frequency_values[-4:],
                ddof=1
            )

            values["freq_hz_4h_mean"] = np.mean(
                frequency_values[-16:]
            )

            values["freq_hz_4h_std"] = np.std(
                frequency_values[-16:],
                ddof=1
            )

            values["freq_hz_change_15m"] = (
                frequency_values[-1] - frequency_values[-2]
            )

            values["freq_hz_change_1h"] = (
                frequency_values[-1] - frequency_values[-5]
            )

        target_timestamp = (
            last_timestamp + pd.Timedelta(minutes=15)
        )

        target_minutes = (
            target_timestamp.hour * 60
            + target_timestamp.minute
        )

        target_dow = target_timestamp.dayofweek

        values["target_tod_sin"] = np.sin(
            2 * np.pi * target_minutes / 1440
        )

        values["target_tod_cos"] = np.cos(
            2 * np.pi * target_minutes / 1440
        )

        values["target_dow_sin"] = np.sin(
            2 * np.pi * target_dow / 7
        )

        values["target_dow_cos"] = np.cos(
            2 * np.pi * target_dow / 7
        )

        feature_row = pd.DataFrame([values])

        expected_columns = artifact["feature_columns"]

        missing_features = (
            set(expected_columns) - set(feature_row.columns)
        )

        if missing_features:
            raise ValueError(
                f"Frequency feature construction mismatch: "
                f"{sorted(missing_features)}"
            )

        feature_row = feature_row.reindex(
            columns=expected_columns
        )

        return (
            feature_row,
            float(frequency_values[-1]),
            last_timestamp
        )

    def _prepare_interday(self, raw):

        df = raw.copy()

        if "date" not in df.columns:
            raise ValueError(
                "Interday data must contain a date column."
            )

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        ).dt.normalize()

        df = df.dropna(
            subset=["date"]
        )

        df = df.loc[
            ~df["date"].dt.strftime("%Y-%m-%d").isin(BAD_DATES)
        ].copy()

        df = df.sort_values(
            "date"
        )

        if df["date"].duplicated().any():
            raise ValueError(
                "Duplicate daily observations detected."
            )

        original_columns = list(df.columns)

        for column in original_columns:

            if column == "date":
                continue

            if column.startswith("time_max_demand_met_"):

                time_parts = (
                    df[column]
                    .astype("string")
                    .str.extract(r"^(\d{1,2}):(\d{2})$")
                )

                hour = pd.to_numeric(
                    time_parts[0],
                    errors="coerce"
                )

                minute = pd.to_numeric(
                    time_parts[1],
                    errors="coerce"
                )

                time_minutes = hour * 60 + minute

                df[f"{column}_sin"] = np.sin(
                    2 * np.pi * time_minutes / 1440
                )

                df[f"{column}_cos"] = np.cos(
                    2 * np.pi * time_minutes / 1440
                )

                df = df.drop(
                    columns=column
                )

            else:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        candidate_columns = self.registry[
            "interday"
        ]["numeric_feature_candidates"]

        missing = (
            set(candidate_columns) - set(df.columns)
        )

        if missing:
            raise ValueError(
                f"Missing interday feature columns: {sorted(missing)}"
            )

        target_columns = [
            config["target_column"]
            for config in self.registry[
                "interday"
            ]["regions"].values()
        ]

        for column in target_columns:

            if column not in df.columns:
                raise ValueError(
                    f"Missing outage target history: {column}"
                )

            df.loc[
                df[column] < 0,
                column
            ] = np.nan

        df = df.set_index(
            "date"
        )

        daily_index = pd.date_range(
            df.index.min(),
            df.index.max(),
            freq="D"
        )

        full = df.reindex(
            daily_index
        )

        full.index.name = "date"

        if len(full) < 15:
            raise ValueError(
                "Interday forecasting requires at least "
                "15 calendar days of historical data."
            )

        return full

    def _build_outage_feature_row(
        self,
        full,
        target_key,
        configuration,
        candidate_columns
    ):

        target_column = configuration[
            "target_column"
        ]

        predictor_columns = [
            column
            for column in candidate_columns
            if column != target_column
        ]

        feature_frame = full[
            predictor_columns
        ].copy()

        target_series = full[
            target_column
        ]

        feature_frame[
            f"outage_{target_key}_origin_day"
        ] = target_series

        feature_frame[
            f"outage_{target_key}_lag_1d"
        ] = target_series.shift(1)

        feature_frame[
            f"outage_{target_key}_lag_7d"
        ] = target_series.shift(7)

        feature_frame[
            f"outage_{target_key}_lag_14d"
        ] = target_series.shift(14)

        feature_frame[
            f"outage_{target_key}_rolling_7d_mean"
        ] = target_series.rolling(
            7,
            min_periods=5
        ).mean()

        feature_frame[
            f"outage_{target_key}_rolling_14d_mean"
        ] = target_series.rolling(
            14,
            min_periods=10
        ).mean()

        feature_frame[
            f"outage_{target_key}_rolling_7d_std"
        ] = target_series.rolling(
            7,
            min_periods=5
        ).std()

        forecast_dates = (
            full.index + pd.Timedelta(days=1)
        )

        feature_frame["forecast_dow_sin"] = np.sin(
            2 * np.pi * forecast_dates.dayofweek / 7
        )

        feature_frame["forecast_dow_cos"] = np.cos(
            2 * np.pi * forecast_dates.dayofweek / 7
        )

        feature_frame["forecast_doy_sin"] = np.sin(
            2 * np.pi * forecast_dates.dayofyear / 365.25
        )

        feature_frame["forecast_doy_cos"] = np.cos(
            2 * np.pi * forecast_dates.dayofyear / 365.25
        )

        feature_frame = feature_frame.replace(
            [np.inf, -np.inf],
            np.nan
        )

        expected_columns = configuration[
            "feature_columns"
        ]

        missing = (
            set(expected_columns) - set(feature_frame.columns)
        )

        if missing:
            raise ValueError(
                f"Outage feature construction mismatch for "
                f"{target_key}: {sorted(missing)}"
            )

        return feature_frame.loc[
            [full.index[-1]],
            expected_columns
        ]

    def predict_outages(self, interday_data):

        full = self._prepare_interday(
            interday_data
        )

        latest_date = full.index[-1]

        candidate_columns = self.registry[
            "interday"
        ]["numeric_feature_candidates"]

        forecasts = {}

        for target_key, configuration in self.registry[
            "interday"
        ]["regions"].items():

            target_column = configuration[
                "target_column"
            ]

            if configuration["model_type"] == "baseline":

                method = configuration["strategy"]

                if method == "Persistence":

                    prediction = full[
                        target_column
                    ].iloc[-1]

                elif method == "Rolling_7D":

                    prediction = full[
                        target_column
                    ].rolling(
                        7,
                        min_periods=5
                    ).mean().iloc[-1]

                else:
                    raise ValueError(
                        f"Unsupported baseline: {method}"
                    )

                if not np.isfinite(prediction):
                    raise ValueError(
                        f"Baseline input unavailable for {target_key}."
                    )

                model_name = method

            elif configuration["model_type"] == "estimator":

                artifact = self.outage_models[
                    target_key
                ]

                feature_row = self._build_outage_feature_row(
                    full,
                    target_key,
                    {
                        **configuration,
                        "feature_columns": artifact[
                            "feature_columns"
                        ]
                    },
                    candidate_columns
                )

                prediction = float(
                    artifact["model"].predict(
                        feature_row
                    )[0]
                )

                if artifact["target_transform"] == "log1p":
                    prediction = np.expm1(
                        prediction
                    )

                prediction = max(
                    float(prediction),
                    0.0
                )

                model_name = artifact["model_name"]

            else:
                raise ValueError(
                    f"Unsupported model type for {target_key}."
                )

            forecasts[target_key] = {
                "region": configuration["target_name"],
                "model": model_name,
                "predicted_outage_mw": float(prediction),
                "unit": "MW"
            }

        regional_keys = [
            "nr",
            "wr",
            "sr",
            "er",
            "ner"
        ]

        regional_sum = sum(
            forecasts[key]["predicted_outage_mw"]
            for key in regional_keys
        )

        national_prediction = forecasts[
            "all_india"
        ]["predicted_outage_mw"]

        return {
            "forecast_horizon_days": 1,
            "data_date": latest_date.strftime("%Y-%m-%d"),
            "forecast_date": (
                latest_date + pd.Timedelta(days=1)
            ).strftime("%Y-%m-%d"),
            "unit": "MW",
            "forecasts": forecasts,
            "regional_sum_mw": float(regional_sum),
            "national_direct_prediction_mw": float(
                national_prediction
            ),
            "national_minus_regional_sum_mw": float(
                national_prediction - regional_sum
            )
        }

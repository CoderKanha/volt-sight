from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from utils.config import FORECAST_ENDPOINT, API_BASE_URL
from utils.style import apply_voltsight_theme

# -------------------------------------------------------------------
# VoltSight - Next-day forecast dashboard
# API reads the latest 14 daily records directly from Neon.
# No historical feature fields are required from the Streamlit user.
# -------------------------------------------------------------------

st.set_page_config(
    page_title="VoltSight | Forecast",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_voltsight_theme()

# ---------- Helpers ----------
def pretty_name(name: str) -> str:
    return (
        str(name).replace("_mu", "").replace("_mw", "")
        .replace("_", " ").title()
    )


def format_mu(value):
    try:
        return f"{float(value):,.2f} MU"
    except (TypeError, ValueError):
        return "—"


def api_error_message(response):
    try:
        payload = response.json()
        detail = payload.get("detail", payload)
        return str(detail)
    except Exception:
        return response.text[:1500]


def fetch_forecast(as_of_date=None):
    params = {}
    if as_of_date is not None:
        params["as_of_date"] = as_of_date.isoformat()

    try:
        response = requests.post(
            FORECAST_ENDPOINT,
            params=params,
            timeout=(10, 180),
        )
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Cannot connect to VoltSight API at {API_BASE_URL}. "
            "Check that FastAPI is running and VOLT_SIGHT_API_URL is correct."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "The forecast request timed out. The model may need more time; "
            "please retry."
        ) from exc

    if not response.ok:
        raise RuntimeError(
            f"API returned HTTP {response.status_code}: "
            f"{api_error_message(response)}"
        )

    data = response.json()
    if data.get("status") != "success" or "forecast" not in data:
        raise RuntimeError(f"Unexpected API response: {data}")
    return data


def get_forecast_payload(api_data):
    # The current API response wraps run_forecast() output in "forecast".
    return api_data["forecast"]


def national_dataframe(national):
    rows = []
    for key, values in (national or {}).items():
        if not isinstance(values, dict):
            continue
        rows.append({
            "Metric": pretty_name(key),
            "Target": key,
            "Predicted (MU)": values.get("predicted_mu"),
            "Lower 80% (MU)": values.get("lower_80pct_mu"),
            "Upper 80% (MU)": values.get("upper_80pct_mu"),
        })
    return pd.DataFrame(rows)


def regional_dataframe(regional):
    rows = []
    for region, values in (regional or {}).items():
        rows.append({
            "Region": region,
            "Energy met (MU)": values.get("energy_met_mu"),
            "Net exchange (MU)": values.get("net_exchange_mu"),
            "Net generation (MU)": values.get("net_generation_mu"),
            "Gross generation (MU)": values.get("gross_generation_mu"),
            "Hydro (MU)": values.get("hydro_mu"),
            "Solar (MU)": values.get("solar_mu"),
            "Wind (MU)": values.get("wind_mu"),
        })
    return pd.DataFrame(rows)


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ⚡ VoltSight")
    st.caption("Electricity forecasting intelligence")
    st.markdown("---")
    st.markdown("### Forecast settings")
    use_cutoff = st.checkbox(
        "Choose a historical data cutoff",
        value=False,
        help="If enabled, the API uses the latest 14 unique daily records on or before this date.",
    )
    cutoff_date = None
    if use_cutoff:
        cutoff_date = st.date_input(
            "Data available up to",
            value=date.today(),
            help="This is a data cutoff, not the forecast date.",
        )
    st.markdown("---")
    st.markdown("**Data source**")
    st.caption("Neon PostgreSQL via FastAPI")
    st.caption("14 unique daily records")
    st.caption("Next-day forecast")
    st.markdown("---")
    st.caption("API endpoint")
    st.code(FORECAST_ENDPOINT, language="text")


# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">GRID INTELLIGENCE • NEXT-DAY OUTLOOK</div>
      <div class="hero-title">Power Forecast Dashboard</div>
      <div class="hero-sub">Explore national generation estimates, regional performance,
      and model uncertainty — powered by your trained VoltSight forecasting model.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([4, 1])
with left:
    st.markdown(
        '<span class="status-pill">● DATABASE-DRIVEN FORECAST</span>',
        unsafe_allow_html=True,
    )
    st.caption(
        "No manual feature entry is required. FastAPI retrieves the required "
        "14 daily records from Neon and runs the trained model."
    )
with right:
    run_clicked = st.button(
        "⚡ Generate forecast",
        type="primary",
        use_container_width=True,
    )

if "voltsight_forecast_response" not in st.session_state:
    st.session_state.voltsight_forecast_response = None
if "voltsight_forecast_cutoff" not in st.session_state:
    st.session_state.voltsight_forecast_cutoff = None

if run_clicked:
    with st.spinner("Retrieving daily history from Neon and running the ML models..."):
        try:
            result = fetch_forecast(cutoff_date)
            st.session_state.voltsight_forecast_response = result
            st.session_state.voltsight_forecast_cutoff = cutoff_date
            st.success("Forecast generated successfully.")
        except Exception as exc:
            st.session_state.voltsight_forecast_response = None
            st.error(str(exc))

api_data = st.session_state.voltsight_forecast_response

if api_data is None:
    st.markdown(
        """
        <div class="note">
        <b>Ready to forecast.</b><br>
        Select <i>Generate forecast</i> to request a next-day prediction.
        The API uses the latest 14 unique daily observations stored in Neon.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

forecast = get_forecast_payload(api_data)
national = forecast.get("national_forecast", {})
regional = forecast.get("regional_forecast", {})
all_targets = forecast.get("all_target_forecasts", {})

national_df = national_dataframe(national)
regional_df = regional_dataframe(regional)

forecast_date = forecast.get("forecast_date", "—")
data_date = forecast.get("data_up_to_date") or api_data.get("data_up_to_date", "—")
unit = forecast.get("unit", "MU")

st.markdown("---")
st.markdown(f"### Forecast for **{forecast_date}**")
st.caption(
    f"Based on data through {data_date} · "
    f"{api_data.get('historical_records_used', 14)} historical daily records · "
    f"Unit: {unit}"
)

# ---------- KPI cards ----------
def find_value(candidates):
    for candidate in candidates:
        if candidate in national:
            return national[candidate].get("predicted_mu")
        if candidate in all_targets:
            return all_targets[candidate].get("predicted_mu")
    return None


generation = find_value(["gen_total_mu"])
energy_met = find_value(["energy_met_total_mu"])
solar = find_value(["solar_gen_total_mu"])
wind = find_value(["wind_gen_total_mu"])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total generation forecast", format_mu(generation))
k2.metric("Energy met forecast", format_mu(energy_met))
k3.metric("Solar generation", format_mu(solar))
k4.metric("Wind generation", format_mu(wind))

# ---------- Tabs ----------
overview_tab, national_tab, regional_tab, detail_tab = st.tabs(
    ["✦ Overview", "▥ National forecast", "⌖ Regional forecast", "☷ All model targets"]
)

with overview_tab:
    st.markdown('<div class="section-title">National energy outlook</div>', unsafe_allow_html=True)
    chart_rows = []
    for key in ["gen_total_mu", "energy_met_total_mu", "solar_gen_total_mu", "wind_gen_total_mu"]:
        values = national.get(key) or all_targets.get(key)
        if values:
            chart_rows.append({
                "Metric": pretty_name(key),
                "Predicted (MU)": values.get("predicted_mu"),
                "Lower 80% (MU)": values.get("lower_80pct_mu"),
                "Upper 80% (MU)": values.get("upper_80pct_mu"),
            })
    if chart_rows:
        overview_df = pd.DataFrame(chart_rows)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=overview_df["Metric"],
            y=overview_df["Predicted (MU)"],
            name="Predicted",
            marker=dict(color="#36cbb5"),
            error_y=dict(
                type="data",
                symmetric=False,
                array=overview_df["Upper 80% (MU)"] - overview_df["Predicted (MU)"],
                arrayminus=overview_df["Predicted (MU)"] - overview_df["Lower 80% (MU)"],
                color="#d1e8f2",
                thickness=1.5,
                width=5,
            ),
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=390,
            yaxis_title=f"Energy ({unit})",
            xaxis_title="",
            margin=dict(l=10, r=10, t=25, b=10),
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("The API did not return the expected national KPI targets.")

    if not regional_df.empty:
        st.markdown('<div class="section-title">Regional generation snapshot</div>', unsafe_allow_html=True)
        regional_chart = regional_df.melt(
            id_vars="Region",
            value_vars=["Gross generation (MU)", "Energy met (MU)"],
            var_name="Measure",
            value_name="MU",
        )
        fig = px.bar(
            regional_chart,
            x="Region",
            y="MU",
            color="Measure",
            barmode="group",
            template="plotly_dark",
            color_discrete_sequence=["#36cbb5", "#5b8def"],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            margin=dict(l=10, r=10, t=25, b=10),
            legend_title="",
        )
        st.plotly_chart(fig, use_container_width=True)

with national_tab:
    st.markdown('<div class="section-title">National forecast with 80% model interval</div>', unsafe_allow_html=True)
    if not national_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=national_df["Metric"],
            y=national_df["Predicted (MU)"],
            name="Median prediction",
            marker_color="#36cbb5",
            error_y=dict(
                type="data",
                symmetric=False,
                array=national_df["Upper 80% (MU)"] - national_df["Predicted (MU)"],
                arrayminus=national_df["Predicted (MU)"] - national_df["Lower 80% (MU)"],
                color="#d1e8f2",
            ),
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=460,
            yaxis_title=f"MU",
            xaxis_tickangle=-25,
            margin=dict(l=10, r=10, t=20, b=90),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            national_df.drop(columns=["Target"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Predicted (MU)": st.column_config.NumberColumn(format="%.2f"),
                "Lower 80% (MU)": st.column_config.NumberColumn(format="%.2f"),
                "Upper 80% (MU)": st.column_config.NumberColumn(format="%.2f"),
            },
        )
    else:
        st.info("No national forecast values were returned.")

with regional_tab:
    st.markdown('<div class="section-title">Regional forecast comparison</div>', unsafe_allow_html=True)
    if not regional_df.empty:
        metric_options = [
            "Gross generation (MU)", "Net generation (MU)",
            "Energy met (MU)", "Hydro (MU)", "Solar (MU)", "Wind (MU)"
        ]
        selected_metric = st.selectbox("Compare regions by", metric_options)
        sorted_regions = regional_df.sort_values(selected_metric, ascending=False)
        fig = px.bar(
            sorted_regions,
            x="Region",
            y=selected_metric,
            color="Region",
            template="plotly_dark",
            text_auto=".2f",
        )
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=390,
            yaxis_title="MU",
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Regional breakdown")
        st.dataframe(
            regional_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(format="%.2f")
                for col in regional_df.columns if col != "Region"
            },
        )
    else:
        st.info("No regional forecast values were returned.")

with detail_tab:
    st.markdown('<div class="section-title">All 34 model target predictions</div>', unsafe_allow_html=True)
    target_rows = []
    for key, values in all_targets.items():
        target_rows.append({
            "Target": pretty_name(key),
            "Raw target": key,
            "Predicted (MU)": values.get("predicted_mu"),
            "Lower 80% (MU)": values.get("lower_80pct_mu"),
            "Upper 80% (MU)": values.get("upper_80pct_mu"),
        })
    targets_df = pd.DataFrame(target_rows)
    if not targets_df.empty:
        query = st.text_input("Filter target names", placeholder="e.g. hydro, energy, solar")
        if query:
            targets_df = targets_df[
                targets_df["Target"].str.contains(query, case=False, na=False)
            ]
        st.dataframe(
            targets_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(format="%.2f")
                for col in ["Predicted (MU)", "Lower 80% (MU)", "Upper 80% (MU)"]
            },
        )
        csv_bytes = targets_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download target forecast CSV",
            data=csv_bytes,
            file_name=f"voltsight_forecast_{forecast_date}.csv",
            mime="text/csv",
        )
    else:
        st.info("No target-level forecast values were returned.")

# ---------- Footer / interpretation ----------
st.markdown("---")
st.markdown(
    """
    <div class="note">
    <b>How to interpret this dashboard</b><br>
    The central prediction is the model's q50 estimate. The lower and upper
    bounds are its q10 and q90 estimates (an 80% prediction interval).
    They are model uncertainty ranges, not a guarantee of the actual outcome.
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "Shortage probability or shortage percentage is not currently returned by "
    "this forecasting API. This screen visualizes generation, energy met, "
    "exchange and regional forecast outputs; it does not label these values "
    "as a shortage probability."
)

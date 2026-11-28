import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.config import OUTAGE_ENDPOINT
from utils.style import apply_voltsight_theme


st.title("⚡ Outage Prediction")
st.caption("All-India and regional forced-outage capacity forecast • One-day horizon")

apply_voltsight_theme()

REGION_LABELS = {
    "all_india": "All India",
    "nr": "North",
    "wr": "West",
    "sr": "South",
    "er": "East",
    "ner": "North-East",
}

with st.sidebar:
    st.subheader("Outage forecast")
    st.write("Source: daily grid history stored in the backend database.")
    st.code(OUTAGE_ENDPOINT, language="text")
    st.caption("The model predicts outage capacity in MW for the next day.")
    if st.button("Refresh prediction", type="primary", use_container_width=True):
        st.session_state["outage_refresh"] = datetime.now().isoformat()

st.markdown("""
<style>
div[data-testid="stMetric"] {background:rgba(35,50,70,.35);padding:12px 14px;border:1px solid rgba(120,160,200,.18);border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.subheader("Optional shortage estimate")
st.caption(
    "To calculate shortage, provide demand and available supply BEFORE subtracting predicted outages. "
    "Leave this section empty to show outage forecasts only."
)
with st.expander("Enter demand and pre-outage supply (optional)", expanded=False):
    selected_region = st.selectbox(
        "Region for shortage calculation",
        options=list(REGION_LABELS),
        format_func=lambda key: REGION_LABELS[key],
        key="shortage_region",
    )
    a, b = st.columns(2)
    demand = a.number_input("Demand (MW)", min_value=0.0, value=0.0, step=100.0, key="shortage_demand")
    supply = b.number_input(
        "Available supply before outages (MW)",
        min_value=0.0, value=0.0, step=100.0, key="shortage_supply",
        help="Do not enter supply that has already been reduced by the predicted outage."
    )
    use_shortage = st.checkbox("Include this shortage calculation in the API request", value=False)
    if use_shortage and demand <= 0:
        st.warning("Demand must be greater than zero to calculate shortage.")

request_body = {}
if use_shortage:
    if demand <= 0:
        st.error("Enter a demand greater than zero, or uncheck the shortage calculation.")
        st.stop()
    request_body = {
        "shortage_inputs": {
            selected_region: {
                "demand_mw": float(demand),
                "available_supply_before_outages_mw": float(supply),
            }
        }
    }

def get_outage_prediction(body_json):
    response = requests.post(OUTAGE_ENDPOINT, json=body_json, timeout=120)
    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"API returned HTTP {response.status_code}: {detail}")
    return response.json()

try:
    with st.spinner("Fetching daily grid history and calculating next-day outage forecasts..."):
        payload = get_outage_prediction(request_body)
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to the VoltSight API. Check that FastAPI is running and VOLT_SIGHT_API_URL is correct.")
    st.stop()
except requests.exceptions.Timeout:
    st.error("The outage prediction request timed out. Please try again.")
    st.stop()
except Exception as exc:
    st.error(f"Outage prediction failed: {exc}")
    st.stop()

if payload.get("status") != "success":
    st.error(payload)
    st.stop()

forecasts = payload.get("forecasts", {})
if not isinstance(forecasts, dict) or not forecasts:
    st.error("The API response did not contain a valid 'forecasts' object.")
    st.json(payload)
    st.stop()

data_date = payload.get("data_date", "Not provided")
forecast_date = payload.get("forecast_date", "Not provided")
national = forecasts.get("all_india", {}).get("predicted_outage_mw")
regional_sum = payload.get("regional_sum_mw")

m1, m2, m3 = st.columns(3)
m1.metric("Forecast date", str(forecast_date))
m2.metric("All-India predicted outage", f"{float(national):,.1f} MW" if national is not None else "N/A")
m3.metric("Sum of regional forecasts", f"{float(regional_sum):,.1f} MW" if regional_sum is not None else "N/A")

st.caption(f"Latest daily input date: {data_date} • Forecast horizon: {payload.get('forecast_horizon_days', 1)} day")
st.divider()

rows = []
for key in ["all_india", "nr", "wr", "sr", "er", "ner"]:
    item = forecasts.get(key)
    if not isinstance(item, dict):
        continue
    rows.append({
        "Region": item.get("region", REGION_LABELS.get(key, key)),
        "Region key": key,
        "Predicted outage (MW)": item.get("predicted_outage_mw"),
        "Model": item.get("model", "Not provided"),
    })

df = pd.DataFrame(rows)
if not df.empty:
    national_df = df[df["Region key"] == "all_india"]
    regional_df = df[df["Region key"] != "all_india"]

    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("Regional outage forecast")
        if not regional_df.empty:
            chart = px.bar(
                regional_df.sort_values("Predicted outage (MW)", ascending=True),
                x="Predicted outage (MW)", y="Region", orientation="h",
                color="Predicted outage (MW)", color_continuous_scale="Teal",
                hover_data=["Model"]
            )
            chart.update_layout(
                height=390, template="plotly_dark",
                coloraxis_showscale=False,
                margin=dict(l=10,r=10,t=20,b=10),
                xaxis_title="Predicted outage (MW)", yaxis_title=""
            )
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No regional predictions were returned.")
    with right:
        st.subheader("Prediction table")
        display_df = df[["Region", "Predicted outage (MW)", "Model"]].copy()
        display_df["Predicted outage (MW)"] = pd.to_numeric(
            display_df["Predicted outage (MW)"], errors="coerce"
        ).map(lambda value: f"{value:,.1f}" if pd.notna(value) else "N/A")
        st.dataframe(display_df, hide_index=True, use_container_width=True)

    if not national_df.empty and not regional_df.empty:
        national_value = pd.to_numeric(national_df.iloc[0]["Predicted outage (MW)"], errors="coerce")
        regional_total = pd.to_numeric(regional_df["Predicted outage (MW)"], errors="coerce").sum()
        difference = payload.get("national_minus_regional_sum_mw")
        st.subheader("National vs regional consistency")
        x, y = st.columns(2)
        x.metric("Direct All-India model", f"{national_value:,.1f} MW" if pd.notna(national_value) else "N/A")
        y.metric("All regional models combined", f"{regional_total:,.1f} MW")
        if difference is not None:
            st.caption(
                f"Direct national prediction minus regional sum: {float(difference):,.1f} MW. "
                "The All-India prediction is produced by its own model and is not forced to equal the regional sum."
            )

shortages = payload.get("shortage_calculations", {})
if shortages:
    st.divider()
    st.subheader("Optional shortage calculation")
    calc = shortages.get(selected_region, {})
    if calc.get("shortage_percentage") is not None:
        q1, q2, q3 = st.columns(3)
        q1.metric("Estimated shortage", f"{float(calc['shortage_mw']):,.1f} MW")
        q2.metric("Shortage as % of demand", f"{float(calc['shortage_percentage']):.2f}%")
        q3.metric("Outage burden / demand", f"{float(calc['outage_burden_percentage_of_demand']):.2f}%")
        st.write({
            "Demand (MW)": calc.get("demand_mw"),
            "Supply before outages (MW)": calc.get("available_supply_before_outages_mw"),
            "Predicted outage (MW)": calc.get("predicted_outage_mw"),
            "Estimated supply after outages (MW)": calc.get("estimated_supply_after_outages_mw"),
        })
    else:
        st.info(
            "No shortage percentage was calculated. Provide demand and pre-outage supply for a region above, "
            "then enable the optional calculation."
        )

note = payload.get("shortage_metric_note")
if note:
    st.caption(note)

st.caption(
    "Outage forecasts represent predicted forced-outage capacity, not automatically unmet demand. "
    "The national direct forecast and sum of regional forecasts may differ because they are separately modelled."
)
with st.expander("View raw API response"):
    st.json(payload)

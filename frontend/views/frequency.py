import requests
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from utils.config import FREQUENCY_ENDPOINT
from utils.style import apply_voltsight_theme


st.title("〰️ Grid Frequency Prediction")
st.caption("National grid frequency forecast • 15-minute horizon • Model-backed prediction")

apply_voltsight_theme()

with st.sidebar:
    st.subheader("Frequency forecast")
    st.write("Source: frequency history stored in the backend database.")
    st.code(FREQUENCY_ENDPOINT, language="text")
    if st.button("Refresh prediction", type="primary", use_container_width=True):
        st.session_state["frequency_refresh"] = datetime.now().isoformat()

st.markdown("""
<style>
.metric-card {background:linear-gradient(135deg,rgba(28,45,68,.85),rgba(16,27,43,.9));padding:18px 20px;border:1px solid rgba(120,160,200,.22);border-radius:14px;}
.small-muted {color:#9aa9ba;font-size:.88rem;}
</style>
""", unsafe_allow_html=True)

def get_frequency_prediction():
    response = requests.post(FREQUENCY_ENDPOINT, timeout=90)
    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"API returned HTTP {response.status_code}: {detail}")
    return response.json()

try:
    with st.spinner("Fetching the latest 24-hour frequency history and generating the next 15-minute forecast..."):
        payload = get_frequency_prediction()
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to the VoltSight API. Check that FastAPI is running and VOLT_SIGHT_API_URL is correct.")
    st.stop()
except requests.exceptions.Timeout:
    st.error("The frequency prediction request timed out. Please try again.")
    st.stop()
except Exception as exc:
    st.error(f"Frequency prediction failed: {exc}")
    st.stop()

if payload.get("status") != "success":
    st.error(payload)
    st.stop()

required = ["current_frequency_hz", "predicted_frequency_hz", "predicted_delta_hz"]
missing = [key for key in required if payload.get(key) is None]
if missing:
    st.error(f"The API response is missing expected fields: {', '.join(missing)}")
    st.json(payload)
    st.stop()

current = float(payload["current_frequency_hz"])
predicted = float(payload["predicted_frequency_hz"])
delta = float(payload["predicted_delta_hz"])
forecast_at = payload.get("forecast_timestamp", "Not provided")
data_at = payload.get("data_timestamp", "Not provided")

def fmt_ts(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(value)

c1, c2, c3 = st.columns(3)
c1.metric("Current frequency", f"{current:.4f} Hz")
c2.metric("Predicted frequency", f"{predicted:.4f} Hz", delta=f"{delta:+.4f} Hz")
c3.metric("Forecast horizon", f"{payload.get('forecast_horizon_minutes', 15)} min")

st.divider()
left, right = st.columns([1.35, 1])
with left:
    st.subheader("Current vs predicted frequency")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=["Latest observation", "Next 15-minute forecast"],
        y=[current, predicted],
        mode="lines+markers+text",
        text=[f"{current:.4f} Hz", f"{predicted:.4f} Hz"],
        textposition="top center",
        line=dict(width=3),
        marker=dict(size=11),
        name="Frequency"
    ))
    fig.add_hline(y=50.0, line_dash="dash", annotation_text="50 Hz nominal reference")
    fig.update_layout(
        height=370, yaxis_title="Frequency (Hz)", xaxis_title="",
        margin=dict(l=15,r=15,t=35,b=15), showlegend=False,
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Forecast details")
    st.markdown(f"**Latest input timestamp**  \n{fmt_ts(data_at)}")
    st.markdown(f"**Forecast timestamp**  \n{fmt_ts(forecast_at)}")
    st.markdown(f"**Model ID**  \n`{payload.get('model_id', 'Not provided')}`")
    direction = "increase" if delta > 0 else "decrease" if delta < 0 else "no change"
    st.info(f"The model predicts a {direction} of **{abs(delta):.4f} Hz** over the next 15 minutes.")

st.caption("This page displays the model's point prediction. It does not calculate a probability of grid instability or provide a confidence interval.")
with st.expander("View raw API response"):
    st.json(payload)

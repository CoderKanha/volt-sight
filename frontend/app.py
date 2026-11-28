import streamlit as st
from pathlib import Path

st.set_page_config(page_title="VoltSight | Power Intelligence", page_icon="⚡", layout="wide")
pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/dashboard.py", title="Dashboard", icon="📊"),
    st.Page("views/eda.py", title="EDA Analytics", icon="🔎"),
    st.Page("views/insights.py", title="Data Insights", icon="💡"),
    st.Page("views/forecast.py", title="Power Forecast", icon="📈"),
    st.Page("views/frequency.py", title="Frequency Prediction", icon="〰️"),
    st.Page("views/outages.py", title="Outage Prediction", icon="⚡"),
    st.Page("views/about.py", title="About VoltSight", icon="ℹ️")
]
st.navigation(pages, position="sidebar").run()

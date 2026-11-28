import streamlit as st
from utils.data_loader import render_data_source
from utils.style import apply_style, page_header

apply_style()
page_header("PROJECT OVERVIEW","About VoltSight","An analytics and forecasting interface for electricity-system observations.")
render_data_source()
st.markdown("""
### The problem
Electricity planning requires understanding generation, energy met, exchange and regional operating patterns.

### VoltSight workflow
1. Explore historical observations directly from a CSV in Streamlit.
2. Inspect missing values, distributions and relationships before modelling.
3. Request forecasts through FastAPI using the trained model and historical records stored in Neon.
4. Present forecast outputs as clear numbers, charts and regional comparisons.

### Architecture
- **Streamlit:** Home, Dashboard, EDA, Data Insights and Forecast UI.
- **FastAPI:** Prediction endpoints and model inference.
- **Neon PostgreSQL:** Historical data used by the prediction API.
- **Pickle artifact:** Trained forecasting pipeline loaded by the backend.
""")
st.warning("Do not label generation or energy-met forecasts as shortage probability unless a separate, validated shortage-risk calculation or model is implemented.")

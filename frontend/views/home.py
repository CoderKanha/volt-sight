import streamlit as st
from utils.data_loader import render_data_source
from utils.style import apply_style

apply_style()
df, source = render_data_source()
st.markdown("""
<div class="hero">
 <div class="eyebrow">POWER SYSTEM INTELLIGENCE</div>
 <h1 style="font-size:3rem;margin:.4rem 0">See the grid.<br>Anticipate the gap.</h1>
 <p style="font-size:1.08rem;color:#c2d6e5;max-width:760px">
 VoltSight turns electricity-system data into operational insights and machine-learning forecasts
 to support better power planning.
 </p>
</div>""", unsafe_allow_html=True)
st.write("")
a,b,c = st.columns(3)
a.markdown("### 📊 Explore"); a.write("Review historical observations, trends, distributions and relationships.")
b.markdown("### 🧭 Understand"); b.write("Compare indicators and identify unusual patterns across available fields.")
c.markdown("### ⚡ Forecast"); c.write("Use the trained model through FastAPI to view forecasts from stored history.")
st.divider()
st.subheader("Get started")
if df is None:
    st.info("Upload your grid CSV using the Dataset uploader in the sidebar.")
else:
    st.success(f"Dataset ready: **{source}** — {len(df):,} rows × {len(df.columns):,} columns.")
    x,y,z=st.columns(3)
    x.metric("Rows",f"{len(df):,}"); y.metric("Columns",f"{len(df.columns):,}")
    z.metric("Numeric fields",f"{len(df.select_dtypes(include='number').columns):,}")
st.caption("CSV analytics run in Streamlit. Forecasting remains connected to FastAPI + Neon + your model.")

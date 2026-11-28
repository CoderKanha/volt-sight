import streamlit as st

def apply_style():
    st.markdown("""
    <style>
    .stApp {background:#07111f;color:#e8f1fa}
    [data-testid="stSidebar"] {background:#0b1728;border-right:1px solid #20374d}
    [data-testid="stMetric"] {background:linear-gradient(135deg,#10243a,#0c1b2d);padding:15px;border:1px solid #1d3b53;border-radius:14px}
    .hero {padding:2rem;border-radius:20px;background:radial-gradient(circle at 80% 20%,#164b60 0,#102c43 38%,#0c1b2d 78%);border:1px solid #1c4257}
    .eyebrow {color:#55d6c2;letter-spacing:.12em;font-size:.78rem;font-weight:700;text-transform:uppercase}
    .muted {color:#9fb5c9}
    </style>""", unsafe_allow_html=True)

def page_header(kicker, title, subtitle):
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="muted">{subtitle}</p>', unsafe_allow_html=True)

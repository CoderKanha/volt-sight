import os
import requests
import streamlit as st

st.set_page_config(page_title="VoltSight | Grid Intelligence", page_icon="⚡",
                   layout="wide", initial_sidebar_state="collapsed")

API_BASE_URL = os.getenv("VOLT_SIGHT_API_URL", "http://localhost:8000").rstrip("/")
APP_URL = os.getenv("VOLT_SIGHT_APP_URL", "").strip()

@st.cache_data(ttl=30, show_spinner=False)
def backend_health():
    """Checks API reachability only; this does not verify model readiness."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=(3, 5))
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

online = backend_health()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#07111f;--cyan:#35d9ed;--green:#a3f36b;--muted:#91a6b9}
.stApp{background:radial-gradient(ellipse at 85% 8%,rgba(25,180,204,.13),transparent 32%),#07111f;color:#edf6ff;font-family:'DM Sans',sans-serif}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1250px;padding-top:1.5rem;padding-bottom:4rem}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;color:#edf6ff!important}
p,li{color:var(--muted)}
#MainMenu,footer{visibility:hidden}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.navbar{display:flex;justify-content:space-between;align-items:center;padding:12px 0 25px;border-bottom:1px solid #ffffff18;margin-bottom:48px;animation:rise .6s both}
.brand{font-family:'Space Grotesk';font-size:25px;font-weight:700;color:white}.brand span{color:var(--cyan)}
.nav-label{color:#a9bacb;font-size:12px;letter-spacing:1.4px}
.tag{display:inline-block;padding:8px 13px;border:1px solid #35d9ed55;border-radius:30px;background:#35d9ed12;color:var(--cyan);font-size:11px;font-weight:700;letter-spacing:1.4px;margin-bottom:20px}
.hero-title{font-family:'Space Grotesk';font-size:clamp(42px,6vw,68px);line-height:1.05;font-weight:700;letter-spacing:-2.8px;color:white;margin:0 0 20px;animation:rise .7s .1s both}
.hero-title span{background:linear-gradient(90deg,#35d9ed,#a3f36b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-desc{font-size:16px;line-height:1.8;max-width:650px;color:#9db0c3;margin-bottom:22px}
.hero-visual{background:radial-gradient(circle at 50% 45%,#35d9ed25,transparent 45%),linear-gradient(145deg,#12283a,#091523);border:1px solid #35d9ed38;border-radius:24px;min-height:320px;padding:26px}
.visual-center{text-align:center;padding:38px 0 24px}.bolt{font-size:68px;color:var(--cyan);animation:float 4s ease-in-out infinite}
.visual-heading{font-family:'Space Grotesk';color:white;font-size:23px;font-weight:700}.visual-sub{color:#8da6b8;font-size:12px}
.visual-footer{display:flex;justify-content:space-between;border-top:1px solid #ffffff1a;padding-top:17px;gap:10px}
.visual-footer strong{display:block;color:white;font-size:16px}.visual-footer small{color:#8199ad;font-size:9px}
.kicker{color:var(--cyan);font-size:11px;font-weight:700;letter-spacing:2px;margin-bottom:9px}
.section-title{font-family:'Space Grotesk';font-size:32px;font-weight:700;color:white;letter-spacing:-1px;margin-bottom:10px}
.metric,.feature,.workflow,.status{background:linear-gradient(145deg,#14283a,#0d1b2b);border:1px solid #ffffff14;border-radius:15px;padding:19px;height:100%;transition:transform .25s,border-color .25s;animation:rise .6s both}
.metric:hover,.feature:hover,.workflow:hover{transform:translateY(-5px);border-color:#35d9ed66}
.metric-value{color:white;font-family:'Space Grotesk';font-size:26px;font-weight:700}.metric-label{color:#8ea6b9;font-size:12px;margin-top:5px}
.feature{min-height:175px}.feature-icon{font-size:27px;margin-bottom:14px}.feature-title{font-family:'Space Grotesk';color:white;font-size:17px;font-weight:600;margin-bottom:8px}.feature-desc{color:#91a6b9;font-size:12px;line-height:1.7}
.workflow{border-top:2px solid var(--cyan);min-height:145px}.footer{border-top:1px solid #ffffff18;margin-top:60px;padding-top:25px;color:#748da2;font-size:12px;text-align:center}
div.stButton>button,div.stLinkButton>a{background:linear-gradient(90deg,#35d9ed,#8fe9a4);color:#07111f!important;border:0;border-radius:9px;font-weight:700;min-height:44px}
div.stButton>button:hover,div.stLinkButton>a:hover{filter:brightness(1.08);transform:translateY(-2px)}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="navbar">
 <div class="brand">⚡ Volt<span>Sight</span></div>
 <div class="nav-label">POWERING GRID INTELLIGENCE</div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.35, 1], gap="large")
with left:
    st.markdown("""
    <div class="tag">INTELLIGENCE FOR THE POWER GRID</div>
    <div class="hero-title">See the Grid.<br><span>Understand What's Next.</span></div>
    <div class="hero-desc">
      VoltSight brings historical electricity-grid data, interactive analytics
      and machine-learning forecasts into one place. Explore national and
      regional patterns, inspect data quality, and review forecast outputs
      generated by the trained model.
    </div>
    """, unsafe_allow_html=True)
    if APP_URL:
        st.link_button("Explore VoltSight Analytics →", APP_URL)
    else:
        st.info("Set VOLT_SIGHT_APP_URL to your analytics application's URL to enable the Explore button.")
with right:
    st.markdown("""
    <div class="hero-visual">
      <div class="kicker">VOLT SIGHT / GRID INTELLIGENCE</div>
      <div class="visual-center">
        <div class="bolt">ϟ</div>
        <div class="visual-heading">Power. Data. Intelligence.</div>
        <div class="visual-sub">From historical observations to model forecasts</div>
      </div>
      <div class="visual-footer">
        <div><strong>EDA</strong><small>DATA EXPLORATION</small></div>
        <div><strong>ML</strong><small>MODEL FORECASTS</small></div>
        <div><strong>API</strong><small>FASTAPI BACKEND</small></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="kicker">PLATFORM AT A GLANCE</div><div class="section-title">A connected analytics workflow.</div>', unsafe_allow_html=True)
cols = st.columns(3)
for col, val, label in zip(cols, ["CSV", "ML", "ONLINE" if online else "OFFLINE"],
                           ["Local dataset exploration", "Trained forecasting pipeline", "FastAPI health endpoint"]):
    with col:
        st.markdown(f'<div class="metric"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status" style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;gap:15px">
 <div><div style="color:white;font-weight:700">FastAPI backend status</div>
 <div style="color:#829caf;font-size:12px;margin-top:5px">Health check: {API_BASE_URL}/health</div></div>
 <div style="color:{'#a3f36b' if online else '#ff8585'};font-size:13px;font-weight:700">● {'Backend responding' if online else 'Backend not reachable'}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="kicker">CURRENT PLATFORM CAPABILITIES</div><div class="section-title">Explore the electricity data.</div>', unsafe_allow_html=True)
st.write("The analytics frontend reads the selected CSV directly. Forecast requests use FastAPI and its database-backed model workflow.")
features = [
    ("📊","Grid Dashboard","Dataset coverage, numeric summaries, historical trends and indicator distributions."),
    ("🔎","EDA Analytics","Missing values, distributions, correlations, relationships and raw records."),
    ("💡","Data Quality Insights","Null counts, duplicate rows, constant fields and modelling checks."),
    ("⚡","Power Forecast","National and regional target forecasts returned by the trained model through FastAPI."),
    ("🗄️","Database-backed inference","FastAPI retrieves the required historical records from Neon rather than requiring a large manual input form."),
    ("🧠","Model output review","Inspect supported target forecasts and uncertainty bounds when supplied by the API."),
]
for i in range(0, len(features), 3):
    cols = st.columns(3, gap="medium")
    for col, (icon, title, desc) in zip(cols, features[i:i+3]):
        with col:
            st.markdown(f'<div class="feature"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-desc">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="kicker">HOW VOLTSIGHT WORKS</div><div class="section-title">Two paths. One platform.</div>', unsafe_allow_html=True)
l, r = st.columns(2, gap="large")
with l:
    st.markdown("#### 📂 Analytics workflow")
    st.markdown('<div class="workflow"><div class="kicker">STREAMLIT + CSV</div><div class="feature-title">Local data exploration</div><div class="feature-desc">CSV upload or configured file path → cached pandas DataFrame → Dashboard / EDA / Data Insights.</div></div>', unsafe_allow_html=True)
with r:
    st.markdown("#### ⚡ Forecast workflow")
    st.markdown('<div class="workflow"><div class="kicker">FASTAPI + NEON + PICKLE</div><div class="feature-title">Database-backed prediction</div><div class="feature-desc">Streamlit forecast page → FastAPI → historical records from Neon → feature preparation → trained pickle model → forecast response.</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="status">
 <div class="kicker">MODEL SCOPE</div>
 <div style="color:white;font-weight:700;font-size:17px;margin-bottom:8px">Forecasts must be interpreted according to the model's actual targets.</div>
 <div class="feature-desc">
  The current forecasting interface presents target variables produced by the trained model,
  including supported national and regional forecasts. These outputs should not be described
  as shortage probability or shortage percentage unless a separate validated shortage-risk
  model or calculation is implemented.
 </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="kicker">DEVELOPER ACCESS</div><div class="section-title">Explore the backend API.</div>', unsafe_allow_html=True)
st.write("Open the FastAPI Swagger documentation to inspect the available endpoints.")
st.link_button("Open API Documentation ↗", f"{API_BASE_URL}/docs")

st.markdown("""
<div class="footer">
 <div class="brand" style="font-size:21px;margin-bottom:10px">⚡ Volt<span>Sight</span></div>
 See the Grid. Understand What's Next.<br><br>
 Electricity Grid Analytics & Forecasting Platform<br>
 Built with Python · Streamlit · FastAPI · Neon PostgreSQL · Machine Learning
</div>
""", unsafe_allow_html=True)

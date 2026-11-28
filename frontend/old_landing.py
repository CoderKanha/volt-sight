# import os
# import requests
# import streamlit as st

# # --------------------------------------------------
# # CONFIGURATION
# # --------------------------------------------------

# st.set_page_config(
#     page_title="VoltSight | Grid Intelligence",
#     page_icon="⚡",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# API_BASE_URL = os.getenv(
#     "VOLT_SIGHT_API_URL",
#     "http://localhost:8000"
# ).rstrip("/")

# # --------------------------------------------------
# # API HELPERS
# # --------------------------------------------------

# @st.cache_data(ttl=30, show_spinner=False)
# def get_api_data(endpoint):
#     try:
#         response = requests.get(
#             f"{API_BASE_URL}{endpoint}",
#             timeout=5
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException:
#         return None

# def api_is_online():
#     data = get_api_data("/health")
#     return data is not None

# # --------------------------------------------------
# # THEME AND CUSTOM CSS
# # --------------------------------------------------

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

# :root {
#     --bg: #07111f;
#     --panel: #101f30;
#     --panel2: #14283a;
#     --cyan: #35d9ed;
#     --green: #a3f36b;
#     --text: #edf6ff;
#     --muted: #91a6b9;
# }

# .stApp {
#     background:
#         radial-gradient(ellipse at 85% 8%, rgba(25, 180, 204, .13), transparent 32%),
#         radial-gradient(ellipse at 5% 30%, rgba(75, 180, 110, .08), transparent 30%),
#         var(--bg);
#     color: var(--text);
#     font-family: 'DM Sans', sans-serif;
# }

# header[data-testid="stHeader"] {
#     background: transparent;
# }

# .block-container {
#     max-width: 1250px;
#     padding-top: 1.5rem;
#     padding-bottom: 4rem;
# }

# h1, h2, h3 {
#     font-family: 'Space Grotesk', sans-serif !important;
#     color: var(--text) !important;
# }

# p, li {
#     color: var(--muted);
# }

# #MainMenu, footer {
#     visibility: hidden;
# }

# /* Motion system: subtle entrance, hover and ambient movement */
# @keyframes fadeUp {
#     from { opacity: 0; transform: translateY(22px); }
#     to   { opacity: 1; transform: translateY(0); }
# }
# @keyframes fadeIn {
#     from { opacity: 0; }
#     to   { opacity: 1; }
# }
# @keyframes floatSoft {
#     0%, 100% { transform: translateY(0); }
#     50%      { transform: translateY(-9px); }
# }
# @keyframes glowPulse {
#     0%, 100% { text-shadow: 0 0 22px rgba(53,217,237,.35); }
#     50%      { text-shadow: 0 0 42px rgba(53,217,237,.75); }
# }
# @keyframes borderGlow {
#     0%, 100% { border-color: rgba(53,217,237,.18); }
#     50%      { border-color: rgba(53,217,237,.48); }
# }

# /* Main page entrance */
# .block-container {
#     animation: fadeIn .75s ease-out both;
# }
# .navbar {
#     animation: fadeUp .65s cubic-bezier(.2,.7,.2,1) both;
# }
# .hero-tag {
#     animation: fadeUp .7s .08s cubic-bezier(.2,.7,.2,1) both;
# }
# .hero-title {
#     animation: fadeUp .8s .16s cubic-bezier(.2,.7,.2,1) both;
# }
# .hero-description {
#     animation: fadeUp .8s .25s cubic-bezier(.2,.7,.2,1) both;
# }
# .st-key-explore {
#     animation: fadeUp .8s .34s cubic-bezier(.2,.7,.2,1) both;
# }
# .hero-visual {
#     animation: fadeUp .9s .2s cubic-bezier(.2,.7,.2,1) both,
#                borderGlow 5s 1.2s ease-in-out infinite;
# }
# .visual-bolt {
#     animation: floatSoft 4s ease-in-out infinite,
#                glowPulse 3s ease-in-out infinite;
# }

# /* Navigation */

# .navbar {
#     display: flex;
#     align-items: center;
#     justify-content: space-between;
#     padding: 12px 0 25px 0;
#     border-bottom: 1px solid rgba(255,255,255,.08);
#     margin-bottom: 55px;
# }

# .brand {
#     font-family: 'Space Grotesk', sans-serif;
#     font-size: 25px;
#     font-weight: 700;
#     color: white;
#     letter-spacing: -1px;
# }

# .brand span {
#     color: var(--cyan);
# }

# .brand-icon {
#     color: var(--green);
#     margin-right: 8px;
# }

# .nav-label {
#     color: #a9bacb;
#     font-size: 13px;
#     letter-spacing: 1px;
# }

# /* Hero */

# .hero-tag {
#     display: inline-block;
#     padding: 8px 13px;
#     border-radius: 30px;
#     border: 1px solid rgba(53,217,237,.3);
#     background: rgba(53,217,237,.08);
#     color: var(--cyan);
#     font-size: 12px;
#     font-weight: 700;
#     letter-spacing: 1.5px;
#     margin-bottom: 22px;
# }

# .hero-title {
#     font-family: 'Space Grotesk', sans-serif;
#     font-size: clamp(42px, 6vw, 70px);
#     line-height: 1.04;
#     font-weight: 700;
#     letter-spacing: -3px;
#     color: white;
#     margin: 0 0 22px 0;
# }

# .hero-title span {
#     background: linear-gradient(90deg, #35d9ed, #a3f36b);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
# }

# .hero-description {
#     font-size: 17px;
#     line-height: 1.8;
#     max-width: 650px;
#     color: #9db0c3;
#     margin-bottom: 25px;
# }

# .hero-visual {
#     background:
#         radial-gradient(circle at 50% 50%, rgba(53,217,237,.15), transparent 45%),
#         linear-gradient(145deg, #12283a, #091523);
#     border: 1px solid rgba(53,217,237,.22);
#     border-radius: 24px;
#     min-height: 330px;
#     padding: 28px;
#     position: relative;
#     overflow: hidden;
# }

# .visual-label {
#     font-size: 11px;
#     letter-spacing: 2px;
#     color: #7e9bb0;
#     font-weight: 700;
# }

# .visual-center {
#     text-align: center;
#     padding: 43px 0 22px 0;
# }

# .visual-bolt {
#     font-size: 70px;
#     color: var(--cyan);
#     text-shadow: 0 0 35px rgba(53,217,237,.55);
# }

# .visual-heading {
#     font-family: 'Space Grotesk', sans-serif;
#     color: white;
#     font-size: 24px;
#     font-weight: 700;
# }

# .visual-sub {
#     color: #8da6b8;
#     font-size: 12px;
# }

# .visual-footer {
#     display: flex;
#     justify-content: space-between;
#     border-top: 1px solid rgba(255,255,255,.1);
#     padding-top: 18px;
#     margin-top: 10px;
# }

# .visual-footer strong {
#     display: block;
#     color: white;
#     font-size: 17px;
# }

# .visual-footer small {
#     color: #8199ad;
#     font-size: 10px;
# }

# .st-key-explore button p {
#     color: var(--bg);
# }

# /* Metrics */

# .workflow-card:hover {
#     transform: translateY(-6px);
#     border-top-color: #a3f36b !important;
#     box-shadow: 0 12px 28px rgba(0,0,0,.2);
# }

# .metric-card {
#     background: linear-gradient(145deg, #14283a, #0d1b2b);
#     border: 1px solid rgba(255,255,255,.08);
#     border-radius: 15px;
#     padding: 20px;
#     min-height: 112px;
#     transition: transform .28s ease, border-color .28s ease,
#                 box-shadow .28s ease;
#     animation: fadeUp .7s both;
# }
# .metric-card:hover {
#     transform: translateY(-5px);
#     border-color: rgba(53,217,237,.32);
#     box-shadow: 0 12px 28px rgba(0,0,0,.2);
# }
# .metric-value {
#     transition: color .25s ease, text-shadow .25s ease;
# }
# .metric-card:hover .metric-value {
#     color: var(--cyan);
#     text-shadow: 0 0 18px rgba(53,217,237,.25);
# }

# .metric-value {
#     color: white;
#     font-family: 'Space Grotesk', sans-serif;
#     font-size: 29px;
#     font-weight: 700;
# }

# .metric-label {
#     color: #8ea6b9;
#     font-size: 12px;
#     margin-top: 5px;
# }

# /* Feature cards */

# .feature-card {
#     background: linear-gradient(145deg, #13273a, #0d1a29);
#     border: 1px solid rgba(255,255,255,.075);
#     border-radius: 17px;
#     padding: 23px;
#     min-height: 205px;
#     transition: transform .28s cubic-bezier(.2,.7,.2,1),
#                 border-color .28s ease,
#                 box-shadow .28s ease,
#                 background .28s ease;
#     animation: fadeUp .7s both;
# }
# .feature-card:hover {
#     transform: translateY(-7px);
#     border-color: rgba(53,217,237,.38);
#     box-shadow: 0 14px 34px rgba(0,0,0,.22),
#                 0 0 22px rgba(53,217,237,.07);
#     background: linear-gradient(145deg, #183249, #102236);
# }
# .feature-icon {
#     transition: transform .3s ease, filter .3s ease;
# }
# .feature-card:hover .feature-icon {
#     transform: translateY(-3px) scale(1.08);
#     filter: drop-shadow(0 0 9px rgba(53,217,237,.35));
# }

# .feature-icon {
#     font-size: 27px;
#     margin-bottom: 17px;
# }

# .feature-title {
#     font-family: 'Space Grotesk', sans-serif;
#     color: white;
#     font-size: 18px;
#     font-weight: 600;
#     margin-bottom: 9px;
# }

# .feature-description {
#     color: #91a6b9;
#     font-size: 13px;
#     line-height: 1.7;
# }

# .section-kicker {
#     color: var(--cyan);
#     font-size: 11px;
#     font-weight: 700;
#     letter-spacing: 2px;
#     margin-bottom: 10px;
# }

# .section-heading {
#     font-family: 'Space Grotesk', sans-serif;
#     font-size: 34px;
#     font-weight: 700;
#     color: white;
#     letter-spacing: -1px;
#     margin-bottom: 10px;
# }

# .dataset-card {
#     background: #102236;
#     border: 1px solid rgba(255,255,255,.08);
#     border-radius: 13px;
#     padding: 18px;
#     min-height: 145px;
#     transition: transform .28s ease, border-color .28s ease,
#                 box-shadow .28s ease;
#     animation: fadeUp .7s both;
# }
# .dataset-card:hover {
#     transform: translateY(-6px);
#     border-color: rgba(163,243,107,.3);
#     box-shadow: 0 12px 28px rgba(0,0,0,.2);
# }

# .dataset-name {
#     color: white;
#     font-weight: 700;
#     font-size: 15px;
#     margin: 9px 0;
# }

# .dataset-desc {
#     color: #8ea6b9;
#     font-size: 12px;
#     line-height: 1.6;
# }

# .status-dot {
#     display: inline-block;
#     height: 8px;
#     width: 8px;
#     border-radius: 50%;
#     background: #a3f36b;
#     box-shadow: 0 0 10px #a3f36b;
#     margin-right: 7px;
# }

# .footer {
#     border-top: 1px solid rgba(255,255,255,.09);
#     margin-top: 65px;
#     padding-top: 25px;
#     color: #748da2;
#     font-size: 12px;
#     text-align: center;
# }

# div.stButton > button {
#     background: linear-gradient(90deg, #35d9ed, #8fe9a4);
#     color: #07111f;
#     border: none;
#     border-radius: 9px;
#     font-weight: 700;
#     padding: 0.65rem 1.4rem;
#     min-height: 45px;
#     transition: transform .22s ease, box-shadow .22s ease,
#                 filter .22s ease;
#     box-shadow: 0 5px 18px rgba(53,217,237,.12);
# }

# div.stButton > button:hover {
#     border: none;
#     color: #07111f;
#     filter: brightness(1.08);
#     transform: translateY(-2px);
#     box-shadow: 0 9px 24px rgba(53,217,237,.22);
# }
# div.stButton > button:active {
#     transform: translateY(0) scale(.985);
# }
# a, button {
#     transition: color .2s ease, background-color .2s ease,
#                 border-color .2s ease, box-shadow .2s ease,
#                 transform .2s ease;
# }
# .stLinkButton a:hover {
#     transform: translateY(-2px);
# }

# /* Respect users who prefer reduced motion */
# @media (prefers-reduced-motion: reduce) {
#     *, *::before, *::after {
#         animation-duration: .01ms !important;
#         animation-iteration-count: 1 !important;
#         scroll-behavior: auto !important;
#         transition-duration: .01ms !important;
#     }
# }
# </style>
# """, unsafe_allow_html=True)

# # --------------------------------------------------
# # NAVIGATION HEADER
# # --------------------------------------------------

# st.markdown("""
# <div class="navbar">
#     <div class="brand">
#         <span class="brand-icon">⚡</span>Volt<span>Sight</span>
#     </div>
#     <div class="nav-label">
#         POWERING GRID INTELLIGENCE
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # --------------------------------------------------
# # HERO SECTION
# # --------------------------------------------------

# hero_left, hero_right = st.columns([1.35, 1], gap="large")

# with hero_left:
#     st.markdown("""
#     <div class="hero-tag">INTELLIGENCE FOR THE POWER GRID</div>

#     <div class="hero-title">
#         See the Grid.<br>
#         <span>Predict the Future.</span>
#     </div>

#     <div class="hero-description">
#         VoltSight transforms electricity-grid data into actionable
#         intelligence. Explore demand patterns, identify power shortages,
#         monitor grid frequency and uncover state-level insights through
#         data analytics and machine learning.
#     </div>
#     """, unsafe_allow_html=True)

#     st.button(
#         "Explore Grid Intelligence  →",
#         key="explore",
#         on_click=lambda: st.toast(
#             "Open the analytics pages from the Streamlit navigation menu."
#         )
#     )

# with hero_right:
#     st.html("""
#     <div class="hero-visual">
#         <div class="visual-label">VOLT SIGHT / GRID OVERVIEW</div>

#         <div class="visual-center">
#             <div class="visual-bolt">ϟ</div>
#             <div class="visual-heading">Power. Data. Intelligence.</div>
#             <div class="visual-sub">
#                 Turning complex grid data into clearer decisions
#             </div>
#         </div>

#         <div class="visual-footer">
#             <div>
#                 <strong>4</strong>
#                 <small>DATA SOURCES</small>
#             </div>
#             <div>
#                 <strong>ML</strong>
#                 <small>PREDICTIVE ANALYTICS</small>
#             </div>
#             <div>
#                 <strong>API</strong>
#                 <small>INTEGRATED PLATFORM</small>
#             </div>
#         </div>
#     </div>
#     """)

# # --------------------------------------------------
# # PLATFORM METRICS
# # --------------------------------------------------

# st.markdown("<br><br>", unsafe_allow_html=True)
# st.markdown('<div class="section-kicker">PLATFORM AT A GLANCE</div>',
#             unsafe_allow_html=True)
# st.markdown('<div class="section-heading">One platform. Multiple perspectives.</div>',
#             unsafe_allow_html=True)

# online = api_is_online()
# datasets = get_api_data("/api/datasets")

# if isinstance(datasets, dict):
#     dataset_count = len(datasets.get("datasets", [])) if isinstance(
#         datasets.get("datasets"), list
#     ) else 4
# elif isinstance(datasets, list):
#     dataset_count = len(datasets)
# else:
#     dataset_count = 4

# m1, m2, m3, m4 = st.columns(4)

# metrics = [
#     (str(dataset_count), "Electricity data sources"),
#     ("10+", "Backend API capabilities"),
#     ("4", "Analytical dimensions"),
#     ("ONLINE" if online else "OFFLINE", "Backend connection")
# ]

# for column, (value, label) in zip([m1, m2, m3, m4], metrics):
#     with column:
#         st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-value">{value}</div>
#             <div class="metric-label">{label}</div>
#         </div>
#         """, unsafe_allow_html=True)

# # --------------------------------------------------
# # FEATURE SECTION
# # --------------------------------------------------

# st.markdown("<br><br>", unsafe_allow_html=True)
# st.markdown('<div class="section-kicker">WHAT VOLTSIGHT CAN DO</div>',
#             unsafe_allow_html=True)
# st.markdown('<div class="section-heading">Intelligence across the grid</div>',
#             unsafe_allow_html=True)
# st.markdown(
#     "Explore the major analytical capabilities of the VoltSight platform."
# )

# features = [
#     (
#         "⚡",
#         "National Shortage Analytics",
#         "Study peak demand shortages, energy shortages and historical electricity supply patterns."
#     ),
#     (
#         "📈",
#         "Demand & Generation",
#         "Explore national and regional demand, generation patterns and electricity consumption trends."
#     ),
#     (
#         "〰️",
#         "Grid Stability",
#         "Analyze SCADA frequency measurements and screen for unusual frequency behaviour."
#     ),
#     (
#         "🗺️",
#         "State Intelligence",
#         "Compare state-level demand, energy met, shortage indicators and regional performance."
#     ),
#     (
#         "🧠",
#         "Machine Learning Lab",
#         "Experiment with baseline shortage regression and shortage classification models."
#     ),
#     (
#         "🔍",
#         "Data Quality Intelligence",
#         "Inspect dataset structures, missing values, column availability and data completeness."
#     )
# ]

# for row_start in range(0, len(features), 3):
#     cols = st.columns(3, gap="medium")

#     for col, feature in zip(cols, features[row_start:row_start + 3]):
#         icon, title, description = feature
#         with col:
#             st.markdown(f"""
#             <div class="feature-card">
#                 <div class="feature-icon">{icon}</div>
#                 <div class="feature-title">{title}</div>
#                 <div class="feature-description">{description}</div>
#             </div>
#             """, unsafe_allow_html=True)

#     st.markdown("<br>", unsafe_allow_html=True)

# # --------------------------------------------------
# # DATA SOURCES
# # --------------------------------------------------

# st.markdown("<br>", unsafe_allow_html=True)
# st.markdown('<div class="section-kicker">OUR DATA FOUNDATION</div>',
#             unsafe_allow_html=True)
# st.markdown('<div class="section-heading">Built around electricity-grid data</div>',
#             unsafe_allow_html=True)

# data_sources = [
#     (
#         "01",
#         "National Daily Dataset",
#         "study1_daily.csv",
#         "Daily national electricity indicators, demand, supply and shortage information."
#     ),
#     (
#         "02",
#         "National Hourly Dataset",
#         "study1_hourly.csv",
#         "Hourly national demand and electricity-system behaviour."
#     ),
#     (
#         "03",
#         "SCADA Dataset",
#         "study2_scada.csv",
#         "Grid measurements including frequency and operational variables."
#     ),
#     (
#         "04",
#         "State-wise Dataset",
#         "study3_states.csv",
#         "State-level demand, energy met and shortage indicators."
#     )
# ]

# cols = st.columns(4, gap="medium")

# for col, (number, name, filename, description) in zip(cols, data_sources):
#     with col:
#         st.markdown(f"""
#         <div class="dataset-card">
#             <div class="section-kicker">{number} / DATA SOURCE</div>
#             <div class="dataset-name">{name}</div>
#             <div style="color:#35d9ed;font-size:11px;margin-bottom:9px;">
#                 {filename}
#             </div>
#             <div class="dataset-desc">{description}</div>
#         </div>
#         """, unsafe_allow_html=True)

# # --------------------------------------------------
# # WORKFLOW SECTION
# # --------------------------------------------------

# st.markdown("<br><br>", unsafe_allow_html=True)
# st.markdown('<div class="section-kicker">HOW IT WORKS</div>',
#             unsafe_allow_html=True)
# st.markdown('<div class="section-heading">From raw data to grid intelligence</div>',
#             unsafe_allow_html=True)

# steps = [
#     ("01", "Collect", "Load and organize electricity-grid datasets."),
#     ("02", "Analyze", "Process data and discover meaningful patterns."),
#     ("03", "Predict", "Apply machine learning to analytical problems."),
#     ("04", "Visualize", "Present insights through interactive dashboards.")
# ]

# cols = st.columns(4)

# for col, (number, title, description) in zip(cols, steps):
#     with col:
#         st.markdown(f"""
#         <div class="workflow-card" style="
#             border-top:2px solid #35d9ed;
#             background:#102236;
#             transition: transform .28s ease, box-shadow .28s ease,
#                         border-color .28s ease;
#             animation: fadeUp .7s both;
#             padding:20px;
#             border-radius:0 0 13px 13px;
#             min-height:155px;">
#             <div style="color:#35d9ed;font-size:12px;font-weight:700;">
#                 STEP {number}
#             </div>
#             <div style="
#                 font-family:'Space Grotesk';
#                 font-size:20px;
#                 color:white;
#                 font-weight:700;
#                 margin:12px 0;">
#                 {title}
#             </div>
#             <div style="font-size:12px;color:#91a6b9;line-height:1.6;">
#                 {description}
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

# # --------------------------------------------------
# # API STATUS
# # --------------------------------------------------

# st.markdown("<br><br>", unsafe_allow_html=True)

# status_text = "Backend connected" if online else "Backend unavailable"
# status_color = "#a3f36b" if online else "#ff7777"

# st.markdown(f"""
# <div style="
#     background:#102236;
#     border:1px solid rgba(255,255,255,.08);
#     border-radius:13px;
#     padding:18px 22px;
#     display:flex;
#     justify-content:space-between;
#     align-items:center;">
#     <div>
#         <div style="color:white;font-weight:700;">
#             VoltSight API Infrastructure
#         </div>
#         <div style="color:#829caf;font-size:12px;margin-top:5px;">
#             FastAPI backend · Data analytics · ML services
#         </div>
#     </div>
#     <div style="color:{status_color};font-size:13px;font-weight:700;">
#         ● {status_text}
#     </div>
# </div>
# """, unsafe_allow_html=True)

# st.markdown("<br>", unsafe_allow_html=True)

# st.link_button(
#     "Open API Documentation ↗",
#     f"{API_BASE_URL}/docs"
# )

# # --------------------------------------------------
# # FOOTER
# # --------------------------------------------------

# st.markdown("""
# <div class="footer">
#     <div class="brand" style="font-size:21px;margin-bottom:10px;">
#         ⚡ Volt<span>Sight</span>
#     </div>
#     See the Grid. Predict the Future.<br><br>
#     Intelligent Electricity Grid Analytics Platform<br>
#     Built with Python · FastAPI · Streamlit · Machine Learning
# </div>
# """, unsafe_allow_html=True)

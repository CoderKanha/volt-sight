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


def apply_voltsight_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background: #07111f;
            color: #e8f0fb;
        }

        [data-testid="stSidebar"] {
            background: #0b192a;
            border-right: 1px solid #1b3048;
        }

        /* Hero section */
        .hero {
            padding: 1.5rem 1.7rem;
            border-radius: 20px;
            background:
                radial-gradient(circle at 85% 20%, #164e63 0, transparent 34%),
                linear-gradient(120deg, #10243a, #102c3b 58%, #123c43);
            border: 1px solid #24516a;
            margin-bottom: 1.2rem;
        }

        .hero-kicker {
            color: #68e0ce;
            letter-spacing: .16em;
            font-size: .72rem;
            font-weight: 700;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.25rem;
            font-weight: 700;
            margin: .25rem 0;
            color: #f4f8ff;
        }

        .hero-sub {
            color: #b7c9d9;
            font-size: .96rem;
        }

        /* Section headings */
        .section-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.2rem;
            font-weight: 600;
            color: #eff6ff;
            margin: .4rem 0 .8rem;
        }

        .small-muted {
            color: #9bb0c4;
            font-size: .82rem;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, #10243a, #0d1d30);
            border: 1px solid #1d3a52;
            padding: 15px 17px;
            border-radius: 15px;
        }

        div[data-testid="stMetricLabel"] {
            color: #a9bfd2;
        }

        div[data-testid="stMetricValue"] {
            color: #f4f8ff;
            font-family: 'Space Grotesk', sans-serif;
        }

        /* Status indicator */
        .status-pill {
            display: inline-block;
            padding: 5px 11px;
            border-radius: 30px;
            background: #103b39;
            color: #75ead5;
            border: 1px solid #1e7168;
            font-size: .78rem;
            font-weight: 700;
        }

        /* Information note */
        .note {
            background: #10263a;
            border: 1px solid #24455f;
            border-radius: 12px;
            padding: 12px 15px;
            color: #c7d7e6;
            font-size: .88rem;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(120deg, #164e63, #126b78);
            color: #f4f8ff;
            border: 1px solid #28758a;
            border-radius: 10px;
            font-weight: 600;
        }

        .stButton > button:hover {
            border-color: #68e0ce;
            color: #ffffff;
        }

        /* Input fields */
        div[data-baseweb="input"] input,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] textarea {
            background-color: #10243a;
            color: #e8f0fb;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            color: #a9bfd2;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #68e0ce;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

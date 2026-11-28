from pathlib import Path
import os, io
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="Loading VoltSight CSV...")
def _read_bytes(raw: bytes):
    last = None
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise ValueError(f"Unable to read CSV: {last}")

@st.cache_data(show_spinner="Loading CSV from disk...")
def _read_path(path: str, mtime: float):
    return pd.read_csv(path, low_memory=False)

def get_dataset():
    raw = st.session_state.get("voltsight_csv_bytes")
    if raw:
        return _read_bytes(raw), st.session_state.get("voltsight_csv_name", "uploaded.csv")
    configured = os.getenv("VOLT_SIGHT_DATA_PATH", "").strip()
    if configured and Path(configured).expanduser().is_file():
        p = Path(configured).expanduser().resolve()
        return _read_path(str(p), p.stat().st_mtime), p.name
    return None, None

def render_data_source():
    with st.sidebar:
        st.markdown("### Dataset")
        uploaded = st.file_uploader("Upload grid CSV", type=["csv"], key="voltsight_upload",
            help="Used by Streamlit analytics pages; it is not sent to FastAPI.")
        if uploaded is not None:
            st.session_state["voltsight_csv_bytes"] = uploaded.getvalue()
            st.session_state["voltsight_csv_name"] = uploaded.name
        df, source = get_dataset()
        if df is not None:
            st.caption(f"{source} · {len(df):,} rows · {len(df.columns):,} columns")
        else:
            st.info("Upload a CSV to enable analytics.")
    return df, source

def find_date_column(df):
    if df is None: return None
    lookup = {str(c).strip().lower(): c for c in df.columns}
    for name in ("date", "datetime", "timestamp", "day", "observation_date"):
        if name in lookup: return lookup[name]
    for col in df.columns:
        if "date" in str(col).lower() or "time" in str(col).lower():
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() > .5: return col
    return None

def numeric_columns(df):
    return list(df.select_dtypes(include="number").columns)

def parse_date(df, col):
    out = df.copy()
    if col: out[col] = pd.to_datetime(out[col], errors="coerce")
    return out

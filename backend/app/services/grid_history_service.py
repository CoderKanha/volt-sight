import re
import pandas as pd
from sqlalchemy import text
from app.core.database import engine

def _table_identifier(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,62}", name or ""):
        raise ValueError("Invalid table name configured for grid history.")
    return name

def fetch_daily_grid_history(table_name: str, limit: int = 120) -> pd.DataFrame:
    table = _table_identifier(table_name)
    query = text(f"""
        SELECT *
        FROM (
            SELECT DISTINCT ON (date::date) *
            FROM public."{table}"
            WHERE date IS NOT NULL
            ORDER BY date::date DESC, ctid DESC
        ) AS unique_daily
        ORDER BY date::date DESC
        LIMIT :limit
    """)
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection, params={"limit": limit})
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return df

def fetch_frequency_grid_history(table_name: str, limit: int = 120) -> pd.DataFrame:
    table = _table_identifier(table_name)
    query = text(f"""
        SELECT *
        FROM public."{table}"
        WHERE timestamp IS NOT NULL
        ORDER BY timestamp::timestamp DESC
        LIMIT :limit
    """)
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection, params={"limit": limit})
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return df

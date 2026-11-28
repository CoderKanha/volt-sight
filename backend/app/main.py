from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import data_ingestion, data_fetch, forecast, outages, frequency
from app.routers.forecast import lifespan

app = FastAPI(
    title="VoltSight API",
    version="2.0.0",
    description=(
        "Unified VoltSight API: CSV ingestion, Neon data retrieval, "
        "legacy daily forecasting, new outage forecasting and frequency forecasting."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your Streamlit frontend origin in production.
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_ingestion.router)
app.include_router(data_fetch.router)
app.include_router(forecast.router)
app.include_router(outages.router)
app.include_router(frequency.router)

@app.get("/")
def root():
    return {
        "name": "VoltSight",
        "status": "running",
        "docs": "/docs",
        "modules": ["data_ingestion", "data_fetch", "legacy_forecast", "outages", "frequency"],
    }

@app.get("/health")
def health():
    return {"status": "ok"}

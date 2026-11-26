from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(title="VoltSight API",version="1.0.0",description="Electricity dataset analytics and baseline ML API")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

FILES={"daily":"study1_daily.csv","hourly":"study1_hourly.csv","scada":"study2_scada.csv","states":"study3_states.csv"}


@app.get("/")
def root(): return {"name":"VoltSight","status":"running","docs":"/docs"}

@app.get("/health")
def health(): return {"status":"ok","datasets":list(FILES)}
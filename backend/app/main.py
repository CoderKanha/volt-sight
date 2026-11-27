import pickle
from pathlib import Path
from contextlib import asynccontextmanager

from app.routers import forecast
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import data_ingestion, data_fetch, forecast
from app.routers.forecast import lifespan

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "power_shortage_model.pickle"
)

app=FastAPI(title="VoltSight API",version="1.0.0",description="Electricity dataset analytics and baseline ML API", lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

FILES={"daily":"study1_daily.csv","hourly":"study1_hourly.csv","scada":"study2_scada.csv","states":"study3_states.csv"}

# Register CSV ingestion API
app.include_router(data_ingestion.router)
app.include_router(data_fetch.router)
app.include_router(forecast.router)


@app.get("/")
def root(): return {"name":"VoltSight","status":"running","docs":"/docs"}

@app.get("/health")
def health(): return {"status":"ok","datasets":list(FILES)}

# @app.get("/test-db")
# def test_database():

#     try:
#         # Establish database connection
#         conn = psycopg2.connect(DATABASE_URL)

#         cursor = conn.cursor(cursor_factory=RealDictCursor)

#         # Create a dummy table if it doesn't exist
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS connectivity_test (
#                 id SERIAL PRIMARY KEY,
#                 name VARCHAR(100),
#                 message VARCHAR(255)
#             );
#         """)

#         # Insert dummy data
#         cursor.execute("""
#             INSERT INTO connectivity_test (name, message)
#             VALUES (%s, %s)
#             RETURNING id, name, message;
#         """, ("FastAPI Test", "Successfully connected to Neon PostgreSQL!"))

#         inserted_data = cursor.fetchone()

#         # Fetch records from database
#         cursor.execute("""
#             SELECT * FROM connectivity_test
#             ORDER BY id DESC
#             LIMIT 5;
#         """)

#         records = cursor.fetchall()

#         # Commit transaction
#         conn.commit()

#         cursor.close()
#         conn.close()

#         return {
#             "status": "success",
#             "database_connected": True,
#             "message": "FastAPI successfully connected to Neon PostgreSQL!",
#             "inserted_record": inserted_data,
#             "records": records
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "status": "failed",
#                 "database_connected": False,
#                 "error": str(e)
#             }
#         )
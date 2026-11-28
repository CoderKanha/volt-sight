# GridSense AI full-stack prototype

Contains `backend/` (FastAPI + baseline ML endpoints + supplied datasets) and `frontend/` (Streamlit multi-page dashboard).

## Run in two terminals

Backend:
```bash
cd backend
python -m venv .venv
# activate environment
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
python -m venv .venv
# activate environment
pip install -r requirements.txt
streamlit run app.py

Note: To see the analytics in UI use the study1_daily.csv file when asked to updload CSV
```

FastAPI docs: http://localhost:8000/docs | Streamlit: http://localhost:8501

Source CSVs and dictionary are bundled in `backend/data`. The models are chronological research baselines, not operational forecasts. Validate definitions, feature timing, missingness, leakage and baselines before presenting results. CORS is permissive for local development; restrict it before deployment.

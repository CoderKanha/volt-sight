# FastAPI backend

```bash
cd backend
python -m venv .venv
# activate: Windows .venv\\Scripts\\activate | macOS/Linux source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation: http://localhost:8000/docs

Endpoints: `GET /health`, `GET /api/datasets`, `GET /api/datasets/{name}/schema`, `GET /api/datasets/{name}/missingness`, `GET /api/daily/indicators`, `GET /api/scada/frequency`, `GET /api/states/summary`, `GET /api/dictionary`, `POST /api/models/daily-shortage`, `POST /api/models/shortage-classifier`.

The model routes train chronological baseline models on request. They are research prototypes, not production grid-control systems. Review feature availability, target definitions and leakage before reporting results. Restrict CORS origins before deployment.

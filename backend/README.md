# FastAPI backend

```bash
cd backend
python -m venv .venv
# activate: Windows .venv\\Scripts\\activate | macOS/Linux source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

--> Build Docker Image: docker build -t voltsight-api .
```

Interactive API documentation: http://localhost:8000/docs

Endpoints: `GET /health`, `GET /api/datasets`, `GET /api/datasets/{name}/schema`, `GET /api/datasets/{name}/missingness`, `GET /api/daily/indicators`, `GET /api/scada/frequency`, `GET /api/states/summary`, `GET /api/dictionary`, `POST /api/models/daily-shortage`, `POST /api/models/shortage-classifier`.

The model routes train chronological baseline models on request. They are research prototypes, not production grid-control systems. Review feature availability, target definitions and leakage before reporting results. Restrict CORS origins before deployment.


Command to Sync uv and venv
uv init
uv venv .backend
.backend\Scripts\activate
uv add "fastapi[standard]"
uv sync --active
uv lock


## Unified model runtime (legacy + handoff models)

The API now serves all model endpoints in one FastAPI process. See the repository-level
`UNIFIED_SETUP.md` for setup, shared dependency versions, model compatibility shim,
database table names and smoke testing.

Run:
```bash
uv lock
uv sync
uv run python smoke_test_models.py
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Python runtime: 3.13.5. The shared ML pins are NumPy 2.5.5, Pandas 3.1.1,
Scikit-learn 1.9.1 and Joblib 1.6.0.

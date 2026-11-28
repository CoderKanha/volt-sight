
FROM python:3.13-slim

WORKDIR /app

# Required Linux libraries for LightGBM and scientific packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgomp1 \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy project configuration
COPY pyproject.toml README.md ./

# Copy FastAPI application, new model bundle and legacy model
COPY app/ ./app/
COPY models/ ./models/

# Install project and dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Start FastAPI on Render's assigned port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

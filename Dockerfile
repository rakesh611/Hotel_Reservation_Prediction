# =========================
# Base Image (stable Python)
# =========================
FROM python:3.10-slim

# =========================
# Environment variables
# =========================
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2

# =========================
# Work directory
# =========================
WORKDIR /app

# =========================
# System dependencies (LightGBM + ML libs)
# =========================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Install dependencies (cached layer)
# =========================
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =========================
# Copy application code
# =========================
COPY . .

# =========================
# (IMPORTANT) Ensure model + features exist
# =========================
RUN test -f model.pkl || echo "WARNING: model.pkl missing"
RUN test -f features.pkl || echo "WARNING: features.pkl missing"

# =========================
# Expose Flask/Gunicorn port
# =========================
EXPOSE 8080

# =========================
# Production server (BEST PRACTICE)
# =========================
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "3", \
     "--timeout", "120", \
     "application:app"]

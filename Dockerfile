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
# System dependencies
# =========================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
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
# Expose Flask port
# =========================
EXPOSE 8080

# =========================
# Production server (IMPORTANT)
# =========================
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "application:app"]

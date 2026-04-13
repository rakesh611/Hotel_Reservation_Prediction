FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# requirements first (cache layer)
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# copy full project INCLUDING artifacts
COPY . .

# ensure model exists (debug step)
RUN ls -R artifacts/models || true

EXPOSE 8080

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "application:app"]

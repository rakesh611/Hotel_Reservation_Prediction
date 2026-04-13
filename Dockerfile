FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 🔥 IMPORTANT: include trained ML artifacts
COPY artifacts/ /app/artifacts/

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "application:app"]

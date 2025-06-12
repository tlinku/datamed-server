# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
FROM --platform=$TARGETPLATFORM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p logs
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "run.py"]

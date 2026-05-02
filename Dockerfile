FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY planner_core ./planner_core
COPY web ./web
COPY LICENSE README.md ./

# Render (and some hosts) set PORT at runtime; local default 8080.
EXPOSE 8080

CMD uvicorn web.main:app --host 0.0.0.0 --port "${PORT:-8080}"

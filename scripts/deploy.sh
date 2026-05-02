#!/usr/bin/env bash
# Easy install / run / Docker for Financial Planner (repo root).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV="${VENV:-$ROOT/.venv}"
PORT_WEB="${PORT_WEB:-${WEB_PORT:-8080}}"
HOST="${HOST:-0.0.0.0}"

usage() {
  cat <<EOF
$0 — venv, local web, Docker

Commands:
  install       Create venv + pip install -r requirements.txt
  web           Run FastAPI + Jinja UI on PORT_WEB (default $PORT_WEB)
  dev-web       web with --reload
  docker-build  docker build -t financial-planner:local .
  docker-web    Run API container on PORT_WEB
  compose-up    docker compose up --build (foreground)
  health        curl local /docs (expects web already running)
EOF
}

case "${1:-}" in
  install)
    "$PYTHON" -m venv "$VENV"
    "$VENV/bin/pip" install -U pip
    "$VENV/bin/pip" install -r "$ROOT/requirements.txt"
    echo "OK: venv at $VENV"
    ;;
  web)
    exec "$VENV/bin/uvicorn" web.main:app --app-dir "$ROOT" --host "$HOST" --port "$PORT_WEB"
    ;;
  dev-web)
    exec "$VENV/bin/uvicorn" web.main:app --app-dir "$ROOT" --host "$HOST" --port "$PORT_WEB" --reload
    ;;
  docker-build)
    docker build -t financial-planner:local "$ROOT"
    ;;
  docker-web)
    docker run --rm -p "${PORT_WEB}:8080" -e HOST=0.0.0.0 financial-planner:local
    ;;
  compose-up)
    docker compose -f "$ROOT/docker-compose.yml" up --build
    ;;
  health)
    curl -sf "http://127.0.0.1:${PORT_WEB}/docs" >/dev/null && echo "OK: /docs reachable" || {
      echo "FAIL: start web first (./scripts/deploy.sh web)"
      exit 1
    }
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    echo "Unknown: $1"
    usage
    exit 1
    ;;
esac

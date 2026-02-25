#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f .env ]]; then
  if [[ -f .env.example ]]; then
    cp .env.example .env
    echo "[INFO] .env not found, created from .env.example"
    echo "[INFO] Please edit .env if needed, then rerun this script."
  else
    echo "[ERROR] Missing .env and .env.example"
    exit 1
  fi
fi

set -a
source ./.env
set +a

prepare_host_if_needed() {
  local need_prepare=0

  if ! command -v docker >/dev/null 2>&1; then
    need_prepare=1
  elif ! docker info --format '{{json .Runtimes}}' 2>/dev/null | grep -q '"nvidia"'; then
    need_prepare=1
  fi

  if [[ "$need_prepare" -eq 1 ]]; then
    echo "[INFO] Docker/NVIDIA runtime is not ready, running preparation.sh..."
    bash ./preparation.sh
  fi
}

prepare_host_if_needed

mkdir -p data

docker compose --env-file .env up -d --build

echo "[OK] Services started."
echo "[OK] vLLM API:   http://localhost:${VLLM_PORT:-8000}/v1"

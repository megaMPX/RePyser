#!/bin/bash
set -e

IMAGE="repyser"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

SAMPLES="$PROJECT_DIR/samples"
REPORTS="$PROJECT_DIR/reports"

if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Docker не установлен"
    exit 1
fi

if [ ! -d "$SAMPLES" ]; then
    mkdir -p "$SAMPLES"
fi

if [ ! -d "$REPORTS" ]; then
    mkdir -p "$REPORTS"
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker build -t "$IMAGE" .
fi

if [ -n "$DISPLAY" ]; then
    xhost +local:docker >/dev/null 2>&1 || true
fi

docker run --rm \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /run \
  --tmpfs /home/sandbox/.cache \
  --network none \
  --cap-drop ALL \
  --pids-limit 128 \
  --memory 1g \
  -e DISPLAY="$DISPLAY" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$SAMPLES":/samples:ro \
  -v "$REPORTS":/reports:rw \
  "$IMAGE"

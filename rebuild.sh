#!/bin/bash
set -e

IMAGE="repyser"

echo "[*] RePyser rebuild script"

if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Docker не установлен"
    exit 1
fi

if docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker rmi "$IMAGE"
fi

docker build -t "$IMAGE" .

echo "[+] OK"

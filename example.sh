#!/usr/bin/env bash
# 示例预览：首次构建 + 后台 --watch + 前台 http.server（与 example.bat 等价）。
# 用法（仓库根）：bash example.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PORT="${PORT:-8000}"
SITE_NAME="${SITE_NAME:-Docserver Example}"

if [[ -f "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
elif [[ -f "$ROOT/.venv/Scripts/python.exe" ]]; then
  PY="$ROOT/.venv/Scripts/python.exe"
else
  echo "==> 创建 .venv 并安装依赖"
  python3 -m venv "$ROOT/.venv"
  PY="$ROOT/.venv/bin/python"
  "$PY" -m pip install -q -U pip setuptools wheel
  "$PY" -m pip install -q -e ".[dev]"
fi

echo "[1/4] Initial build (example/source -> dist)..."
rm -rf "$ROOT/dist"
"$PY" src -s "$ROOT/example/source" -o "$ROOT/dist" --site-name "$SITE_NAME"

echo "[2/4] Watch example/source + theme/ + src/ in background..."
echo "      UI/theme changes need watch or re-run example.sh; then hard-refresh (Ctrl+F5)."
"$PY" src -s "$ROOT/example/source" -o "$ROOT/dist" -v \
  --site-name "$SITE_NAME" --watch --skip-initial &
WATCH_PID=$!
trap 'kill "$WATCH_PID" 2>/dev/null || true' EXIT

echo "[3/4] Open http://127.0.0.1:${PORT}/  (hard refresh after rebuild)"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 || true
fi

echo "[4/4] Static server http.server, Ctrl+C to stop"
exec "$PY" -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT/dist"

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
_child_pids() {
  local pid="$1"
  if command -v pgrep >/dev/null 2>&1; then
    pgrep -P "$pid" 2>/dev/null || true
  elif command -v ps >/dev/null 2>&1; then
    ps -eo pid=,ppid= | awk -v ppid="$pid" '$2 == ppid { print $1 }'
  fi
}

_kill_descendants() {
  local pid="$1"
  local child=""
  for child in $(_child_pids "$pid"); do
    _kill_descendants "$child"
    kill -TERM "$child" 2>/dev/null || true
  done
}

_kill_tree() {
  local pid="$1"
  [[ -z "$pid" ]] && return 0
  kill -0 "$pid" 2>/dev/null || return 0
  _kill_descendants "$pid"
  kill -TERM "$pid" 2>/dev/null || true
  local waited=0
  while kill -0 "$pid" 2>/dev/null && [[ $waited -lt 50 ]]; do
    sleep 0.1
    waited=$((waited + 1))
  done
  if kill -0 "$pid" 2>/dev/null; then
    _kill_descendants "$pid"
    kill -KILL "$pid" 2>/dev/null || true
  fi
}

"$PY" src -s "$ROOT/example/source" -o "$ROOT/dist" -v \
  --site-name "$SITE_NAME" --watch --skip-initial &
WATCH_PID=$!
HTTP_PID=
_cleanup() {
  trap - EXIT INT TERM HUP
  [[ -n "${HTTP_PID:-}" ]] && _kill_tree "$HTTP_PID"
  [[ -n "${WATCH_PID:-}" ]] && _kill_tree "$WATCH_PID"
}
trap _cleanup EXIT INT TERM HUP

echo "[3/4] Open http://127.0.0.1:${PORT}/  (hard refresh after rebuild)"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:${PORT}/" >/dev/null 2>&1 || true
fi

echo "[4/4] Static server http.server, Ctrl+C to stop"
"$PY" -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT/dist" &
HTTP_PID=$!
wait "$HTTP_PID"

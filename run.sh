#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# 源目录（可多个，按顺序合并；后者覆盖同路径文件）
SOURCES=(
  demo
)
OUT=output/site
CACHE_DIR=
BASE_URL=/
SITE_NAME="docserver 示例"
SITE_URL=
LOG=
LOG_LEVEL=INFO
# 1=持续监视源与 theme 变更并重建；0=仅构建一次后退出（解压后快速体验）
WATCH=0

SYNC="$ROOT/dist/docserver-sync"
PIDFILE="$ROOT/.docserver-sync.pid"
ARGS=(
  -s "${SOURCES[@]}"
  -o "$OUT"
  --base-url "$BASE_URL"
  --site-name "$SITE_NAME"
)
if [[ "$WATCH" == "1" ]]; then
  ARGS+=(--watch)
fi
if [[ -n "$SITE_URL" ]]; then
  ARGS+=(--site-url "$SITE_URL")
fi
if [[ -n "$CACHE_DIR" ]]; then
  ARGS+=(--cache-dir "$CACHE_DIR")
fi
if [[ -n "$LOG" ]]; then
  ARGS+=(--log "$LOG")
fi
ARGS+=(--log-level "$LOG_LEVEL")

_kill_sync_group() {
  local pid="$1"
  [[ -z "$pid" ]] && return 0
  kill -0 "$pid" 2>/dev/null || return 0
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
  local waited=0
  while kill -0 "$pid" 2>/dev/null && [[ $waited -lt 50 ]]; do
    sleep 0.1
    waited=$((waited + 1))
  done
  if kill -0 "$pid" 2>/dev/null; then
    kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
  fi
}

_stop_stale_sync() {
  [[ -f "$PIDFILE" ]] || return 0
  local old=""
  old="$(<"$PIDFILE")" || true
  rm -f "$PIDFILE"
  if [[ -n "$old" ]]; then
    echo "停止上次未退出的 docserver-sync (PID $old)…" >&2
    _kill_sync_group "$old"
  fi
}

_cleanup_trap() {
  trap - EXIT INT TERM HUP
  if [[ -n "${SYNC_PID:-}" ]]; then
    _kill_sync_group "$SYNC_PID"
    SYNC_PID=
  fi
  rm -f "$PIDFILE"
}

trap _cleanup_trap EXIT INT TERM HUP
_stop_stale_sync

if command -v setsid >/dev/null 2>&1; then
  setsid "$SYNC" "${ARGS[@]}" &
else
  "$SYNC" "${ARGS[@]}" &
fi
SYNC_PID=$!
echo "$SYNC_PID" >"$PIDFILE"

wait "$SYNC_PID"
exit_code=$?
SYNC_PID=
exit "$exit_code"

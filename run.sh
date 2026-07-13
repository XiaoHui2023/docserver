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

_kill_sync_tree() {
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

_stop_stale_sync() {
  [[ -f "$PIDFILE" ]] || return 0
  local old=""
  old="$(<"$PIDFILE")" || true
  rm -f "$PIDFILE"
  if [[ -n "$old" ]]; then
    echo "停止上次未退出的 docserver-sync (PID $old)…" >&2
    _kill_sync_tree "$old"
  fi
}

_stop_stale_sync

if [[ ! -x "$SYNC" ]]; then
  echo "错误: 未找到可执行文件 $SYNC" >&2
  exit 1
fi

echo "$$" >"$PIDFILE"
exec "$SYNC" "${ARGS[@]}"

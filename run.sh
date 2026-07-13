#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Source directories. Multiple entries are merged in order; later entries override
# the same destination path from earlier entries.
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
# 1 = watch and rebuild; 0 = build once and exit.
WATCH=0
# Polling interval in seconds when WATCH=1. Also controls retry wait after
# recoverable watch/build errors.
INTERVAL=2
# Optional explicit instance id. By default the instance is derived from source,
# output, base URL, site name, and site URL.
DOCSERVER_INSTANCE="${DOCSERVER_INSTANCE:-}"

SYNC="$ROOT/dist/docserver-sync"

_hash_key() {
  local key="$1"
  if command -v cksum >/dev/null 2>&1; then
    printf '%s' "$key" | cksum | awk '{ print $1 }'
  else
    printf '%s' "$key" | tr -c 'A-Za-z0-9_.-' '_'
  fi
}

_instance_key() {
  if [[ -n "$DOCSERVER_INSTANCE" ]]; then
    printf '%s' "$DOCSERVER_INSTANCE"
    return
  fi
  printf '%s' "${SOURCES[*]}|$OUT|$BASE_URL|$SITE_NAME|$SITE_URL"
}

INSTANCE_KEY="$(_instance_key)"
INSTANCE_ID="$(_hash_key "$INSTANCE_KEY")"
if [[ -n "$CACHE_DIR" ]]; then
  EFFECTIVE_CACHE_DIR="$CACHE_DIR"
else
  EFFECTIVE_CACHE_DIR=".docserver-cache/$INSTANCE_ID"
fi
PIDFILE="$EFFECTIVE_CACHE_DIR/.docserver-sync.pid"

ARGS=(
  -s "${SOURCES[@]}"
  -o "$OUT"
  --base-url "$BASE_URL"
  --site-name "$SITE_NAME"
)
if [[ "$WATCH" == "1" ]]; then
  ARGS+=(--watch)
  ARGS+=(--interval "$INTERVAL")
fi
if [[ -n "$SITE_URL" ]]; then
  ARGS+=(--site-url "$SITE_URL")
fi
ARGS+=(--cache-dir "$EFFECTIVE_CACHE_DIR")
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

_pid_matches_sync() {
  local pid="$1"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  if [[ -r "/proc/$pid/cmdline" ]]; then
    tr '\0' '\n' <"/proc/$pid/cmdline" | grep -Fx -- "$SYNC" >/dev/null 2>&1
    return $?
  fi
  if command -v ps >/dev/null 2>&1; then
    ps -p "$pid" -o command= 2>/dev/null | grep -F -- "$SYNC" >/dev/null 2>&1
    return $?
  fi
  return 1
}

_stop_same_instance() {
  [[ -f "$PIDFILE" ]] || return 0
  local old=""
  old="$(<"$PIDFILE")" || true
  rm -f "$PIDFILE"
  if [[ -z "$old" ]]; then
    return 0
  fi
  if _pid_matches_sync "$old"; then
    echo "Stopping previous docserver-sync for this instance (PID $old)..." >&2
    _kill_sync_tree "$old"
  else
    echo "Ignoring stale pidfile for this instance (PID $old is not $SYNC)." >&2
  fi
}

mkdir -p "$(dirname "$PIDFILE")"
_stop_same_instance

if [[ ! -x "$SYNC" ]]; then
  echo "Error: executable not found: $SYNC" >&2
  exit 1
fi

echo "$$" >"$PIDFILE"
exec "$SYNC" "${ARGS[@]}"

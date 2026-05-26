#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

SOURCES=(
  example/source
  other/docs
)
OUT=output/site
BASE_URL=/
SITE_NAME=文档
SITE_URL=
LOG=

SYNC=release/bin/docserver-sync
ARGS=(
  -s "${SOURCES[@]}"
  -o "$OUT"
  --base-url "$BASE_URL"
  --site-name "$SITE_NAME"
  --watch
)
if [[ -n "$SITE_URL" ]]; then
  ARGS+=(--site-url "$SITE_URL")
fi
if [[ -n "$LOG" ]]; then
  ARGS+=(--log "$LOG")
fi

exec "$SYNC" "${ARGS[@]}"

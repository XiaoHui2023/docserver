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
# 1=持续监视源与 theme 变更并重建；0=仅构建一次后退出（解压后快速体验）
WATCH=0

SYNC="$ROOT/release/bin/docserver-sync"
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

exec "$SYNC" "${ARGS[@]}"

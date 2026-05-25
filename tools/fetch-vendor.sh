#!/usr/bin/env bash
# 在线机构建时拉取 theme 所需第三方脚本（仅 build 调用）。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/theme/javascripts/mermaid.min.js"
URL="https://unpkg.com/mermaid@11/dist/mermaid.min.js"

mkdir -p "$(dirname "$DEST")"
if [[ -s "$DEST" ]]; then
  exit 0
fi

if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o "$DEST" "$URL"
elif command -v wget >/dev/null 2>&1; then
  wget -q -O "$DEST" "$URL"
else
  echo "错误: 需要 curl 或 wget 以下载 mermaid.min.js" >&2
  exit 1
fi

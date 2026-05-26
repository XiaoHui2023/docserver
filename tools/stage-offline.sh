#!/usr/bin/env bash
# 组装离线运行目录并打成压缩包（由 build.sh 调用）。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="$ROOT/release/staging"
BIN_NAME="docserver-sync"

rm -rf "$STAGE"
mkdir -p "$STAGE/release/bin"

if [[ -f "$ROOT/dist/${BIN_NAME}" ]]; then
  cp -f "$ROOT/dist/${BIN_NAME}" "$STAGE/release/bin/${BIN_NAME}"
  chmod +x "$STAGE/release/bin/${BIN_NAME}"
elif [[ -f "$ROOT/dist/${BIN_NAME}.exe" ]]; then
  cp -f "$ROOT/dist/${BIN_NAME}.exe" "$STAGE/release/bin/${BIN_NAME}.exe"
else
  echo "错误: 未找到 dist/${BIN_NAME} 或 dist/${BIN_NAME}.exe" >&2
  exit 1
fi

cp -f "$ROOT/run.sh" "$STAGE/"
cp -a "$ROOT/theme" "$STAGE/"
if [[ -d "$ROOT/cache/plugin/privacy" ]]; then
  mkdir -p "$STAGE/cache/plugin"
  cp -a "$ROOT/cache/plugin/privacy" "$STAGE/cache/plugin/"
fi

chmod +x "$STAGE/run.sh"
if [[ -f "$STAGE/release/bin/${BIN_NAME}" ]]; then
  chmod +x "$STAGE/release/bin/${BIN_NAME}"
fi

cp -f "$ROOT/tools/offline-package-readme.txt" "$STAGE/README.txt"

OS_TAG="$(uname -s 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo unknown)"
ARCH_TAG="$(uname -m 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo unknown)"
ARCHIVE="$ROOT/release/docserver-offline-${OS_TAG}-${ARCH_TAG}.tar.gz"
tar -czpf "$ARCHIVE" -C "$STAGE" .

echo "  $ARCHIVE"
echo "  （内含 release/bin、run.sh、theme/、cache/plugin/privacy/）"

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

cp -f "$ROOT/project.yaml" "$ROOT/run.sh" "$ROOT/run.bat" "$STAGE/"
cp -a "$ROOT/theme" "$STAGE/"

cat >"$STAGE/README.txt" <<EOF
docserver 离线运行包

1. 解压到目标目录。
2. 编辑 project.yaml（或 run.sh / run.bat 顶部变量）中的 source、out。
3. 运行 bash run.sh 或 run.bat，将 Markdown 源目录构建为静态站。
4. 用 Nginx 等托管 out 目录。

可执行文件: release/bin/${BIN_NAME}（Windows 为 .exe）
EOF

OS_TAG="$(uname -s 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo unknown)"
ARCH_TAG="$(uname -m 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo unknown)"
ARCHIVE="$ROOT/release/docserver-offline-${OS_TAG}-${ARCH_TAG}.tar.gz"
tar -czf "$ARCHIVE" -C "$STAGE" .

echo "  $ARCHIVE"
echo "  （内含 release/bin、project.yaml、run.sh、run.bat、theme/）"

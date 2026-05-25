#!/usr/bin/env bash
# 将 Markdown 源目录构建为静态站点（调用 docserver-sync / python src，不直接执行 mkdocs 命令）。
# 用法：编辑下方变量后，在仓库根执行 bash run.sh
set -euo pipefail

# ---------- 按需修改 ----------
SOURCE="${DOCSERVER_SOURCE:-docs}"
OUT="${DOCSERVER_OUT:-output/site}"
BASE_URL="${DOCSERVER_BASE_URL:-/}"
SITE_NAME="${DOCSERVER_SITE_NAME:-文档}"
SITE_URL="${DOCSERVER_SITE_URL:-}"
# ------------------------------

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

resolve_path() {
  local p="$1"
  if [[ "$p" = /* ]]; then
    echo "$p"
  else
    echo "$ROOT/$p"
  fi
}

SOURCE="$(resolve_path "$SOURCE")"
OUT="$(resolve_path "$OUT")"

if [[ ! -d "$SOURCE" ]]; then
  echo "错误: 源目录不存在: $SOURCE" >&2
  echo "请创建目录并放入 Markdown，或修改本脚本顶部 SOURCE。" >&2
  exit 1
fi

BIN="$ROOT/release/bin/docserver-sync"
ARGS=(-S "$SOURCE" -O "$OUT" --base-url "$BASE_URL" --site-name "$SITE_NAME" --clean)
if [[ -n "$SITE_URL" ]]; then
  ARGS+=(--site-url "$SITE_URL")
fi

run_build() {
  echo "==> $*"
  "$@"
}

if [[ -x "$BIN" ]]; then
  run_build "$BIN" "${ARGS[@]}"
elif [[ -f "$ROOT/.venv/bin/python" ]]; then
  echo "提示: 未找到 release/bin/docserver-sync，使用 .venv"
  run_build "$ROOT/.venv/bin/python" src "${ARGS[@]}"
else
  echo "错误: 未找到 release/bin/docserver-sync，且无 .venv。" >&2
  echo "请先在在线机执行 bash build.sh，或将 offline-packages 安装为 .venv：" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/pip install --no-index --find-links=offline-packages -e ." >&2
  exit 1
fi

echo ""
echo "已构建到: $OUT"
echo "部署: 将上述目录作为 Web 静态根目录（Nginx / 对象存储等）。"

#!/usr/bin/env bash
# 将 Markdown 源目录构建为静态站点（调用 docserver-sync / python src，不直接执行 mkdocs 命令）。
# 用法：编辑下方变量后，在仓库根执行 bash run.sh
set -euo pipefail

# ---------- 默认值（可被 project.yaml 或环境变量覆盖）----------
SOURCE="example/source"
OUT="output/site"
BASE_URL="/"
SITE_NAME="文档"
SITE_URL=""
# ------------------------------

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

load_project_yaml() {
  local f="$ROOT/project.yaml"
  [[ -f "$f" ]] || return 0
  local line key val
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^([A-Za-z0-9_]+):[[:space:]]*(.*)$ ]] || continue
    key="${BASH_REMATCH[1]}"
    val="${BASH_REMATCH[2]}"
    val="${val#"${val%%[![:space:]]*}"}"
    val="${val%"${val##*[![:space:]]}"}"
    val="${val%\"}"
    val="${val#\"}"
    val="${val%\'}"
    val="${val#\'}"
    case "$key" in
      source) SOURCE="$val" ;;
      out) OUT="$val" ;;
      base_url) BASE_URL="$val" ;;
      site_name) SITE_NAME="$val" ;;
      site_url) SITE_URL="$val" ;;
    esac
  done <"$f"
}

load_project_yaml
[[ -n "${DOCSERVER_SOURCE:-}" ]] && SOURCE="$DOCSERVER_SOURCE"
[[ -n "${DOCSERVER_OUT:-}" ]] && OUT="$DOCSERVER_OUT"
[[ -n "${DOCSERVER_BASE_URL:-}" ]] && BASE_URL="$DOCSERVER_BASE_URL"
[[ -n "${DOCSERVER_SITE_NAME:-}" ]] && SITE_NAME="$DOCSERVER_SITE_NAME"
[[ -n "${DOCSERVER_SITE_URL:-}" ]] && SITE_URL="$DOCSERVER_SITE_URL"

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

ARGS=(-s "$SOURCE" -o "$OUT" --base-url "$BASE_URL" --site-name "$SITE_NAME" --clean)
if [[ -n "$SITE_URL" ]]; then
  ARGS+=(--site-url "$SITE_URL")
fi

run_build() {
  echo "==> $*"
  "$@"
}

resolve_python() {
  if [[ -f "$ROOT/.venv/bin/python" ]]; then
    echo "$ROOT/.venv/bin/python"
  elif [[ -f "$ROOT/.venv/Scripts/python.exe" ]]; then
    echo "$ROOT/.venv/Scripts/python.exe"
  else
    return 1
  fi
}

BIN=""
if [[ -x "$ROOT/release/bin/docserver-sync" ]]; then
  BIN="$ROOT/release/bin/docserver-sync"
elif [[ -f "$ROOT/release/bin/docserver-sync.exe" ]]; then
  BIN="$ROOT/release/bin/docserver-sync.exe"
fi

if [[ -n "$BIN" ]]; then
  run_build "$BIN" "${ARGS[@]}"
elif PY="$(resolve_python)"; then
  echo "提示: 未找到 release/bin/docserver-sync，使用 .venv"
  run_build "$PY" src "${ARGS[@]}"
else
  echo "错误: 未找到 release/bin/docserver-sync（或 .exe），且无 .venv。" >&2
  echo "请先在在线机执行 bash build.sh / build.bat，或将 offline-packages 安装为 .venv：" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/pip install --no-index --find-links=offline-packages -e ." >&2
  echo "（Windows 离线安装用 .venv/Scripts/pip.exe）" >&2
  exit 1
fi

echo ""
echo "已构建到: $OUT"
echo "部署: 将上述目录作为 Web 静态根目录（Nginx / 对象存储等）。"

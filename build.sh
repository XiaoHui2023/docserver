#!/usr/bin/env bash
# 在线机构建（需联网）：安装依赖、拉取 vendor 与 privacy 缓存、示例构建、打包 docserver 可执行文件。
# 用法（仓库根）：bash build.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.venv/bin/python" ]]; then
  PY=("$ROOT/.venv/bin/python")
elif [[ -f "$ROOT/.venv/Scripts/python.exe" ]]; then
  PY=("$ROOT/.venv/Scripts/python.exe")
else
  echo "==> 创建 .venv"
  python3 -m venv "$ROOT/.venv"
  PY=("$ROOT/.venv/bin/python")
fi

echo "==> Python: $("${PY[@]}" -V)"

"${PY[@]}" -m pip install -q -U pip setuptools wheel
"${PY[@]}" -m pip install -q -e ".[dev]"
"${PY[@]}" -m pip install -q "pyinstaller>=6.0"

echo "==> 拉取 theme/vendor（mermaid 等）"
bash "$ROOT/tools/fetch-vendor.sh"

echo "==> 示例构建（写入 privacy 缓存）-> output/smoke-test/"
rm -rf "$ROOT/output/smoke-test"
mkdir -p "$ROOT/output"
"${PY[@]}" src -s "$ROOT/example/source" -o "$ROOT/output/smoke-test" --site-name "构建检查"

echo "==> PyInstaller 打包"
rm -rf "$ROOT/build" "$ROOT/dist" "$ROOT/release"
bash "$ROOT/tools/pack.sh" src

echo "==> 组装离线压缩包 -> release/docserver-offline-*.tar.gz"
bash "$ROOT/tools/stage-offline.sh"
mkdir -p "$ROOT/release/bin"
cp -f "$ROOT/dist/docserver-sync" "$ROOT/release/bin/docserver-sync"
chmod +x "$ROOT/release/bin/docserver-sync"

echo ""
echo "完成。产物："
echo "  release/docserver-offline-*.tar.gz   # 拷到内网机解压即用"
echo "  release/bin/docserver-sync           # 本机调试副本"
echo "  output/smoke-test/                   # 在线构建自检静态站"
echo "下一步：将 tar.gz 拷到离线机解压，编辑 run.sh 后运行 bash run.sh"

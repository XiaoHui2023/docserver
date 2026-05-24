#!/usr/bin/env bash
# 在线机构建（需联网）：安装依赖、预下载离线 wheel、示例站构建（拉取 privacy/字体/CDN）、打包 docserver 可执行文件。
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

echo "==> 下载离线 pip 包到 offline-packages/（供离线机可选安装 .venv）"
rm -rf "$ROOT/offline-packages"
mkdir -p "$ROOT/offline-packages"
"${PY[@]}" -m pip download -d "$ROOT/offline-packages" -e ".[dev]"

echo "==> 示例构建（触发 privacy / 插件外链资源下载）-> output/smoke-test/"
rm -rf "$ROOT/output/smoke-test"
mkdir -p "$ROOT/output"
"${PY[@]}" src build -S "$ROOT/example/source" -O "$ROOT/output/smoke-test" --site-name "构建检查"

echo "==> PyInstaller 打包 -> release/bin/"
rm -rf "$ROOT/build" "$ROOT/dist" "$ROOT/release"
mkdir -p "$ROOT/release/bin"
bash "$ROOT/tools/pack.sh" src
cp -f "$ROOT/dist/docserver-sync" "$ROOT/release/bin/docserver-sync"
chmod +x "$ROOT/release/bin/docserver-sync"

cat >"$ROOT/release/README.txt" <<EOF
docserver 离线运行包（$(date -Iseconds)）

1. 将整个仓库（含 release/bin、theme/、src/、offline-packages/）拷到离线机。
2. 在离线机编辑 run.sh / run.bat 顶部的 SOURCE、OUT。
3. 运行 run：生成静态站到 OUT 目录，用 Nginx 等托管 OUT 即可。

可执行文件：release/bin/docserver-sync
若无网络且未装 .venv，优先使用该二进制执行 build。
EOF

echo ""
echo "完成。产物："
echo "  release/bin/docserver-sync   # 离线机 build 用"
echo "  offline-packages/            # 离线机 pip install --no-index 用（可选）"
echo "  output/smoke-test/           # 在线构建自检静态站"
echo "下一步：将仓库拷到离线机，运行 bash run.sh"

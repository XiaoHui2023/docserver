#!/usr/bin/env bash
# 在线机打包（需联网）：依赖、theme vendor、PyInstaller、离线压缩包。
#
# 用法（仓库根）：
#   ./tools/pack.sh
#   bash tools/pack.sh
# 产物（均在 dist/）：
#   dist/docserver-sync              # 本机可直接运行（Linux 经 staticx）
#   dist/docserver-sync-pyi          # Linux：staticx 前保留的 PyInstaller onefile
#   dist/docserver-offline-*.tar.gz  # 拷到内网机解压即用（含 run.sh、demo/、theme/）
# Linux staticx 另需系统 patchelf（如 apt install patchelf）；macOS 跳过 staticx。
# Spec：仓库根 docserver-cli.spec → docserver-sync。
# 兼容：单文件 ABI 取决于构建机 glibc；旧 Linux 须在目标机实测 staticx 产物。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DIST_NAME="docserver-sync"
SPEC="$ROOT/docserver-cli.spec"

ensure_venv() {
  if [[ -f "$ROOT/.venv/Scripts/python.exe" ]]; then
    PYTHON_CMD=("$ROOT/.venv/Scripts/python.exe")
  elif [[ -f "$ROOT/.venv/bin/python" ]]; then
    PYTHON_CMD=("$ROOT/.venv/bin/python")
  else
    echo "==> 创建 .venv"
    case "$(uname -s 2>/dev/null || true)" in
      MINGW*|MSYS*|CYGWIN*|Windows_NT)
        if command -v py >/dev/null 2>&1; then
          py -3 -m venv "$ROOT/.venv"
        else
          python -m venv "$ROOT/.venv"
        fi
        PYTHON_CMD=("$ROOT/.venv/Scripts/python.exe")
        ;;
      *)
        if ! command -v python3 >/dev/null 2>&1; then
          echo "错误: 需要 python3 以创建 .venv。" >&2
          exit 1
        fi
        python3 -m venv "$ROOT/.venv"
        PYTHON_CMD=("$ROOT/.venv/bin/python")
        ;;
    esac
  fi
  echo "==> Python: $("${PYTHON_CMD[@]}" -V)"
}

apply_staticx_linux() {
  local pyi_out="$ROOT/dist/${DIST_NAME}"
  local pyi_keep="$ROOT/dist/${DIST_NAME}-pyi"
  if [[ ! -f "$pyi_out" ]]; then
    return 0
  fi
  if ! command -v patchelf >/dev/null 2>&1; then
    echo "错误: Linux 下 staticx 需要系统命令 patchelf（例如: sudo apt install patchelf）。" >&2
    exit 1
  fi
  local venv_bin
  venv_bin="$(dirname "${PYTHON_CMD[0]}")"
  export PATH="$venv_bin:$PATH"
  # staticx wheels embed a musl bootloader that old objcopy versions can mangle
  # on Ubuntu 16.04/CentOS 7 class builders. Build staticx from source instead.
  "${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall scons
  "${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall --no-cache-dir --no-build-isolation --no-binary=staticx staticx
  local staticx="$ROOT/.venv/bin/staticx"
  if [[ ! -x "$staticx" ]]; then
    echo "错误: 未找到可执行的 .venv/bin/staticx。" >&2
    exit 1
  fi
  echo "==> 保留 PyInstaller onefile（非 staticx）: $pyi_keep"
  cp -f "$pyi_out" "$pyi_keep"
  chmod +x "$pyi_keep"
  local tmp_out="$ROOT/dist/.${DIST_NAME}-staticx.tmp"
  rm -f "$tmp_out"
  echo "==> staticx: $pyi_keep -> $DIST_NAME"
  if ! "$staticx" "$pyi_keep" "$tmp_out"; then
    rm -f "$tmp_out"
    echo "==> staticx 失败，重试 staticx --no-compress"
    if ! "$staticx" --no-compress "$pyi_keep" "$tmp_out"; then
      echo "错误: staticx 与 staticx --no-compress 均失败；不得跳过 staticx，请检查 patchelf、依赖库与构建日志。" >&2
      exit 1
    fi
  fi
  mv -f "$tmp_out" "$pyi_out"
  chmod +x "$pyi_out"
  local first_load_vaddr
  first_load_vaddr="$(readelf -Wl "$pyi_out" | awk '$1 == "LOAD" { print $3; exit }')"
  if [[ "$first_load_vaddr" == "0x0000000000000000" ]]; then
    echo "错误: staticx 产物 ELF 被旧 objcopy 损坏（首个 LOAD VirtAddr 为 0x0）；请确保 staticx 从源码构建，且不要使用 PyPI wheel bootloader。" >&2
    exit 1
  fi
  echo "完成: $pyi_out（staticx 自解压包；请在目标机实测）"
  echo "      $pyi_keep（仅 PyInstaller；staticx 失败时可单独运行排查）"
}

build_binary() {
  if [[ ! -f "$SPEC" ]]; then
    echo "错误: 未找到 $SPEC" >&2
    exit 1
  fi
  echo "==> PyInstaller: $SPEC"
  "${PYTHON_CMD[@]}" -m PyInstaller --clean --noconfirm "$SPEC"
  if [[ -f "$ROOT/dist/${DIST_NAME}.exe" ]]; then
    echo "完成: $ROOT/dist/${DIST_NAME}.exe（Windows：无 staticx 步骤）"
    return 0
  fi
  if [[ ! -f "$ROOT/dist/${DIST_NAME}" ]]; then
    echo "错误: 未在 dist 找到 ${DIST_NAME} 或 ${DIST_NAME}.exe。" >&2
    exit 1
  fi
  case "$(uname -s 2>/dev/null || true)" in
    Linux)
      if [[ "${PACK_LINUX_SKIP_STATICX:-}" == "1" ]]; then
        echo "完成: $ROOT/dist/${DIST_NAME}（PACK_LINUX_SKIP_STATICX=1，已显式跳过 staticx）"
      else
        apply_staticx_linux
      fi
      ;;
    *) echo "完成: $ROOT/dist/${DIST_NAME}（非 Linux，跳过 staticx）" ;;
  esac
}

ensure_venv

"${PYTHON_CMD[@]}" -m pip install -q -U pip setuptools wheel
"${PYTHON_CMD[@]}" -m pip install -q -e ".[dev]"
"${PYTHON_CMD[@]}" -m pip install -q "pyinstaller>=6.0"

echo "==> 拉取 theme/vendor（mermaid 等）"
bash "$ROOT/tools/fetch-vendor.sh"

echo "==> PyInstaller 打包"
rm -rf "$ROOT/build" "$ROOT/dist"
build_binary

echo "==> 组装离线压缩包 -> dist/docserver-offline-*.tar.gz"
bash "$ROOT/tools/stage-offline.sh"

echo "==> 组装版本化发布压缩包"
"${PYTHON_CMD[@]}" "$ROOT/tools/bundle_release.py"

echo ""
echo "完成。产物（均在 dist/）："
echo "  dist/docserver-sync                  # 本机可直接运行"
echo "  dist/docserver-offline-*.tar.gz      # 拷到内网机解压即用"
echo "  dist/docserver-<version>-<platform>.tar.gz  # GitHub Release 附件"
echo "下一步：将 tar.gz 拷到离线机解压，运行 bash run.sh（默认构建 demo/），再托管 output/site/"

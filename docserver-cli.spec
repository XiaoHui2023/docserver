# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 规格：docserver-sync 主入口 onefile。

构建：仓库根执行 ./pack.sh（Linux 上再 staticx）。
"""
from __future__ import annotations

from pathlib import Path

from PyInstaller.building.api import EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_all, copy_metadata

block_cipher = None

# MkDocs 通过 importlib.metadata 的 entry_points 发现 theme/plugins；
# onefile 须打包包数据与 *.dist-info，否则 theme: material 不可用。
_BUNDLE_IMPORTS = (
    "material",
    "mkdocs",
    "mkdocs_awesome_pages_plugin",
    "pymdownx",
    "markdown",
    "jinja2",
    "babel",
    "pygments",
)
_BUNDLE_METADATA = (
    "mkdocs-material",
    "mkdocs",
    "mkdocs-awesome-pages-plugin",
    "pymdown-extensions",
)


def _collect_pyinstaller_bundle() -> tuple[list, list, list]:
    datas: list = []
    binaries: list = []
    hiddenimports: list = []
    for name in _BUNDLE_IMPORTS:
        pkg_datas, pkg_bins, pkg_hidden = collect_all(name)
        datas += pkg_datas
        binaries += pkg_bins
        hiddenimports += pkg_hidden
    for dist_name in _BUNDLE_METADATA:
        datas += copy_metadata(dist_name)
    hiddenimports += [
        "mkdocs.commands.build",
        "mkdocs.config",
        "material.plugins.privacy.plugin",
        "material.plugins.search.plugin",
        "mkdocs_awesome_pages_plugin",
    ]
    return datas, binaries, hiddenimports


def _repo_root_from_spec() -> Path:
    spec = Path(SPECPATH).resolve()
    seeds = [spec.parent]
    try:
        seeds.append(Path.cwd().resolve())
    except OSError:
        pass
    for seed in seeds:
        for base in [seed, *seed.parents]:
            if (base / "pyproject.toml").is_file() and (base / "src" / "__main__.py").is_file():
                return base
    return spec.parent


_bundle_datas, _bundle_binaries, _bundle_hiddenimports = _collect_pyinstaller_bundle()

repo_root = _repo_root_from_spec()
entry = repo_root / "src" / "__main__.py"

a = Analysis(
    [str(entry)],
    pathex=[str(repo_root / "src")],
    binaries=_bundle_binaries,
    datas=_bundle_datas,
    hiddenimports=_bundle_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="docserver-sync",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

from __future__ import annotations

import shutil
from pathlib import Path

from paths import docs_dir, repo_root

_REPO_ROOT = repo_root()
_REPO_THEME = _REPO_ROOT / "theme"


def engine_watch_paths() -> list[Path]:
    """watch 需监视的引擎路径（主题、构建逻辑与 mkdocs 配置生成）。"""
    return [
        _REPO_THEME,
        _REPO_ROOT / "src",
    ]


def install_theme_assets(work_root: Path) -> None:
    """将 theme/ 复制到工作区 docs/，供 MkDocs extra_css / extra_javascript 打包进站点。"""
    if not _REPO_THEME.is_dir():
        return
    work_root = work_root.resolve()
    docs = docs_dir(work_root)
    stylesheets = docs / "stylesheets"
    javascripts = docs / "javascripts"

    base_css = _REPO_THEME / "docserver-base.css"
    if base_css.is_file():
        stylesheets.mkdir(parents=True, exist_ok=True)
        shutil.copy2(base_css, stylesheets / "docserver-base.css")

    palettes_src = _REPO_THEME / "palettes"
    if palettes_src.is_dir():
        dest_palettes = stylesheets / "palettes"
        dest_palettes.mkdir(parents=True, exist_ok=True)
        for item in palettes_src.glob("*.css"):
            if item.is_file():
                shutil.copy2(item, dest_palettes / item.name)

    js_src = _REPO_THEME / "javascripts"
    if js_src.is_dir():
        javascripts.mkdir(parents=True, exist_ok=True)
        for item in js_src.iterdir():
            if item.is_file():
                shutil.copy2(item, javascripts / item.name)

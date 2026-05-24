from __future__ import annotations

import shutil
from pathlib import Path

from paths import docs_dir

_REPO_ROOT = Path(__file__).resolve().parent.parent
_REPO_THEME = _REPO_ROOT / "theme"


def engine_watch_paths() -> list[Path]:
    """watch 需监视的引擎路径（主题与 mkdocs 配置生成）。"""
    return [
        _REPO_THEME,
        _REPO_ROOT / "src" / "mkdocs_config.py",
        _REPO_ROOT / "src" / "theme_assets.py",
    ]


def install_theme_assets(work_root: Path) -> None:
    """将 theme/ 复制到工作区 docs/，供 MkDocs extra_css / extra_javascript 打包进站点。"""
    if not _REPO_THEME.is_dir():
        return
    work_root = work_root.resolve()
    docs = docs_dir(work_root)

    css_src = _REPO_THEME / "github.css"
    if css_src.is_file():
        dest_css = docs / "stylesheets" / "github.css"
        dest_css.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(css_src, dest_css)

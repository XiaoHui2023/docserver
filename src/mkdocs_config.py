from __future__ import annotations

from pathlib import Path

from paths import MKDOCS_FILE, docs_dir


def _extra_javascript_yaml_lines(work_root: Path) -> str:
    scripts = [
        "javascripts/docserver-boot.js",
        "javascripts/theme-switcher.js",
        "javascripts/path-index.js",
        "javascripts/sidebar-scroll-persist.js",
    ]
    if (work_root / "docs" / "javascripts" / "mermaid.min.js").is_file():
        scripts.insert(0, "javascripts/mermaid-init.js")
    return "\n".join(f"  - {name}" for name in scripts) + "\n"


def _privacy_plugin_yaml() -> str:
    """privacy：仅保留缓存配置；不抓取正文内外链图片/附件，避免内网 URL 构建失败。

    输出为静态 HTML，图片仍用 Markdown 中的原始 URL，由浏览器打开站点时再请求（非构建时下载）。
    主题 bundle 中的脚本仍可在在线 build 时通过 cache 目录处理；正文 ``![](http://…)`` 不再镜像。
    """
    return (
        "  - privacy:\n"
        "      cache: true\n"
        "      cache_dir: cache/plugin/privacy\n"
        "      assets_fetch: false\n"
        "      log: false\n"
    )


def normalize_base_url(base_url: str) -> str:
    raw = (base_url or "/").strip()
    if not raw or raw == "/":
        return "/"
    if not raw.startswith("/"):
        raw = "/" + raw
    return raw.rstrip("/") or "/"


def site_url_from_base(base_url: str, host: str = "https://docs.local") -> str:
    base = normalize_base_url(base_url)
    if base == "/":
        return f"{host.rstrip('/')}/"
    return f"{host.rstrip('/')}{base}/"


def _palette_css_yaml_lines(work_root: Path) -> str:
    pal_dir = work_root / "docs" / "stylesheets" / "palettes"
    if not pal_dir.is_dir():
        return ""
    lines = [
        f"  - stylesheets/palettes/{path.name}"
        for path in sorted(pal_dir.glob("*.css"))
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def write_mkdocs_yml(
    work_root: Path,
    *,
    site_name: str = "文档",
    base_url: str = "/",
    site_url: str | None = None,
) -> Path:
    work_root = work_root.resolve()
    config_path = work_root / MKDOCS_FILE
    resolved_site_url = site_url or site_url_from_base(base_url)
    palette_css = _palette_css_yaml_lines(work_root)
    extra_js = _extra_javascript_yaml_lines(work_root)
    privacy_plugin = _privacy_plugin_yaml()

    text = f"""site_name: {site_name!r}
site_url: {resolved_site_url!r}
docs_dir: docs
use_directory_urls: true
extra:
  generator: false
theme:
  name: material
  language: zh
  font: false
  features:
    - navigation.instant
    - navigation.instant.prefetch
    - navigation.instant.progress
    - navigation.sections
    - navigation.expand
    - navigation.top
    - navigation.indexes
    - navigation.path
    - toc.follow
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.tooltips
  palette:
    # 方案 J（GitHub 灰栏）：grey + blue
    - scheme: default
      primary: grey
      accent: blue
      toggle:
        icon: material/brightness-7
        name: 切换到深色模式
    - scheme: slate
      primary: black
      accent: light blue
      toggle:
        icon: material/brightness-4
        name: 切换到浅色模式
extra_css:
  - stylesheets/docserver-base.css
{palette_css}extra_javascript:
{extra_js}plugins:
{privacy_plugin}  - search:
      lang:
        - zh
        - en
  - awesome-pages
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.snippets
  - attr_list
  - md_in_html
  - tables
  - toc:
      permalink: false
"""
    config_path.write_text(text, encoding="utf-8")
    if not docs_dir(work_root).is_dir():
        raise FileNotFoundError(f"工作区缺少 docs 目录: {docs_dir(work_root)}")
    return config_path

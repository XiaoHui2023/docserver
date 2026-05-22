from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from paths import IGNORE_DIR_NAMES, README_NAMES


@dataclass(frozen=True)
class DocEntry:
    """源目录中的一份 Markdown 与在站点中的目标路径。"""

    source: Path
    rel_source: Path
    dest_rel: Path
    link: str
    title: str


def _title_from_markdown(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or None
    return None


def _title_from_stem(stem: str) -> str:
    return stem.replace("-", " ").replace("_", " ").strip() or stem


def _dest_rel_for_source(rel: Path) -> Path:
    name = rel.name
    parent = rel.parent
    if name in README_NAMES:
        return parent / "index.md"
    return rel


def _link_for_dest(dest_rel: Path) -> str:
    parts = dest_rel.with_suffix("").parts
    if not parts or parts == ("index",):
        return "/"
    if parts[-1] == "index":
        base = "/" + "/".join(parts[:-1])
        return base if base != "/" else "/"
    return "/" + "/".join(parts)


def scan_source(source_root: Path) -> list[DocEntry]:
    """递归扫描源目录中的 Markdown 文件。"""
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(f"源目录不存在: {source_root}")

    entries: list[DocEntry] = []
    for path in sorted(source_root.rglob("*.md")):
        if not path.is_file():
            continue
        rel = path.relative_to(source_root)
        if any(part in IGNORE_DIR_NAMES for part in rel.parts):
            continue
        dest_rel = _dest_rel_for_source(rel)
        title = _title_from_markdown(path) or _title_from_stem(dest_rel.stem)
        entries.append(
            DocEntry(
                source=path,
                rel_source=rel,
                dest_rel=dest_rel,
                link=_link_for_dest(dest_rel),
                title=title,
            )
        )
    return entries

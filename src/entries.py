from __future__ import annotations

from pathlib import Path

ENTRY_STEMS = frozenset({"readme", "index"})


def is_entry_md(filename: str) -> bool:
    stem = Path(filename).stem
    if Path(filename).suffix.lower() != ".md":
        return False
    return stem.lower() in ENTRY_STEMS


def entry_priority(filename: str) -> int:
    """同一目录多入口时：index 优先于 readme。"""
    stem = Path(filename).stem.lower()
    if stem == "index":
        return 0
    if stem == "readme":
        return 1
    return 2


def dest_rel_for_source(rel: Path) -> Path:
    if rel.suffix.lower() == ".md" and is_entry_md(rel.name):
        return rel.parent / "index.md"
    return rel

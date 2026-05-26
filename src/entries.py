from __future__ import annotations

from functools import lru_cache
from pathlib import Path

ENTRY_STEMS = frozenset({"readme", "index"})

_INDEX_STEMS_ORDER = ("index", "Index", "INDEX")


@lru_cache(maxsize=1)
def _readme_stems_order() -> tuple[str, ...]:
    word = "readme"
    variants: list[str] = []
    for mask in range(1 << len(word)):
        chars = [
            word[i].upper() if mask & (1 << i) else word[i].lower()
            for i in range(len(word))
        ]
        variants.append("".join(chars))
    return tuple(
        sorted(set(variants), key=lambda s: (sum(1 for c in s if c.isupper()), s))
    )


def is_entry_md(filename: str) -> bool:
    stem = Path(filename).stem
    if Path(filename).suffix.lower() != ".md":
        return False
    return stem.lower() in ENTRY_STEMS


def entry_home_priority(filename: str) -> tuple[int, int, str]:
    """同一目录入口 Markdown 争首页时：index 类优先于 readme；同类按大小写次序。"""
    stem = Path(filename).stem
    lower = stem.lower()
    if lower == "index":
        if stem in _INDEX_STEMS_ORDER:
            return (0, _INDEX_STEMS_ORDER.index(stem), stem)
        return (0, len(_INDEX_STEMS_ORDER), stem)
    if lower == "readme":
        order = _readme_stems_order()
        if stem in order:
            return (1, order.index(stem), stem)
        return (1, len(order), stem)
    return (2, 0, stem)


def dest_rel_for_source(rel: Path, *, as_homepage: bool) -> Path:
    if as_homepage and rel.suffix.lower() == ".md" and is_entry_md(rel.name):
        return rel.parent / "index.md"
    return rel

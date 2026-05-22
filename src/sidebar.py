from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scan import DocEntry


@dataclass
class _TreeNode:
    name: str
    children: dict[str, _TreeNode] = field(default_factory=dict)
    entries: list[DocEntry] = field(default_factory=list)


def _insert_entry(root: _TreeNode, entry: DocEntry) -> None:
    parts = entry.dest_rel.with_suffix("").parts
    if not parts or parts == ("index",):
        return
    if parts[-1] == "index":
        dir_parts = parts[:-1]
    else:
        dir_parts = parts[:-1]
    node = root
    for part in dir_parts:
        node = node.children.setdefault(part, _TreeNode(name=part))
    node.entries.append(entry)


def _node_to_sidebar_items(node: _TreeNode) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for entry in sorted(node.entries, key=lambda e: e.link):
        items.append({"text": entry.title, "link": entry.link})

    for key in sorted(node.children):
        child = node.children[key]
        child_items = _node_to_sidebar_items(child)
        if not child_items:
            continue
        group_title = key.replace("-", " ").replace("_", " ")
        items.append({"text": group_title, "collapsed": False, "items": child_items})

    return items


def build_sidebar(entries: list[DocEntry]) -> list[dict[str, Any]]:
    """由文档条目生成 VitePress 侧栏结构。"""
    root = _TreeNode(name="")
    home: DocEntry | None = None
    for entry in entries:
        if entry.link == "/":
            home = entry
            continue
        _insert_entry(root, entry)

    sidebar = _node_to_sidebar_items(root)
    if home is not None:
        sidebar.insert(0, {"text": home.title, "link": "/"})
    return sidebar

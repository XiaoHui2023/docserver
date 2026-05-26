from __future__ import annotations

from pathlib import Path

from scan import FileEntry

def _dir_contains_markdown(docs_root: Path, rel_dir: Path) -> bool:
    """目录树内是否至少有一个 .md（无则勿写入 nav，避免 awesome-pages 报错）。"""
    target = docs_root / rel_dir
    if not target.is_dir():
        return False
    try:
        return any(path.is_file() for path in target.rglob("*.md"))
    except OSError:
        return False


def _dir_titles(entries: list[FileEntry]) -> dict[Path, str]:
    titles: dict[Path, str] = {}
    for entry in entries:
        if not entry.is_markdown or entry.title is None or entry.dest_rel.stem != "index":
            continue
        parent = entry.dest_rel.parent
        dir_path = Path(".") if parent == Path(".") else Path(*parent.parts)
        titles[dir_path] = entry.title
    return titles


def _list_dir_content(docs_root: Path, dir_path: Path) -> tuple[list[str], list[str]]:
    full = docs_root / dir_path
    if not full.is_dir():
        return [], []
    md_files: list[str] = []
    subdirs: list[str] = []
    try:
        children = sorted(full.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return [], []
    for child in children:
        if child.name.startswith(".") or child.name == ".pages":
            continue
        if child.is_dir():
            rel_sub = dir_path / child.name
            if _dir_contains_markdown(docs_root, rel_sub):
                subdirs.append(child.name)
        elif child.suffix.lower() == ".md":
            md_files.append(child.name)
    return md_files, subdirs


def _yaml_scalar(value: str) -> str:
    """生成可安全写入 .pages 的 YAML 标量（避免 @、: 等触发解析错误）。"""
    return repr(value)


def _format_pages_yaml(title: str | None, nav: list[str]) -> str:
    lines: list[str] = []
    if title:
        lines.append(f"title: {_yaml_scalar(title)}")
    if nav:
        lines.append("nav:")
        for item in nav:
            lines.append(f"  - {_yaml_scalar(item)}")
    return "\n".join(lines) + "\n"


def write_pages_files(docs_root: Path, entries: list[FileEntry]) -> int:
    """为含导航的目录写入 .pages（mkdocs-awesome-pages）。"""
    titles = _dir_titles(entries)
    written = 0
    seen_dirs: set[Path] = {Path(".")}

    for entry in entries:
        if entry.is_markdown:
            seen_dirs.add(entry.dest_rel.parent)

    stack = list(seen_dirs)
    while stack:
        dir_path = stack.pop()
        md_files, subdirs = _list_dir_content(docs_root, dir_path)
        for sub in subdirs:
            sub_path = dir_path / sub
            if sub_path not in seen_dirs:
                seen_dirs.add(sub_path)
                stack.append(sub_path)

        if not md_files and not subdirs:
            continue

        nav: list[str] = []
        if "index.md" in md_files:
            nav.append("index.md")
        for name in md_files:
            if name != "index.md":
                nav.append(name)
        nav.extend(subdirs)

        if not nav:
            continue

        title = titles.get(dir_path)
        pages_path = docs_root / dir_path / ".pages"
        pages_path.write_text(_format_pages_yaml(title, nav), encoding="utf-8")
        written += 1

    return written

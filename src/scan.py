from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from entries import dest_rel_for_source, entry_priority, is_entry_md
from paths import IGNORE_DIR_NAMES


@dataclass(frozen=True)
class FileEntry:
  source: Path
  rel_source: Path
  dest_rel: Path
  is_markdown: bool
  link: str
  title: str | None


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


def _link_for_dest(dest_rel: Path) -> str:
  parts = dest_rel.with_suffix("").parts
  if not parts or parts == ("index",):
    return "/"
  if parts[-1] == "index":
    base = "/" + "/".join(parts[:-1])
    return base if base != "/" else "/"
  return "/" + "/".join(parts)


def _page_title(path: Path, dest_rel: Path) -> str:
  title = _title_from_markdown(path)
  if title:
    return title
  stem = dest_rel.stem
  if stem == "index" and dest_rel.parent != Path("."):
    stem = dest_rel.parent.name
  return _title_from_stem(stem)


def _should_skip(rel: Path) -> bool:
  return any(part in IGNORE_DIR_NAMES for part in rel.parts)


def scan_source(source_root: Path) -> list[FileEntry]:
  """递归扫描源目录中的全部文件（含静态资源）。"""
  source_root = source_root.resolve()
  if not source_root.is_dir():
    raise FileNotFoundError(f"源目录不存在: {source_root}")

  chosen: dict[Path, tuple[Path, Path]] = {}

  for path in sorted(source_root.rglob("*")):
    if not path.is_file():
      continue
    rel = path.relative_to(source_root)
    if _should_skip(rel):
      continue
    dest_rel = dest_rel_for_source(rel)
    prev = chosen.get(dest_rel)
    if prev is None:
      chosen[dest_rel] = (path, rel)
      continue
    _prev_path, prev_rel = prev
    if path.suffix.lower() == ".md" and is_entry_md(rel.name) and is_entry_md(prev_rel.name):
      if entry_priority(rel.name) < entry_priority(prev_rel.name):
        chosen[dest_rel] = (path, rel)
    else:
      chosen[dest_rel] = (path, rel)

  if not any(d.suffix.lower() == ".md" for d in chosen):
    raise ValueError(f"源目录下未找到 Markdown 文件: {source_root}")

  entries: list[FileEntry] = []
  for dest_rel in sorted(chosen, key=lambda p: str(p).replace("\\", "/")):
    path, rel = chosen[dest_rel]
    is_md = path.suffix.lower() == ".md"
    title = _page_title(path, dest_rel) if is_md else None
    entries.append(
      FileEntry(
        source=path,
        rel_source=rel,
        dest_rel=dest_rel,
        is_markdown=is_md,
        link=_link_for_dest(dest_rel) if is_md else "",
        title=title,
      )
    )
  return entries

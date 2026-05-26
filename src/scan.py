from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from entries import dest_rel_for_source, entry_home_priority, is_entry_md
from paths import IGNORE_DIR_NAMES


@dataclass(frozen=True)
class FileEntry:
  source: Path
  source_root: Path
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
    if base == "/":
      return "/"
    return base + "/"
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


def _homepage_winner_by_dir(
  files: list[tuple[Path, Path]],
) -> dict[Path, Path]:
  """每个目录选出唯一首页源文件（rel）；其余入口 Markdown 保留原文件名。"""
  by_dir: dict[Path, list[Path]] = defaultdict(list)
  for _path, rel in files:
    if rel.suffix.lower() != ".md" or not is_entry_md(rel.name):
      continue
    by_dir[rel.parent].append(rel)

  winners: dict[Path, Path] = {}
  for parent, rels in by_dir.items():
    winners[parent] = min(
      rels,
      key=lambda r: (entry_home_priority(r.name), str(r).replace("\\", "/")),
    )
  return winners


def _dest_rel(rel: Path, homepage_winners: dict[Path, Path]) -> Path:
  winner = homepage_winners.get(rel.parent)
  as_homepage = winner is not None and rel == winner
  return dest_rel_for_source(rel, as_homepage=as_homepage)


def scan_source(source_root: Path) -> list[FileEntry]:
  """递归扫描单个源目录中的全部文件（含静态资源）。"""
  source_root = source_root.resolve()
  if not source_root.is_dir():
    raise FileNotFoundError(f"源目录不存在: {source_root}")

  raw: list[tuple[Path, Path]] = []
  for path in sorted(source_root.rglob("*")):
    if not path.is_file():
      continue
    rel = path.relative_to(source_root)
    if _should_skip(rel):
      continue
    raw.append((path, rel))

  if not any(p.suffix.lower() == ".md" for p, _ in raw):
    raise ValueError(f"源目录下未找到 Markdown 文件: {source_root}")

  homepage_winners = _homepage_winner_by_dir(raw)
  chosen: dict[Path, tuple[Path, Path]] = {}

  for path, rel in raw:
    dest_rel = _dest_rel(rel, homepage_winners)
    prev = chosen.get(dest_rel)
    if prev is None:
      chosen[dest_rel] = (path, rel)
      continue
    _prev_path, prev_rel = prev
    if path.suffix.lower() == ".md" and is_entry_md(rel.name) and is_entry_md(prev_rel.name):
      if entry_home_priority(rel.name) < entry_home_priority(prev_rel.name):
        chosen[dest_rel] = (path, rel)
    else:
      chosen[dest_rel] = (path, rel)

  entries: list[FileEntry] = []
  for dest_rel in sorted(chosen, key=lambda p: str(p).replace("\\", "/")):
    path, rel = chosen[dest_rel]
    is_md = path.suffix.lower() == ".md"
    title = _page_title(path, dest_rel) if is_md else None
    entries.append(
      FileEntry(
        source=path,
        source_root=source_root,
        rel_source=rel,
        dest_rel=dest_rel,
        is_markdown=is_md,
        link=_link_for_dest(dest_rel) if is_md else "",
        title=title,
      )
    )
  return entries


def scan_sources(source_roots: Sequence[Path]) -> list[FileEntry]:
  """按顺序深合并多个源目录；同相对路径后者覆盖前者。"""
  if not source_roots:
    raise ValueError("至少指定一个源目录")

  merged: dict[Path, FileEntry] = {}
  for root in source_roots:
    for entry in scan_source(root):
      merged[entry.dest_rel] = entry

  if not merged:
    raise ValueError("合并后未找到任何文件")
  if not any(e.is_markdown for e in merged.values()):
    raise ValueError("合并后未找到 Markdown 文件")

  return sorted(merged.values(), key=lambda e: str(e.dest_rel).replace("\\", "/"))

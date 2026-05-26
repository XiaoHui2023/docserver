from __future__ import annotations

import json
import shutil
from pathlib import Path

from paths import MANIFEST_NAME, NAV_META_NAME, docs_dir
from collections.abc import Sequence

from scan import FileEntry, scan_sources

# 由 install_theme_assets 写入，勿当作源目录镜像的一部分删除
_RESERVED_DOC_TOP_DIRS = frozenset({"stylesheets", "javascripts"})


def _prune_orphaned_docs(docs: Path, current: set[Path]) -> None:
  """删除 docs/ 中不在本次同步列表内的文件（含历史遗留页）。"""
  for path in list(docs.rglob("*")):
    if not path.is_file():
      continue
    rel = path.relative_to(docs)
    if rel.parts and rel.parts[0] in _RESERVED_DOC_TOP_DIRS:
      continue
    if rel in current:
      continue
    try:
      path.unlink()
    except OSError:
      continue
    parent = path.parent
    while parent != docs and parent.is_dir() and not any(parent.iterdir()):
      try:
        parent.rmdir()
      except OSError:
        break
      parent = parent.parent


def _write_manifest(work_root: Path, entries: list[FileEntry]) -> None:
  manifest = {
    "files": [str(e.dest_rel).replace("\\", "/") for e in entries],
  }
  (work_root / MANIFEST_NAME).write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )


def _write_nav_meta(docs: Path, entries: list[FileEntry]) -> None:
  """侧栏/面包屑脚本用：有目录入口 index 的 URL 路径集合。"""
  index_paths = sorted(
    {e.link for e in entries if e.is_markdown and e.dest_rel.stem == "index"}
  )
  js_dir = docs / "javascripts"
  js_dir.mkdir(parents=True, exist_ok=True)
  (js_dir / NAV_META_NAME).write_text(
    json.dumps({"index_paths": index_paths}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )


def sync_to_work(
  sources: Path | Sequence[Path],
  work_root: Path,
  *,
  clean: bool = False,
  verbose: bool = False,
) -> list[FileEntry]:
  """将源目录（可多个，按顺序深合并）镜像到工作区 docs/。"""
  if isinstance(sources, Path):
    roots = [sources.resolve()]
  else:
    roots = [p.resolve() for p in sources]
  work_root = work_root.resolve()
  docs = docs_dir(work_root)
  docs.mkdir(parents=True, exist_ok=True)

  entries = scan_sources(roots)
  current = {e.dest_rel for e in entries}
  _prune_orphaned_docs(docs, current)

  for entry in entries:
    dest = docs / entry.dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(entry.source, dest)
    if verbose:
      prefix = f"[{entry.source_root.name}] " if len(roots) > 1 else ""
      print(f"  {prefix}{entry.rel_source} -> docs/{entry.dest_rel}")

  _write_manifest(work_root, entries)
  _write_nav_meta(docs, entries)
  return entries

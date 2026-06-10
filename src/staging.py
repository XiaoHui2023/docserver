from __future__ import annotations

import json
import re
import shutil
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import yaml

from paths import IGNORE_FILE_NAMES, MANIFEST_NAME, NAV_META_NAME, docs_dir
from collections.abc import Sequence

from scan import FileEntry, scan_sources

# 由 install_theme_assets 写入，勿当作源目录镜像的一部分删除
_RESERVED_DOC_TOP_DIRS = frozenset({"stylesheets", "javascripts"})

_SYNC_IO_MAX_ATTEMPTS = 8
_SYNC_IO_BASE_DELAY_SEC = 0.05

_T = TypeVar("_T")


def _with_sync_io_retry(action: Callable[[], _T], *, path: Path) -> _T:
  """编辑器保存时源文件可能短暂不可读，短暂重试后再失败。"""
  last_exc: OSError | None = None
  for attempt in range(_SYNC_IO_MAX_ATTEMPTS):
    try:
      return action()
    except FileNotFoundError as exc:
      last_exc = exc
    except PermissionError as exc:
      last_exc = exc
    except OSError as exc:
      if getattr(exc, "errno", None) not in (2, 13):
        raise
      last_exc = exc
    if attempt + 1 < _SYNC_IO_MAX_ATTEMPTS:
      time.sleep(_SYNC_IO_BASE_DELAY_SEC * (attempt + 1))
  if last_exc is not None:
    raise last_exc
  raise FileNotFoundError(path)


def _read_source_text(path: Path) -> str:
  return _with_sync_io_retry(
    lambda: path.read_text(encoding="utf-8"),
    path=path,
  )


def _copy_source_file(source: Path, dest: Path) -> None:
  def _do_copy() -> None:
    shutil.copy2(source, dest)

  _with_sync_io_retry(_do_copy, path=source)

_YAML_FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)


def _split_front_matter(text: str) -> tuple[dict[str, object], str]:
  m = _YAML_FRONT_MATTER_RE.match(text)
  if not m:
    return {}, text
  try:
    parsed = yaml.safe_load(m.group(1))
  except yaml.YAMLError:
    return {}, text
  if not isinstance(parsed, dict):
    return {}, text
  body = text[m.end() :]
  if body.startswith("\n"):
    body = body[1:]
  return parsed, body


def _merge_nav_title(text: str, title: str) -> str:
  """写入 MkDocs / awesome-pages 用的 title，避免全小写文件名被 capitalize。"""
  meta, body = _split_front_matter(text)
  if meta.get("title") is not None:
    return text
  meta = dict(meta)
  meta["title"] = title
  dumped = yaml.safe_dump(
    meta,
    allow_unicode=True,
    default_flow_style=False,
    sort_keys=False,
  ).rstrip()
  return f"---\n{dumped}\n---\n\n{body}"


def _remove_junk_doc_files(docs: Path) -> None:
  """删除 docs/ 内已知的非文档垃圾文件（如 GNU Make 的 makefile.curdir）。"""
  if not docs.is_dir():
    return
  for name in IGNORE_FILE_NAMES:
    candidates: set[Path] = {docs / name}
    candidates.update(docs.rglob(name))
    for path in candidates:
      if not path.is_file():
        continue
      try:
        path.unlink()
      except OSError:
        pass


def _ensure_parent_dirs(dest: Path, docs: Path) -> None:
  """创建目标文件的父目录；若路径上有同名文件则先删除（避免 ENOTDIR）。"""
  try:
    rel_parent = dest.parent.relative_to(docs)
  except ValueError:
    dest.parent.mkdir(parents=True, exist_ok=True)
    return
  cur = docs
  for part in rel_parent.parts:
    cur = cur / part
    if cur.is_file():
      cur.unlink()
  dest.parent.mkdir(parents=True, exist_ok=True)


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
    while parent != docs and parent.is_dir():
      try:
        if any(parent.iterdir()):
          break
      except OSError:
        break
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


def _normalize_nav_path(link: str) -> str:
  if link == "/":
    return "/"
  return link.rstrip("/") + "/"


def _write_nav_meta(docs: Path, entries: list[FileEntry]) -> None:
  """面包屑脚本用：index_paths 为目录入口页；page_paths 为全部 Markdown 页面。"""
  index_paths = sorted(
    {
      _normalize_nav_path(e.link)
      for e in entries
      if e.is_markdown and e.dest_rel.stem == "index"
    }
  )
  page_paths = sorted(
    {_normalize_nav_path(e.link) for e in entries if e.is_markdown}
  )
  js_dir = docs / "javascripts"
  js_dir.mkdir(parents=True, exist_ok=True)
  (js_dir / NAV_META_NAME).write_text(
    json.dumps(
      {"index_paths": index_paths, "page_paths": page_paths},
      ensure_ascii=False,
      indent=2,
    )
    + "\n",
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
  _remove_junk_doc_files(docs)

  entries = scan_sources(roots)
  current = {e.dest_rel for e in entries}
  _prune_orphaned_docs(docs, current)
  _remove_junk_doc_files(docs)

  for entry in entries:
    dest = docs / entry.dest_rel
    _ensure_parent_dirs(dest, docs)
    if entry.is_markdown and entry.title:
      raw = _read_source_text(entry.source)
      dest.write_text(_merge_nav_title(raw, entry.title), encoding="utf-8")
    else:
      _copy_source_file(entry.source, dest)
    if verbose:
      prefix = f"[{entry.source_root.name}] " if len(roots) > 1 else ""
      print(f"  {prefix}{entry.rel_source} -> docs/{entry.dest_rel}")

  _write_manifest(work_root, entries)
  _write_nav_meta(docs, entries)
  return entries

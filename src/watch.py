from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path

from build_site import prepare_work, rebuild_docs
from session_log import format_timestamp, note
from paths import IGNORE_DIR_NAMES
from theme_assets import engine_watch_paths

_WATCH_SKIP_DIR_NAMES = IGNORE_DIR_NAMES | frozenset({".pytest_cache", ".mypy_cache"})


def _source_roots(sources: Path | Sequence[Path]) -> list[Path]:
  if isinstance(sources, Path):
    return [sources.resolve()]
  return [p.resolve() for p in sources]


def _snapshot(roots: list[Path]) -> dict[Path, float]:
  snap: dict[Path, float] = {}
  for root in roots:
    if root.is_file():
      try:
        snap[root.resolve()] = root.stat().st_mtime
      except OSError:
        continue
      continue
    if not root.is_dir():
      continue
    for path in root.rglob("*"):
      if not path.is_file():
        continue
      if any(part in _WATCH_SKIP_DIR_NAMES for part in path.parts):
        continue
      try:
        snap[path.resolve()] = path.stat().st_mtime
      except OSError:
        continue
  return snap


_ROOT_DIR_LABEL = "(根目录)"


def _diff_snapshots(
  before: dict[Path, float], after: dict[Path, float]
) -> set[Path]:
  changed: set[Path] = set()
  for path in set(before) | set(after):
    if before.get(path) != after.get(path):
      changed.add(path)
  return changed


def _subrepo_label(
  path: Path,
  sources: list[Path],
  engine_roots: list[Path],
) -> str:
  """将变更文件归到源下一级子目录，或引擎监视根目录名。"""
  resolved = path.resolve()
  source_set = {s.resolve() for s in sources}
  for source in sources:
    source_r = source.resolve()
    try:
      rel = resolved.relative_to(source_r)
      if len(sources) > 1:
        if len(rel.parts) <= 1:
          return f"{source_r.name}/{_ROOT_DIR_LABEL}"
        return f"{source_r.name}/{rel.parts[0]}"
      if len(rel.parts) <= 1:
        return _ROOT_DIR_LABEL
      return rel.parts[0]
    except ValueError:
      continue
  for root in engine_roots:
    root_r = root.resolve()
    if root_r in source_set:
      continue
    try:
      resolved.relative_to(root_r)
      return root_r.name if root_r.is_dir() else root_r.stem
    except ValueError:
      continue
  return resolved.parent.name


def _format_change_dirs(labels: set[str]) -> str:
  root = _ROOT_DIR_LABEL
  ordered = sorted(x for x in labels if x != root and not x.endswith(f"/{root}"))
  rootish = [x for x in labels if x == root or x.endswith(f"/{root}")]
  if rootish:
    ordered.extend(sorted(rootish))
  return "、".join(ordered)


def _changed_subrepos(
  before: dict[Path, float],
  after: dict[Path, float],
  sources: list[Path],
  watch_roots: list[Path],
) -> set[str]:
  paths = _diff_snapshots(before, after)
  if not paths:
    return set()
  source_set = {s.resolve() for s in sources}
  engine = [r for r in watch_roots if r.resolve() not in source_set]
  return {_subrepo_label(p, sources, engine) for p in paths}


def watch_and_build(
  sources: Path | Sequence[Path],
  out_root: Path,
  *,
  base_url: str = "/",
  site_url: str | None = None,
  site_name: str = "文档",
  interval: float = 2.0,
  verbose: bool = False,
  skip_initial: bool = False,
) -> None:
  """监视源目录任意文件变更并重新构建（不提供 HTTP 预览）。"""
  roots = _source_roots(sources)
  watch_roots = [*roots, *engine_watch_paths()]
  if len(roots) == 1:
    note(f"监视源目录: {roots[0]}")
  else:
    note("监视源目录（按顺序合并）:")
    for root in roots:
      note(f"  - {root}")
  note("监视引擎: theme/、构建配置等")
  note(f"输出目录: {out_root.resolve()}")
  note(f"子路径: {base_url!r}  监视间隔: {interval} 秒（Ctrl+C 结束）")

  def _rebuild() -> None:
    note(f"构建开始: {format_timestamp()}")
    config_path, _ = prepare_work(
      roots,
      out_root,
      base_url=base_url,
      site_url=site_url,
      site_name=site_name,
      verbose=verbose,
    )
    rebuild_docs(config_path, out_root, verbose=verbose)
    note(f"构建结束: {format_timestamp()}")

  if not skip_initial:
    _rebuild()
  last = _snapshot(watch_roots)
  while True:
    time.sleep(interval)
    current = _snapshot(watch_roots)
    dirs = _changed_subrepos(last, current, roots, watch_roots)
    if dirs:
      note(f"检测到变更: {_format_change_dirs(dirs)}，正在重新构建…")
      _rebuild()
      last = current

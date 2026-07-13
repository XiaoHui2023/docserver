from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from pathlib import Path

from build_site import prepare_work, rebuild_docs
from session_log import debug, format_timestamp, note
from paths import IGNORE_DIR_NAMES, IGNORE_FILE_NAMES, WATCH_SOURCE_SUFFIXES, resolve_cache_dir
from scan import iter_source_files
from theme_assets import engine_watch_paths

_WATCH_SKIP_DIR_NAMES = IGNORE_DIR_NAMES | frozenset({".pytest_cache", ".mypy_cache"})


def _skip_watch_rel(rel: Path) -> bool:
  if rel.name in IGNORE_FILE_NAMES:
    return True
  return any(part in _WATCH_SKIP_DIR_NAMES for part in rel.parts)


def _watchable_source_file(path: Path) -> bool:
  return path.suffix.lower() in WATCH_SOURCE_SUFFIXES


def _is_under_any(path: Path, roots: set[Path]) -> bool:
  path_r = path.resolve()
  for root in roots:
    try:
      path_r.relative_to(root.resolve())
      return True
    except ValueError:
      continue
  return False


def _source_roots(sources: Path | Sequence[Path]) -> list[Path]:
  if isinstance(sources, Path):
    return [sources.resolve()]
  return [p.resolve() for p in sources]


def _snapshot(
  roots: list[Path],
  *,
  source_roots: set[Path] | None = None,
  excluded_roots: set[Path] | None = None,
) -> dict[Path, float]:
  started = time.perf_counter()
  source_set = source_roots or set()
  excluded_set = excluded_roots or set()
  snap: dict[Path, float] = {}
  roots_seen = 0
  dirs_seen = 0
  files_seen = 0
  files_kept = 0
  skipped_suffix = 0
  skipped_excluded = 0
  skipped_ignored = 0
  for root in roots:
    roots_seen += 1
    root_r = root.resolve()
    if _is_under_any(root_r, excluded_set):
      skipped_excluded += 1
      continue
    filter_source = root_r in source_set
    if root.is_file():
      if filter_source and not _watchable_source_file(root):
        skipped_suffix += 1
        continue
      if _is_under_any(root.resolve(), excluded_set):
        skipped_excluded += 1
        continue
      try:
        snap[root.resolve()] = root.stat().st_mtime
        files_seen += 1
        files_kept += 1
      except OSError:
        continue
      continue
    if not root.is_dir():
      continue
    dirs_seen += 1
    if filter_source:
      for path in iter_source_files(root_r):
        files_seen += 1
        rel = path.relative_to(root_r)
        if _skip_watch_rel(rel):
          skipped_ignored += 1
          continue
        if _is_under_any(path, excluded_set):
          skipped_excluded += 1
          continue
        if not _watchable_source_file(path):
          skipped_suffix += 1
          continue
        try:
          snap[path] = path.stat().st_mtime
          files_kept += 1
        except OSError:
          continue
      continue
    for path in root.rglob("*"):
      if not path.is_file():
        if path.is_dir():
          dirs_seen += 1
        continue
      files_seen += 1
      if any(part in _WATCH_SKIP_DIR_NAMES for part in path.parts):
        skipped_ignored += 1
        continue
      if _is_under_any(path, excluded_set):
        skipped_excluded += 1
        continue
      try:
        snap[path.resolve()] = path.stat().st_mtime
        files_kept += 1
      except OSError:
        continue
  elapsed = time.perf_counter() - started
  debug(
    "watch.snapshot "
    f"elapsed={elapsed:.3f}s roots={roots_seen} dirs={dirs_seen} "
    f"files_seen={files_seen} files_kept={files_kept} "
    f"skipped_suffix={skipped_suffix} skipped_ignored={skipped_ignored} "
    f"skipped_excluded={skipped_excluded}"
  )
  return snap


_MAX_CHANGED_FILES_LISTED = 8


def _retry_pause_for_interval(interval: float) -> float:
  return max(0.5, interval)


def _diff_snapshots(
  before: dict[Path, float], after: dict[Path, float]
) -> set[Path]:
  changed: set[Path] = set()
  for path in set(before) | set(after):
    if before.get(path) != after.get(path):
      changed.add(path)
  return changed


def _change_kind(path: Path, before: dict[Path, float], after: dict[Path, float]) -> str:
  if path not in before:
    return "新增"
  if path not in after:
    return "删除"
  return "修改"


def _watch_display_path(
  path: Path,
  sources: list[Path],
  engine_roots: list[Path],
) -> str:
  """监视日志用的相对路径（多源时带源目录名前缀）。"""
  source_set = {s.resolve() for s in sources}
  for source in sources:
    source_r = source.resolve()
    try:
      rel = path.relative_to(source_r).as_posix()
      if len(sources) > 1:
        return f"{source_r.name}/{rel}"
      return rel
    except ValueError:
      pass
    try:
      rel = path.resolve().relative_to(source_r).as_posix()
      if len(sources) > 1:
        return f"{source_r.name}/{rel}"
      return rel
    except ValueError:
      continue
  for root in engine_roots:
    root_r = root.resolve()
    if root_r in source_set:
      continue
    try:
      rel = path.resolve().relative_to(root_r).as_posix()
      prefix = root_r.name if root_r.is_dir() else root_r.stem
      return f"{prefix}/{rel}"
    except ValueError:
      continue
  return path.resolve().name


def _rebuild_until_stable(
  *,
  watch_roots: list[Path],
  source_set: set[Path],
  sources: list[Path],
  run_rebuild: Callable[[], None],
  fail_pause: float,
  excluded_roots: set[Path] | None = None,
) -> dict[Path, float]:
  """失败时等待重试；成功后再检查构建期间是否又有变更。"""
  attempt = 0
  while True:
    attempt += 1
    started = time.perf_counter()
    debug(f"watch.rebuild_attempt start attempt={attempt}")
    before = _snapshot(
      watch_roots,
      source_roots=source_set,
      excluded_roots=excluded_roots,
    )
    try:
      run_rebuild()
    except Exception as exc:
      elapsed = time.perf_counter() - started
      debug(
        "watch.rebuild_attempt failed "
        f"attempt={attempt} elapsed={elapsed:.3f}s retry_after={fail_pause:g}s "
        f"error={type(exc).__name__}: {exc}"
      )
      note(f"构建失败，{fail_pause:g}s 后重试: {exc}")
      time.sleep(fail_pause)
      continue
    after = _snapshot(
      watch_roots,
      source_roots=source_set,
      excluded_roots=excluded_roots,
    )
    changed = _diff_snapshots(before, after)
    elapsed = time.perf_counter() - started
    debug(
      "watch.rebuild_attempt done "
      f"attempt={attempt} elapsed={elapsed:.3f}s changed_after_build={len(changed)}"
    )
    if not changed:
      return after
    note("构建期间仍有变更，继续重建…")
    for line in _format_changed_files(before, after, sources, watch_roots):
      note(line)


def _format_changed_files(
  before: dict[Path, float],
  after: dict[Path, float],
  sources: list[Path],
  watch_roots: list[Path],
  *,
  limit: int = _MAX_CHANGED_FILES_LISTED,
) -> list[str]:
  """返回变更文件说明行（已排序；超出 limit 时末尾追加省略提示）。"""
  paths = _diff_snapshots(before, after)
  if not paths:
    return []
  source_set = {s.resolve() for s in sources}
  engine = [r for r in watch_roots if r.resolve() not in source_set]
  entries = sorted(
    (
      _watch_display_path(p, sources, engine),
      _change_kind(p, before, after),
    )
    for p in paths
  )
  lines = [f"  [{kind}] {label}" for label, kind in entries[:limit]]
  extra = len(entries) - limit
  if extra > 0:
    lines.append(f"  … 另有 {extra} 个文件")
  return lines


def _wait_for_settle(
  *,
  watch_roots: list[Path],
  source_set: set[Path],
  baseline: dict[Path, float],
  settle: float,
  poll_interval: float | None = None,
  excluded_roots: set[Path] | None = None,
) -> dict[Path, float]:
  """变更后等待一段时间再采样；与变更初快照一致则视为稳定。"""
  if settle <= 0:
    return baseline
  sleep_for = max(settle, poll_interval) if poll_interval is not None else settle
  debug(f"watch.settle start sleep_for={sleep_for:g}s baseline_files={len(baseline)}")
  loops = 0
  while True:
    loops += 1
    time.sleep(sleep_for)
    current = _snapshot(
      watch_roots,
      source_roots=source_set,
      excluded_roots=excluded_roots,
    )
    changed = _diff_snapshots(baseline, current)
    debug(
      "watch.settle sample "
      f"loop={loops} current_files={len(current)} changed={len(changed)}"
    )
    if not changed:
      return current
    baseline = current


def watch_and_build(
  sources: Path | Sequence[Path],
  out_root: Path,
  *,
  cache_dir: Path | None = None,
  base_url: str = "/",
  site_url: str | None = None,
  site_name: str = "文档",
  interval: float = 2.0,
  settle: float = 1.0,
  verbose: bool = False,
  skip_initial: bool = False,
) -> None:
  """监视源目录与引擎路径变更并重新构建（不提供 HTTP 预览）。"""
  roots = _source_roots(sources)
  source_set = {r.resolve() for r in roots}
  watch_roots = [*roots, *engine_watch_paths()]
  cache_root = resolve_cache_dir(cache_dir)
  excluded_roots = {out_root.resolve(), cache_root.resolve()}
  if len(roots) == 1:
    note(f"监视源目录: {roots[0]}")
  else:
    note("监视源目录（按顺序合并）:")
    for root in roots:
      note(f"  - {root}")
  note(
    "源目录仅监视可能影响构建的后缀（如 .md、.png、.svg、.pdf 等）；"
    "theme/、src/ 仍监视全部文件"
  )
  note("监视引擎: theme/、构建配置等")
  note(f"输出目录: {out_root.resolve()}")
  note(f"构建缓存: {resolve_cache_dir(cache_dir)}")
  note(
    f"子路径: {base_url!r}  监视间隔: {interval} 秒  "
    f"稳定时间: {settle} 秒（Ctrl+C 结束）"
  )
  debug(
    "watch.config "
    f"sources={len(roots)} watch_roots={len(watch_roots)} "
    f"excluded_roots={len(excluded_roots)} skip_initial={skip_initial}"
  )

  def _run_rebuild() -> None:
    started = time.perf_counter()
    note(f"构建开始: {format_timestamp()}")
    config_path, _ = prepare_work(
      roots,
      out_root,
      cache_dir=cache_dir,
      base_url=base_url,
      site_url=site_url,
      site_name=site_name,
      verbose=verbose,
    )
    prepared = time.perf_counter()
    debug(
      "watch.prepare_work "
      f"elapsed={prepared - started:.3f}s config={config_path}"
    )
    rebuild_docs(config_path, out_root, verbose=verbose, live_publish=True)
    rebuilt = time.perf_counter()
    debug(
      "watch.rebuild_docs "
      f"elapsed={rebuilt - prepared:.3f}s total={rebuilt - started:.3f}s"
    )
    note(f"构建结束: {format_timestamp()}")

  fail_pause = _retry_pause_for_interval(interval)

  def _drain_rebuilds() -> dict[Path, float]:
    return _rebuild_until_stable(
      watch_roots=watch_roots,
      source_set=source_set,
      excluded_roots=excluded_roots,
      sources=roots,
      run_rebuild=_run_rebuild,
      fail_pause=fail_pause,
    )

  if not skip_initial:
    last = _drain_rebuilds()
  else:
    debug("watch.skip_initial snapshot start")
    last = _snapshot(
      watch_roots,
      source_roots=source_set,
      excluded_roots=excluded_roots,
    )
  while True:
    try:
      debug(f"watch.loop sleep interval={interval:g}s")
      time.sleep(interval)
      current = _snapshot(
        watch_roots,
        source_roots=source_set,
        excluded_roots=excluded_roots,
      )
      changed_lines = _format_changed_files(last, current, roots, watch_roots)
      debug(
        "watch.loop sample "
        f"last_files={len(last)} current_files={len(current)} "
        f"changed_lines={len(changed_lines)}"
      )
      if changed_lines:
        note("检测到变更，等待稳定…")
        for line in changed_lines:
          note(line)
        _wait_for_settle(
          watch_roots=watch_roots,
          source_set=source_set,
          excluded_roots=excluded_roots,
          baseline=current,
          settle=settle,
          poll_interval=max(settle, interval),
        )
        note("文件已稳定，正在重新构建…")
        last = _drain_rebuilds()
    except Exception as exc:
      debug(
        "watch.loop exception "
        f"retry_after={fail_pause:g}s error={type(exc).__name__}: {exc}"
      )
      note(f"监视异常，{fail_pause:g}s 后继续: {exc}")
      time.sleep(fail_pause)

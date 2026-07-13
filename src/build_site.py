from __future__ import annotations

import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path

from mkdocs_config import normalize_base_url, site_url_from_base, write_mkdocs_yml
from pages import write_pages_files
from paths import (
  docs_dir,
  resolve_cache_dir,
  staging_dir_for,
  validate_cache_staging,
  validate_out_and_cache,
)
from process_priority import background_priority, run_background
from publish import publish_staging_to_out, publish_staging_to_out_live
from session_log import debug, format_timestamp, note
from staging import sync_to_work
from theme_assets import install_theme_assets


def _mkdocs_build_argv(
  config_path: Path,
  out_root: Path,
  *,
  clean_site: bool,
) -> list[str]:
  argv = [
    "build",
    "-f",
    str(config_path),
    "-d",
    str(out_root),
  ]
  if clean_site:
    argv.append("--clean")
  return argv


def _run_mkdocs_inprocess(argv: list[str], *, verbose: bool) -> None:
  from mkdocs.__main__ import cli

  if verbose:
    print("执行: mkdocs", " ".join(argv))
  started = time.perf_counter()
  debug(f"mkdocs.inprocess start argv={' '.join(argv)}")
  saved_argv = sys.argv
  sys.argv = ["mkdocs", *argv]
  try:
    with background_priority():
      exit_code = cli(standalone_mode=False)
  except SystemExit as exc:
    exit_code = exc.code if isinstance(exc.code, int) else 1
  finally:
    sys.argv = saved_argv
  elapsed = time.perf_counter() - started
  debug(f"mkdocs.inprocess done elapsed={elapsed:.3f}s exit_code={exit_code}")
  if exit_code:
    raise subprocess.CalledProcessError(
      exit_code if isinstance(exit_code, int) else 1,
      ["mkdocs", *argv],
    )


def _run_mkdocs(
  config_path: Path,
  out_root: Path,
  *,
  verbose: bool,
  clean_site: bool = True,
) -> None:
  argv = _mkdocs_build_argv(config_path, out_root, clean_site=clean_site)
  if getattr(sys, "frozen", False):
    _run_mkdocs_inprocess(argv, verbose=verbose)
    return
  cmd = [sys.executable, "-m", "mkdocs", *argv]
  if verbose:
    print("执行:", " ".join(cmd))
  started = time.perf_counter()
  debug(f"mkdocs.subprocess start argv={' '.join(cmd)}")
  run_background(cmd, verbose=False)
  elapsed = time.perf_counter() - started
  debug(f"mkdocs.subprocess done elapsed={elapsed:.3f}s")


def _source_roots(source: Path | Sequence[Path]) -> list[Path]:
  if isinstance(source, Path):
    return [source.resolve()]
  return [p.resolve() for p in source]


def prepare_work(
  source: Path | Sequence[Path],
  out_root: Path,
  *,
  cache_dir: Path | None = None,
  base_url: str = "/",
  site_url: str | None = None,
  site_name: str = "文档",
  verbose: bool = False,
) -> tuple[Path, int]:
  """同步源目录到构建缓存并生成 mkdocs.yml，返回 (config_path, 页面数)。"""
  roots = _source_roots(source)
  out_root = out_root.resolve()

  work = resolve_cache_dir(cache_dir)
  staging = staging_dir_for(work)
  validate_out_and_cache(out_root, work)
  validate_cache_staging(work, staging)
  work.mkdir(parents=True, exist_ok=True)

  started = time.perf_counter()
  entries = sync_to_work(roots, work, clean=True, verbose=verbose)
  synced = time.perf_counter()
  page_count = sum(1 for e in entries if e.is_markdown)
  static_count = len(entries) - page_count
  debug(
    "prepare.sync_to_work "
    f"elapsed={synced - started:.3f}s entries={len(entries)} "
    f"pages={page_count} static={static_count}"
  )
  install_theme_assets(work)
  themed = time.perf_counter()
  debug(f"prepare.install_theme_assets elapsed={themed - synced:.3f}s")
  pages_written = write_pages_files(docs_dir(work), entries)
  pages_done = time.perf_counter()
  debug(
    "prepare.write_pages "
    f"elapsed={pages_done - themed:.3f}s pages_files={pages_written}"
  )
  config_path = write_mkdocs_yml(
    work,
    site_name=site_name,
    base_url=base_url,
    site_url=site_url,
  )
  configured = time.perf_counter()
  debug(
    "prepare.write_mkdocs_yml "
    f"elapsed={configured - pages_done:.3f}s total={configured - started:.3f}s "
    f"work={work} staging={staging}"
  )

  if verbose:
    print(f"构建缓存: {work}")
    print(f"构建暂存: {staging}")
    print(
      f"已准备 {page_count} 个页面、{pages_written} 个 .pages，"
      f"base_url={normalize_base_url(base_url)!r}"
    )
    print(f"site_url: {site_url or site_url_from_base(base_url)}")

  return config_path, page_count


def _build_to_staging_and_publish(
  config_path: Path,
  out_root: Path,
  *,
  verbose: bool = False,
  live_publish: bool = False,
) -> None:
  cache_root = config_path.parent.resolve()
  staging = staging_dir_for(cache_root)
  validate_cache_staging(cache_root, staging)
  started = time.perf_counter()
  _run_mkdocs(config_path, staging, verbose=verbose, clean_site=True)
  built = time.perf_counter()
  debug(f"build.mkdocs elapsed={built - started:.3f}s staging={staging}")
  if live_publish:
    publish_staging_to_out_live(staging, out_root)
    published = time.perf_counter()
    debug(
      "build.publish_live "
      f"elapsed={published - built:.3f}s total={published - started:.3f}s "
      f"out={out_root}"
    )
    return
  publish_staging_to_out(staging, out_root, cache_root)
  published = time.perf_counter()
  debug(
    "build.publish "
    f"elapsed={published - built:.3f}s total={published - started:.3f}s "
    f"out={out_root}"
  )


def build_docs(
  source: Path | Sequence[Path],
  out_root: Path,
  *,
  cache_dir: Path | None = None,
  base_url: str = "/",
  site_url: str | None = None,
  site_name: str = "文档",
  verbose: bool = False,
) -> int:
  """将源目录构建为可部署的静态站点。"""
  note(f"构建开始: {format_timestamp()}")
  config_path, page_count = prepare_work(
    source,
    out_root,
    cache_dir=cache_dir,
    base_url=base_url,
    site_url=site_url,
    site_name=site_name,
    verbose=verbose,
  )
  _build_to_staging_and_publish(config_path, out_root.resolve(), verbose=verbose)
  note(f"构建结束: {format_timestamp()}")
  return page_count


def rebuild_docs(
  config_path: Path,
  out_root: Path,
  *,
  verbose: bool = False,
  live_publish: bool = False,
) -> None:
  """监视模式下重建：写入暂存目录，成功后一次性替换输出目录。"""
  _build_to_staging_and_publish(
    config_path,
    out_root.resolve(),
    verbose=verbose,
    live_publish=live_publish,
  )

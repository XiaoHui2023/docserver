from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from mkdocs_config import normalize_base_url, site_url_from_base, write_mkdocs_yml
from pages import write_pages_files
from paths import docs_dir, work_dir_for
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
  saved_argv = sys.argv
  sys.argv = ["mkdocs", *argv]
  try:
    exit_code = cli(standalone_mode=False)
  except SystemExit as exc:
    exit_code = exc.code if isinstance(exc.code, int) else 1
  finally:
    sys.argv = saved_argv
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
  subprocess.run(cmd, check=True)


def prepare_work(
  source: Path,
  out_root: Path,
  *,
  base_url: str = "/",
  site_url: str | None = None,
  site_name: str = "文档",
  clean: bool = False,
  verbose: bool = False,
) -> tuple[Path, int]:
  """同步源目录到工作区并生成 mkdocs.yml，返回 (config_path, 页面数)。"""
  source = source.resolve()
  out_root = out_root.resolve()
  out_root.mkdir(parents=True, exist_ok=True)

  work = work_dir_for(out_root)
  work.mkdir(parents=True, exist_ok=True)

  entries = sync_to_work(source, work, clean=clean, verbose=verbose)
  page_count = sum(1 for e in entries if e.is_markdown)
  install_theme_assets(work)
  pages_written = write_pages_files(docs_dir(work), entries)
  config_path = write_mkdocs_yml(
    work,
    site_name=site_name,
    base_url=base_url,
    site_url=site_url,
  )

  if verbose:
    print(
      f"已准备 {page_count} 个页面、{pages_written} 个 .pages，"
      f"base_url={normalize_base_url(base_url)!r}"
    )
    print(f"site_url: {site_url or site_url_from_base(base_url)}")

  return config_path, page_count


def build_docs(
  source: Path,
  out_root: Path,
  *,
  base_url: str = "/",
  site_url: str | None = None,
  site_name: str = "文档",
  clean: bool = False,
  verbose: bool = False,
) -> int:
  """将源目录构建为可部署的静态站点。"""
  config_path, page_count = prepare_work(
    source,
    out_root,
    base_url=base_url,
    site_url=site_url,
    site_name=site_name,
    clean=clean,
    verbose=verbose,
  )
  _run_mkdocs(config_path, out_root.resolve(), verbose=verbose, clean_site=True)
  return page_count


def rebuild_docs(
  config_path: Path,
  out_root: Path,
  *,
  verbose: bool = False,
) -> None:
  """增量重建（不 --clean），供 watch 在静态服务运行时使用。"""
  _run_mkdocs(config_path, out_root.resolve(), verbose=verbose, clean_site=False)

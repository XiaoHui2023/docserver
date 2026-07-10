from __future__ import annotations

import sys
from pathlib import Path

IGNORE_DIR_NAMES = frozenset({
  ".git",
  ".venv",
  "node_modules",
  "__pycache__",
  ".cache",
  "dist",
  "dist-nav-debug",
  "dist.work",
  "build",
  "cache",
  "output",
  "site",
  "site-staging",
  "site-out-backup",
  ".docserver-cache",
})
# GNU Make 在 Windows 等环境下可能在工作目录留下的临时文件，勿当作文档内容
IGNORE_FILE_NAMES = frozenset({
  "makefile.curdir",
})
MANIFEST_NAME = ".docserver-manifest.json"
NAV_META_NAME = "docserver-nav-meta.json"
DOCS_DIR_NAME = "docs"
MKDOCS_FILE = "mkdocs.yml"

# --watch 源目录轮询：仅这些后缀视为可能影响站点构建（引擎 theme/、src/ 仍监视全部文件）
WATCH_SOURCE_SUFFIXES = frozenset({
  ".md",
  ".markdown",
  ".png",
  ".jpg",
  ".jpeg",
  ".gif",
  ".webp",
  ".svg",
  ".ico",
  ".bmp",
  ".avif",
  ".txt",
  ".pdf",
  ".css",
  ".js",
  ".html",
  ".htm",
  ".woff",
  ".woff2",
  ".ttf",
  ".eot",
  ".otf",
  ".mp4",
  ".webm",
  ".mp3",
  ".wav",
  ".ogg",
  ".zip",
  ".tar",
  ".gz",
  ".7z",
})


def repo_root() -> Path:
  """仓库根目录。PyInstaller onefile 下 __file__ 在临时目录，需从 cwd / 可执行文件路径向上查找 theme/。"""
  if not getattr(sys, "frozen", False):
    return Path(__file__).resolve().parent.parent
  seeds: list[Path] = [Path.cwd(), Path(sys.executable).resolve().parent]
  meipass = getattr(sys, "_MEIPASS", None)
  if meipass:
    seeds.append(Path(meipass))
  seen: set[Path] = set()
  for seed in seeds:
    for base in [seed.resolve(), *seed.resolve().parents]:
      if base in seen:
        continue
      seen.add(base)
      if (base / "theme").is_dir():
        return base
  return Path.cwd()


DEFAULT_CACHE_DIR_NAME = ".docserver-cache"
SITE_STAGING_DIR_NAME = "site-staging"
SITE_OUT_BACKUP_DIR_NAME = "site-out-backup"


def resolve_cache_dir(cache_dir: Path | None) -> Path:
  """构建缓存根目录；未指定时使用当前工作目录下的 `.docserver-cache`。"""
  if cache_dir is None:
    return (Path.cwd() / DEFAULT_CACHE_DIR_NAME).resolve()
  return cache_dir.resolve()


def _is_subpath(child: Path, parent: Path) -> bool:
  try:
    child.resolve().relative_to(parent.resolve())
    return True
  except ValueError:
    return False


def staging_dir_for(cache_root: Path) -> Path:
  """MkDocs 写入的临时站点目录（位于构建缓存内）；构建成功后再一次性替换 out_root。"""
  return cache_root.resolve() / SITE_STAGING_DIR_NAME


def publish_backup_dir(cache_root: Path) -> Path:
  """发布替换时暂存旧 out 的目录（位于构建缓存内）。"""
  return cache_root.resolve() / SITE_OUT_BACKUP_DIR_NAME


def validate_out_and_cache(out_root: Path, cache_root: Path) -> None:
  out_r = out_root.resolve()
  cache_r = cache_root.resolve()
  if out_r == cache_r:
    raise ValueError("输出目录与构建缓存目录不能相同")
  if _is_subpath(cache_r, out_r):
    raise ValueError("构建缓存目录不能位于输出目录内")
  if _is_subpath(out_r, cache_r):
    raise ValueError("输出目录不能位于构建缓存目录内")


def validate_cache_staging(cache_root: Path, staging_root: Path) -> None:
  cache_r = cache_root.resolve()
  staging_r = staging_root.resolve()
  if staging_r == cache_r:
    raise ValueError("构建暂存目录不能与构建缓存根目录相同")
  if not _is_subpath(staging_r, cache_r):
    raise ValueError("构建暂存目录须位于构建缓存目录内")


def docs_dir(work_root: Path) -> Path:
  return work_root / DOCS_DIR_NAME

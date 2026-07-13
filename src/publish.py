from __future__ import annotations

import shutil
import time
from pathlib import Path

from paths import publish_backup_dir
from session_log import debug

_PUBLISH_RETRIES = 3
_PUBLISH_RETRY_DELAY_SEC = 0.4


def _replace_dir(src: Path, dst: Path) -> None:
  """将目录 src 移动为 dst（src 不再存在）；dst 须不存在。"""
  started = time.perf_counter()
  src = src.resolve()
  dst = dst.resolve()
  if dst.exists():
    raise FileExistsError(dst)
  last_error: OSError | None = None
  for attempt in range(_PUBLISH_RETRIES):
    try:
      src.rename(dst)
      debug(
        "publish.replace_dir "
        f"method=rename elapsed={time.perf_counter() - started:.3f}s "
        f"src={src} dst={dst}"
      )
      return
    except OSError as exc:
      last_error = exc
      if attempt + 1 < _PUBLISH_RETRIES:
        time.sleep(_PUBLISH_RETRY_DELAY_SEC)
  if last_error is None:
    raise OSError(f"无法移动目录: {src} -> {dst}")
  try:
    shutil.move(str(src), str(dst))
    debug(
      "publish.replace_dir "
      f"method=shutil.move elapsed={time.perf_counter() - started:.3f}s "
      f"src={src} dst={dst}"
    )
  except OSError as move_error:
    raise OSError(
      f"无法替换输出目录 {dst}：请关闭占用该目录的程序"
      f"（如 http.server、资源管理器窗口）后重试"
    ) from move_error


def publish_staging_to_out(
  staging_root: Path,
  out_root: Path,
  cache_root: Path,
) -> None:
  """将暂存站点目录一次性替换为对外输出目录（构建过程中不改动 out_root）。"""
  started = time.perf_counter()
  staging = staging_root.resolve()
  out = out_root.resolve()
  if not staging.is_dir():
    raise FileNotFoundError(f"构建暂存目录不存在: {staging}")

  backup = publish_backup_dir(cache_root)
  if backup.exists():
    shutil.rmtree(backup)

  had_out = out.exists()
  if had_out:
    _replace_dir(out, backup)

  try:
    _replace_dir(staging, out)
  except OSError:
    if had_out and backup.exists() and not out.exists():
      try:
        _replace_dir(backup, out)
      except OSError:
        pass
    raise

  if backup.exists():
    shutil.rmtree(backup)
  debug(
    "publish.atomic "
    f"elapsed={time.perf_counter() - started:.3f}s had_out={had_out} "
    f"staging={staging} out={out}"
  )


def _staged_files(staging: Path) -> list[Path]:
  started = time.perf_counter()
  files = [path for path in staging.rglob("*") if path.is_file()]
  result = sorted(
    files,
    key=lambda path: (
      path.suffix.lower() in {".html", ".htm"},
      str(path.relative_to(staging)).replace("\\", "/"),
    ),
  )
  debug(
    "publish.staged_files "
    f"elapsed={time.perf_counter() - started:.3f}s files={len(result)} "
    f"staging={staging}"
  )
  return result


def publish_staging_to_out_live(
  staging_root: Path,
  out_root: Path,
) -> None:
  """Publish for watch mode without temporarily removing the served directory."""
  started = time.perf_counter()
  staging = staging_root.resolve()
  out = out_root.resolve()
  if not staging.is_dir():
    raise FileNotFoundError(f"构建暂存目录不存在: {staging}")

  out.mkdir(parents=True, exist_ok=True)
  staged_rels: set[Path] = set()
  copied = 0
  for src in _staged_files(staging):
    rel = src.relative_to(staging)
    staged_rels.add(rel)
    dst = out / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    copied += 1

  removed_files = 0
  for cur in sorted((p for p in out.rglob("*") if p.is_file()), reverse=True):
    rel = cur.relative_to(out)
    if rel not in staged_rels:
      cur.unlink()
      removed_files += 1

  removed_dirs = 0
  for cur in sorted((p for p in out.rglob("*") if p.is_dir()), reverse=True):
    try:
      cur.rmdir()
      removed_dirs += 1
    except OSError:
      pass

  shutil.rmtree(staging)
  debug(
    "publish.live "
    f"elapsed={time.perf_counter() - started:.3f}s copied={copied} "
    f"removed_files={removed_files} removed_dirs={removed_dirs} out={out}"
  )

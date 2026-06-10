from __future__ import annotations

import shutil
import time
from pathlib import Path

from paths import publish_backup_dir

_PUBLISH_RETRIES = 3
_PUBLISH_RETRY_DELAY_SEC = 0.4


def _replace_dir(src: Path, dst: Path) -> None:
  """将目录 src 移动为 dst（src 不再存在）；dst 须不存在。"""
  src = src.resolve()
  dst = dst.resolve()
  if dst.exists():
    raise FileExistsError(dst)
  last_error: OSError | None = None
  for attempt in range(_PUBLISH_RETRIES):
    try:
      src.rename(dst)
      return
    except OSError as exc:
      last_error = exc
      if attempt + 1 < _PUBLISH_RETRIES:
        time.sleep(_PUBLISH_RETRY_DELAY_SEC)
  if last_error is None:
    raise OSError(f"无法移动目录: {src} -> {dst}")
  try:
    shutil.move(str(src), str(dst))
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

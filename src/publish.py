from __future__ import annotations

import shutil
from pathlib import Path

from paths import PUBLISH_BACKUP_SUFFIX


def publish_staging_to_out(staging_root: Path, out_root: Path) -> None:
  """将暂存站点目录一次性替换为对外输出目录（构建过程中不改动 out_root）。"""
  staging = staging_root.resolve()
  out = out_root.resolve()
  if not staging.is_dir():
    raise FileNotFoundError(f"构建暂存目录不存在: {staging}")

  backup = out.with_name(out.name + PUBLISH_BACKUP_SUFFIX)
  if backup.exists():
    shutil.rmtree(backup)

  had_out = out.exists()
  if had_out:
    out.rename(backup)

  try:
    staging.rename(out)
  except OSError:
    if had_out and backup.exists() and not out.exists():
      backup.rename(out)
    raise

  if backup.exists():
    shutil.rmtree(backup)

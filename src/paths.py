from __future__ import annotations

import sys
from pathlib import Path

IGNORE_DIR_NAMES = frozenset({
  ".git",
  ".venv",
  "node_modules",
  "__pycache__",
  "dist",
  "build",
})
MANIFEST_NAME = ".docserver-manifest.json"
DOCS_DIR_NAME = "docs"
MKDOCS_FILE = "mkdocs.yml"


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
      if (base / "theme").is_dir() and (
        (base / "pyproject.toml").is_file() or (base / "project.yaml").is_file()
      ):
        return base
  return Path.cwd()


def work_dir_for(out_root: Path) -> Path:
  return out_root.resolve().with_name(out_root.resolve().name + ".work")


def docs_dir(work_root: Path) -> Path:
  return work_root / DOCS_DIR_NAME

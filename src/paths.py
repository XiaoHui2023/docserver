from __future__ import annotations

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


def work_dir_for(out_root: Path) -> Path:
  return out_root.resolve().with_name(out_root.resolve().name + ".work")


def docs_dir(work_root: Path) -> Path:
  return work_root / DOCS_DIR_NAME

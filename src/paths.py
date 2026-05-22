from __future__ import annotations

README_NAMES = frozenset({"readme.md", "README.md", "Readme.md"})
IGNORE_DIR_NAMES = frozenset({".git", ".venv", "node_modules", ".vitepress", "__pycache__", "dist", "build"})
MANIFEST_NAME = ".docserver-manifest.json"
SIDEBAR_FILE = ".vitepress/sidebar.generated.json"

from __future__ import annotations

import json
import shutil
from pathlib import Path

from paths import MANIFEST_NAME, SIDEBAR_FILE
from scan import DocEntry, scan_source
from sidebar import build_sidebar


def _write_sidebar(out_root: Path, entries: list[DocEntry]) -> Path:
    sidebar_path = out_root / SIDEBAR_FILE
    sidebar_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_sidebar(entries)
    sidebar_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return sidebar_path


def _write_manifest(out_root: Path, entries: list[DocEntry]) -> None:
    manifest = {
        "files": [str(e.dest_rel).replace("\\", "/") for e in entries],
        "sidebar": SIDEBAR_FILE,
    }
    (out_root / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _remove_stale(out_root: Path, entries: list[DocEntry], clean: bool) -> None:
    manifest_path = out_root / MANIFEST_NAME
    current = {e.dest_rel for e in entries}
    if clean and manifest_path.is_file():
        try:
            old = json.loads(manifest_path.read_text(encoding="utf-8"))
            for rel_str in old.get("files", []):
                target = out_root / rel_str
                if target.is_file() and Path(rel_str) not in current:
                    target.unlink()
        except (json.JSONDecodeError, OSError):
            pass
    elif clean:
        for path in out_root.rglob("*.md"):
            rel = path.relative_to(out_root)
            if rel.parts and rel.parts[0] in {".vitepress", "node_modules"}:
                continue
            if rel not in current:
                path.unlink()


def sync_docs(source: Path, out_root: Path, *, clean: bool = False, verbose: bool = False) -> int:
    """将源目录 Markdown 同步到 VitePress 站点根目录。"""
    source = source.resolve()
    out_root = out_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    entries = scan_source(source)
    if not entries:
        raise ValueError(f"源目录下未找到 Markdown 文件: {source}")

    _remove_stale(out_root, entries, clean)

    for entry in entries:
        dest = out_root / entry.dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(entry.source, dest)
        if verbose:
            print(f"  {entry.rel_source} -> {entry.dest_rel}")

    sidebar_path = _write_sidebar(out_root, entries)
    _write_manifest(out_root, entries)

    if verbose:
        print(f"侧栏: {sidebar_path}（{len(entries)} 个页面）")
    return len(entries)

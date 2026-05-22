from __future__ import annotations

import time
from pathlib import Path

from sync import sync_docs


def _snapshot(root: Path) -> dict[Path, float]:
    snap: dict[Path, float] = {}
    if not root.is_dir():
        return snap
    for path in root.rglob("*"):
        if path.is_file():
            try:
                snap[path] = path.stat().st_mtime
            except OSError:
                continue
    return snap


def _changed(before: dict[Path, float], after: dict[Path, float]) -> bool:
    if before.keys() != after.keys():
        return True
    for path, mtime in after.items():
        if before.get(path) != mtime:
            return True
    return False


def serve_watch(
    source: Path,
    out_root: Path,
    *,
    interval: float = 2.0,
    clean: bool = False,
    verbose: bool = False,
) -> None:
    """轮询源目录变更并重复同步。"""
    print(f"监视源目录: {source.resolve()}")
    print(f"输出站点根: {out_root.resolve()}")
    print(f"轮询间隔: {interval} 秒（Ctrl+C 结束）")

    last = _snapshot(source)
    sync_docs(source, out_root, clean=clean, verbose=verbose)

    while True:
        time.sleep(interval)
        current = _snapshot(source)
        if _changed(last, current):
            if verbose:
                print("检测到变更，正在同步…")
            sync_docs(source, out_root, clean=clean, verbose=verbose)
            last = current

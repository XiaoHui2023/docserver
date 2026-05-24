from __future__ import annotations

import time
from pathlib import Path

from build_site import prepare_work, rebuild_docs
from theme_assets import engine_watch_paths


def _snapshot(roots: list[Path]) -> dict[Path, float]:
    snap: dict[Path, float] = {}
    for root in roots:
        if root.is_file():
            try:
                snap[root.resolve()] = root.stat().st_mtime
            except OSError:
                continue
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                try:
                    snap[path.resolve()] = path.stat().st_mtime
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


def watch_and_build(
    source: Path,
    out_root: Path,
    *,
    base_url: str = "/",
    site_url: str | None = None,
    site_name: str = "文档",
    interval: float = 2.0,
    clean: bool = False,
    verbose: bool = False,
    skip_initial: bool = False,
) -> None:
    """监视源目录任意文件变更并重新构建（不提供 HTTP 预览）。"""
    watch_roots = [source.resolve(), *engine_watch_paths()]
    print(f"监视源目录: {source.resolve()}")
    print(f"监视引擎: theme/、mkdocs_config.py 等")
    print(f"输出目录: {out_root.resolve()}")
    print(f"子路径: {base_url!r}  监视间隔: {interval} 秒（Ctrl+C 结束）")

    def _rebuild() -> None:
        config_path, _ = prepare_work(
            source,
            out_root,
            base_url=base_url,
            site_url=site_url,
            site_name=site_name,
            clean=clean,
            verbose=verbose,
        )
        rebuild_docs(config_path, out_root, verbose=verbose)

    if not skip_initial:
        _rebuild()
    last = _snapshot(watch_roots)
    while True:
        time.sleep(interval)
        current = _snapshot(watch_roots)
        if _changed(last, current):
            if verbose:
                print("检测到变更，正在重新构建…")
            _rebuild()
            last = current

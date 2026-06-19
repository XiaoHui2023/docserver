"""Assemble versioned release archive: dist binary plus offline run layout."""

from __future__ import annotations

import pathlib
import platform
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

BINARY_NAMES = ("docserver-sync",)
RELEASE_PATHS = (
    "run.sh",
    "demo",
    "theme",
)
README_SRC = ROOT / "tools" / "offline-package-readme.txt"


def _project_version(root: pathlib.Path) -> str:
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        print("错误: 未在 pyproject.toml 找到 version。", file=sys.stderr)
        raise SystemExit(1)
    return match.group(1)


def _platform_tag() -> str:
    return {"Linux": "linux", "Darwin": "macos", "Windows": "windows"}.get(
        platform.system(), platform.system().lower()
    )


def main() -> int:
    dist = ROOT / "dist"
    tag = f"docserver-{_project_version(ROOT)}-{_platform_tag()}"
    staging_root = dist / ".release-staging"
    bundle_dir = staging_root / tag
    if staging_root.exists():
        shutil.rmtree(staging_root)
    bundle_dir.mkdir(parents=True)
    bundle_dist = bundle_dir / "dist"
    bundle_dist.mkdir(parents=True)

    copied = False
    for name in BINARY_NAMES:
        for candidate in (dist / name, dist / f"{name}.exe"):
            if candidate.is_file():
                shutil.copy2(candidate, bundle_dist / candidate.name)
                if candidate.suffix != ".exe":
                    (bundle_dist / candidate.name).chmod(0o755)
                copied = True
    if not copied:
        print("错误: dist 中未找到可执行文件。", file=sys.stderr)
        return 1

    for rel in RELEASE_PATHS:
        src = ROOT / rel
        if not src.exists():
            print(f"错误: 未找到 {src}", file=sys.stderr)
            return 1
        dest = bundle_dir / rel
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            dest.chmod(0o755)

    if README_SRC.is_file():
        shutil.copy2(README_SRC, bundle_dir / "README.txt")

    privacy_cache = ROOT / "cache" / "plugin" / "privacy"
    if privacy_cache.is_dir():
        dest_privacy = bundle_dir / "cache" / "plugin" / "privacy"
        dest_privacy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(privacy_cache, dest_privacy)

    archive_base = dist / tag
    fmt = "zip" if platform.system() == "Windows" else "gztar"
    for old in (dist / f"{tag}.zip", dist / f"{tag}.tar.gz"):
        if old.is_file():
            old.unlink()
    shutil.make_archive(str(archive_base), fmt, staging_root, tag)
    shutil.rmtree(staging_root)
    suffix = ".zip" if fmt == "zip" else ".tar.gz"
    print(f"完成: {archive_base}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Run the docserver frozen executable against demo/ and verify stable outputs."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"


def _binary_path() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    name = "docserver-sync.exe" if sys.platform == "win32" else "docserver-sync"
    return ROOT / "dist" / name


def _run(binary: Path, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    cmd = [str(binary), *args]
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        print(f"command failed: {' '.join(cmd)}", file=sys.stderr)
        print(completed.stdout, file=sys.stderr)
        print(completed.stderr, file=sys.stderr)
        if completed.returncode in (139, -11):
            print(
                "frozen executable crashed (segmentation fault). "
                "This often indicates a staticx launcher or native library issue. "
                "Do not skip staticx or publish Release unless the user explicitly "
                "requested PACK_LINUX_SKIP_STATICX=1; fix the build or try "
                "staticx --no-compress in pack.sh.",
                file=sys.stderr,
            )
        raise SystemExit(completed.returncode)
    return completed


def _assert_file(path: Path, label: str) -> None:
    if not path.is_file():
        print(f"missing {label}: {path}", file=sys.stderr)
        raise SystemExit(1)


def _assert_contains(path: Path, needle: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        print(f"missing {label!r} in {path}", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    binary = _binary_path()
    if not binary.is_file():
        print(f"frozen executable not found: {binary}", file=sys.stderr)
        return 1
    if not DEMO.is_dir():
        print(f"demo source not found: {DEMO}", file=sys.stderr)
        return 1
    if not (ROOT / "theme").is_dir():
        print(f"theme/ not found under repo root: {ROOT}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="docserver-frozen-example-") as tmp:
        work = Path(tmp)
        output = work / "site"
        _run(
            binary,
            [
                "-s",
                str(DEMO),
                "-o",
                str(output),
                "--base-url",
                "/",
                "--site-name",
                "docserver smoke",
            ],
            ROOT,
        )

        _assert_file(output / "index.html", "index.html")
        _assert_file(output / "search" / "search_index.json", "search index")
        _assert_contains(output / "index.html", "docserver", "site title fragment")
        _assert_contains(
            output / "search" / "search_index.json",
            "docserver",
            "search index content",
        )

    print("frozen example passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

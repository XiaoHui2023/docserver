from __future__ import annotations

import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, TextIO


class _TeeIO(TextIO):
    def __init__(self, stream: TextIO, log_file: TextIO) -> None:
        self._stream = stream
        self._log_file = log_file

    def write(self, data: str) -> int:
        n = self._stream.write(data)
        self._log_file.write(data)
        return n

    def flush(self) -> None:
        self._stream.flush()
        self._log_file.flush()

    def isatty(self) -> bool:
        return self._stream.isatty()

    def __getattr__(self, name: str):
        return getattr(self._stream, name)


def log_file_path(log_dir: Path, when: datetime | None = None) -> Path:
    moment = when or datetime.now()
    return log_dir / moment.strftime("%Y-%m-%d") / f"{moment.strftime('%H-%M-%S')}.log"


def format_timestamp(when: datetime | None = None) -> str:
    return (when or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def session(log_dir: Path | None) -> Iterator[Path | None]:
    """将 stdout/stderr 同时写入日志文件；log_dir 为空则不做文件日志。"""
    if log_dir is None:
        yield None
        return

    path = log_file_path(log_dir.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    log_file = path.open("w", encoding="utf-8")
    orig_out = sys.stdout
    orig_err = sys.stderr
    sys.stdout = _TeeIO(orig_out, log_file)  # type: ignore[assignment]
    sys.stderr = _TeeIO(orig_err, log_file)  # type: ignore[assignment]
    print(f"日志: {path}")
    try:
        yield path
    finally:
        sys.stdout = orig_out
        sys.stderr = orig_err
        log_file.close()


def note(message: str) -> None:
    print(message, flush=True)

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

_LOW_THREAD_ENV = {
  "OMP_NUM_THREADS": "1",
  "OPENBLAS_NUM_THREADS": "1",
  "MKL_NUM_THREADS": "1",
  "NUMEXPR_NUM_THREADS": "1",
  "VECLIB_MAXIMUM_THREADS": "1",
}

_BELOW_NORMAL_PRIORITY_CLASS = 0x00004000


def background_build_env() -> dict[str, str]:
  """Return an environment that avoids helper libraries fanning out CPU threads."""
  env = os.environ.copy()
  for key, value in _LOW_THREAD_ENV.items():
    env.setdefault(key, value)
  return env


def background_subprocess_kwargs() -> dict[str, Any]:
  """Platform subprocess options for a build that should not steal interactivity."""
  if sys.platform == "win32":
    return {"creationflags": _BELOW_NORMAL_PRIORITY_CLASS}
  return {}


@contextmanager
def background_priority() -> Iterator[None]:
  """Temporarily lower the current process priority where it can be restored."""
  if sys.platform != "win32":
    yield
    return

  kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
  handle = kernel32.GetCurrentProcess()
  original = kernel32.GetPriorityClass(handle)
  if not original:
    yield
    return

  changed = bool(kernel32.SetPriorityClass(handle, _BELOW_NORMAL_PRIORITY_CLASS))
  try:
    yield
  finally:
    if changed:
      kernel32.SetPriorityClass(handle, original)


def run_background(cmd: list[str], *, verbose: bool) -> None:
  if verbose:
    print("执行:", " ".join(cmd))
  subprocess.run(
    cmd,
    check=True,
    env=background_build_env(),
    **background_subprocess_kwargs(),
  )

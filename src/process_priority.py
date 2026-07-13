from __future__ import annotations

import ctypes
import os
import signal
import subprocess
import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from typing import Any

_LOW_THREAD_ENV = {
  "OMP_NUM_THREADS": "1",
  "OPENBLAS_NUM_THREADS": "1",
  "MKL_NUM_THREADS": "1",
  "NUMEXPR_NUM_THREADS": "1",
  "VECLIB_MAXIMUM_THREADS": "1",
}

_BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
_CREATE_NEW_PROCESS_GROUP = 0x00000200
_TERMINATE_TIMEOUT_SEC = 5.0


def background_build_env() -> dict[str, str]:
  """Return an environment that avoids helper libraries fanning out CPU threads."""
  env = os.environ.copy()
  for key, value in _LOW_THREAD_ENV.items():
    env.setdefault(key, value)
  return env


def background_subprocess_kwargs() -> dict[str, Any]:
  """Platform subprocess options for a build that should not steal interactivity."""
  if sys.platform == "win32":
    return {"creationflags": _BELOW_NORMAL_PRIORITY_CLASS | _CREATE_NEW_PROCESS_GROUP}
  return {"preexec_fn": _posix_child_setup}


def _posix_child_setup() -> None:
  os.setsid()
  if sys.platform.startswith("linux"):
    _set_linux_parent_death_signal()


def _set_linux_parent_death_signal() -> None:
  try:
    libc = ctypes.CDLL(None)
    pr_set_pdeathsig = 1
    libc.prctl(pr_set_pdeathsig, signal.SIGTERM)
  except Exception:
    pass


def _terminate_process_tree(proc: subprocess.Popen[Any]) -> None:
  if proc.poll() is not None:
    return
  if sys.platform == "win32":
    subprocess.run(
      ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
      check=False,
    )
  else:
    try:
      os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
      return
    except OSError:
      proc.terminate()
  try:
    proc.wait(timeout=_TERMINATE_TIMEOUT_SEC)
    return
  except subprocess.TimeoutExpired:
    pass
  if sys.platform == "win32":
    subprocess.run(
      ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
      check=False,
    )
  else:
    try:
      os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
      return
    except OSError:
      proc.kill()
  proc.wait()


@contextmanager
def _cleanup_child_on_signals(proc: subprocess.Popen[Any]) -> Iterator[None]:
  if threading.current_thread() is not threading.main_thread():
    yield
    return
  signals = [signal.SIGINT, signal.SIGTERM]
  if hasattr(signal, "SIGHUP"):
    signals.append(signal.SIGHUP)
  previous: dict[int, Any] = {}

  def handler(signum: int, frame: Any) -> None:
    _terminate_process_tree(proc)
    if signum == signal.SIGINT:
      raise KeyboardInterrupt
    raise SystemExit(128 + signum)

  try:
    for sig in signals:
      previous[sig] = signal.getsignal(sig)
      signal.signal(sig, handler)
    yield
  finally:
    for sig, old_handler in previous.items():
      signal.signal(sig, old_handler)


def _subprocess_context(proc: subprocess.Popen[Any]) -> Any:
  try:
    return _cleanup_child_on_signals(proc)
  except ValueError:
    return nullcontext()


def _run_process(cmd: list[str], *, verbose: bool) -> None:
  if verbose:
    print("执行:", " ".join(cmd))
  proc = subprocess.Popen(
    cmd,
    env=background_build_env(),
    **background_subprocess_kwargs(),
  )
  try:
    with _subprocess_context(proc):
      returncode = proc.wait()
  except BaseException:
    _terminate_process_tree(proc)
    raise
  if returncode:
    raise subprocess.CalledProcessError(returncode, cmd)


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
  _run_process(cmd, verbose=verbose)

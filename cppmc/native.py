"""C++ native UI helpers loaded through ctypes, with a pure-Python fallback.

The compiled module lives in ``native/cppmc_native.cpp`` (C++17, plain C ABI) and
smooths the progress bar plus paces UI refreshes. When the DLL is missing — a
dev machine without a compiler, or a fallback build — every function has an
identical pure-Python implementation, so the launcher always works.
"""

from __future__ import annotations

import ctypes
import sys
import time
from pathlib import Path

_lib = None


def _candidates() -> list[Path]:
    here = Path(__file__).resolve().parent
    frozen = getattr(sys, "_MEIPASS", None)
    paths: list[Path] = []
    if frozen:
        paths.append(Path(frozen) / "cppmc" / "native" / "cppmc_native.dll")
    # repo / source layout: cppmc/native/cppmc_native.dll
    paths.append(here / "native" / "cppmc_native.dll")
    # repo layout with the source dir next to the package
    paths.append(here.parent / "native" / "cppmc_native.dll")
    return paths


def _load() -> ctypes.CDLL | None:
    for path in _candidates():
        if not path.is_file():
            continue
        try:
            lib = ctypes.CDLL(str(path))
            for name in ("cppmc_ease", "cppmc_mix", "cppmc_approach"):
                getattr(lib, name).restype = ctypes.c_double
                getattr(lib, name).argtypes = [ctypes.c_double] * (
                    3 if name != "cppmc_ease" else 1
                )
            lib.cppmc_frame_pace.restype = ctypes.c_int
            lib.cppmc_frame_pace.argtypes = [ctypes.c_int64, ctypes.c_int64, ctypes.c_int]
            lib.cppmc_clip_int.restype = ctypes.c_int
            lib.cppmc_clip_int.argtypes = [ctypes.c_int] * 3
            return lib
        except OSError:
            continue
    return None


_lib = _load()


def available() -> bool:
    """True when the compiled C++ module was loaded."""
    return _lib is not None


# -------------------------------------------------------------------------- #
# pure-Python fallbacks (identical math)
# -------------------------------------------------------------------------- #

def ease(t: float) -> float:
    """Smoothstep easing, clamped to [0, 1]."""
    if _lib is not None:
        return float(_lib.cppmc_ease(float(t)))
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return t * t * (3.0 - 2.0 * t)


def mix(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    if _lib is not None:
        return float(_lib.cppmc_mix(float(a), float(b), float(t)))
    return a + (b - a) * t


def approach(shown: float, target: float, k: float) -> float:
    """Move ``shown`` toward ``target`` by factor ``k`` each frame."""
    if _lib is not None:
        return float(_lib.cppmc_approach(float(shown), float(target), float(k)))
    return shown + (target - shown) * k


def frame_pace(now_ms: int, last_ms: int, min_interval_ms: int) -> int:
    """Return 1 once ``min_interval_ms`` has passed since ``last_ms``."""
    if _lib is not None:
        return int(_lib.cppmc_frame_pace(int(now_ms), int(last_ms), int(min_interval_ms)))
    return 1 if (now_ms - last_ms) >= min_interval_ms else 0


def clip_int(value: int, lo: int, hi: int) -> int:
    """Clamp ``value`` into [lo, hi]."""
    if _lib is not None:
        return int(_lib.cppmc_clip_int(int(value), int(lo), int(hi)))
    return max(lo, min(hi, value))


def now_ms() -> int:
    return time.time_ns() // 1_000_000

"""
Style-match metric: DTW distance between a rollout's joint-angle trajectory and a
reference swing (data/references/<style>_swing.npz, key 'joints_rad', shape (T, 11)).

Definition
  1. Each trajectory is (T, 11) in radians (env qpos[14:25]).
  2. Classic DTW (full window) with Euclidean frame cost over the 11 joints.
  3. Score = DTW path cost / (len(path)) i.e. mean per-aligned-frame joint-space
     distance in radians. 0 = identical; lower = closer to the reference style.
  DTW makes the score tolerant to tempo differences; tempo is not scored.
  Per-episode scores are averaged (also reported as std via style_match_stats).
"""
from pathlib import Path
from typing import Dict, Sequence

import numpy as np

REF_DIR = Path(__file__).resolve().parent.parent / "data" / "references"


try:
    from numba import njit
except Exception:  # numba optional: slow pure-python fallback
    def njit(f=None, **k):
        return f if f is not None else (lambda g: g)


@njit(cache=True)
def _dtw(cost):
    n, m = cost.shape
    acc = np.full((n + 1, m + 1), np.inf); acc[0, 0] = 0.0
    steps = np.zeros((n + 1, m + 1), np.int64)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            a, b, c = acc[i - 1, j - 1], acc[i - 1, j], acc[i, j - 1]
            if a <= b and a <= c:
                best, bs = a, steps[i - 1, j - 1]
            elif b <= c:
                best, bs = b, steps[i - 1, j]
            else:
                best, bs = c, steps[i, j - 1]
            acc[i, j] = cost[i - 1, j - 1] + best
            steps[i, j] = bs + 1
    return acc[n, m] / steps[n, m]


def dtw_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Length-normalized DTW distance between (Ta, D) and (Tb, D) sequences."""
    a = np.atleast_2d(np.asarray(a, float)); b = np.atleast_2d(np.asarray(b, float))
    cost = np.ascontiguousarray(np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1))
    return float(_dtw(cost))


UPPER_COLS = slice(0, 5)   # joint cols 0-4 (shoulder/elbow block); cols 5-10 = legs (unreliable in Mason refs)


def reference_path(style: str) -> Path:
    # "scott" -> scott_swing.npz ; "mason_swing_part1_s05_refined" -> that file
    return REF_DIR / (f"{style}.npz" if style.startswith("mason_") else f"{style}_swing.npz")


def load_reference(style: str) -> np.ndarray:
    """(T, 11) radians. Synthetic refs: key 'joints_rad'. Mason video refs: key 'joints' is DEGREES (same 11-col
    order as env qpos[14:25]); converted with deg2rad and only frames with valid_mask kept (DTW tolerates the gaps/tempo)."""
    path = reference_path(style)
    if not path.exists():
        raise FileNotFoundError(f"no reference for style '{style}': {path}")
    d = np.load(path, allow_pickle=True)
    if "joints_rad" in d.files:
        return d["joints_rad"]
    j = np.deg2rad(d["joints"].astype(float))
    if "valid_mask" in d.files and d["valid_mask"].any():
        j = j[d["valid_mask"].astype(bool)]
    return j


def style_match_stats(trajs: Sequence[np.ndarray], style: str, cols=None) -> Dict[str, float]:
    ref = load_reference(style)
    if cols is not None:
        ref = ref[:, cols]; trajs = [t[:, cols] for t in trajs]
    s = np.array([dtw_distance(t, ref) for t in trajs])
    return {"mean": float(s.mean()), "std": float(s.std()), "min": float(s.min()), "max": float(s.max())}


def style_match_score(trajs: Sequence[np.ndarray], style: str) -> float:
    return style_match_stats(trajs, style)["mean"]

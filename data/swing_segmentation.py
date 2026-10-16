"""Numeric core for splitting screen recordings of a social feed into individual golf swings.

No cv2/mediapipe needed here (so it is unit-testable).  Three jobs:

1. Layout   - find the video tile inside a dark-mode feed screenshot (`find_video_rows`),
              group frames into spans where the tile is stationary (`stable_spans`) and
              mark hard cuts / duplicate frames (`frame_changes`).  Scrolling frames and
              UI-only frames never become swing candidates.
2. Swings   - `detect_swings` finds address -> top -> impact -> finish windows from the
              image-space hand track, using per-frame timestamps (variable fps safe).
3. Dedup    - `trajectory_signature` / `is_duplicate` flag autoplay-loop repeats.

Units: pixel tracks are normalised by torso length, so speeds are in torso-lengths/s and
do not depend on how big the golfer is in the tile.  Tempo = backswing time / downswing
time, measured takeaway -> top -> peak-hand-speed (a proxy for impact).  At ~30 fps source
video, one frame is ~0.033 s, i.e. ~12% of a 0.28 s downswing: tempo is +-15% at best.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    from scipy.signal import find_peaks, savgol_filter
except Exception:  # pragma: no cover
    find_peaks = savgol_filter = None


# ------------------------------------------------------------------------------ layout
def find_video_rows(frame_bgr: np.ndarray, *, dark_thr: int = 45, row_frac: float = 0.8,
                    close_gap: int = 12, min_rows: int = 50, max_rows: Optional[int] = None
                    ) -> Optional[Tuple[int, int]]:
    """Return (top_row, bottom_row) of the video tile in a low-res (h,w,3) dark-UI frame.

    A row belongs to the tile when >= row_frac of its pixels are brighter than the dark UI
    background.  Short dark gaps (night scenes, black letterbox) up to `close_gap` rows are
    bridged.  The tallest run wins; None if no run is >= min_rows (UI-only / full-screen
    white app / too small).  Runs taller than max_rows (default 0.6*h) are rejected, which
    removes full-screen non-feed screens."""
    h = frame_bgr.shape[0]
    max_rows = max_rows if max_rows is not None else int(0.6 * h)
    frac = (frame_bgr.max(axis=2) >= dark_thr).mean(axis=1)
    idx = np.flatnonzero(frac >= row_frac)
    if idx.size == 0:
        return None
    runs, st, prev = [], int(idx[0]), int(idx[0])
    for i in idx[1:]:
        if i - prev <= close_gap + 1:
            prev = int(i)
        else:
            runs.append((st, prev))
            st = prev = int(i)
    runs.append((st, prev))
    runs = [r for r in runs if min_rows <= r[1] - r[0] + 1 <= max_rows]
    if not runs:
        return None
    return max(runs, key=lambda r: r[1] - r[0])


@dataclass
class Span:
    start: int          # first frame index
    end: int            # last frame index (inclusive)
    top: int
    bottom: int


def stable_spans(rows: Sequence[Optional[Tuple[int, int]]], t: np.ndarray, *, tol: int = 2,
                 min_dur_s: float = 1.0, cut_flags: Optional[np.ndarray] = None) -> List[Span]:
    """Group consecutive frames whose tile (top,bottom) stays within `tol` rows of the
    span's first frame and that have no hard cut inside; keep spans >= min_dur_s long."""
    spans: List[Span] = []
    cur: Optional[List[int]] = None
    ref: Optional[Tuple[int, int]] = None
    for i, r in enumerate(rows):
        cut = bool(cut_flags[i]) if cut_flags is not None else False
        ok = r is not None and ref is not None and abs(r[0] - ref[0]) <= tol \
            and abs(r[1] - ref[1]) <= tol and not cut
        if ok:
            cur[1] = i
            continue
        if cur is not None:
            spans.append(Span(cur[0], cur[1], ref[0], ref[1]))
        if r is None:
            cur, ref = None, None
        else:
            cur, ref = [i, i], r
    if cur is not None:
        spans.append(Span(cur[0], cur[1], ref[0], ref[1]))
    return [s for s in spans if t[s.end] - t[s.start] >= min_dur_s]


def frame_changes(gray_small: np.ndarray, *, dup_thr: float = 0.1, cut_thr: float = 20.0
                  ) -> Tuple[np.ndarray, np.ndarray]:
    """gray_small: (n,h,w) uint8 crop (or whole low-res frame).  Returns (is_dup, is_cut),
    both (n,) bool; entry i compares frame i with i-1 (frame 0 is neither)."""
    g = gray_small.astype(np.int16)
    d = np.zeros(len(g))
    if len(g) > 1:
        d[1:] = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    return d < dup_thr, d > cut_thr


def pose_jump_cuts(xy: np.ndarray, torso_len: float, thr: float = 1.0) -> np.ndarray:
    """Indices i where the body 'teleports' between unique frame i-1 and i.

    Autoplay loops and edited clips jump the pose while the background is unchanged, so a
    pixel-difference cut detector misses them.  xy is (n,K,2) landmark pixels (NaN ok).
    A jump = any tracked landmark moves more than thr torso-lengths in one frame step.
    Measured on real data: loop/edit jumps were 1.65-1.7 torso/step; the fastest real
    downswing hand step at ~30 fps was ~0.55 (so thr=1.0 separates them with margin)."""
    if len(xy) < 2 or not np.isfinite(torso_len) or torso_len <= 0:
        return np.zeros(0, int)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        step = np.nanmax(np.linalg.norm(np.diff(xy, axis=0), axis=2), axis=1) / torso_len
    return np.flatnonzero(np.nan_to_num(step, nan=0.0) > thr) + 1


# ------------------------------------------------------------------------------ swings
@dataclass
class SwingParams:
    fs: float = 60.0               # analysis rate after uniform resampling (Hz)
    smooth_s: float = 0.12         # Savitzky-Golay window for the hand track
    max_gap_s: float = 0.25        # longer tracking gaps invalidate the track
    peak_speed: float = 5.0        # torso-lengths/s needed for a downswing peak
    quiet_speed: float = 0.7       # below this the hands count as "still"
    quiet_hold_s: float = 0.10
    min_peak_gap_s: float = 1.0
    max_backswing_s: float = 2.5
    max_follow_s: float = 1.5
    min_phase_s: float = 0.10      # backswing and downswing must each last at least this
    pad_before_s: float = 0.4
    pad_after_s: float = 0.3
    top_above_shoulder: float = 0.05   # hands must reach this * torso above shoulder line
    tempo_range: Tuple[float, float] = (1.0, 6.0)


@dataclass
class Swing:
    start_t: float
    end_t: float
    takeaway_t: float
    top_t: float
    impact_t: float
    peak_speed: float
    backswing_s: float
    downswing_s: float
    tempo: float                   # NaN when not reliably measurable
    flags: List[str] = field(default_factory=list)


def _interp_nan(t: np.ndarray, y: np.ndarray, tg: np.ndarray, max_gap_s: float
                ) -> Tuple[np.ndarray, np.ndarray]:
    """Resample y(t) to tg; returns (values, valid) where valid is False inside gaps
    longer than max_gap_s or outside the observed range."""
    ok = np.isfinite(y)
    if ok.sum() < 2:
        return np.full(tg.shape, np.nan), np.zeros(tg.shape, bool)
    tt, yy = t[ok], y[ok]
    out = np.interp(tg, tt, yy)
    k = np.clip(np.searchsorted(tt, tg), 1, len(tt) - 1)
    gap = tt[k] - tt[k - 1]
    valid = (gap <= max_gap_s) & (tg >= tt[0]) & (tg <= tt[-1])
    return out, valid


def hand_speed(t: np.ndarray, hands_xy: np.ndarray, torso_len: float, p: SwingParams
               ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return (tg, speed[torso/s], hand_y_smoothed[px], valid) on a uniform grid."""
    tg = np.arange(t[0], t[-1], 1.0 / p.fs)
    if len(tg) < 8:
        z = np.zeros(len(tg))
        return tg, z, z, np.zeros(len(tg), bool)
    x, vx = _interp_nan(t, hands_xy[:, 0], tg, p.max_gap_s)
    y, vy = _interp_nan(t, hands_xy[:, 1], tg, p.max_gap_s)
    valid = vx & vy
    w = max(5, int(p.smooth_s * p.fs) | 1)
    if savgol_filter is not None and len(tg) > w:
        x = savgol_filter(np.nan_to_num(x), w, 2)
        y = savgol_filter(np.nan_to_num(y), w, 2)
    sp = np.hypot(np.gradient(x, 1.0 / p.fs), np.gradient(y, 1.0 / p.fs)) / max(torso_len, 1e-6)
    sp = np.where(valid, sp, 0.0)
    k = max(3, int(0.1 * p.fs))   # moving average: frame-drop / pose jitter makes raw speed spiky
    sp = np.convolve(sp, np.ones(k) / k, mode="same")
    return tg, sp, y, valid


def detect_swings(t: np.ndarray, hands_xy: np.ndarray, shoulder_y: np.ndarray, torso_len: float,
                  params: Optional[SwingParams] = None
                  ) -> Tuple[List[Swing], List[Dict]]:
    """Find swings in one continuous clip (no cuts inside).

    t          (n,) seconds, strictly increasing, may be irregular (variable fps).
    hands_xy   (n,2) pixel position of the hands (mean of wrists); NaN where untracked.
    shoulder_y (n,) pixel y of the shoulder midline (image y grows downward).
    torso_len  pixels, shoulder-mid to hip-mid; normalises speed and heights.
    Returns (swings, rejected); each rejected entry is {"t": peak time, "reason": str}."""
    p = params or SwingParams()
    t = np.asarray(t, float)
    hands_xy = np.asarray(hands_xy, float)
    if len(t) < 8 or not np.isfinite(torso_len) or torso_len <= 0:
        return [], []
    if np.any(np.diff(t) <= 0):
        raise ValueError("timestamps must be strictly increasing")
    tg, sp, hy, valid = hand_speed(t, hands_xy, torso_len, p)
    if len(tg) < 8:
        return [], []
    sy, _ = _interp_nan(t, np.asarray(shoulder_y, float), tg, 1e9)
    fs = p.fs
    peaks, _ = find_peaks(sp, height=p.peak_speed, distance=max(1, int(p.min_peak_gap_s * fs)))
    swings: List[Swing] = []
    rejected: List[Dict] = []
    hold = max(1, int(p.quiet_hold_s * fs))
    quiet = sp < p.quiet_speed

    def quiet_run_before(i: int, lo: int) -> int:
        """Walk back from i; return the index where a quiet run of `hold` samples begins
        (i.e. the takeaway: last non-quiet sample after the quiet run)."""
        run = 0
        for j in range(i, lo, -1):
            run = run + 1 if quiet[j] else 0
            if run >= hold:
                return min(j + run - 1, i)
        return lo

    def quiet_run_after(i: int, hi: int) -> int:
        run = 0
        for j in range(i, hi):
            run = run + 1 if quiet[j] else 0
            if run >= int(0.15 * fs):
                return j - run + 1
        return hi

    # Greedy non-maximum suppression: strongest peak first; weaker peaks that fall inside an
    # already accepted swing (follow-through flourish, walking away) are not new swings.
    taken: List[Tuple[int, int]] = []          # (takeaway_idx, finish_idx) of accepted swings
    n = len(tg)
    for pk in sorted(peaks, key=lambda i: -sp[i]):
        if any(a0 - int(0.5 * fs) <= pk <= a1 + int(0.5 * fs) for a0, a1 in taken):
            continue
        b0 = max(0, pk - int(p.max_backswing_s * fs))
        top = b0 + int(np.argmin(np.where(valid[b0:pk + 1], hy[b0:pk + 1], np.inf)))
        reason = None
        if pk - top < int(p.min_phase_s * fs):
            reason = "no_backswing_before_peak"
        elif not np.isfinite(sy[top]) or hy[top] > sy[top] - p.top_above_shoulder * torso_len:
            reason = "hands_not_above_shoulder_at_top (partial swing / chip / waggle)"
        if reason:
            rejected.append({"t": float(tg[pk]), "reason": reason})
            continue
        take = quiet_run_before(top, max(0, top - int(p.max_backswing_s * fs)))
        fin = quiet_run_after(pk, min(n - 1, pk + int(p.max_follow_s * fs)))
        taken.append((take, fin))
        back, down = (top - take) / fs, (pk - top) / fs
        flags: List[str] = []
        tempo = float("nan")
        if back >= p.min_phase_s and down >= p.min_phase_s:
            tempo = back / down
            if not (p.tempo_range[0] <= tempo <= p.tempo_range[1]):
                flags.append(f"tempo_out_of_range({tempo:.2f})")
                tempo = float("nan")
        else:
            flags.append("phase_too_short_for_tempo")
        if take < int(0.2 * fs):
            flags.append("little_address_before_takeaway")
        if n - 1 - fin < int(0.1 * fs) or fin - pk < int(0.1 * fs):
            flags.append("clipped_follow_through")
        swings.append(Swing(float(tg[take]), float(tg[fin]), float(tg[take]), float(tg[top]),
                            float(tg[pk]), float(sp[pk]), back, down, tempo, flags))
    # chronological order, add address/finish padding, never overlap a neighbour
    swings.sort(key=lambda s: s.impact_t)
    for i, s in enumerate(swings):
        lo = tg[0] if i == 0 else 0.5 * (swings[i - 1].end_t + s.start_t)
        hi = tg[-1] if i == len(swings) - 1 else 0.5 * (s.end_t + swings[i + 1].start_t)
        s.start_t = max(lo, s.takeaway_t - p.pad_before_s)
        s.end_t = min(hi, s.end_t + p.pad_after_s)
        sl = (tg >= s.start_t) & (tg <= s.end_t)
        if valid[sl].mean() < 0.8:
            s.flags.append("tracking_gaps_in_window")
    return swings, rejected


# ------------------------------------------------------------------------------ dedup
def trajectory_signature(hands_xy: np.ndarray, centre_xy: np.ndarray, torso_len: float,
                         n: int = 40) -> np.ndarray:
    """Hand path relative to the hip centre, in torso lengths, resampled to n points."""
    rel = (np.asarray(hands_xy, float) - np.asarray(centre_xy, float)) / max(torso_len, 1e-6)
    ok = np.isfinite(rel).all(axis=1)
    if ok.sum() < 3:
        return np.full((n, 2), np.nan)
    src = np.linspace(0, 1, len(rel))
    u = np.linspace(0, 1, n)
    return np.column_stack([np.interp(u, src[ok], rel[ok, c]) for c in range(2)])


def is_duplicate(sig_a: np.ndarray, sig_b: np.ndarray, tol: float = 0.08) -> bool:
    """True when two signatures are within `tol` torso-lengths RMS (autoplay-loop repeat).
    Threshold is a heuristic (not calibrated on labelled loops)."""
    if np.isnan(sig_a).any() or np.isnan(sig_b).any():
        return False
    return float(np.sqrt(np.mean((sig_a - sig_b) ** 2))) < tol

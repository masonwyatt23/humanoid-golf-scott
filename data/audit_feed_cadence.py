"""Cadence audit: true unique-frame rate and downswing frame counts for every mason_v2 swing window.

Decodes the three recordings (media band y 9-86 %, 236x394 gray), flags a frame as unique when its mean abs
difference to the previous frame is >= 0.1 (grey levels; duplicates measure ~0.00-0.05, real frames >= 0.5),
then for each swing window in data/references/mason_v2_*.npz reports unique fps, median/p90 unique-frame
interval, and the number of UNIQUE frames in backswing and downswing.  Writes
data/references/mason_cadence_audit.json (deterministic; videos themselves are not stored).

    python -m data.audit_feed_cadence
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
DUP_THR = 0.1


def frame_diffs(video: Path):
    import cv2
    cap = cv2.VideoCapture(str(video))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    y0, y1 = int(0.09 * H), int(0.86 * H)
    ts, prev, d = [], None, []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        ts.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        g = cv2.cvtColor(cv2.resize(f[y0:y1], (236, 394), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.int16)
        d.append(0.0 if prev is None else float(np.abs(g - prev).mean()))
        prev = g
    cap.release()
    return np.array(ts), np.array(d)


def main(video_dir=ROOT / "mason_swings", refs=ROOT / "references"):
    out = {"dup_threshold_gray_levels": DUP_THR, "videos": {}, "swings": []}
    cad = {}
    for p in (1, 2, 3):
        t, d = frame_diffs(Path(video_dir) / f"mason_swing_part{p}.mov")
        cad[p] = (t, d)
        u = d >= DUP_THR
        u[0] = True
        iv = np.diff(t[u])
        iv = iv[iv < 0.2]
        out["videos"][f"part{p}"] = dict(
            n_frames=int(len(t)), duration_s=round(float(t[-1]), 2), unique_frame_fraction=round(float(u.mean()), 3),
            interval_hist_17_33_50_67_83plus=[int(((iv > a) & (iv <= b)).sum()) for a, b in
                                              ((0.01, .025), (.025, .042), (.042, .058), (.058, .075), (.075, .2))])
    for f in sorted(Path(refs).glob("mason_v[23]_p*_s*.npz")):
        if "unmirrored" in f.name or "mirrored" in f.name:
            continue
        p = int(f.name.split("_p")[1][0])
        t, d = cad[p]
        with np.load(f, allow_pickle=True) as z:
            t0, t1 = float(z["t_start_in_video"]), float(z["t_end_in_video"])
            ta, tt, ti = float(z["t_takeaway"]), float(z["t_top"]), float(z["t_impact"])
            partial = bool(z["partial"])
        u = (t >= t0) & (t <= t1) & (d >= DUP_THR)
        ut = t[u]
        iv = np.diff(ut)
        n = lambda a, b: int(((ut >= a) & (ut <= b)).sum())
        out["swings"].append(dict(
            file=f.name, partial=partial, unique_fps=round(len(ut) / (t1 - t0), 1),
            median_interval_ms=round(float(np.median(iv)) * 1000) if len(iv) else None,
            backswing_s=round(tt - ta, 3), downswing_s=round(ti - tt, 3),
            backswing_unique_frames=n(ta, tt), downswing_unique_frames=n(tt, ti)))
    (Path(refs) / "mason_cadence_audit.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("wrote", Path(refs) / "mason_cadence_audit.json", len(out["swings"]), "swings")


if __name__ == "__main__":
    main()

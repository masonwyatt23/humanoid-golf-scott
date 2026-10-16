"""Second-pass, higher-quality pose for the best swings found by ingest_feed_recordings.

    python -m data.refine_swings --report <report.json> --video data/mason_swings/<file>.mov \
        --model <pose_landmarker_heavy.task> --out data/references --top 5 [--debug-dir DIR]

Per swing (window from the report):
  1. re-decode the full-resolution frames of that window (HEVC via OpenCV/ffmpeg);
  2. tight person crop (union of confident landmarks over the window, +25% pad);
  3. per frame run the PoseLandmarker on THREE views of the frame - tight crop at native
     resolution, tight crop upscaled to ~960 px tall (cubic), and the whole tile - and keep
     the candidate with the best mean key-landmark visibility whose torso length is
     consistent with the window median (rejects hallucinated skeletons);
  4. outlier rejection: a landmark further than 0.4 torso-lengths (image) from its rolling
     7-frame median is dropped (NaN) and re-interpolated;
  5. cut the window at any pose-jump (loop restart / edit) so one file = one continuous swing;
  6. process_landmarks (gap-fill, Savitzky-Golay smoothing, resample to dt=0.01) -> joints.
Output  data/references/<stem>_sNN_refined.npz  (source=mason_self_filmed, is_synthetic=False,
refined=True) + a quality score in [0,1].  Same caveats as the feed ingest: single-view,
screen-recorded, 2D-proxy joint angles, no club, not physically consistent with MuJoCo.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
try:
    from data import provenance as _prov
except ImportError:  # run as a script
    import provenance as _prov

try:
    from data import ingest_feed_recordings as fr
    from data import process_video as pv
    from data import swing_segmentation as ss
except Exception:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from data import ingest_feed_recordings as fr
    from data import process_video as pv
    from data import swing_segmentation as ss

KEY = fr.KEY


def quality_score(meta: Dict) -> float:
    """0..1 heuristic used to rank swings: visibility, upper-body tracking, leg tracking,
    a golf-plausible tempo (2-4.5:1), subject size, and no warning flags.  Not a ground-truth accuracy."""
    s = 0.35 * float(meta.get("mean_visibility", 0)) + 0.25 * float(meta.get("process_valid_frac", 0)) \
        + 0.15 * float(meta.get("leg_valid_frame_ratio", 0)) \
        + 0.15 * (1.0 if meta.get("tempo_ratio") is not None and 2.0 <= meta["tempo_ratio"] <= 4.5 else 0.0) \
        + 0.10 * min(1.0, float(meta.get("torso_frac_of_tile_h", 0)) / 0.2)
    s -= 0.05 * len([f for f in meta.get("flags", []) if "clipped" not in f])
    return float(np.clip(s, 0, 1))


def reject_outliers(img: np.ndarray, world: np.ndarray, torso: float, win: int = 7,
                    thr_torso: float = 0.4) -> Tuple[np.ndarray, np.ndarray, float]:
    """NaN landmarks that jump away from their rolling median. Returns (img, world, frac_dropped)."""
    img, world = img.copy(), world.copy()
    n = len(img)
    bad = np.zeros((n, 33), bool)
    h = win // 2
    for i in range(n):
        lo, hi = max(0, i - h), min(n, i + h + 1)
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                med = np.nanmedian(img[lo:hi, :, :2], axis=0)
        dev = np.linalg.norm(img[i, :, :2] - med, axis=1) / max(torso, 1e-6)
        bad[i] = np.nan_to_num(dev, nan=0.0) > thr_torso
    seen = np.isfinite(img[:, :, 0])
    img[bad] = np.nan
    world[bad] = np.nan
    return img, world, float(bad.sum() / max(seen.sum(), 1))


def refine_window(frames: List[np.ndarray], lander, bbox, tile_wh) -> Dict:
    import cv2
    H, W = tile_wh[1], tile_wh[0]
    x0, y0, x1, y1 = bbox
    n = len(frames)
    img = np.full((n, 33, 4), np.nan)
    wld = np.full((n, 33, 4), np.nan)
    used = np.zeros(n, int)       # 0 none, 1 native crop, 2 upscaled crop, 3 tile
    scale = max(1.0, 960.0 / max(y1 - y0, 1))
    for i, f in enumerate(frames):
        cands = []
        crop = f[y0:y1, x0:x1]
        for code, im, ox, oy, sx, sy in (
                (1, crop, x0, y0, 1.0, 1.0),
                (2, cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC), x0, y0, scale, scale),
                (3, f, 0, 0, 1.0, 1.0)):
            r = lander(im)
            if r is None:
                continue
            a, w = r
            ih, iw = im.shape[:2]
            px = np.column_stack([a[:, 0] * iw / sx + ox, a[:, 1] * ih / sy + oy, a[:, 2], a[:, 3]])
            cands.append((code, px, w, float(np.mean(a[KEY, 3]))))
        if not cands:
            continue
        tl = [np.linalg.norm(c[1][[11, 12], :2].mean(0) - c[1][[23, 24], :2].mean(0)) for c in cands]
        med = np.median(tl)
        ok = [c for c, t_ in zip(cands, tl) if 0.6 * med <= t_ <= 1.6 * med] or cands
        code, px, w, _ = max(ok, key=lambda c: c[3])
        img[i], wld[i], used[i] = px, w, code
    return {"img": img, "world": wld, "used": used}


def refine_swing(video: Path, sw: Dict, span: Dict, lander, args, debug_dir: Optional[Path]) -> Optional[Dict]:
    import cv2
    cache = np.load(Path(args.cache_dir) / f"{video.stem}_span{span['span']:02d}.npz")
    tc, imc = cache["t"], cache["img"].astype(float)
    t0, t1 = max(sw["t_start"] - 0.2, span["t0"]), min(sw["t_end"] + 0.2, span["t1"])
    sel = (tc >= t0) & (tc <= t1)
    pts = [imc[sel][:, :, :]]
    bbox = fr.person_bbox([a for a in imc[sel]], pad=0.25, tile_wh=tuple(int(v) for v in cache["tile_wh"]),
                          min_side=320)
    if bbox is None:
        return None
    tile_wh = tuple(int(v) for v in cache["tile_wh"])
    # decode window frames (every frame, then drop exact duplicates)
    cap = cv2.VideoCapture(str(video))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    y0 = int(round(span["tile_rows_thumb"][0] * H / fr.THUMB_H))
    y1 = int(round((span["tile_rows_thumb"][1] + 1) * H / fr.THUMB_H))
    frames, ts = [], []
    prev = None
    while True:
        ok, f = cap.read()
        if not ok:
            break
        tm = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if tm > t1:
            break
        if tm < t0:
            continue
        tile = f[y0:y1]
        g = cv2.cvtColor(cv2.resize(tile, (118, 118), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.int16)
        if prev is not None and np.abs(g - prev).mean() < 0.1:
            continue
        prev = g
        frames.append(tile)
        ts.append(tm)
    cap.release()
    if len(frames) < 12:
        return None
    t = np.array(ts)
    tr = refine_window(frames, lander, bbox, tile_wh)
    img0, wld0, used = tr["img"], tr["world"], tr["used"]
    _, _, hip, tl = fr.hand_track(img0)
    img, wld, drop = reject_outliers(img0, wld0, tl)
    # cut at pose jumps; keep the piece holding the impact
    cuts = ss.pose_jump_cuts(img[:, KEY, :2], tl)
    edges = [0, *[int(c) for c in cuts], len(t)]
    piece = next(((a, b) for a, b in zip(edges[:-1], edges[1:]) if t[a] <= sw["t_impact"] <= t[b - 1]), (0, len(t)))
    a, b = piece
    flags = list(sw.get("flags", []))
    if (a, b) != (0, len(t)):
        flags.append(f"trimmed_at_pose_jump({t[a]:.2f}-{t[b-1]:.2f}s)")
    t, img, wld = t[a:b], img[a:b], wld[a:b]
    if len(t) < 12:
        return None
    lm = fr.resample_world(t, wld, 60.0, t[0], t[-1])
    ns = argparse.Namespace(**vars(args))
    try:
        data = pv.process_landmarks(lm, 60.0, min_visibility=args.min_visibility, max_gap=8,
                                    min_valid_frac=args.min_valid_frac, out_dt=args.out_dt, key=fr.UPPER)
    except ValueError as e:
        return {"error": str(e)}
    hands, sh_y, hipc, tl2 = fr.hand_track(img)
    swings, _ = ss.detect_swings(t, hands, sh_y, tl2)
    best = min(swings, key=lambda s: abs(s.impact_t - sw["t_impact"])) if swings else None
    legs = img[:, [pv.L_KNEE, pv.R_KNEE, pv.L_ANK, pv.R_ANK], 3]
    leg_ratio = float((np.nan_to_num(legs, nan=0) >= args.min_visibility).all(1).mean())
    meta = {"mean_visibility": float(np.nanmean(img[:, KEY, 3])), "process_valid_frac": float(data["valid_frac"]),
            "leg_valid_frame_ratio": leg_ratio, "tempo_ratio": None if best is None or not np.isfinite(best.tempo) else float(best.tempo),
            "torso_frac_of_tile_h": float(tl2 / tile_wh[1]), "flags": flags}
    q = quality_score(meta)
    name = Path(sw["file"]).stem + "_refined"
    data.update(source=np.array(fr.SOURCE_LABEL), style=np.array("mason"), is_synthetic=np.array(False),
                capture=np.array(fr.CAPTURE_LABEL), refined=np.array(True), source_file=np.array(video.name),
                view=np.array("unknown"), handedness=np.array(args.handedness), club=np.array("unknown"),
                capture_fps=np.array(0.0), t_start_in_video=np.array(float(t[0])), t_end_in_video=np.array(float(t[-1])),
                tempo_ratio=np.array(np.nan if meta["tempo_ratio"] is None else meta["tempo_ratio"]),
                backswing_s=np.array(best.backswing_s if best else np.nan), downswing_s=np.array(best.downswing_s if best else np.nan),
                t_top=np.array(best.top_t if best else np.nan), t_impact=np.array(best.impact_t if best else np.nan),
                mean_visibility=np.array(meta["mean_visibility"]), leg_valid_frame_ratio=np.array(leg_ratio),
                outlier_landmark_frac=np.array(drop), quality_score=np.array(q), quality_flags=np.array(flags, dtype=str),
                refine_method=np.array("tight-crop native/upscaled/tile best-of-3 + rolling-median outlier rejection + SG smoothing"),
                limits=np.array("single-view monocular, screen-recorded & re-encoded (~30 fps source); joints are 2D-proxy angles "
                                "(not retargeted/IK-solved); no club; leg joints unreliable if leg_valid_frame_ratio<0.6"))
    out = Path(args.out) / f"{name}.npz"
    if not args.dry_run:
        _prov.tag(data, "mason_self_filmed")
        tmp = out.with_name(out.stem + ".tmp.npz")
        np.savez(tmp, **data)
        tmp.replace(out)
    if debug_dir:
        debug_dir.mkdir(parents=True, exist_ok=True)
        picks = np.linspace(0, len(t) - 1, 6).astype(int)
        sheet = []
        for i in picks:
            f = frames[a + i].copy()
            for p, q_ in fr.SKELETON:
                lm_ = img[i]
                if lm_[p, 3] > 0.3 and lm_[q_, 3] > 0.3 and np.isfinite(lm_[[p, q_], :2]).all():
                    cv2.line(f, tuple(int(v) for v in lm_[p, :2]), tuple(int(v) for v in lm_[q_, :2]), (0, 255, 0), 3)
            f = cv2.resize(f, (300, int(300 * f.shape[0] / f.shape[1])))
            cv2.putText(f, f"{t[i]:.2f}", (4, 20), 0, 0.6, (0, 255, 255), 2)
            sheet.append(f)
        h = min(s.shape[0] for s in sheet)
        cv2.imwrite(str(debug_dir / f"{name}.jpg"), np.hstack([s[:h] for s in sheet]))
    return {"file": out.name, "quality_score": round(q, 3), "frames_out": int(len(data["time"])),
            "mean_visibility": round(meta["mean_visibility"], 3), "upper_valid_frac": round(meta["process_valid_frac"], 3),
            "leg_valid_frame_ratio": round(leg_ratio, 3), "tempo_ratio": meta["tempo_ratio"],
            "outlier_landmark_frac": round(drop, 3), "frames_native_crop/upscaled/tile": [int((used == k).sum()) for k in (1, 2, 3)],
            "window_s": [round(float(t[0]), 2), round(float(t[-1]), 2)], "flags": flags}


def rejoint(path: Path, min_visibility: float = 0.3, min_valid_frac: float = 0.6) -> Dict:
    """Recompute joints of an existing refined/feed .npz from its stored 60 Hz world landmarks
    (used after a process_landmarks fix, so no video / pose re-run is needed)."""
    d = dict(np.load(path, allow_pickle=True))
    out = pv.process_landmarks(d["landmarks"].astype(float), 60.0, min_visibility=min_visibility,
                               max_gap=8, min_valid_frac=min_valid_frac, out_dt=float(d["dt"]), key=fr.UPPER)
    d.update({k: out[k] for k in ("time", "joints", "dt", "valid_mask", "valid_frac", "landmarks")})
    np.savez(path, **d)
    return {"file": path.name, "joint_min": np.round(out["joints"].min(0)).tolist(),
            "joint_max": np.round(out["joints"].max(0)).tolist()}


def main(argv=None) -> int:
    if argv is None and len(sys.argv) > 1 and sys.argv[1] == "--rejoint":
        for p in sys.argv[2:]:
            print(rejoint(Path(p)))
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--cache-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "references")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--only", help="comma list of swing files, e.g. mason_swing_part2_s02.npz")
    ap.add_argument("--debug-dir", type=Path)
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--handedness", default="right")
    ap.add_argument("--min-visibility", type=float, default=0.3)
    ap.add_argument("--min-valid-frac", type=float, default=0.6)
    ap.add_argument("--out-dt", type=float, default=0.01)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    rep = next(v for v in json.loads(args.report.read_text())["videos"] if v["video"] == args.video.name)
    spans = {s["span"]: s for s in rep["spans"]}
    sws = sorted(rep["swings"], key=lambda s: -quality_score({**s, "process_valid_frac": s["process_valid_frac"]}))
    if args.only:
        want = set(args.only.split(","))
        sws = [s for s in sws if s["file"] in want]
    else:
        sws = sws[:args.top]
    args.out.mkdir(parents=True, exist_ok=True)
    lander = fr.Landmarker(args.model)
    results = []
    try:
        for sw in sws:
            r = refine_swing(args.video, sw, spans[sw["span"]], lander, args, args.debug_dir)
            print(sw["file"], r, flush=True)
            results.append({"source_swing": sw["file"], "result": r})
    finally:
        lander.close()
    if args.summary:
        args.summary.write_text(json.dumps(results, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

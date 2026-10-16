"""Ingest Mason's own filmed swings -> real (non-synthetic) reference .npz files.

    python -m data.ingest_mason_swings                  # scan data/mason_swings/
    python -m data.ingest_mason_swings --capture-fps 240 --dry-run
    python -m data.ingest_mason_swings --force          # ignore resume index

Per video: validate (extension, readable, resolution, fps, duration) -> pose (MediaPipe via
data.process_video) -> person-detected / enough-valid-frames checks -> joints -> save
data/references/mason_<stem>.npz with source="mason_self_filmed", is_synthetic=False.

Optional sidecar (club, view, handedness, capture_fps) in the video folder:
  metadata.json  {"swing_001.mp4": {"club": "driver", "view": "dtl", ...}, ...}
  metadata.csv   header: filename,club,view,handedness,capture_fps
  <stem>.json    per-video file with the same keys
Precedence: CLI --capture-fps > per-video .json > metadata.csv/json > filename tokens > default.

Exit codes: 0 all ok (or nothing to do), 1 backend failure, 2 bad arguments, 3 some videos failed.
Raw videos are git-ignored; never commit them. Nothing here touches the network.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
try:
    from data import provenance as _prov
except ImportError:  # run as a script
    import provenance as _prov

try:  # works as `python -m data.ingest_mason_swings` and `python data/ingest_mason_swings.py`
    from data import process_video as pv
except Exception:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from data import process_video as pv

ROOT = Path(__file__).parent
SOURCE_LABEL = "mason_self_filmed"
EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi"}
VIEWS = {"dtl", "fo", "faceon", "face-on", "side", "unknown"}
CLUBS = {"driver", "wood", "hybrid", "iron", "wedge", "putter", "unknown"}
HANDS = {"right", "left"}
VIEW_ALIASES = {"faceon": "fo", "face-on": "fo", "down-the-line": "dtl"}


class IngestError(Exception):
    """A per-file problem with a human-readable message and a short machine code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


# ------------------------------------------------------------------ metadata sidecars
def _clean_meta(raw: Dict) -> Dict:
    out: Dict = {}
    for k, v in (raw or {}).items():
        k = str(k).strip().lower()
        if v is None or str(v).strip() == "":
            continue
        if k in ("club", "view", "handedness"):
            v = str(v).strip().lower()
            if k == "view":
                v = VIEW_ALIASES.get(v, v)
        elif k == "capture_fps":
            try:
                v = float(v)
            except (TypeError, ValueError):
                raise IngestError("bad_metadata", f"capture_fps '{v}' in sidecar is not a number")
        elif k in ("filename", "file"):
            continue
        out[k] = v
    return out


def load_sidecars(folder: Path) -> Dict[str, Dict]:
    """Return {filename: meta}. Malformed sidecars raise IngestError carrying the filename."""
    table: Dict[str, Dict] = {}
    j = folder / "metadata.json"
    if j.exists():
        try:
            data = json.loads(j.read_text())
        except Exception as e:
            raise IngestError("bad_metadata", f"{j.name} is not valid JSON ({e})")
        if not isinstance(data, dict):
            raise IngestError("bad_metadata", f"{j.name} must be an object keyed by filename")
        for name, m in data.items():
            table[name] = {**table.get(name, {}), **_clean_meta(m)}
    c = folder / "metadata.csv"
    if c.exists():
        with c.open(newline="") as f:
            for row in csv.DictReader(f):
                name = (row.get("filename") or row.get("file") or "").strip()
                if name:
                    table[name] = {**table.get(name, {}), **_clean_meta(row)}
    return table


def filename_tokens(stem: str) -> Dict:
    """Pick club/view out of names like mason_20261016_driver_dtl_001."""
    toks = set(re.split(r"[^a-z0-9-]+", stem.lower()))
    meta: Dict = {}
    for t in toks:
        t2 = VIEW_ALIASES.get(t, t)
        if t2 in VIEWS and t2 != "unknown":
            meta["view"] = t2
        if t in CLUBS and t != "unknown":
            meta["club"] = t
    return meta


def resolve_meta(video: Path, table: Dict[str, Dict], cli_fps: Optional[float],
                 default_hand: str) -> Dict:
    meta = {"club": "unknown", "view": "unknown", "handedness": default_hand}
    meta.update(filename_tokens(video.stem))
    meta.update(table.get(video.name, {}))
    per = video.with_suffix(".json")
    if per.exists():
        try:
            meta.update(_clean_meta(json.loads(per.read_text())))
        except IngestError:
            raise
        except Exception as e:
            raise IngestError("bad_metadata", f"{per.name} is not valid JSON ({e})")
    if cli_fps:
        meta["capture_fps"] = cli_fps
    if meta["handedness"] not in HANDS:
        raise IngestError("bad_metadata", f"handedness '{meta['handedness']}' must be right or left")
    if meta["view"] not in VIEWS:
        raise IngestError("bad_metadata", f"view '{meta['view']}' must be one of dtl, fo, side")
    return meta


# ------------------------------------------------------------------ validation
def probe_video(path: Path) -> Dict:
    """Open with OpenCV and return header facts, or raise IngestError."""
    if path.suffix.lower() not in EXTS:
        raise IngestError("bad_extension", f"unsupported file type '{path.suffix}' "
                          f"(use {', '.join(sorted(EXTS))})")
    if path.stat().st_size == 0:
        raise IngestError("empty_file", "file is empty (0 bytes) - the copy/export probably failed")
    import cv2
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise IngestError("unreadable", "cannot open as a video (corrupt, partial download, or "
                              "unsupported codec). Re-export it, or convert with: "
                              "ffmpeg -i in.mov -c:v libx264 out.mp4")
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        ok, _ = cap.read()
        if not ok:
            raise IngestError("unreadable", "opened but the first frame cannot be decoded")
    finally:
        cap.release()
    return {"header_fps": fps, "frames": n, "width": w, "height": h}


def validate_probe(info: Dict, meta: Dict, *, min_short_side: int, min_duration: float,
                   max_duration: float, min_fps: float) -> List[str]:
    """Raise IngestError for fatal problems; return list of warnings."""
    warns: List[str] = []
    short = min(info["width"], info["height"])
    if short < min_short_side:
        raise IngestError("low_resolution", f"resolution {info['width']}x{info['height']} too small "
                          f"(short side must be >= {min_short_side}px); film at 1080p")
    fps = info["header_fps"]
    cap = meta.get("capture_fps")
    if not (np.isfinite(fps) and fps > 0):
        if not cap:
            raise IngestError("bad_fps", "video header has no fps; pass --capture-fps or add "
                              "capture_fps to the sidecar")
        warns.append("header fps missing; using capture_fps")
        fps = cap
    if cap:
        if cap < 15 or cap > 2000:
            raise IngestError("bad_fps", f"capture_fps {cap} is implausible (expected 15-2000)")
        if cap < fps - 0.5:
            raise IngestError("bad_fps", f"capture_fps {cap:g} is lower than the file's playback fps "
                              f"{fps:g}; capture fps must be the real camera rate (e.g. 240)")
        eff = cap
    else:
        eff = fps
        if fps >= 100:
            warns.append("fps >= 100 with no capture_fps: assuming file timing is real time")
        elif fps <= 31:
            warns.append("30 fps clip: the swing downswing is only ~8 frames; tempo will be coarse. "
                         "If this is slow-mo exported at 30 fps, pass --capture-fps 240")
    if eff < min_fps:
        raise IngestError("low_fps", f"effective fps {eff:g} < {min_fps:g}")
    nframes = info["frames"]
    if nframes <= 0:
        raise IngestError("unreadable", "frame count unavailable/zero")
    # real seconds = frames / true capture rate (capture_fps if given, else header fps)
    info["real_duration_s"] = round(nframes / eff, 3)
    info["effective_fps"] = eff
    d = info["real_duration_s"]
    if d < min_duration:
        raise IngestError("too_short", f"only {d:.2f}s of real time (< {min_duration}s); "
                          "a full swing needs the setup through the finish")
    if d > max_duration:
        raise IngestError("too_long", f"{d:.1f}s of real time (> {max_duration}s); trim to a single "
                          "swing (one swing per file)")
    return warns


# ------------------------------------------------------------------ per-video work
def ingest_one(video: Path, out_dir: Path, backend, meta: Dict, args) -> Dict:
    info = probe_video(video)
    warns = validate_probe(info, meta, min_short_side=args.min_short_side,
                           min_duration=args.min_duration, max_duration=args.max_duration,
                           min_fps=args.min_fps)
    lm, hdr_fps = pv.read_landmarks(video, backend)
    n = lm.shape[0]
    detected = np.isfinite(lm[:, pv.R_SH, 0])
    det_frac = float(detected.mean())
    if detected.sum() == 0:
        raise IngestError("no_person", "no person detected in any frame. Make sure the whole body "
                          "is in frame, well lit, and not cropped (try the DTL/face-on full-body view)")
    if det_frac < args.min_detect_frac:
        raise IngestError("person_intermittent", f"person detected in only {det_frac:.0%} of frames "
                          f"(need {args.min_detect_frac:.0%}); check framing, lighting, other people")
    if meta["handedness"] == "left":  # mirror so a lefty maps onto the right-handed joint model
        lm = lm.copy()
        lm[..., 0] = -lm[..., 0]
    eff = info["effective_fps"]
    try:
        data = pv.process_landmarks(lm, eff, min_visibility=args.min_visibility,
                                    max_gap=args.max_gap, min_valid_frac=args.min_valid_frac,
                                    out_dt=args.out_dt)
    except ValueError as e:
        raise IngestError("insufficient_valid_frames", str(e))
    if len(data["time"]) < args.min_out_frames:
        raise IngestError("insufficient_valid_frames",
                          f"only {len(data['time'])} output frames after trimming "
                          f"(need {args.min_out_frames})")
    if data["valid_mask"].mean() < 0.5:
        warns.append("less than half of output frames are fully tracked; review this clip")
    out = out_dir / f"mason_{video.stem}.npz"
    data.update(source=np.array(SOURCE_LABEL), style=np.array("mason"),
                is_synthetic=np.array(False), source_file=np.array(video.name),
                club=np.array(meta["club"]), view=np.array(meta["view"]),
                handedness=np.array(meta["handedness"]),
                capture_fps=np.array(float(meta.get("capture_fps") or 0.0)),
                effective_fps=np.array(float(eff)), detect_frac=np.array(det_frac))
    _prov.tag(data, "mason_self_filmed")
    tmp = out.with_name(out.stem + ".tmp.npz")
    np.savez(tmp, **data)
    tmp.replace(out)
    return {"output": out.name, "frames_in": int(n), "frames_out": int(len(data["time"])),
            "detect_frac": round(det_frac, 3), "valid_frac": round(float(data["valid_frac"]), 3),
            "warnings": warns, **{k: info[k] for k in ("width", "height", "header_fps",
                                                         "real_duration_s", "effective_fps")}}


def scan(folder: Path) -> List[Path]:
    skip = {"readme.md", "metadata.json", "metadata.csv", "metadata.example.csv", ".gitkeep"}
    files = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name.lower() in skip or p.name.startswith("."):
            continue
        if p.suffix.lower() == ".json":  # per-video sidecar
            continue
        files.append(p)
    return files


def run(args, backend_factory=None) -> int:
    folder, out_dir = args.videos, args.out
    if not folder.exists():
        print(f"ERROR: folder {folder} does not exist. Create it and drop your own videos there.")
        return 2
    files = scan(folder)
    if not files:
        print(f"No videos found in {folder}. Drop your own swing videos there "
              f"(see docs/MASON_SWINGS.md).")
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        table = load_sidecars(folder)
    except IngestError as e:
        print(f"ERROR: {e.message}")
        return 2
    idx_path = out_dir / "mason_index.json"
    idx = {}
    if idx_path.exists() and not args.force:
        try:
            idx = json.loads(idx_path.read_text())
        except Exception:
            print("WARN: corrupt mason_index.json; starting fresh")
    backend = close = None
    results: List[Dict] = []
    seen_stems: Dict[str, str] = {}
    try:
        for v in files:
            rec = {"file": v.name, "status": "failed"}
            results.append(rec)
            try:
                if v.stem in seen_stems:
                    raise IngestError("duplicate_name", f"same base name as {seen_stems[v.stem]}; "
                                      "rename one (outputs are keyed by base name)")
                seen_stems[v.stem] = v.name
                if v.suffix.lower() not in EXTS:
                    raise IngestError("bad_extension", f"unsupported file type '{v.suffix}' "
                                      f"(use {', '.join(sorted(EXTS))})")
                meta = resolve_meta(v, table, args.capture_fps, args.handedness)
                rec["meta"] = {k: meta[k] for k in meta}
                settings = dict(meta=meta, min_visibility=args.min_visibility, max_gap=args.max_gap,
                                min_valid_frac=args.min_valid_frac, out_dt=args.out_dt,
                                min_detect_frac=args.min_detect_frac)
                key = pv._settings_key(v, settings)
                prev = idx.get(v.name)
                if prev and prev.get("key") == key and (out_dir / prev["output"]).exists():
                    rec.update(status="skipped", output=prev["output"], note="already processed (resume)")
                    continue
                if args.dry_run:
                    info = probe_video(v)
                    rec["warnings"] = validate_probe(info, meta, min_short_side=args.min_short_side,
                                                     min_duration=args.min_duration,
                                                     max_duration=args.max_duration,
                                                     min_fps=args.min_fps)
                    rec.update(status="valid", **info)
                    continue
                if backend is None:
                    try:
                        backend, close = (backend_factory or pv.make_backend)(args.model)
                    except Exception as e:
                        print(f"ERROR: cannot start the MediaPipe backend: {e}")
                        return 1
                t0 = time.time()
                rec.update(ingest_one(v, out_dir, backend, meta, args))
                rec.update(status="ok", seconds=round(time.time() - t0, 1))
                idx[v.name] = {"key": key, "output": rec["output"]}
                idx_path.write_text(json.dumps(idx, indent=2))
            except IngestError as e:
                rec.update(error_code=e.code, error=e.message)
            except Exception as e:  # unexpected: still isolate per file
                rec.update(error_code="unexpected", error=f"{type(e).__name__}: {e}")
    finally:
        if close:
            close()
    return _report(results, args)


def _report(results: List[Dict], args) -> int:
    counts = {s: sum(r["status"] == s for r in results) for s in ("ok", "skipped", "valid", "failed")}
    print("\n=== Mason swing ingest ===")
    for r in results:
        if r["status"] == "failed":
            print(f"  FAIL  {r['file']}: [{r['error_code']}] {r['error']}")
        elif r["status"] == "skipped":
            print(f"  skip  {r['file']}: {r['note']}")
        else:
            w = f" (warn: {'; '.join(r['warnings'])})" if r.get("warnings") else ""
            print(f"  {r['status']:5} {r['file']}" + (f" -> {r['output']}, {r['frames_out']} frames" if r["status"] == "ok" else "") + w)
    print(f"total={len(results)} ok={counts['ok']} skipped={counts['skipped']} "
          f"valid(dry-run)={counts['valid']} failed={counts['failed']}")
    report = {"source": SOURCE_LABEL, "is_synthetic": False,
              "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "counts": counts, "files": results}
    if not args.dry_run:
        p = args.out / "mason_ingest_report.json"
        p.write_text(json.dumps(report, indent=2, default=str))
        print(f"report: {p}")
    return 3 if counts["failed"] else 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Mason's own swing videos -> real reference .npz")
    ap.add_argument("--videos", type=Path, default=ROOT / "mason_swings")
    ap.add_argument("--out", type=Path, default=ROOT / "references")
    ap.add_argument("--model", help="pose_landmarker .task file (tasks API only)")
    ap.add_argument("--capture-fps", type=float, help="true camera fps (e.g. 240) for slow-mo files")
    ap.add_argument("--handedness", choices=sorted(HANDS), default="right")
    ap.add_argument("--min-short-side", type=int, default=360)
    ap.add_argument("--min-fps", type=float, default=24.0)
    ap.add_argument("--min-duration", type=float, default=0.8, help="real seconds")
    ap.add_argument("--max-duration", type=float, default=20.0, help="real seconds")
    ap.add_argument("--min-detect-frac", type=float, default=0.7)
    ap.add_argument("--min-out-frames", type=int, default=50)
    ap.add_argument("--min-visibility", type=float, default=0.5)
    ap.add_argument("--max-gap", type=int, default=5)
    ap.add_argument("--min-valid-frac", type=float, default=0.6)
    ap.add_argument("--out-dt", type=float, default=0.01)
    ap.add_argument("--force", action="store_true", help="ignore the resume index")
    ap.add_argument("--dry-run", action="store_true", help="validate only; no pose, no output")
    return ap


def main(argv=None, backend_factory=None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as e:
        return int(e.code or 0) if e.code in (0, None) else 2
    return run(args, backend_factory)


if __name__ == "__main__":
    sys.exit(main())

"""
Video -> reference-motion `.npz` using MediaPipe Pose (a *proxy* pipeline).

Robustness features
-------------------
* Per-video error handling: unreadable/corrupt files are logged and skipped, one bad
  video never stops the batch. Per-frame backend exceptions count as "missing".
* Visibility threshold: landmarks with visibility < `--min-visibility` are NaN'd.
* Missing landmark handling: short gaps (<= `--max-gap` frames) are linearly
  interpolated; longer gaps are left NaN and the clip is rejected if the fraction of
  valid frames is below `--min-valid-frac`.
* Smoothing: Savitzky-Golay filter over the (gap-filled) angle time series, with
  window adapted to the effective fps (never longer than the clip).
* FPS handling: real fps read from the container (fallback `--fps-fallback` when the
  header reports 0/NaN). Slow-motion footage should be declared via `--capture-fps`
  (the true camera fps, e.g. 250) so output `dt` is in *real-time* seconds; otherwise
  tempo/velocities are wrong by the slow-mo factor. Output is resampled to `--out-dt`
  (default 0.01 s) so it matches the synthetic references.
* Resume: finished videos are recorded in `<out>/processed_index.json` (keyed by file
  name + size + mtime + settings). Re-running skips them; `--force` redoes everything.
* Dependencies (cv2, mediapipe) are imported lazily so the numeric core can be
  tested without them. Supports both the legacy `mp.solutions.pose` API and the newer
  `mediapipe.tasks` PoseLandmarker (needs `--model pose_landmarker_*.task`).

Output (`data/references/<video>_processed.npz`) matches `ReferenceDataset`:
  joints (n,11) degrees, dt, time, valid_mask, source, plus `landmarks` (n,33,4).
`club_head` is NOT produced (MediaPipe has no club). The env only needs it if rewards
use it; add a club tracker or derive from hands later.

CAUTION: joint angles here are crude 2D-ish geometric estimates from a single view and
are not physically consistent with the MuJoCo model. For production use WHAM/GVHMR,
see docs/WHAM_GVHMR.md. Mind the licensing of the source video (see
data/download_puregolf_proxy.py).
"""

import argparse
import hashlib
import json
import math
import sys
import traceback
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
try:
    from data import provenance as _prov
except ImportError:  # run as a script
    import provenance as _prov

try:  # scipy is in requirements.txt but keep a fallback
    from scipy.signal import savgol_filter
except Exception:  # pragma: no cover
    savgol_filter = None

# MediaPipe pose landmark indices
L_SH, R_SH, L_EL, R_EL, L_WR, R_WR = 11, 12, 13, 14, 15, 16
R_IDX, L_HIP, R_HIP, L_KNEE, R_KNEE, L_ANK, R_ANK = 20, 23, 24, 25, 26, 27, 28
L_FOOT, R_FOOT = 31, 32
N_LM = 33
JOINT_NAMES = ["right_shoulder_pitch", "right_shoulder_roll", "right_elbow", "right_wrist",
               "left_shoulder_pitch", "right_hip_pitch", "right_knee", "right_ankle",
               "left_hip_pitch", "left_knee", "left_ankle"]

# A pose backend maps a BGR frame -> (33,4) array [x, y, z, visibility] or None.
PoseBackend = Callable[[np.ndarray], Optional[np.ndarray]]


# --------------------------------------------------------------------------------------
# Numeric core (no cv2/mediapipe needed)
# --------------------------------------------------------------------------------------

def mask_low_visibility(lm: np.ndarray, min_vis: float) -> np.ndarray:
    """lm: (n,33,4). Set xyz to NaN where visibility < min_vis (or already NaN)."""
    out = lm.copy()
    bad = ~(out[..., 3] >= min_vis)
    out[bad, :3] = np.nan
    return out


def fill_gaps(x: np.ndarray, max_gap: int) -> np.ndarray:
    """Linear-interpolate NaN runs of length <= max_gap in a 1D/2D(time-first) array.
    Longer runs and leading/trailing NaNs stay NaN."""
    x = np.array(x, dtype=float, copy=True)
    if x.ndim == 1:
        x = x[:, None]
        squeeze = True
    else:
        squeeze = False
    n = x.shape[0]
    for c in range(x.shape[1]):
        col = x[:, c]
        nan = np.isnan(col)
        if not nan.any() or nan.all():
            continue
        idx = np.arange(n)
        interp = np.interp(idx, idx[~nan], col[~nan])
        i = 0
        while i < n:
            if nan[i]:
                j = i
                while j < n and nan[j]:
                    j += 1
                interior = i > 0 and j < n
                if interior and (j - i) <= max_gap:
                    col[i:j] = interp[i:j]
                i = j
            else:
                i += 1
        x[:, c] = col
    return x[:, 0] if squeeze else x


def smooth(x: np.ndarray, fps: float, window_s: float = 0.12, poly: int = 3) -> np.ndarray:
    """Savitzky-Golay smoothing that tolerates NaNs (smooths each finite run)."""
    x = np.array(x, dtype=float, copy=True)
    if x.ndim == 1:
        return smooth(x[:, None], fps, window_s, poly)[:, 0]
    for c in range(x.shape[1]):
        col = x[:, c]
        ok = np.isfinite(col)
        i, n = 0, len(col)
        while i < n:
            if not ok[i]:
                i += 1
                continue
            j = i
            while j < n and ok[j]:
                j += 1
            seg = col[i:j]
            w = int(round(window_s * fps)) | 1  # odd
            w = min(w, len(seg) if len(seg) % 2 else len(seg) - 1)
            if savgol_filter is not None and w >= poly + 2:
                col[i:j] = savgol_filter(seg, w, poly)
            elif w >= 3:
                k = np.ones(w) / w
                pad = np.pad(seg, w // 2, mode="edge")
                col[i:j] = np.convolve(pad, k, mode="valid")
            i = j
        x[:, c] = col
    return x


def _angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Interior angle at b (deg) for (n,2|3) points; NaN-propagating."""
    v1, v2 = a - b, c - b
    cosv = np.sum(v1 * v2, -1) / (np.linalg.norm(v1, axis=-1) * np.linalg.norm(v2, axis=-1) + 1e-9)
    return np.degrees(np.arccos(np.clip(cosv, -1, 1)))


def _signed_angle2d(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """Signed angle (deg) from v1 to v2 in the image plane."""
    cross = v1[:, 0] * v2[:, 1] - v1[:, 1] * v2[:, 0]
    dot = np.sum(v1[:, :2] * v2[:, :2], -1)
    return np.degrees(np.arctan2(cross, dot))


def landmarks_to_joints(lm: np.ndarray) -> np.ndarray:
    """(n,33,>=3) -> (n,11) degrees in the layout of generate_synthetic_scott.py.
    Crude geometric proxies; zero = neutral standing posture, NaN where inputs are NaN."""
    P = lambda i: lm[:, i, :3]
    torso = P(R_SH) - P(R_HIP)                               # hip -> shoulder
    j = np.full((lm.shape[0], 11), np.nan)
    j[:, 0] = _signed_angle2d(torso, P(R_EL) - P(R_SH))  # upper arm vs torso
    j[:, 0] = np.where(np.isnan(j[:, 0]), np.nan, ((j[:, 0] + 180) % 360) - 180)
    j[:, 1] = _angle(P(R_HIP), P(R_SH), P(R_EL)) - 90.0       # arm abduction proxy
    j[:, 2] = 180.0 - _angle(P(R_SH), P(R_EL), P(R_WR))       # elbow flexion
    j[:, 3] = 180.0 - _angle(P(R_EL), P(R_WR), P(R_IDX))      # wrist deviation/hinge proxy
    j[:, 4] = _signed_angle2d(P(L_SH) - P(L_HIP), P(L_EL) - P(L_SH))
    j[:, 5] = 180.0 - _angle(P(R_SH), P(R_HIP), P(R_KNEE))    # hip flexion
    j[:, 6] = 180.0 - _angle(P(R_HIP), P(R_KNEE), P(R_ANK))   # knee flexion
    j[:, 7] = _angle(P(R_KNEE), P(R_ANK), P(R_FOOT)) - 90.0   # ankle
    j[:, 8] = 180.0 - _angle(P(L_SH), P(L_HIP), P(L_KNEE))
    j[:, 9] = 180.0 - _angle(P(L_HIP), P(L_KNEE), P(L_ANK))
    j[:, 10] = _angle(P(L_KNEE), P(L_ANK), P(L_FOOT)) - 90.0
    return j


def resample(x: np.ndarray, src_dt: float, out_dt: float) -> Tuple[np.ndarray, np.ndarray]:
    n = x.shape[0]
    t_src = np.arange(n) * src_dt
    t_out = np.arange(0, t_src[-1] + 1e-9, out_dt)
    out = np.column_stack([np.interp(t_out, t_src, x[:, c]) for c in range(x.shape[1])])
    return t_out, out


def process_landmarks(lm: np.ndarray, fps: float, *, min_visibility: float = 0.5,
                      max_gap: int = 5, min_valid_frac: float = 0.6, out_dt: float = 0.01,
                      key: Optional[List[int]] = None) -> Dict[str, np.ndarray]:
    """Core pipeline: raw landmarks (n,33,4) with NaN rows for missed frames -> reference dict.
    Raises ValueError if the clip is unusable."""
    if lm.ndim != 3 or lm.shape[1] != N_LM or lm.shape[2] < 4:
        raise ValueError(f"landmarks must be (n,33,4), got {lm.shape}")
    if not (fps and np.isfinite(fps) and fps > 0):
        raise ValueError(f"bad fps {fps}")
    n = lm.shape[0]
    if n < 10:
        raise ValueError(f"too few frames ({n})")
    lm = mask_low_visibility(lm, min_visibility)
    flat = fill_gaps(lm[..., :3].reshape(n, -1), max_gap).reshape(n, N_LM, 3)
    lm_f = np.concatenate([flat, lm[..., 3:]], axis=-1)
    key = key or [R_SH, R_EL, R_WR, R_HIP, R_KNEE, R_ANK, L_SH, L_HIP]  # `key`: custom validity set
    valid = np.all(np.isfinite(lm_f[:, key, :3]), axis=(1, 2))
    frac = float(valid.mean())
    if frac < min_valid_frac:
        raise ValueError(f"only {frac:.0%} frames have all key landmarks (need {min_valid_frac:.0%})")
    # Smooth landmark coordinates, then derive angles, then smooth angles lightly.
    sm = smooth(lm_f[..., :3].reshape(n, -1), fps).reshape(n, N_LM, 3)
    joints = landmarks_to_joints(sm)
    # signed image-plane angles wrap at +-180; smoothing across the wrap makes +-200 artefacts.
    for c in (0, 4):
        m = np.isfinite(joints[:, c])
        if m.sum() > 2:
            u = np.degrees(np.unwrap(np.radians(joints[m, c])))
            # arm hanging along the torso is 180 deg apart -> report 0 there (neutral posture)
            joints[m, c] = u - 360.0 * np.round((np.median(u) - 180.0) / 360.0) - 180.0
    joints = smooth(joints, fps, window_s=0.08)
    # Trim leading/trailing invalid frames, fill remaining NaN by interpolation for training.
    first, last = np.argmax(valid), n - 1 - np.argmax(valid[::-1])
    joints, valid_t = joints[first:last + 1], valid[first:last + 1]
    joints = fill_gaps(joints, max_gap=10 ** 6)
    joints = np.nan_to_num(joints, nan=0.0)
    t_out, joints_out = resample(joints, 1.0 / fps, out_dt)
    mask_out = np.interp(t_out, np.arange(len(valid_t)) / fps, valid_t.astype(float)) > 0.5
    return {"time": t_out, "joints": joints_out, "dt": np.array(out_dt),
            "valid_mask": mask_out, "valid_frac": np.array(frac),
            "landmarks": lm_f[first:last + 1].astype(np.float32)}


# --------------------------------------------------------------------------------------
# I/O: backends, video reading, resume index
# --------------------------------------------------------------------------------------

def make_backend(model_path: Optional[str] = None) -> Tuple[PoseBackend, Callable[[], None]]:
    """Return (backend, close). Prefers legacy mp.solutions, else tasks PoseLandmarker."""
    import mediapipe as mp  # lazy
    if hasattr(mp, "solutions") and hasattr(mp.solutions, "pose"):
        pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=2,
                                      smooth_landmarks=True, min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)

        def run(frame_bgr):
            import cv2
            res = pose.process(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
            lms = res.pose_world_landmarks or res.pose_landmarks
            if lms is None:
                return None
            return np.array([[l.x, l.y, l.z, l.visibility] for l in lms.landmark])
        return run, pose.close
    # tasks API (mediapipe >= 0.10.x without solutions)
    if not model_path or not Path(model_path).exists():
        raise RuntimeError("This mediapipe build has no mp.solutions; pass --model "
                           "pose_landmarker_heavy.task (download from the MediaPipe docs).")
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    opts = vision.PoseLandmarkerOptions(
        base_options=mpt.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO)
    lander = vision.PoseLandmarker.create_from_options(opts)
    state = {"ts": 0}

    def run(frame_bgr):
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        state["ts"] += 33
        res = lander.detect_for_video(img, state["ts"])
        pts = (res.pose_world_landmarks or res.pose_landmarks)
        if not pts:
            return None
        return np.array([[l.x, l.y, l.z, l.visibility] for l in pts[0]])
    return run, lander.close


def read_landmarks(video: Path, backend: PoseBackend, max_frames: Optional[int] = None
                   ) -> Tuple[np.ndarray, float]:
    import cv2  # lazy
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise IOError(f"cannot open {video}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    rows: List[np.ndarray] = []
    try:
        while True:
            ok, frame = cap.read()
            if not ok or (max_frames and len(rows) >= max_frames):
                break
            try:
                r = backend(frame)
            except Exception:  # per-frame failure -> treat as missing
                r = None
            rows.append(np.full((N_LM, 4), np.nan) if r is None else np.asarray(r, float)[:N_LM])
    finally:
        cap.release()
    if not rows:
        raise IOError(f"no frames decoded from {video}")
    return np.stack(rows), float(fps)


def _settings_key(path: Path, settings: Dict) -> str:
    st = path.stat()
    h = hashlib.sha1(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:8]
    return f"{path.name}|{st.st_size}|{int(st.st_mtime)}|{h}"


def load_index(out_dir: Path) -> Dict:
    p = out_dir / "processed_index.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            print("WARN: corrupt processed_index.json, starting fresh")
    return {}


def save_index(out_dir: Path, idx: Dict) -> None:
    tmp = out_dir / "processed_index.json.tmp"
    tmp.write_text(json.dumps(idx, indent=2))
    tmp.replace(out_dir / "processed_index.json")  # atomic


def process_video(video: Path, out_dir: Path, backend: PoseBackend, *, capture_fps: Optional[float],
                  fps_fallback: float, **kw) -> Path:
    lm, fps = read_landmarks(video, backend)
    if not (np.isfinite(fps) and fps > 0):
        print(f"  WARN header fps={fps}; using fallback {fps_fallback}")
        fps = fps_fallback
    # Slow-mo: container fps is the *playback* rate; the true capture rate is the real clock.
    # If capture_fps is given and container fps is lower (e.g. 250 fps shot stored as 30 fps),
    # the video is slowed by capture_fps/fps and real dt = 1/capture_fps.
    eff_fps = capture_fps or fps
    data = process_landmarks(lm, eff_fps, **kw)
    data["source"] = np.array(str(video.name))
    data["style"] = np.array("video")
    out = out_dir / f"{video.stem}_processed.npz"
    _prov.tag(data, "unknown")  # origin of arbitrary video unknown; retag via tag_provenance --force
    np.savez(out, **data)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="MediaPipe video -> reference .npz")
    root = Path(__file__).parent
    ap.add_argument("--videos", type=Path, default=root / "raw_videos")
    ap.add_argument("--out", type=Path, default=root / "references")
    ap.add_argument("--model", help="pose_landmarker .task file (tasks API only)")
    ap.add_argument("--capture-fps", type=float, help="true camera fps for slow-mo footage")
    ap.add_argument("--fps-fallback", type=float, default=30.0)
    ap.add_argument("--min-visibility", type=float, default=0.5)
    ap.add_argument("--max-gap", type=int, default=5)
    ap.add_argument("--min-valid-frac", type=float, default=0.6)
    ap.add_argument("--out-dt", type=float, default=0.01)
    ap.add_argument("--force", action="store_true", help="ignore resume index")
    args = ap.parse_args(argv)

    vids = sorted(p for p in args.videos.glob("*") if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm", ".avi"}) \
        if args.videos.exists() else []
    if not vids:
        print(f"No videos in {args.videos}. See data/download_puregolf_proxy.py (licensing!).")
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    idx = {} if args.force else load_index(args.out)
    settings = dict(capture_fps=args.capture_fps, min_visibility=args.min_visibility,
                    max_gap=args.max_gap, min_valid_frac=args.min_valid_frac, out_dt=args.out_dt)
    try:
        backend, close = make_backend(args.model)
    except Exception as e:
        print(f"ERROR: cannot start MediaPipe backend: {e}")
        return 1
    done = skipped = failed = 0
    try:
        for v in vids:
            key = _settings_key(v, settings)
            if idx.get(v.name, {}).get("key") == key and (args.out / idx[v.name]["output"]).exists():
                print(f"skip (done): {v.name}")
                skipped += 1
                continue
            print(f"processing {v.name}")
            try:
                out = process_video(v, args.out, backend, capture_fps=args.capture_fps,
                                    fps_fallback=args.fps_fallback,
                                    min_visibility=args.min_visibility, max_gap=args.max_gap,
                                    min_valid_frac=args.min_valid_frac, out_dt=args.out_dt)
                idx[v.name] = {"key": key, "output": out.name}
                save_index(args.out, idx)  # persist after every video => resumable
                done += 1
                print(f"  saved {out}")
            except Exception as e:
                failed += 1
                print(f"  FAILED {v.name}: {e}")
                if "--debug" in (argv or sys.argv):
                    traceback.print_exc()
    finally:
        close()
    print(f"done={done} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 3


if __name__ == "__main__":
    sys.exit(main())

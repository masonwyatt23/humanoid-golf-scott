"""
Convert CMU Graphics Lab Motion Capture golf swings (BVH conversion of the ASF/AMC data)
into this project's reference ``.npz`` format.

    python -m data.convert_cmu_mocap                      # all swing trials in data/raw_mocap/cmu
    python -m data.convert_cmu_mocap --trials 64_03 64_05
    python -m data.convert_cmu_mocap --raw-dir X --out-dir Y --handedness auto

Source / licence: see docs/CMU_MOCAP_GOLF.md (free for research and for inclusion in
commercial products; the *data itself* may not be resold, even converted).

What it produces (data/references/cmu_<trial>.npz), all arrays float64 unless noted:
  time[n], dt (=0.01), joints[n,11] (DEGREES), joints_rad[n,11], events[2]=[top, impact] s,
  pelvis_rot_deg, thorax_rot_deg, x_factor_deg, lateral_sway_m, wrist_hinge_deg,
  tempo_ratio, and provenance: source="cmu_mocap", is_synthetic=False, subject, trial,
  style="cmu_subject64", has_club_head=False, handedness, qc_flags, source_fps, ...
``club_head`` is deliberately NOT written: CMU captured no club (see docs).

Frames/units/axes (see docs/CMU_MOCAP_GOLF.md for the full discussion):
  * BVH is Y-up, T-pose added by the cgspeed conversion as frame 0 (dropped here).
  * Lengths in BVH are ASF units: metres = value * (1/0.45) * 2.54/100  (CMU FAQ).
  * Euler order from CHANNELS (Zrotation Yrotation Xrotation => R = Rz @ Ry @ Rx).
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ASF_TO_M = (1.0 / 0.45) * 2.54 / 100.0      # CMU FAQ: 0.056444
SRC_FPS = 120.0                              # CMU capture rate (FAQ); BVH Frame Time .0083333
OUT_DT = 0.01
SOURCE = "cmu_mocap"
DEFAULT_TRIALS = [f"64_{i:02d}" for i in range(1, 11)]   # CMU index: subject 64 "Swing"

JOINT_COLUMNS = ["right_shoulder_pitch", "right_shoulder_roll", "right_elbow", "right_wrist",
                 "left_shoulder_pitch", "right_hip_pitch", "right_knee", "right_ankle",
                 "left_hip_pitch", "left_knee", "left_ankle"]


class CmuConvertError(Exception):
    pass


# ----------------------------------------------------------------------------- BVH parsing
@dataclass
class Bvh:
    names: List[str]
    parent: List[int]
    offset: np.ndarray            # (J,3) in ASF units
    channels: List[List[str]]
    motion: np.ndarray            # (frames, total_channels), T-pose frame already NOT removed
    frame_time: float

    def index(self, name: str) -> int:
        return self.names.index(name)


def parse_bvh(path: Path) -> Bvh:
    text = Path(path).read_text().splitlines()
    names: List[str] = []; parent: List[int] = []; offs: List[np.ndarray] = []
    chans: List[List[str]] = []
    stack: List[int] = []; cur = -1; i = 0
    while i < len(text) and not text[i].strip().startswith("MOTION"):
        s = text[i].split()
        if s:
            if s[0] in ("ROOT", "JOINT"):
                names.append(s[1]); parent.append(stack[-1] if stack else -1)
                offs.append(np.zeros(3)); chans.append([]); cur = len(names) - 1
            elif s[0] == "End":
                names.append(names[cur] + "_end"); parent.append(cur)
                offs.append(np.zeros(3)); chans.append([]); cur = len(names) - 1
            elif s[0] == "OFFSET":
                offs[cur] = np.array(s[1:4], float)
            elif s[0] == "CHANNELS":
                chans[cur] = s[2:2 + int(s[1])]
            elif s[0] == "{":
                stack.append(cur)
            elif s[0] == "}":
                stack.pop()
                cur = stack[-1] if stack else cur
        i += 1
    if i >= len(text) or not names:
        raise CmuConvertError(f"{path}: not a BVH file (no HIERARCHY/MOTION)")
    m = re.match(r"Frames:\s*(\d+)", text[i + 1].strip())
    ft = re.match(r"Frame Time:\s*([0-9.eE+-]+)", text[i + 2].strip())
    if not (m and ft):
        raise CmuConvertError(f"{path}: malformed MOTION header")
    nfr, frame_time = int(m.group(1)), float(ft.group(1))
    rows = [list(map(float, ln.split())) for ln in text[i + 3:] if ln.strip()]
    motion = np.array(rows, float)
    ncols = sum(len(c) for c in chans)
    if motion.shape != (nfr, ncols):
        raise CmuConvertError(f"{path}: motion shape {motion.shape} != ({nfr},{ncols})")
    if not np.all(np.isfinite(motion)):
        raise CmuConvertError(f"{path}: non-finite motion values")
    return Bvh(names, parent, np.array(offs), chans, motion, frame_time)


def _rot(axis: str, ang_deg: np.ndarray) -> np.ndarray:
    a = np.deg2rad(ang_deg); c, s = np.cos(a), np.sin(a)
    R = np.zeros(a.shape + (3, 3)); R[..., :, :] = np.eye(3)
    if axis == "X":
        R[..., 1, 1] = c; R[..., 1, 2] = -s; R[..., 2, 1] = s; R[..., 2, 2] = c
    elif axis == "Y":
        R[..., 0, 0] = c; R[..., 0, 2] = s; R[..., 2, 0] = -s; R[..., 2, 2] = c
    else:
        R[..., 0, 0] = c; R[..., 0, 1] = -s; R[..., 1, 0] = s; R[..., 1, 1] = c
    return R


def forward_kinematics(b: Bvh, frames: slice = slice(1, None)) -> np.ndarray:
    """World joint positions (n, J, 3) in METRES. Drops BVH frame 0 (added T-pose) by default."""
    mo = b.motion[frames]
    n = mo.shape[0]; J = len(b.names)
    pos = np.zeros((n, J, 3)); rot = np.zeros((n, J, 3, 3)); rot[:] = np.eye(3)
    col = 0
    for j in range(J):
        ch = b.channels[j]; local_t = np.tile(b.offset[j], (n, 1)); R = np.tile(np.eye(3), (n, 1, 1))
        for k, c in enumerate(ch):
            v = mo[:, col + k]
            if c.endswith("position"):
                local_t[:, "XYZ".index(c[0])] = v     # root: position channels replace offset
            else:
                R = R @ _rot(c[0], v)                 # first listed channel is outermost
        col += len(ch)
        p = b.parent[j]
        if p < 0:
            pos[:, j] = local_t; rot[:, j] = R
        else:
            pos[:, j] = pos[:, p] + np.einsum("nij,nj->ni", rot[:, p], local_t)
            rot[:, j] = rot[:, p] @ R
    return pos * ASF_TO_M


# ----------------------------------------------------------------------------- geometry
def _unit(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def _interior(a, b, c) -> np.ndarray:
    v1, v2 = _unit(a - b), _unit(c - b)
    return np.degrees(np.arccos(np.clip(np.sum(v1 * v2, -1), -1, 1)))


def _yaw(vec: np.ndarray) -> np.ndarray:
    """Heading (deg) of horizontal component (x,z) of vec; unwrapped."""
    return np.degrees(np.unwrap(np.arctan2(vec[:, 0], vec[:, 2])))


def _smooth(x: np.ndarray, fps: float, window_s: float = 0.10) -> np.ndarray:
    from scipy.signal import savgol_filter
    w = int(round(window_s * fps)) | 1
    w = max(w, 5)
    return savgol_filter(x, w, 3, axis=0, mode="interp")


SIDE = {"R": dict(sh="RightArm", el="RightForeArm", wr="RightHand", hand="RightHandIndex1",
                  hip="RightUpLeg", knee="RightLeg", ank="RightFoot", toe="RightToeBase"),
        "L": dict(sh="LeftArm", el="LeftForeArm", wr="LeftHand", hand="LeftHandIndex1",
              hip="LeftUpLeg", knee="LeftLeg", ank="LeftFoot", toe="LeftToeBase")}


def detect_handedness(b: Bvh, P: Dict[str, np.ndarray]) -> str:
    """Right-handed golfers finish with the hands over the LEFT (lead) shoulder.
    Uses the last 20 % of the trial: whichever shoulder the hands' midpoint is closer to,
    laterally, is the lead side."""
    k = max(3, int(0.2 * len(P["RightArm"])))
    hands = 0.5 * (P["RightHand"][-k:] + P["LeftHand"][-k:])
    dR = np.linalg.norm((hands - P["RightArm"][-k:])[:, [0, 2]], axis=1).mean()
    dL = np.linalg.norm((hands - P["LeftArm"][-k:])[:, [0, 2]], axis=1).mean()
    return "right" if dL < dR else "left"


def compute_joints(P: Dict[str, np.ndarray], fps: float, hand: str) -> Dict[str, np.ndarray]:
    """Map 3-D joint positions to the 11-column layout + extras. P = name -> (n,3)."""
    t, l = ("R", "L") if hand == "right" else ("L", "R")   # trail, lead side
    T, Ld = SIDE[t], SIDE[l]
    n = len(P["Hips"])
    hip_c = 0.5 * (P["RightUpLeg"] + P["LeftUpLeg"])
    sh_c = 0.5 * (P["RightArm"] + P["LeftArm"])
    # thorax frame: up = hip->shoulder centre, lateral = trail->lead... use R->L shoulders
    up = _unit(sh_c - hip_c)
    lat = P["LeftArm"] - P["RightArm"]
    lat = _unit(lat - np.sum(lat * up, -1, keepdims=True) * up)
    fwd = np.cross(lat, up)                         # (L x up): forward = facing direction for Y-up, +X=left
    # sanity: forward should point the way the face looks
    face = P["Head_end"] - P["Neck1"]

    def arm_angles(S):
        u = _unit(P[S["el"]] - P[S["sh"]])               # upper-arm direction
        down = -np.sum(u * up, -1); front = np.sum(u * fwd, -1); side = np.sum(u * lat, -1)
        flex = np.degrees(np.arctan2(front, down))       # 0 hanging, 90 forward, 180 overhead
        abd = np.degrees(np.arcsin(np.clip(side, -1, 1)))
        return -flex, abd                                # generator convention: raising = negative

    sp_t, roll_t = arm_angles(T)
    sp_l, _ = arm_angles(Ld)
    j = np.zeros((n, 11))
    j[:, 0] = sp_t
    j[:, 1] = np.abs(roll_t) if t == "R" else np.abs(roll_t)   # abduction magnitude, >=0
    j[:, 2] = 180.0 - _interior(P[T["sh"]], P[T["el"]], P[T["wr"]])
    wrist_dev = 180.0 - _interior(P[T["el"]], P[T["wr"]], P[T["hand"]])
    j[:, 3] = -wrist_dev                                  # cocked = negative (unsigned magnitude)
    j[:, 4] = sp_l
    for base, S in ((5, T), (8, Ld)):
        j[:, base] = 180.0 - _interior(sh_c, P[S["hip"]], P[S["knee"]])
        j[:, base + 1] = 180.0 - _interior(P[S["hip"]], P[S["knee"]], P[S["ank"]])
        j[:, base + 2] = _interior(P[S["knee"]], P[S["ank"]], P[S["toe"]]) - 90.0
    j = _smooth(j, fps)

    # rotations about the vertical axis. Hip/shoulder line heading, relative to address.
    pel_line = P[Ld["hip"]] - P[T["hip"]]       # trail -> lead hip (points toward target at address)
    tho_line = P[Ld["sh"]] - P[T["sh"]]
    return dict(joints=j, wrist_hinge=j[:, 3].copy(), pel_line=pel_line, tho_line=tho_line,
                hip_c=hip_c, sh_c=sh_c, hands=0.5 * (P[T["wr"]] + P[Ld["wr"]]))


# ----------------------------------------------------------------------------- events
def detect_events(hands: np.ndarray, fps: float) -> Dict[str, int]:
    """Takeaway, top of backswing, impact and finish from the 3-D hand-midpoint path.

    peak:     frame of maximum hand speed (m/s) -- the downswing, just before impact
    top:      highest hand position (Y) in [0, peak]
    takeaway: the last at-rest frame (speed < 5 % of peak) before the backswing motion that leads to `top`
    impact:   within [peak-0.08 s, peak+0.12 s], the frame whose hand position is nearest
              the address hand position (hands return to address at impact). Heuristic;
              there is no club or ball in CMU data to validate it.
    finish:   first frame after impact with speed < 5 % of the peak (or the last frame)
    """
    h = _smooth(hands, fps, 0.08)
    speed = np.linalg.norm(np.gradient(h, 1.0 / fps, axis=0), axis=1)
    vmax = float(speed.max())
    if vmax < 1.5:
        raise CmuConvertError(f"hand speed peak {vmax:.2f} m/s too low: not a full swing")
    # downswing peak = highest-speed frame that comes after the highest-hands frame of the
    # first half of the motion (guards against a faster follow-through)
    thr = 0.05 * vmax
    moving = np.where(speed > thr)[0]
    first_move = int(moving[0])
    top_guess = first_move + int(np.argmax(h[first_move:, 1]))
    # use the first strong speed peak after the first rest-to-move transition
    peak = int(np.argmax(speed[: top_guess + int(0.8 * fps)]))
    top = int(np.argmax(h[: peak + 1, 1]))
    k = top
    while k > 0 and speed[k] < 0.15 * vmax:  # skip the slow/paused transition at the top
        k -= 1
    while k > 0 and speed[k] >= thr:         # walk back through the backswing motion
        k -= 1
    take = k                                 # last quiet frame before the backswing began
    addr = h[: max(take, 1) + 1].mean(axis=0) if take > 3 else h[take]
    lo, hi = max(top + 1, peak - int(0.08 * fps)), min(len(h) - 1, peak + int(0.12 * fps))
    if hi <= lo:
        raise CmuConvertError("could not locate impact window")
    imp = lo + int(np.argmin(np.linalg.norm(h[lo:hi + 1] - addr, axis=1)))
    post = np.where(speed[imp:] < thr)[0]
    fin = imp + (int(post[0]) if len(post) else len(h) - 1 - imp)
    return dict(takeaway=take, top=top, impact=imp, finish=fin, peak_speed_frame=peak,
                peak_hand_speed=float(speed[peak]))


# ----------------------------------------------------------------------------- conversion
def convert_bvh(path: Path, *, handedness: str = "auto", pad_s: float = 0.25,
                out_dt: float = OUT_DT) -> Dict[str, np.ndarray]:
    path = Path(path)
    m = re.match(r"(\d+)_(\d+)", path.stem)
    if not m:
        raise CmuConvertError(f"{path.name}: expected CMU name like 64_03.bvh")
    subject, trial = int(m.group(1)), int(m.group(2))
    b = parse_bvh(path)
    fps = 1.0 / b.frame_time
    if abs(fps - SRC_FPS) > 1.0:
        raise CmuConvertError(f"{path.name}: frame rate {fps:.2f} != 120 Hz")
    pos = forward_kinematics(b)
    P = {nm: pos[:, i] for i, nm in enumerate(b.names)}
    hand = detect_handedness(b, P) if handedness == "auto" else handedness
    if hand not in ("left", "right"):
        raise CmuConvertError("handedness must be auto/left/right")
    c = compute_joints(P, fps, hand)
    ev = detect_events(c["hands"], fps)
    n = len(c["hip_c"])
    i0 = max(0, ev["takeaway"] - int(pad_s * fps)); i1 = min(n - 1, ev["finish"] + int(pad_s * fps))
    sl = slice(i0, i1 + 1)
    addr_i = slice(i0, max(ev["takeaway"], i0 + 3))      # quiet address window

    # pelvis / thorax rotation (deg) relative to address; backswing (away from target) negative
    def rot_rel(line):
        y = _yaw(line); y = y - y[addr_i].mean()
        top = y[ev["top"]]
        return y if top < 0 else -y                      # sign so the backswing turn is negative
    pel = rot_rel(c["pel_line"]); tho = rot_rel(c["tho_line"])
    xf = pel - tho                                       # = |thorax| - |pelvis| at top (matches generator)
    # lateral sway toward target along address hip line (trail->lead), metres
    tgt = c["pel_line"][addr_i].mean(axis=0); tgt[1] = 0; tgt = tgt / (np.linalg.norm(tgt) + 1e-12)
    sway = np.sum((c["hip_c"] - c["hip_c"][addr_i].mean(axis=0)) * tgt, -1)

    def cut(x):
        return x[sl]
    t_src = np.arange(i1 - i0 + 1) / fps
    t_out = np.arange(0, t_src[-1] + 1e-9, out_dt)

    def rs(x):
        x = np.asarray(x, float)
        if x.ndim == 1:
            return np.interp(t_out, t_src, x)
        return np.column_stack([np.interp(t_out, t_src, x[:, k]) for k in range(x.shape[1])])

    joints = rs(cut(c["joints"]))
    ev_s = np.array([(ev["top"] - i0) / fps, (ev["impact"] - i0) / fps])
    take_s = (ev["takeaway"] - i0) / fps
    bs, ds = ev_s[0] - take_s, ev_s[1] - ev_s[0]
    tempo = bs / ds if ds > 0 else float("nan")
    flags = []
    if not (1.5 <= tempo <= 5.5): flags.append(f"tempo_out_of_range:{tempo:.2f}")
    if not (0.4 <= bs <= 2.0): flags.append(f"backswing_s_out_of_range:{bs:.2f}")
    if not (0.12 <= ds <= 0.6): flags.append(f"downswing_s_out_of_range:{ds:.2f}")
    if ev["peak_hand_speed"] < 4.0: flags.append(f"low_hand_speed:{ev['peak_hand_speed']:.1f}")
    if np.any(np.abs(joints) > 400): flags.append("extreme_joint_values")
    out = {
        "time": t_out, "joints": joints, "joints_rad": np.deg2rad(joints),
        "pelvis_rot_deg": rs(cut(pel)), "thorax_rot_deg": rs(cut(tho)), "x_factor_deg": rs(cut(xf)),
        "lateral_sway_m": rs(cut(sway)), "wrist_hinge_deg": rs(cut(c["wrist_hinge"])),
        "events": ev_s, "takeaway_s": np.array(take_s), "finish_s": np.array((ev["finish"] - i0) / fps),
        "tempo_ratio": np.array(tempo), "peak_hand_speed_mps": np.array(ev["peak_hand_speed"]),
        "dt": np.array(out_dt), "source_fps": np.array(fps),
        "source": np.array(SOURCE), "is_synthetic": np.array(False), "has_club_head": np.array(False),
        "style": np.array(f"cmu_subject{subject}"), "subject": np.array(subject),
        "trial": np.array(trial), "trial_id": np.array(f"{subject}_{trial:02d}"),
        "handedness": np.array(hand), "source_file": np.array(path.name),
        "qc_flags": np.array(flags, dtype="U64") if flags else np.array([], dtype="U64"),
        "joint_columns": np.array(JOINT_COLUMNS),
    }
    return out


def summarize(d: Dict[str, np.ndarray]) -> Dict:
    t, (top, imp) = d["time"], d["events"]
    i_top = int(round(top / float(d["dt"]))); 
    return {"trial": str(d["trial_id"]), "frames": int(len(t)), "dt": float(d["dt"]),
            "handedness": str(d["handedness"]), "tempo": round(float(d["tempo_ratio"]), 2),
            "backswing_s": round(float(top - d["takeaway_s"]), 3), "downswing_s": round(float(imp - top), 3),
            "top_s": round(float(top), 3), "impact_s": round(float(imp), 3),
            "pelvis_top_deg": round(float(-d["pelvis_rot_deg"][i_top]), 1),
            "thorax_top_deg": round(float(-d["thorax_rot_deg"][i_top]), 1),
            "x_factor_top_deg": round(float(d["x_factor_deg"][i_top]), 1),
            "peak_hand_speed_mps": round(float(d["peak_hand_speed_mps"]), 2),
            "qc_flags": [str(x) for x in d["qc_flags"]]}


def main(argv: Optional[Sequence[str]] = None) -> int:
    root = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--raw-dir", type=Path, default=root / "raw_mocap" / "cmu")
    ap.add_argument("--out-dir", type=Path, default=root / "references")
    ap.add_argument("--trials", nargs="*", default=DEFAULT_TRIALS)
    ap.add_argument("--handedness", choices=["auto", "left", "right"], default="auto")
    args = ap.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report, rc = [], 0
    for tr in args.trials:
        f = args.raw_dir / f"{tr}.bvh"
        try:
            if not f.exists():
                raise CmuConvertError(f"{f} missing (see docs/CMU_MOCAP_GOLF.md for download)")
            d = convert_bvh(f, handedness=args.handedness)
            np.savez(args.out_dir / f"cmu_{tr}.npz", **d)
            s = summarize(d); report.append(s)
            print(f"[ok] {tr}: {s['frames']} frames, tempo {s['tempo']}, flags {s['qc_flags']}")
        except CmuConvertError as e:
            rc = 1; report.append({"trial": tr, "error": str(e)}); print(f"[FAIL] {tr}: {e}")
    (args.out_dir / "cmu_conversion_report.json").write_text(json.dumps(report, indent=2))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

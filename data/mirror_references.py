"""Create left/right-mirrored copies of reference .npz files (additive; originals untouched).

11-column joint layout (see data/process_video.py JOINT_NAMES / generate_synthetic_scott.py):
 0 r_shoulder_pitch 1 r_shoulder_roll 2 r_elbow 3 r_wrist 4 l_shoulder_pitch
 5 r_hip 6 r_knee 7 r_ankle 8 l_hip 9 l_knee 10 l_ankle
Mirror rules:
 * sagittal-plane flexion/pitch angles are mirror-invariant (elbow, wrist hinge, knee, ankle, pitch).
 * roll about the sagittal axis (col 1) flips sign.
 * complete left/right limb pairs are swapped: legs (5,6,7)<->(8,9,10).
 * the arm chain (0-3) has no complete left partner (col 4 has no elbow/wrist), so it stays in
   place; swapping 0<->4 alone would decouple shoulder from elbow/wrist/club_head.
 * pelvis_rot_deg, thorax_rot_deg, x_factor_deg, lateral_sway_m negate; club_head lateral (x) negates.
 * landmarks (n,33,4): x negated (coords are centred) and MediaPipe left/right indices swapped.
 * events, time, tempo, plane, wrist_hinge, quality fields unchanged. Provenance tags copied verbatim.
Mirroring twice returns the original.
"""
import argparse
import glob
import os
from pathlib import Path

import numpy as np

SWAP = [(5, 8), (6, 9), (7, 10)]
FLIP_COLS = [1]
NEGATE_KEYS = ["pelvis_rot_deg", "thorax_rot_deg", "x_factor_deg", "lateral_sway_m"]
NEUTRAL_KEYS = ["time", "events", "dt", "tempo_ratio", "plane_angle_deg", "wrist_hinge_deg"]


def _mirror_joints(j):
    j = np.array(j, dtype=float, copy=True)
    for a, b in SWAP:
        j[:, [a, b]] = j[:, [b, a]]
    for c in FLIP_COLS:
        j[:, c] = -j[:, c]
    return j


def _mirror_landmarks(lm):
    lm = np.array(lm, copy=True)
    for i in range(1, 33, 2):  # odd=left, even=right in MediaPipe (1..32)
        lm[:, [i, i + 1]] = lm[:, [i + 1, i]]
    lm[..., 0] = -lm[..., 0]
    return lm


def mirror_dict(d, source_name=""):
    out = dict(d)
    out["joints"] = _mirror_joints(d["joints"])
    if "joints_rad" in d:
        out["joints_rad"] = np.deg2rad(out["joints"])
    for k in NEGATE_KEYS:
        if k in d:
            out[k] = -np.asarray(d[k])
    if "club_head" in d:
        ch = np.array(d["club_head"], copy=True)
        ch[:, 0] = -ch[:, 0]
        out["club_head"] = ch
    if "landmarks" in d:
        out["landmarks"] = _mirror_landmarks(d["landmarks"])
    already = bool(d.get("mirrored", False))
    out["mirrored"] = np.array(not already)
    if not already:
        out["mirrored_from"] = np.array(source_name)
        orig = str(d.get("handedness", "right"))
        out["original_handedness"] = np.array(orig)
        out["assumed_handedness"] = np.array(orig)
        if not str(source_name).startswith(("multisense", "cmu")):
            out["player_stated_handedness"] = np.array("left")  # only Mason's files; not other subjects
        out["handedness"] = np.array("left" if orig == "right" else "right")
    else:  # un-mirror: restore
        out["handedness"] = np.array(str(d.get("original_handedness", "right")))
        out["mirrored_from"] = np.array("")
    return out


def mirror_file(src, dst=None):
    src = Path(src)
    dst = Path(dst) if dst else src.with_name(src.stem + "_mirrored.npz")
    d = {k: v for k, v in np.load(src, allow_pickle=False).items()}
    out = mirror_dict(d, src.name)
    np.savez(dst, **out)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/references")
    ap.add_argument("--pattern", default="mason_*.npz")
    a = ap.parse_args()
    n = 0
    for f in sorted(glob.glob(os.path.join(a.dir, a.pattern))):
        if f.endswith("_mirrored.npz"):
            continue
        print(mirror_file(f)); n += 1
    print(n, "files")


if __name__ == "__main__":
    main()

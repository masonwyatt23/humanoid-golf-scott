"""Camera-view / projection / noise bias check for Mason's address elbow -> data/references/mason_elbow_camera_bias.json.

Read-only analysis (no env/eval/train edits).  Run:  python -m data.mason_elbow_camera_bias [--out PATH]   (deterministic)

What the pipeline measures (read from data/process_video.py): joints col 2 = 180 - interior angle at the elbow of the
3-D MediaPipe WORLD landmarks (shoulder 12, elbow 14, wrist 16 = lead arm for a lefty).  World landmarks are metric 3-D
but monocular, so their depth axis is model-prior driven.  Hence the question is not only 2-D projection bias but also
(a) how much the depth axis contributes, (b) a positive 'folding' bias of an unsigned angle under landmark noise, and
(c) the takeaway-already-started effect.  All simulation assumptions are listed in the JSON.  Everything UNVERIFIED.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from data.mason_elbow_address_stats import clip_elbow
from data.mason_target_features import events_of

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "references" / "mason_elbow_camera_bias.json"
SH, EL, WR = 12, 14, 16
UPPER_M, FORE_M = 0.29, 0.25      # median segment lengths measured in mason_v2_p1_s03 world landmarks (one clip; assumption)
N_LM_ADDR = 4                     # first landmark frames (~0.066 s at ~60 landmark fps)


def ang(a, b, c):
    v1, v2 = a - b, c - b
    cv = np.sum(v1 * v2, -1) / (np.linalg.norm(v1, axis=-1) * np.linalg.norm(v2, axis=-1) + 1e-12)
    return np.degrees(np.arccos(np.clip(cv, -1, 1)))


def flex(a, b, c):
    return 180.0 - ang(a, b, c)


# ---------- simulation ----------
def arm_points(theta_deg, fwd_deg=10.0, hinge_tilt_deg=0.0):
    """Shoulder origin, y up, bend in the x-y plane (hinge axis = z). Upper arm hangs down, tilted forward (+x) by fwd_deg;
    forearm continues with extra flexion theta (more forward). hinge_tilt_deg rolls the whole arm about the vertical axis y?
    No: it rolls the hinge axis about the upper-arm axis (elbows flaring), i.e. rotates the bend plane."""
    f = np.radians(fwd_deg); t = np.radians(theta_deg)
    u = np.array([np.sin(f), -np.cos(f), 0.0])
    fo = np.array([np.sin(f + t), -np.cos(f + t), 0.0])
    S = np.zeros(3); E = S + UPPER_M * u; W = E + FORE_M * fo
    if hinge_tilt_deg:
        r = np.radians(hinge_tilt_deg)                      # rotate about upper-arm axis u (Rodrigues)
        K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
        R = np.eye(3) + np.sin(r) * K + (1 - np.cos(r)) * K @ K
        W = E + R @ (W - E)
    return S, E, W


def view_basis(yaw_deg):
    """Orthographic camera looking along -z (yaw 0: optical axis parallel to the hinge axis = bend plane seen face-on),
    rotated about the vertical axis by yaw_deg. Returns 2x3 projection matrix (image x, image y)."""
    y = np.radians(yaw_deg)
    ex = np.array([np.cos(y), 0.0, np.sin(y)]); ey = np.array([0.0, 1.0, 0.0])
    return np.stack([ex, ey])


def projected_flexion(theta, yaw, fwd=10.0, tilt=0.0):
    S, E, W = arm_points(theta, fwd, tilt)
    B = view_basis(yaw)
    return float(flex(B @ S, B @ E, B @ W))


def projection_table(thetas=(15, 20, 25, 30, 35, 45), yaws=(0, 15, 30, 45, 60), fwds=(0.0, 10.0, 20.0)):
    tab = {}
    for fwd in fwds:
        for th in thetas:
            tab[f"fwd{int(fwd)}_theta{th}"] = {f"yaw{y}": round(projected_flexion(th, y, fwd), 2) for y in yaws}
    return tab


def noise_fold_bias(thetas=(10, 15, 20, 25, 30, 35, 45), sigmas_m=(0.0, 0.01, 0.02, 0.03, 0.04), n=4000, seed=0):
    """Mean measured 3-D flexion when each landmark gets iid isotropic Gaussian noise (sigma metres): the unsigned angle
    is folded at 0 and biased upward for small true flexion. sigma is an ASSUMPTION (no ground truth)."""
    rng = np.random.default_rng(seed)
    out = {}
    for s in sigmas_m:
        row = {}
        for th in thetas:
            S, E, W = arm_points(th, 10.0)
            P = np.stack([S, E, W])[None] + rng.normal(0, s, (n, 3, 3))
            m = flex(P[:, 0], P[:, 1], P[:, 2])
            row[str(th)] = {"mean": round(float(m.mean()), 2), "median": round(float(np.median(m)), 2), "bias": round(float(np.median(m) - th), 2)}
        out[f"sigma_{s:.2f}m"] = row
    return out


def invert_noise_bias(measured, sigma, thetas=np.arange(0, 60.5, 0.5), n=3000, seed=1):
    rng = np.random.default_rng(seed)
    best, bd = None, 1e9
    for th in thetas:
        S, E, W = arm_points(float(th), 10.0)
        P = np.stack([S, E, W])[None] + rng.normal(0, sigma, (n, 3, 3))
        d = abs(float(np.median(flex(P[:, 0], P[:, 1], P[:, 2]))) - measured)
        if d < bd:
            best, bd = float(th), d
    return best


# ---------- per-clip data ----------
def clip_rows():
    uni = json.loads((ROOT / "data/reference_sets/unified_v2.json").read_text())
    ent = {Path(e["path"]).stem: e for e in uni["entries"]}
    kf = json.loads((ROOT / "data/references/mason_keyframe_targets.json").read_text())
    rows = {}
    for p in sorted((ROOT / "data/references").glob("mason_v[23]_*.npz")):
        n = p.stem
        if "_mirrored" in n or "refined" in n:
            continue
        d = np.load(p, allow_pickle=True)
        g = lambda a: (d[a].item() if a in d.files and d[a].ndim == 0 else None)
        r = clip_elbow(p)
        if r is None:
            continue
        e = ent.get(n, {})
        L = d["landmarks"].astype(float)
        n_l = len(L); tj = d["time"].astype(float); vmj = d["valid_mask"].astype(bool)
        t0j = float(tj[vmj][0]) if vmj.any() else float(tj[0])
        tl = np.arange(n_l) * (float(tj[-1]) / max(n_l - 1, 1))          # landmark cadence (~1/60 s), same axis as joints
        fin = np.isfinite(L[:, [SH, EL, WR], :3]).all((1, 2))
        f = np.where(fin & (tl >= t0j - 1e-9) & (tl <= t0j + 0.07))[0]
        e3 = e2 = zfrac = None
        if len(f) >= 2:
            e3 = float(np.median(flex(L[f, SH, :3], L[f, EL, :3], L[f, WR, :3])))
            e2 = float(np.median(flex(L[f, SH, :2], L[f, EL, :2], L[f, WR, :2])))
            seg = np.concatenate([L[f, EL, :3] - L[f, SH, :3], L[f, WR, :3] - L[f, EL, :3]])
            zfrac = float(np.median(np.abs(seg[:, 2]) / np.linalg.norm(seg, axis=1)))
        try:
            tk, _, _ = events_of(d, "mason")
            in_motion = bool(tk < float(d["time"][0]) - 1e-9)
            lead_s = float(max(0.0, float(d["time"][0]) - tk))
        except Exception:
            in_motion, lead_s = None, None
        t = d["time"].astype(float); el = d["joints"][:, 2].astype(float); vm = d["valid_mask"].astype(bool) & np.isfinite(el)
        w = vm & (t <= t[vm][0] + 0.25)
        slope = float(np.polyfit(t[w], el[w], 1)[0]) if w.sum() >= 5 else None
        flags = []
        if e.get("handedness_unverified") or (g("handedness_verified") is False):
            flags.append("handedness_unverified")
        if g("handedness") == "right":
            flags.append("detected_or_stated_right_handed")
        if g("mirrored"):
            flags.append("mirrored_or_flip_edit")
        if "slowmo" in n:
            flags.append("slowmo_time_stretched")
        if g("partial"):
            flags.append("partial")
        rows[n] = {"view": str(g("view")), "view_confidence": g("view_confidence"), "address_deg": r["address_deg"],
                   "early_mean_deg": r["early_mean_deg"], "elbow3d_first_landmarks_deg": e3, "elbow_xy_only_deg": e2,
                   "depth_fraction_of_arm_segments": zfrac, "address_in_motion": in_motion, "takeaway_lead_s": lead_s,
                   "elbow_slope_deg_per_s_first_0p25s": slope, "in_keyframe_stats": n in kf["clips_used"], "flags": flags,
                   "n_valid_early": r["n_early_frames"]}
    return rows


def stats(v):
    v = np.array([x for x in v if x is not None and np.isfinite(x)], float)
    if not len(v):
        return None
    return {"n": int(len(v)), "median": round(float(np.median(v)), 2), "q25": round(float(np.percentile(v, 25)), 2),
            "q75": round(float(np.percentile(v, 75)), 2), "min": round(float(v.min()), 2), "max": round(float(v.max()), 2)}


def build():
    rows = clip_rows()
    clean = {n: r for n, r in rows.items() if not r["flags"]}                       # unflagged native left, incl. non-kf clips
    per_view = {}
    for view in ("down_the_line", "oblique", "face_on"):
        for label, sel in (("unflagged_all", clean), ("keyframe_clips_only", {n: r for n, r in clean.items() if r["in_keyframe_stats"]})):
            s = {n: r for n, r in sel.items() if r["view"] == view}
            per_view.setdefault(view, {})[label] = {"clips": sorted(s), "address_deg": stats([r["address_deg"] for r in s.values()]),
                                                    "xy_only_deg": stats([r["elbow_xy_only_deg"] for r in s.values()]),
                                                    "depth_fraction": stats([r["depth_fraction_of_arm_segments"] for r in s.values()])}
    kf8 = {n: r for n, r in rows.items() if r["in_keyframe_stats"]}
    z_gap = [r["elbow3d_first_landmarks_deg"] - r["elbow_xy_only_deg"] for r in clean.values() if r["elbow_xy_only_deg"] is not None]
    # takeaway-before-axis effect (per clip: backward linear extrapolation, bounded; strongly assumption-driven)
    back = []
    for r in kf8.values():
        if r["address_in_motion"] and r["elbow_slope_deg_per_s_first_0p25s"] is not None and r["takeaway_lead_s"] is not None:
            back.append(-r["elbow_slope_deg_per_s_first_0p25s"] * r["takeaway_lead_s"])
    nf = noise_fold_bias()
    sim_proj = projection_table()
    # roll sensitivity (elbow flare)
    roll = {f"tilt{t}": {f"yaw{y}": round(projected_flexion(25, y, 10.0, t), 2) for y in (0, 30, 60)} for t in (0, 20, 40)}

    raw_med = float(np.median([r["address_deg"] for r in kf8.values()]))
    raw_q = [float(np.percentile([r["address_deg"] for r in kf8.values()], q)) for q in (25, 75)]
    # corrections (deg, added to raw): noise-fold removes upward bias; takeaway-in-motion removes extra flexion.
    sig_mid = 0.02
    corr_noise = invert_noise_bias(raw_med, sig_mid) - raw_med
    corr_noise_lo = invert_noise_bias(raw_med, 0.01) - raw_med
    corr_noise_hi = invert_noise_bias(raw_med, 0.03) - raw_med
    take_med = float(np.median(back)) if back else 0.0
    take_cl = float(np.clip(take_med, -6.0, 0.0)) if back else 0.0
    center = raw_med + corr_noise + take_cl
    half = 5.0
    lo, hi = max(center - half, 0.0), center + half
    rec = {"raw_median_deg": round(raw_med, 2), "raw_iqr_deg": [round(raw_q[0], 2), round(raw_q[1], 2)],
           "projection_bias_deg": "unquantified for the 3-D landmark angle; 2-D simulation says a pure 2-D read UNDER-states flexion (see table), so projection does NOT explain over-flexion",
           "noise_fold_correction_deg": {"sigma_0.01m": round(corr_noise_lo, 2), "sigma_0.02m": round(corr_noise, 2), "sigma_0.03m": round(corr_noise_hi, 2)},
           "takeaway_in_motion_correction_deg": round(take_cl, 2), "takeaway_in_motion_raw_estimates_deg": [round(x, 1) for x in back],
           "bias_corrected_center_deg": round(center, 1), "bias_corrected_range_deg": [round(lo, 1), round(hi, 1)],
           "bias_corrected_range_rad": [round(float(np.radians(lo)), 3), round(float(np.radians(hi)), 3)],
           "range_half_width_deg_assumed": half,
           "confidence": "low (n=8 clips, 1 mostly-DTL view, no ground truth, simulation assumptions); UNVERIFIED",
           "use": f"Plausible address-elbow support {lo:.1f}-{hi:.1f} deg ({np.radians(lo):.2f}-{np.radians(hi):.2f} rad), centre {center:.1f} deg. The raw 0.509 rad median is upper-leaning, but camera yaw is not the main reason.",
           "env_failure_floor_rad": 0.31}
    out = {
        "version": "mason_elbow_camera_bias_v1", "unverified": True,
        "question": "Is Mason's median address elbow (29.1 deg / 0.509 rad) over-flexed by camera angle?",
        "answer_short": "Probably modestly over-flexed, but not mainly because of camera yaw: the pipeline angle is 3-D (not a 2-D projection); a pure 2-D read of a hinge reads SMALLER. Likelier upward contributors are landmark-depth noise folding an unsigned angle and takeaway having already started. Mason-vs-view differences are within n=1-4 clip noise.",
        "what_pipeline_measures": "joints col 2 = 180 - angle(shoulder12, elbow14, wrist16) on 3-D MediaPipe world landmarks (data/process_video.py:167); matches landmark-recomputed 3-D angle within ~1 deg on checked clip (mason_v2_p1_s03: 31.2 vs 31.5)",
        "view_source": "npz field `view` from data/remine_feed_v2.py (shoulder/stance width ratio; thresholds set by eye on ~6 clips; docs/MASON_VIDEO_REPORT.md); NOT ground truth",
        "per_clip": rows, "per_view": per_view,
        "depth_axis_effect": {"note": "3-D landmark elbow minus xy-only (drop depth) elbow at first landmarks, unflagged clips", "stats_deg": stats(z_gap),
                              "reading": "positive = the model's depth axis ADDS flexion relative to the image plane"},
        "simulation": {
            "assumptions": ["orthographic camera, no perspective", f"segment lengths upper {UPPER_M} m, forearm {FORE_M} m (measured on ONE clip's world landmarks)",
                            "upper arm hangs forward-tilted 0/10/20 deg from vertical; bend in a single plane; hinge axis = z",
                            "yaw 0 = optical axis parallel to hinge axis (bend plane face-on); yaw = rotation about vertical",
                            "true golf-address arm geometry (flared elbows, hinge roll) varied only via the 'roll' table",
                            "noise table: iid isotropic Gaussian per landmark, sigma 0-4 cm, ASSUMED (no ground-truth noise level)"],
            "projected_2d_flexion_deg": sim_proj, "roll_sensitivity_theta25_fwd10": roll, "noise_fold_bias_3d": nf},
        "comparators_3d": {"note": "from mason_elbow_address_stats.json (3-D mocap, mirrored for comparison; MultiSense needs_counsel; statistics only)",
                           "cmu_median_deg": 22.53, "cmu_iqr_deg": [21.65, 23.80], "multisense_mirrored_note": "most clips 1-18 deg (22 clips below 18 deg); different joint-centre definitions vs MediaPipe, small n, golfers differ"},
        "takeaway_effect": {"clips_address_in_motion_of_keyframe_clips": int(sum(1 for r in kf8.values() if r["address_in_motion"])),
                            "raw_median_early_mean_minus_address_deg": round(float(np.median([r["early_mean_deg"] - r["address_deg"] for r in kf8.values()])), 2),
                            "extrapolation_method": "elbow slope over first 0.25 s x (axis start - takeaway), sign flipped; heavy assumption (linear, unobserved interval)"},
        "recommendation": rec,
        "caveats": ["No camera calibration, no ground truth elbow angle, view labels heuristic.", "Simulation conclusions follow from stated geometry only; real arms flare and bend out of plane.",
                    "Noise sigma and the +-5 deg half-width are assumptions, not measured.", "Instagram-derived footage; third-party content unreviewed."],
    }
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(OUT)); a = ap.parse_args()
    Path(a.out).write_text(json.dumps(build(), indent=1) + "\n"); print("wrote", a.out)


if __name__ == "__main__":
    main()

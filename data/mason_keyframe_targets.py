"""Mason keyframe tracking targets -> data/references/mason_keyframe_targets.json.

Run: python -m data.mason_keyframe_targets [--out PATH]      (deterministic; no timestamps in the JSON)

Source clips: unified_v2 manifest entries with source=mason, variant=native, split in {train,val}, and NOT
handedness-flagged (excludes mason_v2_p1_s11, mason_v2_p2_s10), NOT slow-mo (stretched time axis). The caption-flagged
flip-edit clip (mason_v2_p3_s09_unmirrored) is reported separately and is NOT used in the spread statistics.
All clips are left-handed native footage, so no mirroring is applied. Joint columns are the 11-column MediaPipe-derived
2-D proxies (anatomical 'right_*' = lead arm for a lefty); every angle target is therefore UNVERIFIED.

Time handling: joints/time start at the first landmark frame, NOT t_start_in_video (offset ~0.4 s); events are put on
the joint axis with data.mason_target_features.events_of (offset-corrected). Reference dt = 0.01 s; env control dt = 0.02 s.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np

from data.mason_target_features import JOINTS, events_of, mason_time_offset
from data.unified_refset import load_manifest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "references" / "mason_keyframe_targets.json"
KEYFRAMES = ["address", "top", "impact", "finish"]
SEG_N = {"address_to_top": 21, "top_to_impact": 11, "impact_to_finish": 11}
WIN_S = 0.03            # +-3 frames at dt 0.01 (about +-1 source frame at ~30 fps) median window
SIGMA_FLOOR_DEG = 8.0   # 2-D MediaPipe proxy noise + ~30 fps quantisation; spread below this is not believable
MIN_N = 4
LEG_COLS = {5, 6, 7, 8, 9, 10}
IMPACT_LOWPOINT_LAG_S = 0.067   # docs/MASON_IMPACT_GEOMETRY.md: hand low point minus impact event (median, +-0.05 s)
ENV_XML = ROOT / "env" / "models" / "humanoid_golf.xml"


def _s(d, k, default=None):
    return d[k].item() if k in d.files and d[k].ndim == 0 else default


def select_clips(version="unified_v2"):
    """(stat_clips, aux_clips): manifest entries. Stats use native, unflagged, non-slow-mo, train/val only."""
    man = load_manifest(version=version)
    stat, aux = [], []
    for e in man["entries"]:
        if e["source"] != "mason":
            continue
        flagged = e.get("exclude_pending_verification") or e.get("handedness_unverified") or e.get("split") == "excluded"
        if e["variant"] == "native" and not flagged and e.get("split") in ("train", "val") and e.get("handedness") == "left":
            stat.append(e)
        elif e["variant"] == "flip_edit_unmirrored" and not flagged:
            aux.append(e)
    return stat, aux


def settle_time(d, t_imp):
    """Finish proxy: first time after impact when summed arm-joint speed falls under 20% of its post-impact peak
    (fallback impact+0.40 s); capped at the last frame. Heuristic."""
    t = d["time"].astype(float); J = d["joints"].astype(float)
    v = np.abs(np.gradient(J[:, [0, 1, 2, 3, 4]], axis=0)).sum(1)
    k = np.convolve(v, np.ones(5) / 5, "same")
    post = np.where(t >= t_imp)[0]
    if len(post) < 5:
        return float(t[-1])
    pk = post[int(np.argmax(k[post]))]
    after = np.where((np.arange(len(t)) > pk) & (k < 0.2 * k[pk]))[0]
    ts = t[after[0]] if len(after) else t_imp + 0.40
    return float(min(max(ts, t_imp + 0.10), t[-1]))


def clip_events(d):
    tk, top, imp = events_of(d, "mason")
    t = d["time"].astype(float)
    ev = {"takeaway": tk, "top": top, "impact": imp}
    ev["address"] = float(max(t[0], tk))                 # first usable frame; in-motion if takeaway < t[0]
    ev["finish"] = settle_time(d, imp)
    ev["address_in_motion"] = bool(tk < t[0] - 1e-9)
    return ev


def pose_at(d, tq, win=WIN_S):
    """Median of valid joint rows within +-win of tq (11,), NaN where no valid row."""
    t = d["time"].astype(float); J = d["joints"].astype(float); ok = d["valid_mask"].astype(bool)
    m = (np.abs(t - tq) <= win) & ok
    if not m.any():
        return np.full(J.shape[1], np.nan), 0
    return np.median(J[m], 0), int(m.sum())


def resample_segment(d, t0, t1, n):
    t = d["time"].astype(float); J = d["joints"].astype(float)
    if t1 - t0 < 0.02:
        return None
    tt = np.linspace(t0, t1, n)
    return np.stack([np.interp(tt, t, J[:, j]) for j in range(J.shape[1])], 1)


def mad_sigma(x):
    x = x[np.isfinite(x)]
    return float(1.4826 * np.median(np.abs(x - np.median(x)))) if len(x) else float("nan")


def _yaw(p_l, p_r):
    """Horizontal-plane (x,z) angle of the L->R line, degrees; MediaPipe world axes (y = down)."""
    return np.degrees(np.arctan2(p_r[..., 2] - p_l[..., 2], p_r[..., 0] - p_l[..., 0]))


def xfactor_proxy(d, ev):
    """Monocular world-landmark proxy: (shoulder-line yaw change address->top) minus (hip-line yaw change), degrees.
    Depth (z) is model-prior-driven, so this is a LOW-confidence, view-dependent number. None if unusable."""
    if "landmarks" not in d.files:
        return None
    L = d["landmarks"].astype(float); n = len(L)
    if n < 10 or not np.isfinite(L[..., :3]).any():
        return None
    dt_l = float(d["time"][-1]) / (n - 1)               # landmark cadence (~1/60 s)
    tl = np.arange(n) * dt_l
    vis = np.minimum.reduce([L[:, 11, 3], L[:, 12, 3], L[:, 23, 3], L[:, 24, 3]])
    sh = _yaw(L[:, 11, :3], L[:, 12, :3]); hp = _yaw(L[:, 23, :3], L[:, 24, :3])

    def at(sig, tq, w=0.05):
        m = (np.abs(tl - tq) <= w) & (vis > 0.5) & np.isfinite(sig)
        if not m.any():
            return None
        a = np.unwrap(np.radians(sig[m])); return float(np.degrees(np.median(a)))
    out = {}
    for k in ("address", "top"):
        out[k] = (at(sh, ev[k]), at(hp, ev[k]))
    if any(v is None for pair in out.values() for v in pair):
        return None
    dsh = out["top"][0] - out["address"][0]; dhp = out["top"][1] - out["address"][1]
    wrap = lambda a: (a + 180) % 360 - 180
    dsh, dhp = wrap(dsh), wrap(dhp)
    return {"shoulder_turn_deg": abs(dsh), "hip_turn_deg": abs(dhp), "x_factor_proxy_deg": abs(dsh) - abs(dhp),
            "same_direction": bool(np.sign(dsh) == np.sign(dhp))}


def env_joint_limits():
    """Read-only parse of env/models/humanoid_golf.xml hinge ranges (deg), by joint name."""
    out = {}
    try:
        for m in re.finditer(r'<joint name="(\w+)"[^>]*range="(-?[\d.]+) (-?[\d.]+)"', ENV_XML.read_text()):
            out[m.group(1)] = [float(m.group(2)), float(m.group(3))]
    except OSError:
        pass
    return out


def conf_label(j, n, leg_ratio_med, sigma):
    if n < MIN_N:
        return "low"
    if j in LEG_COLS and leg_ratio_med < 0.5:
        return "low"
    if j in (1,):                      # shoulder roll: monocular depth-driven
        return "low"
    return "medium" if sigma <= 20 else "low"


def build():
    stat, aux = select_clips()
    clips = {}
    for e in stat + aux:
        d = np.load(ROOT / e["path"], allow_pickle=True)
        clips[Path(e["path"]).stem] = (e, d, clip_events(d))
    stat_names = [Path(e["path"]).stem for e in stat]
    leg_med = float(np.median([float(clips[n][1]["leg_valid_frame_ratio"]) for n in stat_names]))
    lims = env_joint_limits()

    keyframes = {}
    for k in KEYFRAMES:
        rows, per_clip = [], {}
        for n in stat_names + [Path(e["path"]).stem for e in aux]:
            e, d, ev = clips[n]
            p, nv = pose_at(d, ev[k])
            per_clip[n] = {"t_s": round(ev[k], 3), "valid_rows": nv, "joints_deg": [None if not np.isfinite(x) else round(float(x), 1) for x in p]}
            if n in stat_names:
                rows.append(p)
        R = np.array(rows)
        joints = {}
        for j, name in enumerate(JOINTS):
            col = R[:, j]; v = col[np.isfinite(col)]
            if len(v) == 0:
                joints[name] = {"n": 0, "usable": False}
                continue
            sig = mad_sigma(v)
            sig_s = float(max(sig, SIGMA_FLOOR_DEG)) if len(v) >= MIN_N else None
            med = float(np.median(v))
            lim = lims.get(name)
            joints[name] = {
                "n": int(len(v)), "median_deg": round(med, 1), "q25_deg": round(float(np.percentile(v, 25)), 1),
                "q75_deg": round(float(np.percentile(v, 75)), 1), "min_deg": round(float(v.min()), 1), "max_deg": round(float(v.max()), 1),
                "mad_sigma_deg": round(sig, 1), "sigma_suggested_deg": None if sig_s is None else round(sig_s, 1),
                "tolerance_band_deg": None if sig_s is None else [round(med - 2 * sig_s, 1), round(med + 2 * sig_s, 1)],
                "usable": bool(len(v) >= MIN_N), "confidence": conf_label(j, len(v), leg_med, sig),
                "unverified": True, "env_limit_deg": lim,
                "outside_env_limit": None if lim is None else bool(med < lim[0] or med > lim[1]),
            }
        keyframes[k] = {"definition": {
            "address": "first usable joint frame (takeaway if it falls inside the axis); median of valid rows within +-0.03 s. 'address_in_motion' per clip flags clips whose takeaway precedes the axis start",
            "top": "t_top event (landmark-inferred), offset-corrected", "impact": "t_impact event (landmark-inferred; EARLY vs hand low point by ~0.067 s, +-0.05 s)",
            "finish": "arm-speed settle heuristic after impact (<20% of post-impact peak), capped at last frame"}[k],
            "joints": joints, "per_clip": per_clip}

    # phase-normalised templates
    templates = {}
    for seg, n in SEG_N.items():
        a, b = seg.split("_to_")
        stack = []
        for nm in stat_names:
            _, d, ev = clips[nm]
            r = resample_segment(d, ev[a], ev[b], n)
            if r is not None:
                stack.append(r)
        S = np.array(stack)  # clips x n x 11
        med = np.nanmedian(S, 0)
        sg = np.array([[max(mad_sigma(S[:, i, j]), SIGMA_FLOOR_DEG) for j in range(S.shape[2])] for i in range(n)])
        templates[seg] = {"n_points": n, "n_clips": int(len(stack)), "phase": [round(float(x), 4) for x in np.linspace(0, 1, n)],
                          "median_deg": {JOINTS[j]: [round(float(x), 1) for x in med[:, j]] for j in range(11)},
                          "sigma_deg": {JOINTS[j]: [round(float(x), 1) for x in sg[:, j]] for j in range(11)}}

    # timing
    tr, bs, ds, imp_off = [], [], [], []
    for nm in stat_names:
        e, d, ev = clips[nm]
        bsw, dsw = ev["top"] - ev["takeaway"], ev["impact"] - ev["top"]
        if dsw > 0:
            tr.append(bsw / dsw)
        bs.append(bsw); ds.append(dsw)
    q = lambda x: {"median": round(float(np.median(x)), 3), "q25": round(float(np.percentile(x, 25)), 3),
                   "q75": round(float(np.percentile(x, 75)), 3), "min": round(float(np.min(x)), 3), "max": round(float(np.max(x)), 3), "n": len(x)}
    tempo = {"tempo_ratio": q(tr), "backswing_s_video_time": q(bs), "downswing_s_video_time": q(ds),
             "tempo_ratio_recommended_band": [round(float(np.percentile(tr, 25)), 2), round(float(np.percentile(tr, 75)), 2)],
             "relative_uncertainty": "~0.27 median per swing (downswing only 4-6 source frames at ~30 fps; mason_target_features.json)",
             "caveat": "Absolute seconds come from edited/possibly sped-up feed clips and ~30 fps; a 0.48 s backswing is implausibly short. Trust the ratio band, not the seconds. NOT a speed target."}

    xf = {nm: xfactor_proxy(clips[nm][1], clips[nm][2]) for nm in stat_names}
    xv = [v["x_factor_proxy_deg"] for v in xf.values() if v]
    xfs = {"per_clip": xf, "n_usable": len(xv),
           "x_factor_proxy_deg": ({"median": round(float(np.median(xv)), 1), "q25": round(float(np.percentile(xv, 25)), 1),
                                   "q75": round(float(np.percentile(xv, 75)), 1), "min": round(float(min(xv)), 1), "max": round(float(max(xv)), 1)} if xv else None),
           "confidence": "low", "unverified": True,
           "caveat": ("Shoulder-line yaw minus hip-line yaw change (address->top) from monocular MediaPipe world landmarks; depth is model-prior-driven and "
                      "every non-flagged clip is down-the-line/oblique (the only face-on clip is the handedness-flagged p1_s11). Treat as an order-of-magnitude "
                      "plausibility check only, NOT a target. Real X-factor needs the two-view 240 fps capture (docs/FILMING_PROTOCOL.md).")}

    # recommended sigmas (one per joint, pooled over keyframes) and reward form
    sig_pool = {j: round(float(np.median([keyframes[k]["joints"][j]["sigma_suggested_deg"] for k in KEYFRAMES
                                          if keyframes[k]["joints"][j].get("sigma_suggested_deg")] or [float("nan")])), 1) for j in JOINTS}
    reward = {
        "sparse_keyframe": {
            "form": "r_key = (1/K) * sum_k exp( - mean_j [ (q_j(t_k) - mu_jk) / (s * sigma_jk) ]^2 ),  K = {top, impact, finish}",
            "note_form": "Equivalent to exp(-err^2/sigma^2) per joint when joints are averaged inside the exponent; use joints with usable=true and confidence != low first (arm columns 0,2,3,4).",
            "sigma_jk": "keyframes[k].joints[j].sigma_suggested_deg (max of clip MAD-sigma and the 8 deg floor)", "s_curriculum": "start s=2.0 (loose), anneal to 1.0 as r_key rises; s<1 is not supported by this data",
            "event_detection": "script-free: top = argmax lead-arm shoulder excursion; impact = hand/club low point MINUS 0.067 s (+-0.05) to match the landmark-inferred impact event; finish = arm-speed settle",
            "address": "do NOT reward address pose (video axis begins at/after takeaway in most clips); use it only as an initial-state prior",
            "excluded_joints": "ankles/hips/knees: low leg_valid_frame_ratio and zero-filled where invalid; also hip pitch exceeds env limits. Give legs weight ~0 until the env limits and leg data are resolved"},
        "windowed_dense": {
            "form": "r_dense = exp( - mean_{t in window, j} [ (q_j(t) - template_j(phi(t))) / (s * sigma_j(phi)) ]^2 ), window = +-0.06 s around each event",
            "templates": "templates.* (phase-normalised, median and sigma per point)",
            "why_windowed": "whole-swing dense tracking over-penalises timing drift that the 30 fps data cannot resolve (+-0.05 s); windows around events keep the signal where the data is informative"},
        "suggested_sigma_deg_pooled_per_joint": sig_pool,
        "weights": "r_track = 0.6 * r_key + 0.4 * r_dense; add to the task reward with a coefficient chosen so r_track spread across policies is comparable to the carry/dispersion term (the current term does not move the swing; see doc)",
        "time_indexing": "index templates by simulated time through phase phi(t) (events in sim time), never by env step: reference dt 0.01 s vs env control dt 0.02 s plays 2x fast otherwise (docs/REFSET_TIMING_AUDIT.md)"}

    n_out = sum(1 for k in KEYFRAMES for j in JOINTS if keyframes[k]["joints"][j].get("outside_env_limit"))
    out = {
        "version": "mason_keyframes_v1", "source_set": "unified_v2", "handedness": "left (native; no mirroring)",
        "joint_columns": JOINTS, "units": "degrees; times in seconds on the joint-time axis (dt 0.01 s)",
        "clips_used": stat_names, "clips_aux_not_in_stats": [Path(e["path"]).stem for e in aux],
        "clips_excluded": {"mason_v2_p1_s11": "handedness unverified (detected right, val)", "mason_v2_p2_s10": "handedness unverified (train)",
                           "mason_v3_p2_s03_slowmo": "stretched video time axis (~3-6x), unconfirmed handedness", "mirrored copies": "not needed (native left)"},
        "view_mix": {Path(e["path"]).stem: e["view"] for e in stat},
        "event_offsets_s": {nm: {"joint_axis_offset_s": round(mason_time_offset(clips[nm][1]), 3), **{k: round(clips[nm][2][k], 3) for k in ("takeaway", "top", "impact", "finish")},
                                  "address_in_motion": clips[nm][2]["address_in_motion"]} for nm in stat_names + [Path(e["path"]).stem for e in aux]},
        "keyframes": keyframes, "templates": templates, "tempo": tempo, "x_factor_proxy_at_top": xfs, "reward_recommendation": reward,
        "impact_lowpoint_lag_s": IMPACT_LOWPOINT_LAG_S,
        "n_keyframe_medians_outside_env_limits": n_out,
        "caveats": [
            "All joint angles are 2-D MediaPipe proxies (~30 fps feed screen recordings, mostly down-the-line); view-dependent, UNVERIFIED, not 3-D humanoid joint angles.",
            "Small n (see clips_used); sigma = max(MAD-sigma, 8 deg floor). The spread is across clips and views, not a measurement uncertainty.",
            "Impact is landmark-inferred, early vs the hand low point by ~0.067 s (+-0.05 s); events are +-1 frame (~33 ms).",
            "Mason's 120+ mph is self-reported; nothing here is a speed target.",
            "Instagram-derived: third-party content in the source recordings was never reviewed (see docs/RELEASE_QUESTIONS_FOR_COUNSEL.md)."],
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = build()
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=False) + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()

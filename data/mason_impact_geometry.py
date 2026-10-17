"""Impact-geometry DIAGNOSTIC targets from the references -> data/references/mason_impact_geometry_targets.json.

Run: python -m data.mason_impact_geometry [--refs data/references] [--out PATH] [--cmu-bvh DIR]
Deterministic: no wall-clock values; bootstrap CIs use a fixed seed.

WHAT THIS IS (and is not)
  * Hand path, a hand-forward proxy for shaft lean, and a low-point-timing proxy at the impact event, derived
    from single-view MediaPipe WORLD landmarks (hip-centred, monocular, ~30 unique fps) of Mason's feed clips.
  * There is NO club data anywhere in Mason's files. Shaft lean is NOT measured. Only hand-forward / lead-arm
    line lean proxies exist. Launch angle (and dynamic loft, attack angle, face angle) is NOT derivable: it needs a
    launch monitor or club tracking. Nothing here is a launch angle.
  * Everything depends on camera view (down_the_line / oblique / face_on). Each swing is weighted by view and
    quality and carries explicit uncertainties; unmeasurable fields are the string "unavailable".

Conventions (all Mason features are handedness-invariant: defined by LEAD / TRAIL side, not left/right)
  * Lengths are divided by torso length = |mid-shoulder - mid-hip| (median over the window): unitless "torso".
  * Frame per swing: origin = mid-hip (per frame); up = -y (MediaPipe world y points down);
    tgt = unit address hip-line direction (trail hip -> lead hip) in the image-x/depth-z plane (square stance =>
    toward target); oth = (-tgt_z, tgt_x) (sign arbitrary).  face-on: tgt ~ image x; down-the-line: tgt ~ depth z
    (monocular depth is the least reliable axis) => forward proxies are down-weighted for DTL.
  * Hand = midpoint of the two wrists (landmarks 15/16), NOT the grip centre and not the club.
  * Landmark time alignment: the stored landmarks are trimmed at the start, so their time offset vs the swing
    time axis is recovered per file by cross-correlating wrist height with the stored `hands_px` track.
    Files whose alignment correlation is < 0.9 are rejected.
  * Impact = the file's t_impact event (heuristic, +-1 source frame). Low point = time of minimum hand height in
    [top, min(impact + 0.20 s, end)].
"""
import argparse, glob, json, os
import numpy as np
from scipy.signal import savgol_filter

UNAVAIL = "unavailable"
LM_FPS = 60.0
SRC_FPS = 30.0
SEED = 0
NPATH = 21                       # samples of the takeaway->impact path
LOWPOINT_AFTER_IMPACT_S = 0.20
VIEW_W_VERT = {"down_the_line": 1.0, "oblique": 1.0, "face_on": 1.0}      # height/timing: ~view independent
VIEW_W_FWD = {"face_on": 1.0, "oblique": 0.6, "down_the_line": 0.4}       # forward = depth for DTL: weak
SH_L, SH_R, WR_L, WR_R, HIP_L, HIP_R = 11, 12, 15, 16, 23, 24
LICENSE = {"mason": "self_owned (Mason's own swings, Instagram screen recordings; confirm no third-party content)",
           "cmu": "needs_counsel / commercial_ok=False (CMU Graphics Lab mocap, subject 64; retagged 2026-10, published terms allow commercial products but no resale even converted; counsel item; no standalone "
                  "redistribution; acknowledgment text required)",
           "synthetic": "synthetic (generated, commercial_ok)"}
CMU_ACK = ("The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with "
           "funding from NSF EIA-0196217.")


# ----------------------------------------------------------------------------- small helpers
def _s(d, k, default=None):
    return d[k].item() if k in d.files else default


def _interp_nan(x, t):
    """Linear interpolation over NaN (edges held). Returns (filled, finite_fraction)."""
    x = np.asarray(x, float).copy()
    m = np.isfinite(x)
    if m.sum() < 2:
        return x, float(m.mean()) if x.size else 0.0
    x[~m] = np.interp(t[~m], t[m], x[m])
    return x, float(m.mean())


def _smooth(x, fps, window_s=0.10):
    w = int(round(window_s * fps)) | 1
    w = max(5, w)
    if len(x) < w:
        return x
    return savgol_filter(x, w, 2, axis=0, mode="interp")


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _circ_std_deg(angles_rad):
    c, s = np.mean(np.cos(angles_rad)), np.mean(np.sin(angles_rad))
    r = float(np.hypot(c, s))
    return float(np.degrees(np.sqrt(max(0.0, -2 * np.log(max(r, 1e-9))))))


def _wmedian(v, w):
    v, w = np.asarray(v, float), np.asarray(w, float)
    o = np.argsort(v); c = np.cumsum(w[o])
    return float(v[o][np.searchsorted(c, c[-1] / 2)])


def _num(x):
    return isinstance(x, (int, float, np.floating)) and x is not None and np.isfinite(x)


# ----------------------------------------------------------------------------- core geometry (source agnostic)
def geometry_features(t, hand, hip_c, sh_c, lead_sh, lead_wr, tgt, ev, *, up_axis, address_n):
    """All inputs in a common metric frame. t (n,), points (n,3) in world axes; `up_axis`: unit vec (3,);
    tgt: unit horizontal target-direction vector (3,); ev = (takeaway, top, impact) in t's axis.
    Returns dict of proxies (torso units) or None if the window is unusable."""
    tk, top, imp = ev
    up = _unit(up_axis)
    tg = _unit(tgt - np.dot(tgt, up) * up)
    ot = np.cross(up, tg)
    torso = float(np.nanmedian(np.linalg.norm(sh_c - hip_c, axis=1)))
    if not np.isfinite(torso) or torso < 1e-3:
        return None

    def comp(P):
        R = (P - hip_c) / torso
        return np.stack([R @ tg, R @ up, R @ ot], 1)       # columns: tgt, up, oth

    H = comp(hand)
    ls = comp(lead_sh); lw = comp(lead_wr)
    # lead arm line lean: shoulder->wrist in (tgt, up) plane, 0 = vertical, + = wrist toward target
    dv = lw - ls
    lean = np.degrees(np.arctan2(dv[:, 0], -dv[:, 1]))
    a0 = np.arange(len(t)) < address_n
    out = {"torso_length_world": torso}
    ok_addr = address_n >= 4
    H0 = np.nanmedian(H[a0], 0) if ok_addr else None

    def at(sig, tq):
        return np.array([np.interp(tq, t, sig[:, k]) for k in range(sig.shape[1])]) if sig.ndim == 2 else float(np.interp(tq, t, sig))

    Ht, Hi = at(H, top), at(H, imp)
    out["hand_up_at_top"], out["hand_up_at_impact"] = float(Ht[1]), float(Hi[1])
    out["hand_tgt_at_top"], out["hand_tgt_at_impact"] = float(Ht[0]), float(Hi[0])
    out["hand_oth_at_impact"] = float(Hi[2])
    out["lead_arm_lean_at_impact_deg"] = float(at(lean, imp))
    if ok_addr:
        out["hand_up_at_address"] = float(H0[1])
        out["hand_tgt_at_address"] = float(H0[0])
        out["hand_forward_vs_address_at_impact"] = float(Hi[0] - H0[0])
        out["lead_arm_lean_at_address_deg"] = float(np.nanmedian(lean[a0]))
        out["lead_arm_lean_delta_deg"] = out["lead_arm_lean_at_impact_deg"] - out["lead_arm_lean_at_address_deg"]
        out["hand_height_gain_top_vs_address"] = float(Ht[1] - H0[1])
    else:
        for k in ("hand_up_at_address", "hand_tgt_at_address", "hand_forward_vs_address_at_impact",
                  "lead_arm_lean_at_address_deg", "lead_arm_lean_delta_deg", "hand_height_gain_top_vs_address"):
            out[k] = UNAVAIL
    out["address_frames_used"] = int(address_n)
    # low point of hands after the top
    hi_t = min(t[-1], imp + LOWPOINT_AFTER_IMPACT_S)
    m = (t >= top) & (t <= hi_t)
    if m.sum() >= 4:
        idx = np.where(m)[0]
        j = idx[int(np.argmin(H[m, 1]))]
        out["low_point_t_minus_impact_s"] = float(t[j] - imp)
        out["low_point_frac_of_downswing"] = float((t[j] - top) / (imp - top)) if imp > top else UNAVAIL
        out["hand_up_at_low_point"] = float(H[j, 1])
        out["low_point_at_window_edge"] = bool(j in (idx[0], idx[-1]))
        out["hand_tgt_at_low_point"] = float(H[j, 0])
    else:
        for k in ("low_point_t_minus_impact_s", "low_point_frac_of_downswing", "hand_up_at_low_point",
                  "hand_tgt_at_low_point"):
            out[k] = UNAVAIL
        out["low_point_at_window_edge"] = UNAVAIL
    # hand speed (torso/s): peak, and time of peak vs impact
    spd = np.linalg.norm(np.gradient(H, t, axis=0), axis=1)
    mm = (t >= top) & (t <= min(t[-1], imp + 0.10))
    if mm.sum() >= 3:
        idx = np.where(mm)[0]; j = idx[int(np.argmax(spd[mm]))]
        out["peak_hand_speed_torso_per_s"] = float(spd[j])
        out["peak_hand_speed_t_minus_impact_s"] = float(t[j] - imp)
        out["hand_speed_at_impact_torso_per_s"] = float(np.interp(imp, t, spd))
    # normalised hand path (tgt, up, oth), takeaway -> impact, NPATH samples; 0 = takeaway, 1 = impact
    ph = np.linspace(0, 1, NPATH)
    tq = tk + ph * (imp - tk)
    P = np.stack([np.interp(tq, t, H[:, k]) for k in range(3)], 1)
    if H0 is not None:
        P = P - H0     # relative to address hand position -> removes address posture differences
        out["path_reference"] = "relative_to_address_hand_position"
    else:
        out["path_reference"] = "relative_to_hip_centre_only (address window too short)"
    out["hand_path"] = {"phase": ph.tolist(), "tgt": P[:, 0].tolist(), "up": P[:, 1].tolist(), "oth": P[:, 2].tolist()}
    return out


# ----------------------------------------------------------------------------- Mason
def _align_offset(d):
    """Seconds (swing time axis, t=0 at t_start_in_video) of landmark frame 0. (offset, corr)."""
    L = d["landmarks"].astype(float)
    n = len(L)
    hp = d["hands_px"].astype(float)
    W = L[:, [WR_L, WR_R], 1]
    cnt = np.isfinite(W).sum(1)
    wy = np.where(cnt > 0, np.nansum(W, 1) / np.maximum(cnt, 1), np.nan) if cnt.any() else None
    if wy is None:
        return None, 0.0
    t0 = float(d["t_start_in_video"])
    tv, hy = hp[:, 0] - t0, hp[:, 2]
    f = np.isfinite(hy)
    if f.sum() < 10:
        return None, 0.0
    best = (-2.0, None)
    for off in np.arange(-0.25, 1.5, 1.0 / LM_FPS):
        tt = off + np.arange(n) / LM_FPS
        m = np.isfinite(wy) & (tt >= tv[f][0]) & (tt <= tv[f][-1])
        if m.sum() < 30:
            continue
        h = np.interp(tt[m], tv[f], hy[f])
        c = np.corrcoef(h, wy[m])[0, 1]
        if np.isfinite(c) and c > best[0] + 1e-12:
            best = (float(c), float(off))
    return best[1], best[0]


def mason_swing(path):
    d = np.load(path, allow_pickle=True)
    name = os.path.basename(path)
    base = {"file": name, "view": str(d["view"]), "quality_score": float(d["quality_score"]),
            "handedness_verified": bool(_s(d, "handedness_verified", False)),
            "view_confidence": float(_s(d, "view_confidence", 0.0)),
            "slow_motion": bool(_s(d, "slow_motion", False)),
            "origin": "unmirrored_flipped_edit" if name.endswith("_unmirrored.npz") else "native"}
    off, corr = _align_offset(d)
    base["landmark_time_offset_s"] = off if off is None else float(off)
    base["alignment_corr"] = float(corr)
    if off is None or corr < 0.9:
        base["status"] = "rejected: landmark/time alignment unreliable"
        return base, None
    L = d["landmarks"].astype(float)
    n = len(L)
    t = off + np.arange(n) / LM_FPS
    t0 = float(d["t_start_in_video"])
    tk, top, imp = float(d["t_takeaway"]) - t0, float(d["t_top"]) - t0, float(d["t_impact"]) - t0
    sl_k = 1.0
    if base["slow_motion"]:
        sl_k = float(d["slowdown_factor_est"])
    win = (t >= tk - 0.05) & (t <= imp + LOWPOINT_AFTER_IMPACT_S + 0.05)
    need = [SH_L, SH_R, HIP_L, HIP_R, WR_L, WR_R]
    fin = {}
    for k in need:
        arr = L[:, k, :3]
        filled = np.stack([_interp_nan(arr[:, c], t)[0] for c in range(3)], 1)
        fin[k] = (filled, float(np.isfinite(arr[win, 0]).mean()) if win.any() else 0.0)
    cover = min(fin[k][1] for k in need)
    base["landmark_coverage_window"] = float(cover)
    # swing window must lie inside the landmark span
    if t[0] > top - 0.05 or t[-1] < imp:
        base["status"] = "rejected: landmarks do not cover top..impact"
        return base, None
    if cover < 0.7:
        base["status"] = f"rejected: key-landmark coverage {cover:.2f} < 0.70 in takeaway..impact window"
        return base, None
    P = {k: _smooth(fin[k][0], LM_FPS) for k in need}
    hand = 0.5 * (P[WR_L] + P[WR_R])
    hip_c = 0.5 * (P[HIP_L] + P[HIP_R]); sh_c = 0.5 * (P[SH_L] + P[SH_R])
    lefty = str(d["handedness"]) == "left"
    lead_hip, trail_hip = (P[HIP_R], P[HIP_L]) if lefty else (P[HIP_L], P[HIP_R])
    lead_sh, lead_wr = (P[SH_R], P[WR_R]) if lefty else (P[SH_L], P[WR_L])
    # Address window: frames before takeaway; fall back to the first frames if the file starts late
    na = int(np.sum(t <= tk))
    axis_note = "address window = frames before takeaway"
    ax_n = na
    if na < 4:
        ax_n = 6
        axis_note = "landmarks start at/after takeaway: target axis from first 6 frames; address features unavailable"
    ax_n = min(ax_n, n)
    hv = (lead_hip - trail_hip)[:ax_n]
    hv_xz = hv[:, [0, 2]]
    ang = np.arctan2(hv_xz[:, 1], hv_xz[:, 0])
    ax_dir = np.array([np.median(hv_xz[:, 0]), 0.0, np.median(hv_xz[:, 1])])
    ax_dir = _unit(ax_dir)
    axis_std = _circ_std_deg(ang)
    up = np.array([0.0, -1.0, 0.0])
    ev = (tk, top, imp)
    f = geometry_features(t, hand, hip_c, sh_c, lead_sh, lead_wr, ax_dir, ev, up_axis=up, address_n=na if na >= 4 else 0)
    if f is None:
        base["status"] = "rejected: degenerate torso length"
        return base, None
    base.update({"status": "ok", "target_axis_xz": [float(ax_dir[0]), float(ax_dir[2])],
                 "target_axis_angle_vs_image_x_deg": float(np.degrees(np.arctan2(abs(ax_dir[2]), abs(ax_dir[0])))),
                 "target_axis_dir_std_deg": axis_std, "axis_note": axis_note})
    # uncertainty (1 frame at the real source rate on the impact event + 1 sample)
    q = (1.0 / SRC_FPS) / sl_k
    base["low_point_t_uncertainty_s"] = float(q + 1.0 / LM_FPS / sl_k)
    if base["slow_motion"]:
        # time-valued features are in VIDEO seconds for slow-mo clips; add real-time estimates (+-2x factor)
        base["slowdown_factor_est"] = sl_k
        for k in ("low_point_t_minus_impact_s", "peak_hand_speed_t_minus_impact_s"):
            if _num(f.get(k)):
                f[k + "_real_est"] = f[k] / sl_k
    f_clean = {k: v for k, v in f.items()}
    base.update(f_clean)
    # weights
    vw_v = VIEW_W_VERT.get(base["view"], 0.5); vw_f = VIEW_W_FWD.get(base["view"], 0.3)
    axis_rel = 1.0 / (1.0 + axis_std / 20.0)
    # does the inferred target axis agree with the labelled view? face_on -> axis ~ image x (0 deg from x),
    # down_the_line -> ~ depth (90 deg), oblique -> ~45. Monocular depth often smears DTL axes (observed 40-60 deg).
    expected = {"face_on": 0.0, "oblique": 45.0, "down_the_line": 90.0}.get(base["view"], 45.0)
    agree = max(0.0, 1.0 - abs(base["target_axis_angle_vs_image_x_deg"] - expected) / 45.0)
    base["view_axis_agreement"] = float(agree)
    qual = base["quality_score"] * cover
    base["weight_raw_vertical_timing"] = float(qual * vw_v)
    base["weight_raw_forward"] = float(qual * vw_f * axis_rel * agree * (1.0 if na >= 4 else 0.0))
    return base, f


# ----------------------------------------------------------------------------- CMU (true 3D, same definitions)
def cmu_swing(bvh_path):
    from data import convert_cmu_mocap as cm
    b = cm.parse_bvh(bvh_path)
    fps = 1.0 / b.frame_time
    pos = cm.forward_kinematics(b)
    P = {nm: pos[:, i] for i, nm in enumerate(b.names)}
    hand = cm.detect_handedness(b, P)
    c = cm.compute_joints(P, fps, hand)
    ev = cm.detect_events(c["hands"], fps)
    n = len(c["hip_c"])
    i0 = max(0, ev["takeaway"] - int(0.25 * fps)); i1 = min(n - 1, ev["finish"] + int(0.25 * fps))
    sl = slice(i0, i1 + 1)
    t = np.arange(i1 - i0 + 1) / fps
    T, Ld = ("R", "L") if hand == "right" else ("L", "R")
    lead_sh, lead_wr = P[cm.SIDE[Ld]["sh"]][sl], P[cm.SIDE[Ld]["wr"]][sl]
    wrs = 0.5 * (P["RightHand"] + P["LeftHand"])
    hands = c["hands"][sl]
    hip_c, sh_c = c["hip_c"][sl], c["sh_c"][sl]
    sm = lambda x: _smooth(x, fps)
    hands, hip_c, sh_c, lead_sh, lead_wr = map(sm, (hands, hip_c, sh_c, lead_sh, lead_wr))
    na = max(1, ev["takeaway"] - i0)
    tgt = c["pel_line"][sl][:na].mean(0)
    tgt[1] = 0.0
    evs = ((ev["takeaway"] - i0) / fps, (ev["top"] - i0) / fps, (ev["impact"] - i0) / fps)
    f = geometry_features(t, hands, hip_c, sh_c, lead_sh, lead_wr, tgt, evs, up_axis=np.array([0, 1.0, 0]),
                          address_n=na)
    rec = {"file": os.path.basename(str(bvh_path)).replace(".bvh", ""), "handedness": hand}
    rec.update(f or {})
    return rec, f


def cmu_block(refs, bvh_dir):
    files = sorted(glob.glob(os.path.join(bvh_dir, "64_*.bvh"))) if bvh_dir and os.path.isdir(bvh_dir) else []
    per = []
    for p in files:
        stem = os.path.basename(p)[:-4]
        npz = os.path.join(refs, f"cmu_{stem}.npz")
        if os.path.exists(npz):
            dd = np.load(npz, allow_pickle=True)
            if not bool(dd["commercial_ok"]):
                continue
        try:
            rec, f = cmu_swing(p)
        except Exception as e:      # pragma: no cover - raw conversion issues are reported, not hidden
            per.append({"file": stem, "status": f"failed: {e}"}); continue
        if f is None:
            continue
        rec["status"] = "ok"
        per.append(rec)
    if not per:
        return {"status": UNAVAIL, "reason": "raw BVH not present (data/raw_mocap/cmu is gitignored; re-download per "
                "docs/CMU_MOCAP_GOLF.md and pass --cmu-bvh). Last committed values live in this JSON."}
    return {"status": "ok", "n_swings": len([p for p in per if p.get("status") == "ok"]),
            "license": LICENSE["cmu"], "acknowledgment_text": CMU_ACK, "commercial_ok": False,
            "frame": "TRUE 3-D (not view-limited); same definitions: tgt = address hip line, up = world Y",
            "caveats": ["Slow recreational volunteer (tempo ~1.7), right-handed; features are lead/trail-defined so "
                        "handedness-invariant. Wrist midpoint, no club."],
            "per_swing": per, "aggregate": aggregate([p for p in per if p.get("status") == "ok"])}


# ----------------------------------------------------------------------------- synthetic
def synthetic_block(refs):
    per = []
    for p in sorted(glob.glob(os.path.join(refs, "*_swing.npz"))):
        if "mason" in p or "cmu" in p:
            continue
        d = np.load(p, allow_pickle=True)
        if "club_head" not in d.files or not bool(_s(d, "commercial_ok", False)):
            continue
        t = d["time"].astype(float); top, imp = (float(v) for v in d["events"])
        z = d["club_head"][:, 2]
        m = (t >= top) & (t <= min(t[-1], imp + LOWPOINT_AFTER_IMPACT_S))
        j = np.where(m)[0][int(np.argmin(z[m]))]
        per.append({"file": os.path.basename(p), "style": str(d["style"]),
                    "club_head_low_point_t_minus_impact_s": float(t[j] - imp),
                    "tempo_ratio": float(d["tempo_ratio"])})
    return {"n_swings": len(per), "license": LICENSE["synthetic"], "per_swing": per,
            "hand_path": UNAVAIL, "shaft_lean_proxy": UNAVAIL,
            "caveat": "Generator is a planar joint-angle model with an analytic club-head; stores no hand positions. "
                      "Low point shown is CLUB-HEAD vertical minimum in [top, impact+0.2s] and is a by-construction "
                      "artefact (the model has no ball/ground contact), only a sanity reference."}


# ----------------------------------------------------------------------------- aggregation
SCALARS = ["hand_up_at_address", "hand_up_at_top", "hand_up_at_impact", "hand_height_gain_top_vs_address",
           "hand_tgt_at_top", "hand_tgt_at_impact", "hand_forward_vs_address_at_impact",
           "lead_arm_lean_at_address_deg", "lead_arm_lean_at_impact_deg", "lead_arm_lean_delta_deg",
           "low_point_t_minus_impact_s", "low_point_frac_of_downswing", "hand_up_at_low_point",
           "peak_hand_speed_torso_per_s", "peak_hand_speed_t_minus_impact_s", "hand_speed_at_impact_torso_per_s"]
FORWARD = {"hand_tgt_at_top", "hand_tgt_at_impact", "hand_forward_vs_address_at_impact",
           "lead_arm_lean_at_address_deg", "lead_arm_lean_at_impact_deg", "lead_arm_lean_delta_deg",
           "hand_tgt_at_low_point"}


def _stat(vals, weights=None, boot=500):
    pairs = [(float(v), 1.0 if weights is None else float(w)) for v, w in
             zip(vals, weights if weights is not None else [1] * len(vals)) if _num(v)]
    if not pairs:
        return {"n": 0, "median": UNAVAIL}
    v = np.array([p[0] for p in pairs]); w = np.array([p[1] for p in pairs])
    if w.sum() <= 0:
        w = np.ones_like(w)
    out = {"n": int(v.size), "median": float(np.median(v)), "weighted_median": _wmedian(v, w),
           "iqr": [float(x) for x in np.percentile(v, [25, 75])], "min": float(v.min()), "max": float(v.max())}
    if v.size >= 4:
        rng = np.random.default_rng(SEED)
        bs = []
        for _ in range(boot):
            ii = rng.integers(0, v.size, v.size)
            bs.append(_wmedian(v[ii], w[ii]))
        out["weighted_median_ci90_bootstrap"] = [float(x) for x in np.percentile(bs, [5, 95])]
    out["n_eff"] = float(w.sum() ** 2 / (w ** 2).sum())
    return out


def aggregate(per, wkey_v=None, wkey_f=None):
    ag = {}
    for k in SCALARS + ["hand_tgt_at_low_point"]:
        vals = [p.get(k) for p in per]
        if wkey_v:
            w = [p.get(wkey_f if k in FORWARD else wkey_v, 0.0) for p in per]
            ag[k] = _stat(vals, w)
        else:
            ag[k] = _stat(vals)
    # path: per-phase weighted median for each axis
    if per and "hand_path" in per[0]:
        paths = {"phase": per[0]["hand_path"]["phase"]}
        for ax in ("tgt", "up", "oth"):
            M = np.array([p["hand_path"][ax] for p in per if "hand_path" in p])
            if wkey_v:
                w = np.array([p.get(wkey_f if ax != "up" else wkey_v, 0.0) for p in per if "hand_path" in p])
                w = w if w.sum() > 0 else np.ones(len(M))
            else:
                w = np.ones(len(M))
            paths[ax + "_weighted_median"] = [_wmedian(M[:, i], w) for i in range(M.shape[1])]
            paths[ax + "_iqr_lo"] = np.percentile(M, 25, 0).tolist()
            paths[ax + "_iqr_hi"] = np.percentile(M, 75, 0).tolist()
        ag["hand_path"] = paths
    return ag


# ----------------------------------------------------------------------------- build
def select(refs):
    """v2 selection identical to data.mason_target_features.select_mason, plus recommended native-left v3 slow-mo."""
    from data.mason_target_features import select_mason
    sel = [p for p, _, _ in select_mason(refs)]
    v3 = []
    for p in sorted(glob.glob(os.path.join(refs, "mason_v3_*_slowmo.npz"))):
        d = np.load(p, allow_pickle=True)
        if (bool(d["recommended"]) and bool(d["commercial_ok"]) and str(d["handedness"]) == "left"
                and bool(d["native_footage"]) and not bool(d["mirrored"]) and not bool(d["partial"])):
            v3.append(p)
    return sel, v3


def build(refs="data/references", cmu_bvh="data/raw_mocap/cmu"):
    sel, v3 = select(refs)
    per, rejected = [], []
    for p in sel + v3:
        rec, f = mason_swing(p)
        (per if f is not None else rejected).append(rec)
    for p in per:
        p["weight_vertical_timing"] = None; p["weight_forward"] = None
    for key, src in (("weight_vertical_timing", "weight_raw_vertical_timing"), ("weight_forward", "weight_raw_forward")):
        v2 = [p for p in per if not p["slow_motion"]]
        tot = sum(p[src] for p in v2) or 1.0
        for p in per:
            p[key] = p[src] / tot if not p["slow_motion"] else None
    v2s = [p for p in per if not p["slow_motion"]]
    v3s = [p for p in per if p["slow_motion"]]
    agg = aggregate(v2s, "weight_vertical_timing", "weight_forward")
    views = {}
    for p in v2s:
        views[p["view"]] = views.get(p["view"], 0) + 1
    out = {
        "schema": "mason_impact_geometry_targets/v1",
        "purpose": "DIAGNOSTIC proxies for reward shaping / evaluation. Not measured club or ball data.",
        "units": {"lengths": "torso lengths (|mid-shoulder - mid-hip|, unitless), hip-centred",
                  "time": "seconds in real video time (v2 clips); slow-mo clips in VIDEO seconds with *_real_est",
                  "angles": "degrees", "axes": "tgt = toward target (address hip line), up = vertical, oth = lateral (sign arbitrary)"},
        "field_definitions": {
            "hand_up_at_{address,top,impact}": "mid-wrist height above mid-hip / torso",
            "hand_tgt_at_*": "mid-wrist position along the target axis relative to mid-hip / torso (view-dependent: DTL uses monocular depth)",
            "hand_forward_vs_address_at_impact": "hand_tgt(impact) - hand_tgt(address); + = hands ahead of address, toward target. HAND-FORWARD PROXY (lag/lean), NOT shaft lean",
            "lead_arm_lean_*_deg": "angle of lead-shoulder->lead-wrist line from vertical in the (tgt, up) plane; + = wrist toward target. Arm-line proxy, not shaft",
            "low_point_t_minus_impact_s": "time of minimum mid-wrist height in [top, impact+0.20s] minus impact event (+ = after impact)",
            "low_point_frac_of_downswing": "(t_low - t_top)/(t_impact - t_top)",
            "hand_path": f"{NPATH}-sample path takeaway(0)->impact(1) in (tgt, up, oth), relative to address hand position",
            "peak_hand_speed_*": "mid-wrist speed (torso/s) maximum in [top, impact+0.10s]"},
        "recommended_use": {
            "reward_ready": ["hand_up_at_top", "hand_up_at_impact", "low_point_t_minus_impact_s", "hand_path.up_weighted_median",
                             "peak_hand_speed_torso_per_s"],
            "reward_ready_note": "Use as soft bands (IQR / bootstrap CI), vertical + timing only; Mason's impact event looks early vs "
                                 "the hand low point (see docs), so prefer the low-point-relative form over absolute hand height at the event.",
            "diagnostic_only": ["hand_tgt_*", "hand_forward_vs_address_at_impact", "lead_arm_lean_*_deg", "hand_path.tgt_*", "hand_path.oth_*"],
            "diagnostic_only_note": "Forward/lean proxies are low confidence: only 2-3 clips pass the view-axis agreement test and "
                                    "only 3 have an address window; the DTL depth axis is unreliable."},
        "unavailable": {
            "shaft_lean_deg": UNAVAIL, "dynamic_loft_deg": UNAVAIL, "attack_angle_deg": UNAVAIL,
            "club_path_deg": UNAVAIL, "face_angle_deg": UNAVAIL, "launch_angle_deg": UNAVAIL,
            "club_head_speed_mph": UNAVAIL, "ball_speed_mph": UNAVAIL,
            "reason": "No club or ball data exists in any Mason file. Shaft lean can only be proxied by hand-forward / "
                      "lead-arm-line lean. Launch angle needs a launch monitor or club tracking; it is NOT derived here."},
        "selection": {"mason_v2": "recommended, commercial_ok, not partial, handedness left, native (or un-mirrored flipped edit) "
                                  "- same as data/mason_target_features.py",
                      "mason_v3_slowmo": "recommended native-left slow-motion clips; reported per-swing, excluded from the aggregate",
                      "min_landmark_coverage": 0.7, "min_alignment_corr": 0.9},
        "weights": {"weight_vertical_timing": "quality_score * landmark_coverage * view_weight(all 1.0), normalised",
                    "weight_forward": "quality_score * coverage * view_weight(face_on 1, oblique 0.6, DTL 0.4) * 1/(1+axis_std/20deg) * "
                                      "view_axis_agreement (inferred target axis vs labelled view; 1 = agrees, 0 = >=45 deg off), "
                                      "0 if address window <4 frames; normalised",
                    "note": "quality_score is a ranking heuristic, not accuracy"},
        "mason": {"n_swings_used_v2": len(v2s), "view_counts_v2": views, "aggregate_v2": agg,
                  "per_swing_v2": v2s, "slowmo_v3_per_swing": v3s, "rejected": rejected,
                  "license": LICENSE["mason"], "commercial_ok": True, "handedness": "left (stated; footage-verified where flagged per swing)"},
        "reference_comparisons": {"cmu_subject64": cmu_block(refs, cmu_bvh), "synthetic": synthetic_block(refs)},
        "uncertainty": {
            "time_resolution": "stored landmarks are ~30 unique fps (60 Hz upsampled): low-point / impact timing +-~0.05 s "
                               "(1 source frame on the impact event + 1 sample); events are detector heuristics",
            "geometry": "monocular MediaPipe world landmarks: depth axis (z) is model-prior-driven. Heights are the most reliable; "
                        "target-axis (forward) quantities are weakest in down-the-line clips",
            "bootstrap": "weighted_median_ci90_bootstrap = 5-95% of 500 resamples (seed 0), describes sampling spread only, not bias"},
        "caveats": [
            "Single 2D/monocular view per clip; every number is view-dependent (mostly DTL, some oblique, few face-on).",
            "Hand = wrist midpoint, not grip; there is no club. Shaft lean unavailable; only hand-forward / arm-line lean proxies.",
            "Low point is of the HANDS, not the club head; it is not a divot/low-point-of-arc measurement.",
            "Launch angle is not derived and must not be inferred from these numbers; it requires a launch monitor or club tracking.",
            "Impact/top/takeaway events are detector heuristics at ~30 fps; per-swing noise is large; n is small.",
            "Mason clips may be of mixed camera zoom/tilt; world-landmark vertical assumes an upright camera.",
            "CMU is a slow recreational volunteer (true 3-D, no club); synthetic has no hand data."],
        "provenance": {"license": LICENSE, "cmu_acknowledgment_required": True, "cmu_acknowledgment_text": CMU_ACK,
                       "raw_video_in_json": False, "commercial_only_filter": "only commercial_ok=True files are read",
                       "generator": "python -m data.mason_impact_geometry"},
    }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs", default="data/references")
    ap.add_argument("--out", default=None)
    ap.add_argument("--cmu-bvh", default="data/raw_mocap/cmu")
    a = ap.parse_args(argv)
    out = build(a.refs, a.cmu_bvh)
    path = a.out or os.path.join(a.refs, "mason_impact_geometry_targets.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=False)
        f.write("\n")
    m = out["mason"]
    print(f"wrote {path}: mason v2 n={m['n_swings_used_v2']} views={m['view_counts_v2']} "
          f"v3={len(m['slowmo_v3_per_swing'])} rejected={len(m['rejected'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

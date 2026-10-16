"""Derive Mason target features (per-swing + aggregate) -> data/references/mason_target_features.json.

Run: python -m data.mason_target_features [--refs data/references] [--out PATH]
Deterministic (no randomness, no timestamps in the JSON).

Selection (Mason): mason_v2_*.npz with recommended=True, commercial_ok=True, partial=False,
handedness=left, and either native_footage=True or the explicit un-mirrored copy of a
flipped-edit clip (mason_v2_p3_s09_unmirrored). Other mirrored copies are excluded.

Joint columns (deg): see JOINTS. Mason files have NO pelvis/thorax rotation, X-factor, sway or
club head -> reported as 'unavailable'. Sequencing for Mason uses arm proxies only.
"""
import argparse, glob, json, os
import numpy as np

JOINTS = ["right_shoulder_pitch", "right_shoulder_roll", "right_elbow", "right_wrist",
          "left_shoulder_pitch", "right_hip_pitch", "right_knee", "right_ankle",
          "left_hip_pitch", "left_knee", "left_ankle"]
RANGE_COLS = {"shoulder_pitch_R": 0, "shoulder_roll_R": 1, "elbow_R": 2, "wrist_R": 3,
              "shoulder_pitch_L": 4, "hip_pitch_R": 5, "knee_R": 6, "hip_pitch_L": 8, "knee_L": 9}
SRC_FPS = 30.0  # Instagram feed recordings; capture_fps field is 0 (unknown) in these files
UNAVAIL = "unavailable"


def _s(d, k, default=None):
    return d[k].item() if k in d.files else default


def _vel(x, dt):
    return np.gradient(x, dt)


def _peak_t(sig, t, lo, hi):
    m = (t >= lo) & (t <= hi)
    if m.sum() < 3 or not np.isfinite(sig[m]).any():
        return None
    idx = np.where(m)[0]
    return float(t[idx[int(np.nanargmax(np.abs(sig[m])))]])


def _at(x, t, tq):
    return float(np.interp(tq, t, x))


def events_of(d, kind):
    """(takeaway, top, impact) in the file's own swing-time axis (s)."""
    t = d["time"]
    if kind == "mason":
        t0 = float(d["t_start_in_video"])
        return float(d["t_takeaway"]) - t0, float(d["t_top"]) - t0, float(d["t_impact"]) - t0
    top, imp = (float(v) for v in d["events"])
    if "takeaway_s" in d.files:
        return float(d["takeaway_s"]), top, imp
    # synthetic files: takeaway implied by the stored tempo ratio
    return top - float(d["tempo_ratio"]) * (imp - top), top, imp


def features(d, kind):
    t = d["time"].astype(float)
    dt = float(d["dt"])
    tk, top, imp = events_of(d, kind)
    bs, ds = top - tk, imp - top
    span = imp - tk
    J = d["joints"].astype(float)
    out = {"takeaway_s": tk, "top_s": top, "impact_s": imp, "backswing_s": bs, "downswing_s": ds,
           "tempo_ratio": bs / ds if ds > 0 else None,
           "event_fractions": {"top_frac_of_takeaway_to_impact": (top - tk) / span if span > 0 else None,
                               "impact_frac_of_takeaway_to_impact": 1.0}}
    # tempo uncertainty: +-1 source frame on each event, first-order propagation (conservative sum)
    if kind == "mason" and ds > 0:
        q = 1.0 / SRC_FPS
        out["tempo_rel_uncertainty"] = float(min(2.0, q / bs + q / ds))  # relative, 1-frame events
    else:
        out["tempo_rel_uncertainty"] = 0.02
    # ranges at top/impact
    out["joints_deg_at_top"] = {k: _at(J[:, c], t, top) for k, c in RANGE_COLS.items()}
    out["joints_deg_at_impact"] = {k: _at(J[:, c], t, imp) for k, c in RANGE_COLS.items()}
    # sequencing
    lo, hi = top, min(t[-1], imp + 0.15)
    seq = {}
    for name, col in (("arm_shoulder_pitch_R", 0), ("arm_shoulder_pitch_L", 4), ("elbow_R", 2), ("wrist_R", 3)):
        v = _vel(J[:, col], dt)
        pt = _peak_t(v, t, lo, hi)
        seq[name + "_peak_vel_t"] = pt
        seq[name + "_peak_vel_frac_downswing"] = (pt - top) / ds if (pt is not None and ds > 0) else None
    have_rot = "pelvis_rot_deg" in d.files
    if have_rot:
        pel, tho = d["pelvis_rot_deg"].astype(float), d["thorax_rot_deg"].astype(float)
        for name, sig in (("pelvis", pel), ("thorax", tho)):
            pt = _peak_t(_vel(sig, dt), t, lo, hi)
            seq[name + "_peak_vel_t"] = pt
            seq[name + "_peak_vel_frac_downswing"] = (pt - top) / ds if (pt is not None and ds > 0) else None
        a = seq["pelvis_peak_vel_t"]; b = seq["thorax_peak_vel_t"]
        seq["pelvis_to_thorax_lag_s"] = (b - a) if (a is not None and b is not None) else None
        out["pelvis_turn_top_deg"] = _at(pel, t, top)
        out["thorax_turn_top_deg"] = _at(tho, t, top)
        out["x_factor_top_deg"] = _at(d["x_factor_deg"].astype(float), t, top)
        out["x_factor_max_deg"] = float(np.nanmax(d["x_factor_deg"]))
    else:
        for k in ("pelvis_turn_top_deg", "thorax_turn_top_deg", "x_factor_top_deg", "x_factor_max_deg"):
            out[k] = UNAVAIL
        for k in ("pelvis_peak_vel_t", "pelvis_peak_vel_frac_downswing", "thorax_peak_vel_t",
                  "thorax_peak_vel_frac_downswing", "pelvis_to_thorax_lag_s"):
            seq[k] = UNAVAIL
    wr = seq["wrist_R_peak_vel_t"]; sh = seq["arm_shoulder_pitch_R_peak_vel_t"]
    seq["wrist_minus_shoulder_peak_lag_s"] = (wr - sh) if (wr is not None and sh is not None) else None
    out["sequencing"] = seq
    return out


def _stat(vals):
    v = np.array([x for x in vals if isinstance(x, (int, float)) and x is not None and np.isfinite(x)], float)
    if v.size == 0:
        return {"n": 0, "median": UNAVAIL, "iqr": UNAVAIL}
    q1, q3 = np.percentile(v, [25, 75])
    return {"n": int(v.size), "median": float(np.median(v)), "iqr": [float(q1), float(q3)],
            "iqr_width": float(q3 - q1), "min": float(v.min()), "max": float(v.max())}


def _wmedian(v, w):
    v, w = np.asarray(v, float), np.asarray(w, float)
    o = np.argsort(v); c = np.cumsum(w[o]); return float(v[o][np.searchsorted(c, c[-1] / 2)])


def _flat(f, prefix=""):
    for k, v in f.items():
        if isinstance(v, dict):
            yield from _flat(v, prefix + k + ".")
        else:
            yield prefix + k, v


def aggregate(per, weights=None):
    keys = None
    cols = {}
    for f in per:
        for k, v in _flat(f):
            cols.setdefault(k, []).append(v)
    agg = {k: _stat(v) for k, v in cols.items() if k not in ("takeaway_s", "top_s", "impact_s")}
    if weights is not None:
        for k in ("tempo_ratio", "backswing_s", "downswing_s"):
            vals = np.array(cols[k], float)
            agg[k]["weighted_median"] = _wmedian(vals, weights)
    return agg


def select_mason(refs):
    sel = []
    for p in sorted(glob.glob(os.path.join(refs, "mason_v2_*.npz"))):
        d = np.load(p, allow_pickle=True)
        if not (bool(d["recommended"]) and bool(d["commercial_ok"]) and not bool(d["partial"])
                and str(d["handedness"]) == "left"):
            continue
        native = bool(d["native_footage"])
        unm = os.path.basename(p).endswith("_unmirrored.npz")
        if native and not bool(d["mirrored"]) or unm:
            sel.append((p, d, "unmirrored_flipped_edit" if unm else "native"))
    return sel


def build(refs="data/references"):
    sel = select_mason(refs)
    per, qs, rels = [], [], []
    for p, d, how in sel:
        f = features(d, "mason")
        qual = float(d["quality_score"])
        rel = f["tempo_rel_uncertainty"]
        f.update({"file": os.path.basename(p), "origin": how, "view": str(d["view"]),
                  "quality_score": qual, "valid_frac": float(d["valid_frac"]),
                  "handedness_verified": bool(d["handedness_verified"]),
                  "weight": None})
        per.append(f); qs.append(qual); rels.append(rel)
    w = np.array(qs) / (1.0 + np.array(rels))     # quality discounted by timing reliability
    w = w / w.sum()
    for f, wi in zip(per, w):
        f["weight"] = float(wi)
    # aggregate must be computed on features without non-numeric metadata
    agg = aggregate(per, w)
    for k in ("weight", "quality_score", "valid_frac"):
        agg.pop(k, None)

    def comp(pattern, kind):
        rs = []
        for p in sorted(glob.glob(os.path.join(refs, pattern))):
            d = np.load(p, allow_pickle=True)
            if bool(d["commercial_ok"]) and (not ("mirrored" in d.files) or not bool(d["mirrored"])):
                f = features(d, kind); f["file"] = os.path.basename(p); rs.append(f)
        return rs

    cmu = comp("cmu_64_*.npz", "other")
    syn = [features(np.load(os.path.join(refs, n + "_swing.npz"), allow_pickle=True), "other") | {"file": n + "_swing.npz"}
           for n in ("scott", "rory", "scheffler", "average")
           if os.path.exists(os.path.join(refs, n + "_swing.npz"))]
    scott = [s for s in syn if s["file"] == "scott_swing.npz"]
    ms = comp("multisense_*.npz", "other")
    return {
        "schema": "mason_target_features/v1",
        "joint_columns": JOINTS,
        "mason": {
            "handedness": "left", "n_swings": len(per), "selection": "recommended & commercial_ok & !partial & native-left (+ p3_s09 un-mirrored flipped edit)",
            "provenance": {"license_class": "self_owned", "commercial_ok": True, "source": "mason_self_filmed",
                           "note": "Mason's own swings recorded from an Instagram feed screen-recording; confirm no third-party content. Raw video not stored."},
            "aggregate": agg, "per_swing": per,
            "unavailable_fields": ["pelvis_turn_top_deg", "thorax_turn_top_deg", "x_factor_top_deg", "x_factor_max_deg",
                                   "pelvis/thorax peak-velocity timing", "club head / club speed", "lateral sway", "wrist hinge"],
        },
        "comparison": {
            "cmu_subject64": {"n_swings": len(cmu), "license_class": "cmu_permissive", "commercial_ok": True,
                              "note": "Recreational lab volunteer; slow (tempo ~1.7). Acknowledgment text required (docs/CMU_MOCAP_GOLF.md). Do not redistribute as a dataset.",
                              "aggregate": aggregate(cmu), "per_swing": cmu},
            "synthetic_scott": {"n_swings": len(scott), "license_class": "synthetic", "commercial_ok": True,
                                "note": "Procedurally generated from textbook params, not measured; tempo set to 3.0 by construction.",
                                "aggregate": aggregate(scott), "per_swing": scott},
            "synthetic_all_styles": {"n_swings": len(syn), "aggregate": aggregate(syn)},
            "multisense_cc0_right_handed": {"n_swings": len(ms), "license_class": "cc0", "note": "88-103 mph club speed, right-handed, IMU mocap; legal sign-off pending (see docs/research_open_data_v2.md).",
                                            "aggregate": aggregate(ms)},
        },
        "caveats": [
            "Mason sources are ~30 fps (or lower) screen recordings of Instagram posts; events are +-1 frame (~33 ms). With downswings of ~0.13-0.35 s, per-swing tempo uncertainty is large; treat aggregate tempo as +-15% at best (see tempo_rel_uncertainty).",
            "Mason joint angles are 2D-image proxies from MediaPipe landmarks, not fitted 3D humanoid angles; view-dependent (mostly down-the-line, 1 oblique, 1 face-on).",
            "Pelvis/thorax turn, X-factor and rotational sequencing are unavailable for Mason; sequencing uses arm joint angular-velocity peaks only, within [top, impact+0.15 s] and is a weak proxy.",
            "Reported 'right_*' columns are the golfer's anatomical right (= LEAD arm for a lefty).",
            "Quality weights = quality_score/(1+tempo_rel_uncertainty), normalised; quality_score is a heuristic ranking, not accuracy vs ground truth.",
            "Mason's true speed (120+ mph, 300+ yd) is NOT derivable from this data; do not use these features for speed targets.",
            "Handedness was not footage-verified (handedness_verified=False, relying on stated handedness) for mason_v2_p1_s11 and p2_s10; see per_swing flags.",
            "Mason downswings are only ~4-6 source frames (median ~0.17 s), so the tempo ratio is quantised and per-swing relative uncertainty is ~0.14-0.32 (median ~0.27); the true downswing may well be longer than detected.",
            "Small n; IQR is descriptive, not a confidence interval.",
        ],
    }


def _round(o, nd=4):
    if isinstance(o, float):
        return round(o, nd)
    if isinstance(o, dict):
        return {k: _round(v, nd) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round(v, nd) for v in o]
    return o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs", default="data/references")
    ap.add_argument("--out", default="data/references/mason_target_features.json")
    a = ap.parse_args(argv)
    res = build(a.refs)
    with open(a.out, "w") as fh:
        json.dump(_round(res), fh, indent=1, sort_keys=True, default=lambda o: None)
    print(f"wrote {a.out} (mason n={res['mason']['n_swings']})")


if __name__ == "__main__":
    main()

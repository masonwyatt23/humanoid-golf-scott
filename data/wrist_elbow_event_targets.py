"""Wrist/elbow joint targets at TOP and IMPACT -> data/references/wrist_elbow_event_targets.json.

Run: python -m data.wrist_elbow_event_targets [--out PATH]   (deterministic; no timestamps in the JSON)

Read-only w.r.t. env/ eval/ train/: the XMLs (env/models/humanoid_golf_v3.xml, humanoid_golf_v4_power.xml) are only parsed for joint
names, ranges, damping and motor limits.

KEY CONVENTION FINDING (code/doc reading, not a run): env `right_*` = TRAIL (club) arm, `left_*` = LEAD arm, for both
handednesses (docs/HANDEDNESS.md). The 11-col Mason reference files store the ANATOMICAL right arm in cols 2/3
(`right_elbow`, `right_wrist`), which is the LEAD arm for a left-hander. CMU/MultiSense columns 2/3 are the TRAIL arm
(data/convert_cmu_mocap.py compute_joints: T = trail side). So for Mason the env-role-correct values come from the anatomical
LEFT arm (= trail), which is NOT in the 11 columns; it is recomputed here from the stored 33-landmark world track with the SAME
formulas as data/process_video.landmarks_to_joints. The lead arm (anatomical right) maps to env `left_elbow` (passive,
unmotored in v3/v4_power); there is no left wrist joint in those models.

Event times: Mason joint/time axis starts at the first valid landmark frame, NOT t_start_in_video. We use
data.mason_target_features.events_of (t_* - t_start_in_video - recovered axis offset, offset ~0.4 s in most files). The
audit's get_events() form (t_* - t_start_in_video only) is reported alongside as `events_naive_s`; the two differ by the
axis offset, so the naive form samples the wrong frames for 7/9 clips.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np

from data.mason_target_features import events_of, mason_time_offset

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "references"
OUT = REF / "wrist_elbow_event_targets.json"
MODELS = {"v3": ROOT / "env" / "models" / "humanoid_golf_v3.xml", "v4_power": ROOT / "env" / "models" / "humanoid_golf_v4_power.xml"}
WIN_S = 0.03
VIS_MIN = 0.5
# MediaPipe indices (same as data/process_video.py)
L_SH, R_SH, L_EL, R_EL, L_WR, R_WR = 11, 12, 13, 14, 15, 16
L_PINKY, R_PINKY, L_IDX, R_IDX = 17, 18, 19, 20
ARMS = {  # anatomical side -> landmark ids
    "right": dict(sh=R_SH, el=R_EL, wr=R_WR, idx=R_IDX, pk=R_PINKY),
    "left": dict(sh=L_SH, el=L_EL, wr=L_WR, idx=L_IDX, pk=L_PINKY)}
# left-handed golfer: anatomical right = LEAD, anatomical left = TRAIL
MASON_ROLE = {"left": "trail", "right": "lead"}
BEST_RULE = ("highest quality_score among clips that are recommended=True, native footage, handedness verified left, not partial, "
             "not handedness-flagged and not flip-edit (data/references/mason_v2_report.json has an empty clips list, so quality_score "
             "is read from each npz)")
PRIMARY = "mason_v2_p1_s06"
USER_DEFAULT = "mason_v2_p1_s05"
RUNNERS = ["mason_v2_p1_s03", "mason_v2_p1_s04", "mason_v2_p2_s01", "mason_v2_p2_s02", "mason_v2_p2_s11", "mason_v2_p2_s13"]
CMU = [f"cmu_64_{i:02d}" for i in range(1, 11)]


def _ang(a, b, c):
    u, v = a - b, c - b
    cs = (u * v).sum(-1) / (np.linalg.norm(u, axis=-1) * np.linalg.norm(v, axis=-1) + 1e-9)
    return np.degrees(np.arccos(np.clip(cs, -1, 1)))


def arm_series(lm, side):
    """(elbow_flexion, wrist_dev_idx, wrist_dev_hand_mid, min_visibility) per landmark frame; deg, 0 = straight."""
    a = ARMS[side]
    P = lambda i: lm[:, i, :3].astype(float)
    el = 180.0 - _ang(P(a["sh"]), P(a["el"]), P(a["wr"]))
    wi = 180.0 - _ang(P(a["el"]), P(a["wr"]), P(a["idx"]))
    wm = 180.0 - _ang(P(a["el"]), P(a["wr"]), 0.5 * (P(a["idx"]) + P(a["pk"])))
    vis = np.minimum.reduce([lm[:, a[k], 3].astype(float) for k in ("sh", "el", "wr", "idx", "pk")])
    return el, wi, wm, vis


def lm_time(d):
    n = len(d["landmarks"])
    return np.arange(n) * (float(d["time"][-1]) / (n - 1))


def med_at(sig, t, vis, tq, win=WIN_S):
    m = (np.abs(t - tq) <= win) & (vis > VIS_MIN) & np.isfinite(sig)
    return (float(np.median(sig[m])), int(m.sum())) if m.any() else (None, 0)


def joint_at(d, col, tq, win=WIN_S):
    t = d["time"].astype(float); J = d["joints"][:, col].astype(float); ok = d["valid_mask"].astype(bool)
    m = (np.abs(t - tq) <= win) & ok & np.isfinite(J)
    return (float(np.median(J[m])), int(m.sum())) if m.any() else (None, 0)


def env_limits():
    """Read-only parse: per model {joint: {range_deg, damping, motor_force_range, gear}} for elbow/wrist joints."""
    out = {}
    for tag, p in MODELS.items():
        x = p.read_text()
        dd = re.search(r'<default>.*?<joint [^>]*damping="([\d.]+)"', x, re.S)
        default_damp = float(dd.group(1)) if dd else None
        o = {"default_joint_damping": default_damp}
        for j in ("right_elbow", "right_wrist", "left_elbow"):
            m = re.search(r'<joint name="%s"[^>]*?range="(-?[\d.]+) (-?[\d.]+)"([^>]*)/>' % j, x)
            dm = re.search(r'damping="([\d.]+)"', m.group(0)) if m else None
            mo = re.search(r'<motor name="%s"[^>]*forcerange="(-?[\d.]+) (-?[\d.]+)"[^>]*gear="([\d.]+)"' % j, x)
            o[j] = {"range_deg": [float(m.group(1)), float(m.group(2))] if m else None,
                    "damping": float(dm.group(1)) if dm else default_damp,
                    "motor_peak_torque_Nm": (float(mo.group(2)) * float(mo.group(3))) if mo else None,
                    "has_motor": bool(mo)}
        out[tag] = o
    return out


def _stat(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    a = np.array(v)
    return {"n": len(v), "median": round(float(np.median(a)), 1), "min": round(float(a.min()), 1), "max": round(float(a.max()), 1),
            "q25": round(float(np.percentile(a, 25)), 1), "q75": round(float(np.percentile(a, 75)), 1)}


def mason_clip(name):
    d = np.load(REF / f"{name}.npz", allow_pickle=True)
    ev_tk, top, imp = events_of(d, "mason")
    t0n = float(d["t_start_in_video"])
    naive = {"top": float(d["t_top"]) - t0n, "impact": float(d["t_impact"]) - t0n}
    tl = lm_time(d)
    out = {"quality_score": round(float(d["quality_score"]), 3), "view": str(d["view"]), "handedness": str(d["handedness"]),
           "handedness_verified": bool(d["handedness_verified"]), "recommended": bool(d["recommended"]),
           "axis_offset_s": round(mason_time_offset(d), 3), "events_s": {"top": round(top, 3), "impact": round(imp, 3)},
           "events_naive_s": {k: round(v, 3) for k, v in naive.items()}, "arms": {}}
    for side in ("left", "right"):
        el, wi, wm, vis = arm_series(d["landmarks"], side)
        role = MASON_ROLE[side]
        rec = {"role": role, "anatomical_side": side}
        for ev, tq in (("top", top), ("impact", imp)):
            e, ne = med_at(el, tl, vis, tq); w, nw = med_at(wi, tl, vis, tq); w2, _ = med_at(wm, tl, vis, tq)
            rec[ev] = {"elbow_flexion_deg": None if e is None else round(e, 1), "wrist_dev_deg": None if w is None else round(w, 1),
                       "wrist_dev_handmid_deg": None if w2 is None else round(w2, 1), "n_landmark_frames": nw}
        if side == "right":   # cross-check against the stored 11-col proxies (same formulas)
            for ev, tq in (("top", top), ("impact", imp)):
                je, _ = joint_at(d, 2, tq); jw, _ = joint_at(d, 3, tq)
                rec[ev]["stored_col2_elbow_deg"] = None if je is None else round(je, 1)
                rec[ev]["stored_col3_wrist_deg"] = None if jw is None else round(jw, 1)
                rec[ev]["source"] = "landmarks"
                if rec[ev]["elbow_flexion_deg"] is None and je is not None:   # landmark visibility gate failed -> stored proxies (same formulas)
                    rec[ev].update(elbow_flexion_deg=round(je, 1), wrist_dev_deg=None if jw is None else round(jw, 1), source="stored_cols_2_3_fallback")
        # wrist angular speed proxy (deg/s) on landmark cadence between top and impact + 0.1 s (noisy; ~30 fps source)
        m = (tl >= top) & (tl <= imp + 0.1) & (vis > VIS_MIN) & np.isfinite(wi)
        if m.sum() >= 4:
            sp = np.abs(np.gradient(wi[m], tl[m]))
            rec["wrist_dev_peak_rate_deg_s_top_to_impact_plus0.1"] = round(float(np.percentile(sp, 90)), 0)
            rec["wrist_dev_range_deg_top_to_impact_plus0.1"] = [round(float(wi[m].min()), 1), round(float(wi[m].max()), 1)]
        out["arms"][role] = rec
    return out


def ref_clip(name):
    """CMU / MultiSense (mirrored) files: cols 2/3 = TRAIL arm, wrist col 3 negative = cocked; events on file axis."""
    d = np.load(REF / f"{name}.npz", allow_pickle=True)
    top, imp = (float(x) for x in d["events"])
    r = {"role": "trail", "events_s": {"top": round(top, 3), "impact": round(imp, 3)}}
    for ev, tq in (("top", top), ("impact", imp)):
        e, _ = joint_at_ref(d, 2, tq); w, _ = joint_at_ref(d, 3, tq)
        wh = float(np.median(d["wrist_hinge_deg"][np.abs(d["time"] - tq) <= WIN_S])) if "wrist_hinge_deg" in d.files else None
        r[ev] = {"elbow_flexion_deg": None if e is None else round(e, 1), "wrist_col3_deg": None if w is None else round(w, 1),
                 "wrist_hinge_deg": None if wh is None else round(wh, 1)}
    r["wrist_measured"] = bool(np.ptp(d["joints"][:, 3]) > 1.0)
    return r


def joint_at_ref(d, col, tq, win=WIN_S):
    t = d["time"].astype(float); J = d["joints"][:, col].astype(float)
    m = (np.abs(t - tq) <= win)
    return (float(np.median(J[m])), int(m.sum())) if m.any() else (None, 0)


def env_rows(arm_vals, lims):
    """Turn trail/lead values into env-joint target rows (deg + rad) with limit/sign flags."""
    rows = []
    for ev in ("top", "impact"):
        tr, ld = arm_vals["trail"][ev], arm_vals["lead"][ev]
        spec = [("right_elbow", "trail", tr["elbow_flexion_deg"], "flexion >= 0 (positive = flexion; limits 0..150)", False),
                ("right_wrist", "trail", tr["wrist_dev_deg"], "UNSIGNED magnitude; env sign for cocked is probably NEGATIVE (CMU doc + masonwrist configs); SIGN UNCERTAIN", True),
                ("left_elbow", "lead", ld["elbow_flexion_deg"], "flexion >= 0 (limits -10..150); passive in v3/v4_power (no motor)", False),
                ("left_wrist", "lead", ld["wrist_dev_deg"], "NO env joint (v3/v4_power have no left wrist); reference only", True)]
        for jn, role, v, sign_note, signed in spec:
            if jn == "right_wrist" and ev == "impact":
                sign_note += ("; at impact the unsigned magnitude is as large as or larger than at top in most clips, so it is probably flexion/bowing or "
                              "uncocked-then-bent, NOT cock: do not apply the negative-cock sign blindly")
            row = {"event": ev, "env_joint": jn, "role": role, "value_deg": v, "value_rad": None if v is None else round(float(np.radians(v)), 3),
                   "sign_note": sign_note, "sign_uncertain": signed}
            if signed and jn == "right_wrist" and v is not None and ev == "top":
                row["env_value_deg_if_cocked_negative"] = -v
                row["env_value_rad_if_cocked_negative"] = round(-float(np.radians(v)), 3)
            for tag in lims:
                lj = lims[tag].get(jn)
                if lj and lj["range_deg"] and v is not None:
                    lo, hi = lj["range_deg"]
                    row[f"in_limits_{tag}"] = bool(lo <= v <= hi) if not signed else bool(lo <= -abs(v) and abs(v) <= hi)
                elif jn == "left_wrist":
                    row[f"in_limits_{tag}"] = None
            rows.append(row)
    return rows


def build():
    lims = env_limits()
    names = [PRIMARY, USER_DEFAULT] + RUNNERS
    clips = {n: mason_clip(n) for n in names}

    def arm_ev(n, role, ev):
        return clips[n]["arms"][role][ev]
    primary_vals = {r: {ev: arm_ev(PRIMARY, r, ev) for ev in ("top", "impact")} for r in ("trail", "lead")}
    default_vals = {r: {ev: arm_ev(USER_DEFAULT, r, ev) for ev in ("top", "impact")} for r in ("trail", "lead")}
    spread_names = [USER_DEFAULT, PRIMARY] + RUNNERS
    spread = {}
    for role in ("trail", "lead"):
        for ev in ("top", "impact"):
            for q in ("elbow_flexion_deg", "wrist_dev_deg"):
                spread[f"{role}_{ev}_{q}"] = _stat([arm_ev(n, role, ev)[q] for n in spread_names])
    cmu = {n: ref_clip(n) for n in CMU}
    ms_files = sorted(p.stem for p in REF.glob("multisense_*_mirrored.npz"))
    ms = {n: ref_clip(n) for n in ms_files}

    def agg(group, ev, q):
        return _stat([v[ev][q] for v in group.values()])
    ref_med = {}
    for tag, grp in (("cmu_64_trail_arm", cmu), ("multisense_mirrored_trail_arm", ms)):
        ref_med[tag] = {ev: {"elbow_flexion_deg": agg(grp, ev, "elbow_flexion_deg"), "wrist_col3_deg": agg(grp, ev, "wrist_col3_deg"),
                             "wrist_hinge_deg": agg(grp, ev, "wrist_hinge_deg")} for ev in ("top", "impact")}
    ref_med["multisense_mirrored_trail_arm"]["n_files"] = len(ms)
    ref_med["multisense_mirrored_trail_arm"]["n_wrist_measured"] = int(sum(v["wrist_measured"] for v in ms.values()))
    ref_med["multisense_mirrored_trail_arm"]["license_class"] = "needs_counsel"
    ref_med["multisense_mirrored_trail_arm"]["note"] = ("needs_counsel (participant consent scope not established); analysis only, do not publish. Wrist col 3 is zero-filled "
                                                         "(no finger markers) so wrist values are unavailable when wrist_measured is false.")
    ref_med["cmu_64_trail_arm"]["n_files"] = len(cmu)
    ref_med["cmu_64_trail_arm"]["license_class"] = "cmu_permissive"
    ref_med["cmu_64_trail_arm"]["note"] = ("CMU acknowledgment text required; no standalone redistribution of converted files. Slow recreational mocap (tempo ~1.7). Hand = LeftHandIndex1/RightHandIndex1 bone, "
                                           "wrist col negative = cocked. NOTE: the CMU manifest entry is flagged needs_counsel in the repo's release questions - keep flagged.")

    # actuator vs reference-wrist demand (hypotheses inputs)
    demand = {}
    for n in spread_names:
        r = clips[n]["arms"]["trail"]
        demand[n] = {k: r.get(k) for k in ("wrist_dev_peak_rate_deg_s_top_to_impact_plus0.1", "wrist_dev_range_deg_top_to_impact_plus0.1")}
        demand[n]["top_to_impact_s"] = round(clips[n]["events_s"]["impact"] - clips[n]["events_s"]["top"], 3)
    return {
        "version": "wrist_elbow_event_targets_v1",
        "status": "UNVERIFIED video-derived proxies (MediaPipe world landmarks at ~30 fps source). Not ground-truth joint angles.",
        "best_clip": {"name": PRIMARY, "quality_score": clips[PRIMARY]["quality_score"], "view": clips[PRIMARY]["view"], "rule": BEST_RULE,
                      "note": ("p1_s06 is the top-scoring eligible clip; it is the only eligible clip with an oblique view and its joint axis starts at t_start (offset 0). "
                               f"The requested {USER_DEFAULT} (score {clips[USER_DEFAULT]['quality_score']}) is reported too. Higher scorers excluded: p3_s09_unmirrored 0.83 "
                               "(caption-flagged flip-edit), p2_s05/p2_s08/p3_s08/p3_s09 (handedness detected right), p1_s11 0.756 (handedness unverified, excluded from unified_v2).")},
        "convention": {
            "env_role_rule": "env right_* = TRAIL (club) arm, left_* = LEAD arm, both handednesses (docs/HANDEDNESS.md); pitch-axis signs do not change with handedness",
            "mason_columns": "11-col files: cols 2/3 = anatomical RIGHT arm = LEAD arm for Mason (left-handed). Stored under right_* names -> ROLE MISMATCH vs env",
            "cmu_multisense_columns": "cols 2/3 = TRAIL arm (convert_cmu_mocap.compute_joints)",
            "angle_definitions": "elbow_flexion = 180 - interior(shoulder, elbow, wrist); wrist_dev = 180 - interior(elbow, wrist, index-finger landmark); both >= 0, 0 = straight. "
                                 "Wrist is a 3-D deviation magnitude mixing flexion/extension and radial/ulnar deviation, UNSIGNED, and index-finger landmark is noisy.",
            "event_times": "events_of() (offset-corrected); events_naive_s = t - t_start_in_video only (audit get_events form), differs by axis_offset_s",
            "window": f"median of landmark frames within +-{WIN_S} s of the event, visibility > {VIS_MIN} on shoulder, elbow, wrist, index, pinky"},
        "env_limits": lims,
        "mason_clips": clips,
        "env_targets_best_clip": env_rows(primary_vals, lims),
        "env_targets_user_default_clip": env_rows(default_vals, lims),
        "mason_spread_across_clips": {"clips": spread_names, "stats": spread,
                                      "note": "n=8 single-view clips (7 down-the-line + 1 oblique); not a population estimate. Per-clip detail in mason_clips."},
        "reference_medians": ref_med,
        "published_biomechanics_in_repo": [
            {"item": "Wrist release (uncock) starts when the lead arm is ~30 deg below horizontal", "source": "Hume, Keogh & Reid 2005 (Sports Med 35(5):429-449) quoting Sprigings & Neal 2000", "url": "https://pubmed.ncbi.nlm.nih.gov/15896091/", "in_repo": "docs/research_data_sources.md", "status": "secondary (quoted via Hume), not read directly"},
            {"item": "Wrist cock was the strongest of 15 club-speed predictors (60.3% of variance, between golfers)", "source": "Robinson via Hume 2005", "url": "https://pubmed.ncbi.nlm.nih.gov/15896091/", "in_repo": "docs/research_data_sources.md", "status": "secondary"},
            {"item": "Wrist torque adds ~9% club speed in a 44 m/s simulation; wrist ~70% of linear club speed contribution (Milburn/Neal)", "source": "Hume 2005", "url": "https://pubmed.ncbi.nlm.nih.gov/15896091/", "in_repo": "docs/research_data_sources.md", "status": "secondary"},
            {"item": "Arm->club speed gain 1274 deg/s; wrist-only uncock speed is UNVERIFIED (proxy ~1520 deg/s at 130 mph)", "source": "Cheetham 2008 via docs/research_350yd_profile.md", "url": "https://www.academia.edu/5572510/Comparison_of_Kinematic_Sequence_Parameters_between_Amateur_and_Professional_Golfers", "in_repo": "docs/research_350yd_profile.md", "status": "proxy / unverified"},
            {"item": "Forward-dynamics golf models use wrist torque ~90 N*m (MacKenzie 2009 and a later model, via search)", "source": "docs/research_sim_realism.md", "url": None, "in_repo": "docs/research_sim_realism.md", "status": "search-snippet, unverified"},
            {"item": "Bryson: small lead-wrist hinge, high hands (qualitative only)", "source": "GOLF.com Jun 2025 (Manzella)", "url": None, "in_repo": "data/references/pro_swing_profiles.json (golfcom_bryson_manzella)", "status": "qualitative"}],
        "published_numeric_ranges_for_elbow_or_wrist_angle_at_top_or_impact": "NONE FOUND in the repo docs or pro_swing_profiles.json. Not fetched in this job. UNVERIFIED; do not invent. The Edinburgh DataShare wrist dataset (doi:10.7488/ds/3823) has wrist angular velocity but is gated/license-unread (docs/research_open_data_v2.md).",
        "actuator_demand_vs_reference": demand,
        "caveats": [
            "All Mason angles are monocular 3-D landmark proxies at ~30 fps with MediaPipe noise; event detectors are heuristics (impact is early vs hand low point by ~0.067 s per docs/MASON_IMPACT_GEOMETRY.md).",
            "Wrist deviation is unsigned; the env wrist sign (cock = negative) is inferred from configs/fast_scripted_v3_masonwrist.json (wrist_cock -0.5) and docs/CMU_MOCAP_GOLF.md, not verified in a run.",
            "Trail-arm values (anatomical left for Mason) are NOT in the stored 11-col joints and have never been used by the current references; the left arm is often partially occluded in down-the-line views, so visibility-gated counts are reported per event.",
            "Ranges at the two events are single-instant medians; Mason's video backswing/downswing durations look compressed (feed-clip artifact suspected), so rates are unreliable."],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(OUT)); a = ap.parse_args(argv)
    res = build()
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()

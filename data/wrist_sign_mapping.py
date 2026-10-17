"""Wrist sign / zero-offset mapping: reference wrist column -> env `right_wrist` (v3 / v4_power).

READ-ONLY w.r.t. env/ eval/ train/. Run:  python data/wrist_sign_mapping.py  (writes data/references/wrist_sign_mapping.json)

Findings (all derived here by forward kinematics of the env XML; nothing is trained):
* env right_wrist is a hinge about +y whose child body carries the club along local -z while the forearm runs along +x.
  So env wrist = 0 is a 90-degree L between forearm and club, NOT a straight line. Interior(forearm, club) = 90 - w_deg.
  w = -90 deg -> club collinear with the forearm (180 interior, 'straight'); w > 0 folds the club back toward the forearm
  (more cocked); w < 0 straightens it.
* Reference wrist = 180 - interior(elbow, wrist, index) = HAND deviation from the forearm line, >= 0, 0 = straight (Mason, unsigned;
  CMU stores the same magnitude with a minus sign, 'cocked = negative'). It is a hand angle, not a club angle.
* Physically a larger deviation d means a smaller forearm-shaft interior, i.e. a larger env w:  env_w = +d + offset  (Mason),
  env_w = -col3 + offset (CMU, stored sign is flipped), offset = c0 - 90 deg where c0 = static shaft-vs-hand angle (unmeasured).
* offset is pinned by contact geometry: the env has to reach the ball (distance shoulder->ball) with its own arm/club lengths.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "data" / "references"
CONTACT_TOL_M = 0.06   # head-centre to ball-centre; club_head half-extent 0.05 + ball radius 0.021 (box, so approximate)


def load_env(xml="humanoid_golf_v3.xml"):
    sys.path.insert(0, str(ROOT))
    from env.residual_golf_env import ResidualGolfEnv, DEFAULT_SCRIPT
    e = ResidualGolfEnv(script=dict(DEFAULT_SCRIPT), model_xml=xml)
    e.reset(seed=1)
    return e


def interior_forearm_club_deg(env, w_rad):
    import mujoco
    m, d = env.model, env.data
    q = lambda n: m.joint(n).qposadr[0]
    d.qpos[q("right_wrist")] = w_rad
    mujoco.mj_kinematics(m, d)
    fo = d.xpos[m.body("right_wrist").id] - d.xpos[m.body("right_elbow").id]
    cl = d.geom_xpos[m.geom("club_head").id] - d.xpos[m.body("right_wrist").id]
    ang = np.degrees(np.arccos(fo @ cl / np.linalg.norm(fo) / np.linalg.norm(cl)))
    return 180.0 - float(ang)      # 180 = straight line, 90 = L


def min_head_ball_dist(env, elbow, wrist, shoulders=np.linspace(-1.6, 2.6, 841)):
    """Min over shoulder pitch of |club_head_centre - ball_centre| at fixed elbow/wrist (torso pinned, y/roll/yaw = reset values)."""
    import mujoco
    m, d = env.model, env.data
    q = lambda n: m.joint(n).qposadr[0]
    ball = d.xpos[m.body("ball").id].copy(); hb = m.geom("club_head").id
    d.qpos[q("right_elbow")] = elbow; d.qpos[q("right_wrist")] = wrist
    bd, bs = 9.0, None
    for s in shoulders:
        d.qpos[q("right_shoulder_pitch")] = s; mujoco.mj_kinematics(m, d)
        dd = float(np.linalg.norm(d.geom_xpos[hb] - ball))
        if dd < bd: bd, bs = dd, float(s)
    return bd, bs


def contact_wrist(env, elbow, grid=np.arange(-1.6, 1.6001, 0.02)):
    """(w_best, mindist_best, [w_lo, w_hi] with mindist<=CONTACT_TOL) at this elbow."""
    ds = np.array([min_head_ball_dist(env, elbow, w, shoulders=np.linspace(-1.6, 2.6, 421))[0] for w in grid])
    i = int(np.argmin(ds)); ok = grid[ds <= CONTACT_TOL_M]
    return float(grid[i]), float(ds[i]), ([float(ok.min()), float(ok.max())] if len(ok) else None)


def build():
    T = json.load(open(REF / "wrist_elbow_event_targets.json"))
    out = {"status": "UNVERIFIED: video proxies + env geometry; offset fitted to contact geometry, not measured on a human",
           "env_geometry": {}, "contact_sweep": {}, "mapping": {}, "clips": {}, "cmu": {}}
    envs = {x: load_env(x) for x in ("humanoid_golf_v3.xml", "humanoid_golf_v4_power.xml")}
    e = envs["humanoid_golf_v3.xml"]
    out["env_geometry"] = {
        "ball_xyz": [float(v) for v in e.data.xpos[e.model.body("ball").id]],
        "shoulder_xyz": [float(v) for v in e.data.xpos[e.model.body("right_shoulder").id]],
        "interior_forearm_club_deg_vs_wrist_rad": {f"{w:+.3f}": round(interior_forearm_club_deg(e, w), 1) for w in (-1.5708, -0.977, -0.703, -0.5, 0.0, 0.5, 0.703, 0.977, 1.5708)},
        "identical_v3_v4_power": all(abs(interior_forearm_club_deg(envs["humanoid_golf_v3.xml"], w) - interior_forearm_club_deg(envs["humanoid_golf_v4_power.xml"], w)) < 1e-6 for w in (-1.0, 0.0, 1.0)),
        "wrist_zero": "90 deg L between forearm (+x) and club (-z); interior = 90 - w_deg; straight line at w = -90 deg",
    }
    # contact sweep: elbow x wrist
    els = [0.0, 0.349, 0.42, 0.65, 0.853, 0.981, 1.126]
    for el in els:
        wb, db, win = contact_wrist(e, el)
        out["contact_sweep"][f"elbow_{el:.3f}"] = {"wrist_best_rad": round(wb, 3), "min_dist_m": round(db, 4), "wrist_window_rad_dist_le_%.2f" % CONTACT_TOL_M: win}
    # table of dist for the stored value
    out["stored_impact_0p977"] = {f"elbow_{el:.3f}": round(min_head_ball_dist(e, el, 0.977)[0], 3) for el in (0.349, 0.853)}
    out["stored_impact_minus_0p977"] = {f"elbow_{el:.3f}": round(min_head_ball_dist(e, el, -0.977)[0], 3) for el in (0.349, 0.853)}
    # offset fit from Mason best clip impact and independently from CMU median impact
    best = T["best_clip"]["name"]; tr = T["mason_clips"][best]["arms"]["trail"]
    d_imp, d_top = np.deg2rad(tr["impact"]["wrist_dev_deg"]), np.deg2rad(tr["top"]["wrist_dev_deg"])
    el_imp = np.deg2rad(tr["impact"]["elbow_flexion_deg"])
    w_c, _, _ = contact_wrist(e, el_imp)
    off_m = w_c - d_imp
    cm = T["reference_medians"]["cmu_64_trail_arm"]
    c_imp = np.deg2rad(-cm["impact"]["wrist_col3_deg"]["median"]); c_top = np.deg2rad(-cm["top"]["wrist_col3_deg"]["median"])
    c_el = np.deg2rad(cm["impact"]["elbow_flexion_deg"]["median"])
    w_cc, _, _ = contact_wrist(e, c_el)
    off_c = w_cc - c_imp
    out["offset_fits_rad"] = {"mason_best_clip_impact": round(float(off_m), 3), "cmu_median_impact": round(float(off_c), 3),
                              "mean": round(float((off_m + off_c) / 2), 3), "implied_static_shaft_offset_c0_deg_mean": round(float(90 + np.degrees((off_m + off_c) / 2)), 1)}
    off = float((off_m + off_c) / 2)
    xs = np.array([float(k.split("_")[1]) for k in out["contact_sweep"]]); ys = np.array([v["wrist_best_rad"] for v in out["contact_sweep"].values()])
    sl, ic = np.polyfit(xs, ys, 1)
    out["contact_wrist_vs_elbow_linear_fit"] = {"formula": "w_contact = intercept + slope * elbow_rad (impact pose, v3 == v4_power geometry)", "slope": round(float(sl), 3), "intercept": round(float(ic), 3), "valid_elbow_rad": [0.0, 1.13], "half_width_rad": 0.1}
    out["mapping"] = {
        "mason_v2_col3_unsigned": {"env_wrist_rad": f"+1 * ref_rad + ({off:.2f})", "sign": +1, "offset_rad": round(off, 2)},
        "cmu_col3_cocked_negative": {"env_wrist_rad": f"-1 * ref_rad + ({off:.2f})", "sign": -1, "offset_rad": round(off, 2)},
        "multisense": "wrist not measured (zero-filled): no mapping",
        "tolerance_rad": 0.15,
        "caveat": "offset is constrained only by the ball-contact window (about +/-0.2 rad wide) and is tied to the env's stylised arm/club lengths, not to human anatomy.",
    }
    # clip table
    for k, c in T["mason_clips"].items():
        t = c["arms"]["trail"]; ti, ii = np.deg2rad(t["top"]["wrist_dev_deg"]), np.deg2rad(t["impact"]["wrist_dev_deg"])
        eli = np.deg2rad(t["impact"]["elbow_flexion_deg"]); wcc, dcc, win = contact_wrist(e, eli)
        out["clips"][k] = {"handedness_verified": c.get("handedness_verified"), "view": c.get("view"),
                           "ref_top_rad": round(float(ti), 3), "ref_impact_rad": round(float(ii), 3), "elbow_impact_rad": round(float(eli), 3),
                           "env_top_rad": round(float(ti + off), 3), "env_impact_rad": round(float(ii + off), 3),
                           "contact_wrist_at_this_elbow_rad": round(wcc, 3), "contact_window_rad": win,
                           "impact_inside_contact_window": bool(win and win[0] <= ii + off <= win[1])}
    out["cmu"] = {"top_env_rad": round(float(c_top + off), 3), "impact_env_rad": round(float(c_imp + off), 3), "elbow_impact_rad": round(float(c_el), 3),
                  "contact_wrist_at_this_elbow_rad": round(w_cc, 3)}
    return out


if __name__ == "__main__":
    o = build()
    (REF / "wrist_sign_mapping.json").write_text(json.dumps(o, indent=1))
    print(json.dumps({k: o[k] for k in ("offset_fits_rad", "mapping", "contact_wrist_vs_elbow_linear_fit", "cmu")}, indent=1))

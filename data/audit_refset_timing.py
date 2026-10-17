"""Timing / sanity audit of the unified reference set (unified_v1). Read-only on data and env.

  python -m data.audit_refset_timing            # writes data/references/refset_timing_audit.json
  python -m data.audit_refset_timing --print

Checks per manifest entry (flags, not verdicts):
  nan / shape / time_axis (uniform dt, length==len(joints)) / dt_mismatch / events_missing / events_order /
  events_out_of_range / downswing_implausible / backswing_implausible /
  impact_not_at_arm_peak (impact event vs peak arm angular speed; lag in s) / jump (max frame-to-frame deg) /
  joint_limit (vs env/models/humanoid_golf.xml ranges, parsed as text) / mirror_pair_mismatch /
  mirror_on_load_events (events survive mirror_dict).
Events: [top, impact] seconds for CMU/MultiSense/synthetic; Mason files have no `events` key, they are derived
from t_takeaway/t_top/t_impact minus t_start_in_video (time axis starts at 0 = t_start_in_video; verified).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "references" / "refset_timing_audit.json"
XML = ROOT / "env" / "models" / "humanoid_golf.xml"
COLS = ["right_shoulder_pitch", "right_shoulder_roll", "right_elbow", "right_wrist", "left_shoulder_pitch",
        "right_hip_pitch", "right_knee", "right_ankle", "left_hip_pitch", "left_knee", "left_ankle"]
ARM_COLS = [0, 1, 2, 4]
DOWNSWING_RANGE = (0.12, 0.60)   # s; tour ~0.25-0.35, amateurs to ~0.5 (rule-of-thumb, unverified)
BACKSWING_RANGE = (0.35, 1.8)
PEAK_LAG_TOL = 0.12              # s between impact event and arm-speed peak (heuristic)
JUMP_DEG = 25.0                  # deg per 0.01 s frame (=2500 deg/s) flagged
LIMIT_TOL = 5.0                  # deg beyond range tolerated


def joint_limits(xml_path=XML):
    txt = Path(xml_path).read_text()
    out = {}
    for m in re.finditer(r'<joint name="(\w+)"[^>]*?range="([-\d.]+) ([-\d.]+)"', txt):
        out[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return {c: out[c] for c in COLS if c in out}


def get_events(d):
    """-> (top, impact, source) seconds on the file's own time axis, or (None, None, reason)."""
    if "events" in d and np.size(d["events"]) >= 2:
        e = np.asarray(d["events"], float)
        return float(e[0]), float(e[1]), "events"
    if all(k in d for k in ("t_top", "t_impact", "t_start_in_video")):
        t0 = float(d["t_start_in_video"])
        return float(d["t_top"]) - t0, float(d["t_impact"]) - t0, "t_*_minus_t_start"
    return None, None, "none"


def arm_speed(j, dt):
    v = np.gradient(np.asarray(j, float)[:, ARM_COLS], dt, axis=0)
    return np.linalg.norm(v, axis=1)


def audit_arrays(d, limits=None):
    """Audit one loaded dict; returns (metrics, flags)."""
    flags, m = [], {}
    j = np.asarray(d["joints"], float)
    dt = float(d["dt"]) if "dt" in d else 0.01
    n = len(j)
    m.update(frames=n, dt=dt, duration_s=round((n - 1) * dt, 3))
    if j.ndim != 2 or j.shape[1] != 11:
        flags.append("shape"); return m, flags
    if not np.isfinite(j).all():
        flags.append("nan"); j = np.nan_to_num(j)
    if abs(dt - 0.01) > 1e-9:
        flags.append("dt_mismatch")
    if "time" in d:
        t = np.asarray(d["time"], float)
        if len(t) != n or (n > 1 and (np.abs(np.diff(t) - dt).max() > 1e-6 or abs(t[0]) > 1e-6)):
            flags.append("time_axis")
    if "joints_rad" in d:
        jr = np.asarray(d["joints_rad"], float)
        if jr.shape == j.shape and np.nanmax(np.abs(np.rad2deg(jr) - j)) > 0.01:
            flags.append("deg_rad_mismatch")
    top, imp, src = get_events(d)
    m["event_source"] = src
    if top is None:
        flags.append("events_missing")
    else:
        dur = (n - 1) * dt
        m.update(t_top=round(top, 3), t_impact=round(imp, 3))
        if not (0 <= top < imp):
            flags.append("events_order")
        if imp > dur + 1e-6 or top < 0:
            flags.append("events_out_of_range")
        ds = imp - top
        m["downswing_s"] = round(ds, 3)
        if ds < DOWNSWING_RANGE[0] or ds > DOWNSWING_RANGE[1]:
            flags.append("downswing_implausible")
        tk = float(d["takeaway_s"]) if "takeaway_s" in d else (
            float(d["t_takeaway"]) - float(d["t_start_in_video"]) if "t_takeaway" in d and "t_start_in_video" in d else None)
        if tk is not None:
            bs = top - tk
            m["backswing_s"] = round(bs, 3)
            if bs < BACKSWING_RANGE[0] or bs > BACKSWING_RANGE[1]:
                flags.append("backswing_implausible")
        sp = arm_speed(j, dt)
        lo, hi = int(max(0, round(top / dt))), min(n, int(round((imp + 0.3) / dt)) + 1)
        if hi - lo > 3:
            pk = (lo + int(np.argmax(sp[lo:hi]))) * dt
            m["arm_peak_t"] = round(pk, 3); m["impact_minus_arm_peak_s"] = round(imp - pk, 3)
            if abs(imp - pk) > PEAK_LAG_TOL:
                flags.append("impact_not_at_arm_peak")
    jump = float(np.abs(np.diff(j, axis=0)).max()) if n > 1 else 0.0
    m["max_frame_jump_deg"] = round(jump, 2)
    if jump > JUMP_DEG:
        flags.append("jump")
    if limits:
        worst = 0.0
        for c, (lo_, hi_) in limits.items():
            col = j[:, COLS.index(c)]
            worst = max(worst, float(col.max() - hi_), float(lo_ - col.min()))
        m["worst_limit_exceed_deg"] = round(worst, 2)
        if worst > LIMIT_TOL:
            flags.append("joint_limit")
    return m, flags


def mirror_pair_check(path, d):
    """If file declares mirrored_from, compare with the original's time/events/joints (swapped)."""
    src = d.get("mirrored_from")
    if src is None:
        return []
    o = path.parent / str(src)
    if not o.exists():
        return ["mirror_source_missing"]
    od = dict(np.load(o, allow_pickle=True))
    fl = []
    if len(od["joints"]) != len(d["joints"]) or abs(float(od["dt"]) - float(d["dt"])) > 1e-9:
        fl.append("mirror_pair_mismatch")
    else:
        a, b = get_events(od), get_events(d)
        if a[0] is None or b[0] is None or abs(a[0] - b[0]) > 1e-9 or abs(a[1] - b[1]) > 1e-9:
            fl.append("mirror_pair_mismatch")
        from data.mirror_references import _mirror_joints
        if np.abs(_mirror_joints(od["joints"]) - d["joints"]).max() > 1e-6:
            fl.append("mirror_pair_mismatch")
    return fl


def audit_entry(entry, root=ROOT, limits=None):
    path = Path(root) / entry["path"]
    d = {k: v for k, v in np.load(path, allow_pickle=True).items()}
    m, flags = audit_arrays(d, limits)
    flags += mirror_pair_check(path, d)
    if entry.get("effective_mirrored_on_load"):
        from data.mirror_references import mirror_dict
        md = mirror_dict(d, path.name)
        a, b = get_events(d), get_events(md)
        if a[0] is None or b[0] is None or abs(a[0] - b[0]) > 1e-9 or abs(a[1] - b[1]) > 1e-9 or len(md["joints"]) != len(d["joints"]):
            flags.append("mirror_on_load_events")
        m2, f2 = audit_arrays(md, limits)
        if "joint_limit" in f2 and "joint_limit" not in flags:
            flags.append("joint_limit_after_mirror")
    m.update(source=entry["source"], variant=entry.get("variant"), split=entry.get("split"), weight_train=entry.get("weight_train"))
    return {"path": entry["path"], "flags": sorted(set(flags)), **m}


def resample_for_control(joints, dt=0.01, ctrl_dt=0.02):
    """Linear-resample [n,11] joints from reference dt to the env control dt (index i == time i*ctrl_dt).

    Use this (or index by round(t/dt)) in any tracker that does `ref[episode_step]` with ctrl_dt != dt.
    """
    j = np.asarray(joints, float)
    t_old = np.arange(len(j)) * dt
    t_new = np.arange(0.0, t_old[-1] + 1e-9, ctrl_dt)
    return np.stack([np.interp(t_new, t_old, j[:, k]) for k in range(j.shape[1])], axis=1)


def env_control_dt_check(root=ROOT):
    """Read-only text scan of env/humanoid_golf_env.py: control dt vs index-by-step reference playback."""
    p = Path(root) / "env" / "humanoid_golf_env.py"
    if not p.exists():
        return {"checked": False}
    t = p.read_text()
    ctrl = re.search(r"self\.substeps\s*=\s*int\(round\(([\d.]+)\s*/", t)
    idx = "min(len(self.reference[\"joints\"]) - 1, self.episode_steps)" in t
    resamples = bool(re.search(r"resample|np\.interp|ref_dt|reference\[\"dt\"\]", t.replace('"dt": float(data["dt"])', "")))
    cdt = float(ctrl.group(1)) if ctrl else None
    risk = bool(cdt and idx and not resamples and abs(cdt - 0.01) > 1e-9)
    return {"checked": True, "env_ctrl_dt_s": cdt, "ref_indexed_by_episode_step": idx, "env_resamples_reference": resamples,
            "reference_dt_s": 0.01, "playback_speed_factor_if_unresampled": (round(cdt / 0.01, 3) if cdt else None),
            "RISK_reference_plays_fast": risk,
            "note": "Heuristic text scan of env (read-only). If RISK is true, a ref of dt 0.01 indexed by 0.02 s control steps plays at 2x unless the trainer pre-resamples (resample_for_control)."}


def run(root=ROOT):
    man = json.loads((Path(root) / "data" / "reference_sets" / "unified_v1.json").read_text())
    limits = joint_limits(Path(root) / "env" / "models" / "humanoid_golf.xml")
    files = [audit_entry(e, root, limits) for e in man["entries"]]
    counts = {}
    by_src = {}
    for f in files:
        for fl in f["flags"]:
            counts[fl] = counts.get(fl, 0) + 1
            by_src.setdefault(f["source"], {}).setdefault(fl, 0)
            by_src[f["source"]][fl] += 1
    wsum = {}
    for f in files:
        for fl in f["flags"]:
            wsum[fl] = round(wsum.get(fl, 0) + (f.get("weight_train") or 0), 4)
    return {"manifest": man.get("version"), "n_files": len(files), "joint_limits_deg": limits,
            "thresholds": {"downswing_s": DOWNSWING_RANGE, "backswing_s": BACKSWING_RANGE, "peak_lag_tol_s": PEAK_LAG_TOL,
                           "jump_deg_per_frame": JUMP_DEG, "limit_tol_deg": LIMIT_TOL, "note": "heuristic, unverified"},
            "env_control_dt_check": env_control_dt_check(root),
            "flag_counts": dict(sorted(counts.items())), "flag_counts_by_source": by_src,
            "train_weight_mass_by_flag": wsum, "files": files}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--print", action="store_true"); ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    rep = run()
    Path(a.out).write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: rep[k] for k in ("n_files", "flag_counts", "flag_counts_by_source", "train_weight_mass_by_flag")}, indent=1))
    if a.print:
        for f in rep["files"]:
            print(f["path"].split("/")[-1], f["flags"], f.get("impact_minus_arm_peak_s"), f.get("downswing_s"))


if __name__ == "__main__":
    main()

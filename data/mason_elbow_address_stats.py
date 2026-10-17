"""Elbow-at-address statistics from reference swings, in the env's joint convention.

Read-only analysis (does not modify env/, eval/, train/).  Run:
    python -m data.mason_elbow_address_stats [--out data/references/mason_elbow_address_stats.json]

Mapping (verified by reading env/humanoid_golf_env.py and env/models/*.xml, NOT by running training):
  reference column 2 ('right_elbow', degrees, flexion >= 0)  ->  env joint 'right_elbow'
  (hinge axis 0 1 0, range 0..150 deg in v3/v4_power XML, same sign; env resets via
  qpos[_q_el] = deg2rad(20) + U(-el_noise, el_noise), default el_noise 0.1 rad).
  CAUTION: the imitation reward compares reference columns to qpos[14:25] POSITIONALLY; that matches the
  reference column order only for humanoid_golf.xml / humanoid_golf_v2.xml, not for v3 / v4_power (see doc).
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ELBOW_COL = 2
ELBOW_LIMIT_DEG = (0.0, 150.0)       # env/models/humanoid_golf_v4_power.xml right_elbow range
ENV_RESET_BASE_DEG = 20.0            # env/humanoid_golf_env.py (address_pose == "fixed")
ENV_DEFAULT_EL_NOISE_RAD = 0.1
FAIL_THRESHOLD_RAD = 0.31            # seed-9000 failure threshold reported by the Orchestrator (not independently verified)
MARGIN_RAD = 0.02
ADDRESS_WIN_S = 0.06
EARLY_WIN_S = 0.2


def _stats(a):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return None
    q1, med, q3 = np.percentile(a, [25, 50, 75])
    return {"n": int(a.size), "median": float(med), "q25": float(q1), "q75": float(q3), "iqr": float(q3 - q1),
            "min": float(a.min()), "max": float(a.max()), "mean": float(a.mean()),
            "std": float(a.std(ddof=1)) if a.size > 1 else None}


def both(s):
    """Add rad twin of a degree stats dict."""
    if s is None:
        return None
    out = {"deg": s}
    out["rad"] = {k: (None if v is None else (v if k == "n" else math.radians(v))) for k, v in s.items()}
    return out


def clip_elbow(npz_path):
    z = np.load(npz_path, allow_pickle=True)
    el = np.asarray(z["joints"][:, ELBOW_COL], float)
    vm = np.asarray(z["valid_mask"]).astype(bool) if "valid_mask" in z.files else np.ones(len(el), bool)
    t = np.asarray(z["time"], float)
    ok = vm & np.isfinite(el)
    if not ok.any():
        return None
    t0 = t[ok][0]
    a = ok & (t <= t0 + ADDRESS_WIN_S)
    w = ok & (t <= t0 + EARLY_WIN_S)
    return {"address_deg": float(np.median(el[a])), "early_mean_deg": float(el[w].mean()),
            "early_min_deg": float(el[w].min()), "early_max_deg": float(el[w].max()),
            "first_valid_t_s": float(t0), "n_early_frames": int(w.sum()),
            "valid_frac_early": float(vm[t <= t0 + EARLY_WIN_S].mean()) if (t <= t0 + EARLY_WIN_S).any() else None}


def pooled(rows):
    return {"address_deg": both(_stats([r["address_deg"] for r in rows])),
            "early_window_mean_deg": both(_stats([r["early_mean_deg"] for r in rows])),
            "early_window_min_over_clips_deg": float(min(r["early_min_deg"] for r in rows)),
            "early_window_max_over_clips_deg": float(max(r["early_max_deg"] for r in rows))}


def recommend(address_deg_stats, ks=(1.0, 1.5, 2.0)):
    m, sd = address_deg_stats["mean"], address_deg_stats["std"]
    lo_floor = max(math.degrees(FAIL_THRESHOLD_RAD + MARGIN_RAD), ELBOW_LIMIT_DEG[0])
    out = {}
    for k in ks:
        lo = max(m - k * sd, lo_floor)
        hi = min(m + k * sd, ELBOW_LIMIT_DEG[1])
        c, h = (lo + hi) / 2, (hi - lo) / 2
        out[f"k={k}"] = {"low_deg": lo, "high_deg": hi, "low_rad": math.radians(lo), "high_rad": math.radians(hi),
                         "equiv_env_base_rad": math.radians(c), "equiv_env_el_noise_rad": math.radians(h)}
    return out, lo_floor


def main(out_path=None):
    kf = json.loads((ROOT / "data/references/mason_keyframe_targets.json").read_text())
    uni = json.loads((ROOT / "data/reference_sets/unified_v2.json").read_text())
    by = {Path(e["path"]).stem: e for e in uni["entries"]}
    per_clip, groups = {}, {"mason_native_left_kf_clips": [], "mason_other_v2_train_val_incl_p3_s09": [],
                            "multisense_mirrored": [], "cmu": []}
    for name, e in by.items():
        if e["split"] == "excluded":
            continue
        r = clip_elbow(ROOT / e["path"])
        if r is None:
            continue
        r.update({"source": e["source"], "split": e["split"], "mirrored_on_load": e.get("effective_mirrored_on_load"),
                  "counsel_required": e.get("counsel_required"), "license_class": e.get("license_class")})
        per_clip[name] = r
        if e["source"] == "mason":
            if name in kf["clips_used"]:
                groups["mason_native_left_kf_clips"].append(r)
            elif name.startswith("mason_v2") and "slowmo" not in name:
                groups["mason_other_v2_train_val_incl_p3_s09"].append(r)
        elif e["source"] == "multisense":
            groups["multisense_mirrored"].append(r)
        elif e["source"] == "cmu":
            groups["cmu"].append(r)
    pool = {g: pooled(v) for g, v in groups.items() if v}
    for g in pool:
        pool[g]["n_clips"] = len(groups[g])
    prim = pool["mason_native_left_kf_clips"]["address_deg"]["deg"]
    rec, floor = recommend(prim)
    below = {n: r["address_deg"] for n, r in per_clip.items() if math.radians(r["address_deg"]) < FAIL_THRESHOLD_RAD}
    env_lo = ENV_RESET_BASE_DEG - math.degrees(ENV_DEFAULT_EL_NOISE_RAD)
    res = {
        "version": "mason_elbow_address_stats_v1",
        "source_set": "unified_v2 (+ data/references/mason_keyframe_targets.json clips_used)",
        "mapping": {"reference_column_index": ELBOW_COL, "reference_column_name": "right_elbow", "env_joint": "right_elbow",
                    "units_in_reference": "degrees", "sign": "flexion positive, same as env hinge (axis 0 1 0)",
                    "env_limit_deg": list(ELBOW_LIMIT_DEG), "mapping_confidence": "high for the name->joint/sign/units map "
                    "(read from code + XML); NOT verified that a 2-D MediaPipe elbow flexion equals a 3-D hinge angle",
                    "positional_indexing_warning": "env imitation reward uses qpos[14:25] positionally; correct only for humanoid_golf.xml/v2; "
                    "in v3/v4_power qpos[14:25] starts with hips, so reference column 2 lines up with right_ankle, not the elbow",
                    "unverified": True},
        "env_reset_today": {"base_deg": ENV_RESET_BASE_DEG, "default_noise_rad": ENV_DEFAULT_EL_NOISE_RAD,
                            "range_deg": [env_lo, ENV_RESET_BASE_DEG + math.degrees(ENV_DEFAULT_EL_NOISE_RAD)],
                            "range_rad": [math.radians(ENV_RESET_BASE_DEG) - ENV_DEFAULT_EL_NOISE_RAD,
                                          math.radians(ENV_RESET_BASE_DEG) + ENV_DEFAULT_EL_NOISE_RAD],
                            "fraction_below_failure_threshold": max(0.0, (FAIL_THRESHOLD_RAD - (math.radians(ENV_RESET_BASE_DEG) - ENV_DEFAULT_EL_NOISE_RAD)) / (2 * ENV_DEFAULT_EL_NOISE_RAD)),
                            "note": "uniform noise; fraction below 0.31 rad computed from the uniform range"},
        "failure_threshold_rad": FAIL_THRESHOLD_RAD, "failure_threshold_source": "Orchestrator message (seed 9000); not reproduced here",
        "definitions": {"address_deg": f"median elbow over valid frames within {ADDRESS_WIN_S}s of the first valid frame",
                        "early_window": f"first {EARLY_WIN_S}s of valid frames: mean/min/max per clip"},
        "per_clip": per_clip, "pooled": pool,
        "clips_below_failure_threshold_at_address": below,
        "recommendation": {"based_on": "mason_native_left_kf_clips pooled per-clip address values", "candidates": rec,
                           "lower_floor_deg": floor, "preferred": "k=1.0 (keeps default el_noise 0.1, shifts base to ~0.48 rad)", "clip": "[max(mean-k*std, 0.31+0.02 rad), min(mean+k*std, 150 deg)]"},
        "caveats": [
            "Mason's stored time axis often starts after takeaway has begun ('address_in_motion' in mason_keyframe_targets.json), so the first-frame elbow is a PRIOR for address, biased toward more flexion than true address.",
            "2-D MediaPipe proxies at ~30 fps, mostly down-the-line; small n (8 clips); view dependent; UNVERIFIED.",
            "MultiSense/CMU are mirrored for comparison only; MultiSense is needs_counsel; these are statistics, not redistributed motion.",
            "The elbow at address of a real golfer is near-straight with slight flexion; a video elbow-flexion proxy and the humanoid's 'elbow' (club-grip arm geometry) are not guaranteed equivalent.",
        ],
    }
    out = Path(out_path) if out_path else ROOT / "data/references/mason_elbow_address_stats.json"
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    main(ap.parse_args().out)

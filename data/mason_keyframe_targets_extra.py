"""Per-clip keyframe targets for the REMAINING Mason clips -> data/references/mason_keyframe_targets_extra.json.

Reuses the logic of data.mason_keyframe_targets (clip_events, pose_at). Does NOT alter mason_keyframe_targets.json.
Run: python -m data.mason_keyframe_targets_extra [--out PATH]   (deterministic)

Covers every native mason_v2_* / mason_v3_* npz that is not in the main file's clips_used / clips_aux_not_in_stats.
EVERY clip here is excluded from pooling (no pooled statistics are produced); per-clip values are for inspection or for the
Trainer to opt in knowingly. Angles are 2-D-ish MediaPipe proxies, UNVERIFIED.  Slow-mo clips keep a VIDEO-time axis (stretched
by slowdown_factor_est); mirrored/right-handed clips are flagged, not corrected.  The ~25 v1 mason_swing_part* files and
*_mirrored/_refined copies are superseded duplicates and are not processed here.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from data.mason_keyframe_targets import KEYFRAMES, ROOT, clip_events, pose_at
from data.mason_target_features import JOINTS

OUT = ROOT / "data" / "references" / "mason_keyframe_targets_extra.json"
MAIN = ROOT / "data" / "references" / "mason_keyframe_targets.json"


def _g(d, k, default=None):
    if k not in d.files:
        return default
    v = d[k]
    return v.item() if v.ndim == 0 else default


def remaining_paths():
    main = json.loads(MAIN.read_text())
    done = set(main["clips_used"]) | set(main["clips_aux_not_in_stats"])
    out = []
    for p in sorted((ROOT / "data/references").glob("mason_v[23]_*.npz")):
        if p.stem not in done and "_mirrored" not in p.stem and "refined" not in p.stem:
            out.append(p)
    return out, main


def clip_entry(p, man_by_stem):
    d = np.load(p, allow_pickle=True)
    n = p.stem
    m = man_by_stem.get(n)
    flags, reasons = [], []
    if _g(d, "partial"):
        flags.append("partial")
    if "slowmo" in n:
        flags.append("slowmo_time_stretched")
    if _g(d, "handedness_verified") is False or (m and m.get("handedness_unverified")):
        flags.append("handedness_unverified")
    if str(_g(d, "handedness")) == "right":
        flags.append("detected_or_stated_right_handed")
    if _g(d, "mirrored"):
        flags.append("mirrored_copy_of_swing")
    if _g(d, "native_footage") is False:
        flags.append("not_native_footage")
    if m and m.get("split") == "excluded":
        flags.append("excluded_in_unified_v2")
    reasons.append("not in unified_v2 manifest stats set / not in mason_keyframe_targets.json" if m is None else "in unified_v2 but not used by mason_keyframe_targets.json (flagged, slow-mo or aux)")
    if n == "mason_v2_p3_s09":
        reasons.append("duplicate of mason_v2_p3_s09_unmirrored (aux in main file); this copy was mirrored from a left-handed swing")
    reasons.append("every clip in this file is excluded from pooling by design")
    e = {"view": str(_g(d, "view")), "view_confidence": _g(d, "view_confidence"), "handedness_file": str(_g(d, "handedness")),
         "handedness_detected": str(_g(d, "handedness_detected")), "handedness_verified": _g(d, "handedness_verified"),
         "quality_score": _g(d, "quality_score"), "recommended_in_v2_report": _g(d, "recommended"), "flags": flags,
         "excluded_from_pooling": True, "excluded_reasons": reasons, "unverified": True,
         "in_unified_v2_manifest": m is not None, "manifest_split": None if m is None else m.get("split")}
    if "slowmo" in n:
        e["time_stretch"] = {"slowdown_factor_est": _g(d, "slowdown_factor_est"), "axis": "VIDEO seconds (stretched); not real swing time",
                             "note": "do not use these times for a 0.02 s-step env without dividing by the slowdown factor; factor is an estimate"}
    try:
        ev = clip_events(d)
    except Exception as ex:                                  # keep going: report why
        e["events_error"] = f"{type(ex).__name__}: {ex}"
        e["keyframes"] = None
        return e
    t = d["time"].astype(float)
    ok_order = bool(np.isfinite([ev["takeaway"], ev["top"], ev["impact"]]).all() and ev["takeaway"] < ev["top"] < ev["impact"])
    e["events_s"] = {k: (round(float(ev[k]), 3) if np.isfinite(ev[k]) else None) for k in ("takeaway", "address", "top", "impact", "finish")}
    e["address_in_motion"] = ev["address_in_motion"]
    e["event_order_sane"] = ok_order
    e["event_in_axis"] = {k: bool(t[0] - 1e-9 <= ev[k] <= t[-1] + 1e-9) for k in KEYFRAMES}
    e["events_usable_for_targets"] = bool(ok_order and all(e["event_in_axis"].values()) and ev["finish"] > ev["impact"] + 1e-9)
    e["tempo_ratio_stored"] = _g(d, "tempo_ratio")
    kfs = {}
    for k in KEYFRAMES:
        if not np.isfinite(ev[k]):
            kfs[k] = None
            continue
        pj, nv = pose_at(d, ev[k])
        kfs[k] = {"t_s": round(float(ev[k]), 3), "valid_rows": nv,
                  "joints_deg": {JOINTS[j]: (None if not np.isfinite(x) else round(float(x), 1)) for j, x in enumerate(pj)}}
    e["keyframes"] = kfs
    e["leg_valid_frame_ratio"] = _g(d, "leg_valid_frame_ratio")
    return e


def build():
    paths, main = remaining_paths()
    uni = json.loads((ROOT / "data/reference_sets/unified_v2.json").read_text())
    by = {Path(x["path"]).stem: x for x in uni["entries"]}
    clips = {p.stem: clip_entry(p, by) for p in paths}
    return {"version": "mason_keyframes_extra_v1", "unverified": True, "companion_of": "data/references/mason_keyframe_targets.json (unchanged)",
            "joint_columns": JOINTS, "units": "degrees; times in seconds on each clip's own joint-time axis",
            "pooling": "none: every clip here is excluded_from_pooling=True; no aggregate statistics",
            "clips_in_main_file": sorted(set(main["clips_used"]) | set(main["clips_aux_not_in_stats"])),
            "n_clips": len(clips), "clips": clips,
            "caveats": ["2-D-ish MediaPipe proxies from ~30 fps screen-recorded feed clips; view-dependent, UNVERIFIED, not 3-D humanoid joint angles.",
                        "Flags are carried from the npz / unified_v2 manifest; handedness-unverified, right-handed-detected, mirrored and partial clips must not be trained on as 'Mason left-handed' without confirmation.",
                        "Events are landmark-inferred (+-1 frame ~33 ms) and offset-corrected as in the main file; 'events_usable_for_targets' / 'event_order_sane' / 'event_in_axis' show which clips have usable events.",
                        "Instagram-derived: third-party content unreviewed (docs/RELEASE_QUESTIONS_FOR_COUNSEL.md)."]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(OUT)); a = ap.parse_args()
    Path(a.out).write_text(json.dumps(build(), indent=1) + "\n"); print("wrote", a.out)


if __name__ == "__main__":
    main()

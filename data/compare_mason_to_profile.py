"""Mason-vs-style-profile comparison -> docs/MASON_VS_PROFILES.md + data/references/mason_vs_profiles.json.

Run: python -m data.compare_mason_to_profile [--mason PATH] [--profiles PATH] [--out-json P] [--out-md P]
Deterministic (no timestamps).

Design (see docs/research_pro_swing_profiles.md section 'Mason vs profile design'):
 1. Mason feature set = only what the video pipeline / self-report can support:
      tempo_ratio, backswing_s, downswing_s (video-derived, ~30 fps, loose)
      club_head_speed_mph (SELF-REPORTED 120, not measured)
    Each has value, uncertainty (abs, 1 sigma-ish) and a trust weight 0..1.
 2. For each profile & feature with a profile target (unverified targets kept but down-weighted):
      delta        = mason - target
      band_pos     = 0.5 + delta/(max-min)   (0.5 = on target, 0/1 = band edges, outside <0 / >1)
                     band falls back to an ASSUMED relative tolerance when min/max missing
      significance = |delta| / sqrt(half_band^2 + mason_unc^2)       (dimensionless; <1 = within noise)
      priority     = significance * mason_trust * profile_conf_w * (0.5 if profile unverified)
 3. Rank by priority; wording is hedged by trust. Gaps within noise -> 'no change indicated'.
 4. Features Mason cannot yet supply (x-factor, pelvis/thorax turn & speeds, club/ball speed
    measured, launch, spin, attack angle, setup) are listed as 'measure next', never scored.
Percentile-like position is a band position, NOT a population percentile.
"""
import argparse, json, math, os

ROOT = os.path.join(os.path.dirname(__file__), "..")
MASON = os.path.join(ROOT, "data", "references", "mason_target_features.json")
PROFILES = os.path.join(ROOT, "data", "references", "pro_swing_profiles.json")
OUT_JSON = os.path.join(ROOT, "data", "references", "mason_vs_profiles.json")
OUT_MD = os.path.join(ROOT, "docs", "MASON_VS_PROFILES.md")

CONF_W = {"high": 1.0, "medium": 0.75, "low": 0.4, "none": 0.0}
ASSUMED_REL_TOL = {"tempo_ratio": 0.10, "backswing_s": 0.10, "downswing_s": 0.10, "club_head_speed_mph": 0.05}
SELF_REPORTED_CHS = 120.0  # power_profile_350yd_targets.json mason_gap (self-reported, +3 hcp, 120+ mph)

PLAIN = {
 "tempo_ratio": "backswing:downswing timing ratio",
 "backswing_s": "backswing duration",
 "downswing_s": "downswing duration",
 "club_head_speed_mph": "driver club-head speed",
}
MEASURE_NEXT = [
 ("club_head_speed_mph_measured", "Launch-monitor club/ball speed, smash, launch, spin, attack angle (one 20-shot session)"),
 ("tempo_240fps", "240 fps down-the-line + face-on video of 20+ driver swings to get a trustworthy tempo ratio and downswing time"),
 ("pelvis_thorax_turn_x_factor", "3-D/markerless pelvis & thorax turn and X-factor at top (needs face-on 120+ fps or 3-D capture)"),
 ("segment_peak_speeds", "Pelvis/thorax/arm peak angular speeds and their order (kinematic sequence)"),
 ("setup", "Stance width, ball position, shaft lean at address (a still face-on and DTL photo with a club on the ground works)"),
]


def mason_features(m):
    a = m["mason"]["aggregate"]
    t = a["tempo_ratio"]
    rel = a["tempo_rel_uncertainty"]["median"]
    feats = {
     "tempo_ratio": {"value": t["median"], "iqr": t["iqr"], "unc": rel * t["median"], "trust": 0.35, "n": t["n"],
                     "note": "~30 fps screen recordings; downswing only 4-6 frames; per-swing rel. uncertainty ~%.0f%%" % (100 * rel)},
     "backswing_s": {"value": a["backswing_s"]["median"], "iqr": a["backswing_s"]["iqr"], "unc": 0.05, "trust": 0.2, "n": a["backswing_s"]["n"],
                     "note": "absolute durations from edited/possibly sped-up feed clips are unreliable (0.48 s would be extraordinarily fast); trust the ratio more than the seconds"},
     "downswing_s": {"value": a["downswing_s"]["median"], "iqr": a["downswing_s"]["iqr"], "unc": 0.06, "trust": 0.2, "n": a["downswing_s"]["n"],
                     "note": "likely under-detected (4-6 frames); slow-mo clips suggest ~0.17-0.23 s true; treat as suspect"},
     "club_head_speed_mph": {"value": SELF_REPORTED_CHS, "iqr": None, "unc": 3.0, "trust": 0.5, "n": 0,
                     "note": "SELF-REPORTED (120+ mph), not measured; video cannot measure club speed"},
    }
    return feats


def _band(feat, pf):
    tgt = pf["target"]
    lo, hi = pf.get("min"), pf.get("max")
    assumed = False
    tol = ASSUMED_REL_TOL.get(feat, 0.1) * abs(tgt)
    if lo is None or hi is None or hi <= lo:
        lo, hi, assumed = tgt - tol, tgt + tol, True
    elif (hi - lo) / 2.0 < 0.5 * tol:  # published band narrower than half the assumed tolerance: widen
        lo, hi, assumed = min(lo, tgt - 0.5 * tol), max(hi, tgt + 0.5 * tol), True
    return lo, hi, assumed


def compare(mason, profiles):
    mf = mason_features(mason)
    out = {}
    for pid, p in profiles["profiles"].items():
        rows = []
        for feat, mv in mf.items():
            pf = p["features"].get(feat)
            if not pf or pf.get("target") is None:
                continue
            lo, hi, assumed = _band(feat, pf)
            tgt = pf["target"]
            delta = mv["value"] - tgt
            half = (hi - lo) / 2.0
            sig = abs(delta) / math.sqrt(half ** 2 + mv["unc"] ** 2)
            unv = bool(pf.get("unverified"))
            w = CONF_W.get(pf.get("confidence", "none"), 0.0) * (0.5 if unv else 1.0)
            pri = sig * mv["trust"] * w
            rows.append({
             "feature": feat, "unit": pf["unit"], "mason": round(mv["value"], 4), "profile_target": tgt,
             "profile_band": [round(lo, 4), round(hi, 4)], "band_assumed": assumed,
             "delta": round(delta, 4), "band_position": round(0.5 + delta / (hi - lo), 3),
             "significance": round(sig, 3), "priority": round(pri, 3),
             "profile_confidence": pf.get("confidence"), "profile_unverified": unv,
             "mason_trust": mv["trust"], "mason_note": mv["note"], "profile_sources": pf.get("source_ids", []),
             "direction": "above" if delta > 0 else ("below" if delta < 0 else "on"),
             "within_noise": sig < 1.0,
            })
        rows.sort(key=lambda r: -r["priority"])
        out[pid] = rows
    return mf, out


def advice(r, label):
    name = PLAIN[r["feature"]]
    if r["within_noise"] and r["feature"] != "club_head_speed_mph":
        return "%s: no change indicated vs %s (gap %+.2f %s is inside the measurement noise)." % (name.capitalize(), label, r["delta"], r["unit"])
    if r["feature"] == "club_head_speed_mph":
        return "Speed gap vs %s: %+.1f mph (%.1f vs %.1f; Mason's value is SELF-REPORTED). Not a technique item; get a launch-monitor number first, then use the speed-training/mobility plan." % (label, r["delta"], r["mason"], r["profile_target"])
    word = "higher" if r["direction"] == "above" else "lower"
    base = "%s is %s than the %s target (%.2f vs %.2f %s)" % (name.capitalize(), word, label, r["mason"], r["profile_target"], r["unit"])
    if r["feature"] == "backswing_s":
        return base + " -- absolute seconds from feed clips are unreliable (possible speed edits, ~30 fps); do not act on this; re-film at 240 fps."
    if r["feature"] == "downswing_s":
        return base + " -- probably a ~30 fps detection artifact; re-measure at 240 fps before changing anything."
    if r["feature"] == "tempo_ratio":
        return base + " -- loose band only (30 fps); confirm at 240 fps before drilling tempo."
    return base + "."


def build(mason, profiles):
    mf, per = compare(mason, profiles)
    labels = {pid: p["label"].split(" (")[0].replace("-style profile", " style profile") for pid, p in profiles["profiles"].items()}
    overall = {}
    for pid, rows in per.items():
        if profiles["profiles"][pid]["kind"] != "style_profile":
            continue
        for r in rows:
            overall.setdefault(r["feature"], []).append(r["priority"])
    ranked = sorted(({"feature": f, "mean_priority": round(sum(v) / len(v), 3), "n_profiles": len(v)} for f, v in overall.items()),
                    key=lambda x: -x["mean_priority"])
    what = []
    for pid, rows in per.items():
        what.append({"profile": pid, "label": labels[pid],
                     "items": [dict(r, advice=advice(r, labels[pid])) for r in rows]})
    return {
     "schema": "mason_vs_profiles/v1",
     "generated_by": "python -m data.compare_mason_to_profile",
     "mason_features": {k: {kk: vv for kk, vv in v.items()} for k, v in mf.items()},
     "per_profile": what,
     "overall_ranking_style_profiles": ranked,
     "measure_next": [{"id": i, "what": w} for i, w in MEASURE_NEXT],
     "not_scored": ["x_factor_top_deg", "pelvis_turn_top_deg", "thorax_turn_top_deg", "pelvis/thorax/arm peak speeds",
                    "ball_speed/smash/launch/spin/attack_angle", "setup (stance, ball position, shaft lean)"],
     "caveats": [
      "Mason's tempo comes from ~30 fps video (downswing 4-6 frames); treat as a loose band only (+-~27%).",
      "Club speed is unavailable from video; the 120 mph value is self-reported and unverified.",
      "Mason's joint features are 2-D proxies and have no counterpart in published profile stats, so they are NOT compared.",
      "band_position is position inside a plausibility band (0.5 = target), not a population percentile.",
      "Profiles are style profiles from published numbers (some unverified); not simulations of real persons. Internal reference only; counsel review before any external use.",
      "Priority ranks where a gap is both large relative to noise and trustworthy; it is not a coaching prescription. Consult a coach/fitter.",
     ],
    }


def to_md(res):
    L = ["# Mason vs style profiles", "",
         "Auto-generated by `python -m data.compare_mason_to_profile` (deterministic). Internal reference only; "
         "style profiles from published stats (see `docs/research_pro_swing_profiles.md`), **not** simulations of real persons.", "",
         "## Read this first", ""] + ["- " + c for c in res["caveats"]] + ["", "## Mason inputs", "",
         "| feature | value | ~uncertainty | trust | note |", "|---|---|---|---|---|"]
    for k, v in res["mason_features"].items():
        L.append("| %s | %.3f | +-%.2f | %.2f | %s |" % (k, v["value"], v["unc"], v["trust"], v["note"]))
    L += ["", "## What to change (overall, style profiles averaged)", ""]
    for i, r in enumerate(res["overall_ranking_style_profiles"], 1):
        L.append("%d. `%s` - mean priority %.2f over %d profiles" % (i, r["feature"], r["mean_priority"], r["n_profiles"]))
    for p in res["per_profile"]:
        L += ["", "## vs %s" % p["label"], "", "| feature | Mason | target (band) | delta | band pos | signif. | priority | profile conf. |", "|---|---|---|---|---|---|---|---|"]
        for r in p["items"]:
            L.append("| %s | %.3f | %.3f (%.3f-%.3f%s) | %+.3f | %.2f | %.2f | %.2f | %s%s |" % (
                r["feature"], r["mason"], r["profile_target"], r["profile_band"][0], r["profile_band"][1],
                "*" if r["band_assumed"] else "", r["delta"], r["band_position"], r["significance"], r["priority"],
                r["profile_confidence"], " (unverified)" if r["profile_unverified"] else ""))
        L.append("")
        L.append("`*` = band assumed from a relative tolerance (profile gave no min/max).")
        L.append("")
        for r in p["items"]:
            L.append("- " + r["advice"])
    L += ["", "## Measure next (not scored)", ""] + ["- **%s**: %s" % (m["id"], m["what"]) for m in res["measure_next"]]
    L += ["", "Not scored (no Mason counterpart): " + ", ".join(res["not_scored"]) + ".", ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mason", default=MASON)
    ap.add_argument("--profiles", default=PROFILES)
    ap.add_argument("--out-json", default=OUT_JSON)
    ap.add_argument("--out-md", default=OUT_MD)
    a = ap.parse_args(argv)
    with open(a.mason) as f:
        m = json.load(f)
    with open(a.profiles) as f:
        p = json.load(f)
    res = build(m, p)
    os.makedirs(os.path.dirname(a.out_json), exist_ok=True)
    os.makedirs(os.path.dirname(a.out_md), exist_ok=True)
    with open(a.out_json, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(a.out_md, "w") as f:
        f.write(to_md(res))
    print("wrote", a.out_json, a.out_md)
    return res


if __name__ == "__main__":
    main()

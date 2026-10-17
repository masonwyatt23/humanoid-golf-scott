"""Launch-monitor / hole-play output layer. Reads gate / shot JSON(s) (read-only) and emits per-shot (or per-policy-aggregate)
carry, total, spin, launch, smash, ball speed, club speed in launch-monitor units (yd, mph, deg, rpm) with gate flags.

Accepted inputs (auto-detected):
  * per-shot list  (e.g. results/shots_*.json from eval): [{carry_yd|carry(m), total_yd|total_dist(m), launch_elev_deg, ball_speed_sep|peak_ball_speed (m/s),
      impact_club_speed (m/s), final_y (m), spin_rpm|backspin_rpm (optional), true_contact}, ...]
  * eval.eval_gate JSON: {policy_det|policy_stoch|scripted_zero_residual: {mean_carry(_yd), mean_distance|mean_total_yd, launch_elev_mean_deg, smash_factor_mean, peak_club_mph_mean ...}}
    -> one AGGREGATE row per policy (mean of episodes, not a shot). Metres converted at 1.0936 yd/m.
Spin is absent from today's gate / shot JSONs: it is emitted as null with spin_source="absent" unless the shot carries it. `--ref-spin` adds a
reference-table spin for the shot's club speed, clearly labelled reference_lookup (NOT measured).
Smash/spin limits: published sources, see docs/LAUNCH_TARGETS_120_132.md (data/references/launch_targets_120_132_limits.json on branch launch-tables-only); constants copied below.
Usage: python -m data.launch_output results/shots_x.json [more.json ...] [--hole-yd 450] [--ref-spin] [--json out.json] [--md out.md]
Never edits inputs. Nothing here is a measurement of a person."""
import json, sys, math, argparse
from pathlib import Path

MPS_TO_MPH = 2.23694
M_TO_YD = 1.0936
SMASH_CEIL, SMASH_WARN_HI, SMASH_WARN_LO = 1.50, 1.49, 1.30          # TrackMan 'near 1.50', tour 1.49; WARN_LO derived
SPIN_PASS = (1800, 3000); SPIN_WARN = (1500, 3500); SPIN_FAIL = (1200, 4000)   # derived from published windows (driver, 120-132 mph); NOT published thresholds
LAUNCH_GATE = (5.0, 20.0)                                              # eval_gate headline launch window
# reference spin (rpm) by club speed, driver, TrackMan optimizer AoA 0 rows (published 75/90/105/120; 130+ extrapolated) - reference only
REF_SPIN = [(75, 3121), (90, 3093), (105, 3040), (120, 2890), (130, 2790), (132, 2770)]

def _ref_spin(mph):
    pts = REF_SPIN
    if mph <= pts[0][0]: return pts[0][1]
    for (a, x), (b, y) in zip(pts, pts[1:]):
        if mph <= b: return round(x + (y - x) * (mph - a) / (b - a))
    return pts[-1][1] - round(10 * (mph - pts[-1][0]))

def flags(row):
    f = []; s = row.get("smash"); sp = row.get("spin_rpm"); la = row.get("launch_deg")
    if s is not None:
        if s > SMASH_CEIL: f.append("FAIL smash>1.50")
        elif s > SMASH_WARN_HI: f.append("WARN smash>1.49")
        elif s < SMASH_WARN_LO: f.append("WARN smash<1.30 (poor/non-physical contact?)")
    if sp is not None:
        if sp < SPIN_FAIL[0] or sp > SPIN_FAIL[1]: f.append("FAIL spin")
        elif not (SPIN_WARN[0] <= sp <= SPIN_WARN[1]): f.append("WARN spin")
        elif not (SPIN_PASS[0] <= sp <= SPIN_PASS[1]): f.append("WARN spin")
    if la is not None and not (LAUNCH_GATE[0] <= la <= LAUNCH_GATE[1]): f.append("WARN launch outside 5-20 deg")
    return f

def _pick(d, *keys):
    for k in keys:
        if d.get(k) is not None: return d[k], k
    return None, None

def shot_row(i, s, hole_yd=None, ref_spin=False, label=None):
    carry, ck = _pick(s, "carry_yd", "mean_carry_yd", "carry", "mean_carry")
    if carry is not None and ck in ("carry", "mean_carry"): carry *= M_TO_YD
    total, tk = _pick(s, "total_yd", "mean_total_yd", "total_dist", "mean_distance", "mean_total_m")
    if total is not None and tk in ("total_dist", "mean_distance", "mean_total_m"): total *= M_TO_YD
    bs, bk = _pick(s, "ball_speed_sep", "peak_ball_speed", "mean_peak_ball_speed")
    ball = bs * MPS_TO_MPH if bs is not None else None
    cs, _ = _pick(s, "impact_club_speed", "impact_club_speed_mean")
    club = cs * MPS_TO_MPH if cs is not None else (s["peak_club_mph_mean"] if s.get("peak_club_mph_mean") is not None else None)
    smash, _ = _pick(s, "smash_factor_mean")
    note = []
    if smash is None and ball and club: smash = ball / club
    if bk == "peak_ball_speed": note.append("ball speed is peak_ball_speed (not separation speed); smash may be inflated")
    spin, spk = _pick(s, "spin_rpm", "backspin_rpm")
    spin_source = "measured/simulated (in input)" if spin is not None else "absent"
    row = dict(index=i, label=label, carry_yd=_r(carry, 1), total_yd=_r(total, 1), spin_rpm=_r(spin, 0), spin_source=spin_source,
               launch_deg=_r(_pick(s, "launch_elev_deg", "launch_elev_mean_deg")[0], 2), smash=_r(smash, 3), ball_mph=_r(ball, 1), club_mph=_r(club, 1),
               contact=s.get("true_contact", s.get("contact_rate")), aggregate=label is not None)
    if ref_spin and club: row["ref_spin_rpm_reference_lookup"] = _ref_spin(club)
    if hole_yd is not None and total is not None:
        lat = s.get("final_y", s.get("mean_y"))
        lat_yd = lat * M_TO_YD if lat is not None else 0.0
        row["remaining_to_pin_yd"] = round(math.hypot(hole_yd - total, lat_yd), 1); row["lateral_yd"] = round(lat_yd, 1) if lat is not None else None
    if row["smash"] is not None and row["smash"] < 1.0: note.append("smash<1.0: ball speed/club speed from the input is not a ball-separation ratio (check input)")
    row["flags"] = flags(row); row["notes"] = note
    return row

def _r(x, n): return None if x is None else round(float(x), n)

def rows_from(path, hole_yd=None, ref_spin=False):
    j = json.load(open(path)); name = Path(path).name
    if isinstance(j, list):
        return [dict(source=name, **shot_row(i, s, hole_yd, ref_spin)) for i, s in enumerate(j)]
    rows = []
    for pol in ("policy_det", "policy_stoch", "scripted_zero_residual"):
        if isinstance(j.get(pol), dict): rows.append(dict(source=name, **shot_row(len(rows), j[pol], hole_yd, ref_spin, label=pol)))
    if not rows and isinstance(j.get("seeds"), dict):   # *_summary.json
        for sd, v in j["seeds"].items():
            for pol, m in v.items(): rows.append(dict(source=name, **shot_row(len(rows), m, hole_yd, ref_spin, label=f"seed{sd}/{pol}")))
    if not rows: raise ValueError(f"{path}: unrecognised gate/shot JSON")
    return rows

def to_md(rows):
    h = "| src | row | carry yd | total yd | spin rpm | launch deg | smash | ball mph | club mph | flags |\n|---|---|---|---|---|---|---|---|---|---|\n"
    f = lambda v: "-" if v is None else v
    return h + "\n".join(f"| {r['source']} | {r['label'] or r['index']} | {f(r['carry_yd'])} | {f(r['total_yd'])} | {f(r['spin_rpm'])} | {f(r['launch_deg'])} | {f(r['smash'])} | {f(r['ball_mph'])} | {f(r['club_mph'])} | {'; '.join(r['flags']) or 'ok'} |" for r in rows)

def summarize(rows):
    sh = [r for r in rows if not r["aggregate"]]
    if not sh: return {}
    import statistics as st
    g = lambda k: [r[k] for r in sh if r[k] is not None]
    return {k: dict(n=len(g(k)), mean=round(st.fmean(g(k)), 2), median=round(st.median(g(k)), 2), max=max(g(k))) for k in ("carry_yd", "total_yd", "launch_deg", "smash", "ball_mph") if g(k)} | dict(n_shots=len(sh), n_fail=sum(any(x.startswith("FAIL") for x in r["flags"]) for r in sh))

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("inputs", nargs="+"); ap.add_argument("--hole-yd", type=float); ap.add_argument("--ref-spin", action="store_true")
    ap.add_argument("--json"); ap.add_argument("--md"); a = ap.parse_args(argv)
    rows = [r for p in a.inputs for r in rows_from(p, a.hole_yd, a.ref_spin)]
    out = dict(units="yd, mph, deg, rpm; metres converted at 1.0936", limits_doc="docs/LAUNCH_TARGETS_120_132.md", rows=rows, summary=summarize(rows))
    if a.json: Path(a.json).write_text(json.dumps(out, indent=1))
    md = to_md(rows)
    if a.md: Path(a.md).write_text(md + "\n")
    print(md); print(json.dumps(out["summary"]))
    return out

if __name__ == "__main__":
    main()

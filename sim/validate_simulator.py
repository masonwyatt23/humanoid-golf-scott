"""Validate sim/golf_simulator.py against PUBLISHED TrackMan PGA Tour driver averages.   python -m sim.validate_simulator
Writes results/golf_simulator_validation.md/.json.

VERIFIED benchmark (one self-consistent row; read from TrackMan's published PGA Tour averages table and the USGA 'Equipment Specifications Research' Table 2):
  club 113 mph, attack angle -1.3 deg, ball 167 mph, smash 1.48, launch 10.9 deg, spin 2686 rpm, max height 32 yd (29 m), land angle 38 deg, carry 275 yd (251 m)
  sources: https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf  (meters table: carry 251 m, height 29 m; yards table: 275 yd, 32 yd)
           https://www.usga.org/content/dam/usga/pdf/Equipment/Equipment%20Specifications%20Research.pdf (Table 2: 113 / 167 / 10.9 deg / 2686 rpm)
NOT used as pass/fail: a 282 yd carry figure. It belongs to a different (2023-24, 115 mph / 171 mph / 10.4 deg / 2545 rpm) row that is only available to us from
  secondary web reports, not from the TrackMan table we could read. It is shown as an informational row only.
"""
import json, os, datetime
import numpy as np
from sim.golf_simulator import shot_from_launch, shot_from_club

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BENCH = dict(club_mph=113, attack_deg=-1.3, ball_mph=167, smash=1.48, launch_deg=10.9, spin_rpm=2686, apex_yd=32, land_angle_deg=38, carry_yd=275)
SRC = ["https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf",
       "https://www.usga.org/content/dam/usga/pdf/Equipment/Equipment%20Specifications%20Research.pdf"]
# tolerance: relative for lengths/speeds, absolute for angles
TOL = dict(carry_yd=("rel", 0.05), apex_yd=("rel", 0.10), land_angle_deg=("abs", 3.0), smash=("rel", 0.03), ball_mph=("rel", 0.03),
           launch_deg=("abs", 1.0), backspin_rpm=("rel", 0.10))


def _chk(name, got, ref):
    kind, t = TOL[name]
    err = (got - ref) / ref if kind == "rel" else got - ref
    return dict(metric=name, model=float(got), published=float(ref), error=float(err), error_kind="% /100" if kind == "rel" else "abs", tol=t, passed=bool(abs(err) <= t))


def run():
    b = BENCH
    # 1. flight model from the published launch conditions (this is what the model was calibrated for)
    s1 = shot_from_launch(b["ball_mph"], b["launch_deg"], b["spin_rpm"], club_mph=b["club_mph"])
    c1 = [_chk("carry_yd", s1.carry_yd, b["carry_yd"]), _chk("apex_yd", s1.apex_yd, b["apex_yd"]),
          _chk("land_angle_deg", s1.land_angle_deg, b["land_angle_deg"]), _chk("smash", s1.smash, b["smash"])]
    # 2. impact model: club speed -> ball speed / smash (center hit), then pick dynamic loft giving launch 10.9 at AoA -1.3
    lofts = np.arange(10, 18.01, 0.25)
    sc = [shot_from_club(b["club_mph"], b["attack_deg"], L) for L in lofts]
    i = int(np.argmin([abs(s.launch_deg - b["launch_deg"]) for s in sc])); s2 = sc[i]
    c2 = [_chk("ball_mph", s2.ball_mph, b["ball_mph"]), _chk("smash", s2.smash, b["smash"]), _chk("launch_deg", s2.launch_deg, b["launch_deg"]),
          _chk("backspin_rpm", s2.backspin_rpm, b["spin_rpm"]), _chk("carry_yd", s2.carry_yd, b["carry_yd"]), _chk("apex_yd", s2.apex_yd, b["apex_yd"])]
    # 3. informational: secondary-source 2023-24 row (NOT verified from the primary table)
    s3 = shot_from_launch(171, 10.4, 2545, club_mph=115)
    # 4. sensitivity (model-internal sanity, not published benchmarks)
    base = shot_from_launch(167, 10.9, 2686); fast = shot_from_launch(177, 10.9, 2686); hi = shot_from_launch(167, 10.9, 3686)
    sens = dict(plus10mph_ball_carry_yd=fast.carry_yd - base.carry_yd, plus1000rpm_carry_yd=hi.carry_yd - base.carry_yd)
    out = dict(generated=datetime.datetime.now().isoformat(timespec="seconds"), label="model-based validation vs published TrackMan PGA Tour averages",
               benchmark=b, sources=SRC,
               flight_from_published_launch=dict(shot=s1.as_dict(), checks=c1),
               impact_model=dict(dynamic_loft_deg=float(lofts[i]), shot=s2.as_dict(), checks=c2),
               secondary_row_info_only=dict(inputs="115 mph club, 171 mph ball, 10.4 deg, 2545 rpm (secondary reports, unverified)", shot=s3.as_dict(), reported_carry_yd_secondary=282),
               sensitivity=sens)
    out["all_flight_checks_passed"] = all(c["passed"] for c in c1)
    out["all_impact_checks_passed"] = all(c["passed"] for c in c2)
    json.dump(out, open(os.path.join(ROOT, "results", "golf_simulator_validation.json"), "w"), indent=1)
    md = ["# Golf simulator validation (model-based, analytic ball model)", "",
          "Benchmark: **TrackMan PGA Tour driver average** (113 mph club, AoA -1.3 deg, 167 mph ball, smash 1.48, launch 10.9 deg, 2686 rpm, max height 32 yd, land angle 38 deg, carry 275 yd = 251 m).",
          "Sources: " + "; ".join(SRC), "",
          "Note: the 282 yd carry in the request belongs to a different 2023-24 row (115 mph / 171 mph / 10.4 deg / 2545 rpm) that we only have from secondary web reports; the primary TrackMan row we could read gives 275 yd for 113 mph. 282 yd is therefore informational only.", "",
          "## 1. Flight model from published launch conditions (167 mph, 10.9 deg, 2686 rpm)", "",
          "| metric | model | published | error | tolerance | pass |", "|---|---|---|---|---|---|"]
    def rows(cs): return [f"| {c['metric']} | {c['model']:.2f} | {c['published']:.2f} | {c['error']*100 if c['error_kind'].startswith('%') else c['error']:+.1f}{'%' if c['error_kind'].startswith('%') else ''} | {c['tol']*100 if c['error_kind'].startswith('%') else c['tol']:.0f}{'%' if c['error_kind'].startswith('%') else ''} | {'PASS' if c['passed'] else 'FAIL'} |" for c in cs]
    md += rows(c1) + ["", f"Model total (carry + bounce/roll, fairway): {s1.total_yd:.0f} yd; hang {s1.hang_s:.1f} s. (TrackMan table above gives carry only; total is not benchmarked.)", "",
          f"## 2. Impact model (club 113 mph, AoA -1.3 deg, dynamic loft {lofts[i]:.2f} deg chosen so launch = 10.9 deg)", "", "| metric | model | published | error | tolerance | pass |", "|---|---|---|---|---|---|"] + rows(c2)
    md += ["", "Reading: the impact model gets smash/ball speed right but over-predicts backspin (simple center-hit friction model, no gear effect/loft-spin nuance), which lowers carry and raises apex. "
           "Use `shot_from_launch` when spin is known; treat `shot_from_club` spin as indicative only.", "",
          "## 3. Informational (secondary-source row, not pass/fail)", "", f"115 mph / 171 mph / 10.4 deg / 2545 rpm -> model carry {s3.carry_yd:.0f} yd, apex {s3.apex_yd:.0f} yd (secondary reports quote ~282 yd carry).", "",
          "## 4. Sensitivities (model-internal sanity, not benchmarks)", "", f"- +10 mph ball speed: {sens['plus10mph_ball_carry_yd']:+.1f} yd carry", f"- +1000 rpm backspin: {sens['plus1000rpm_carry_yd']:+.1f} yd carry", "",
          "## Scope / honesty", "", "- This validates the ANALYTIC ball model only. The leaderboard's carry/total yards come from the MuJoCo-physics ball (smash ~1.0 artifact, results/smash_anomaly.md) and are not these numbers.",
          "- One benchmark row only: this is a spot check, not a full calibration across clubs or conditions (no wind, altitude, turf variation)."]
    open(os.path.join(ROOT, "results", "golf_simulator_validation.md"), "w").write("\n".join(md) + "\n")
    return out


if __name__ == "__main__":
    o = run()
    for k in ("flight_from_published_launch", "impact_model"):
        for c in o[k]["checks"]: print(k, c["metric"], round(c["model"], 2), c["published"], "PASS" if c["passed"] else "FAIL")

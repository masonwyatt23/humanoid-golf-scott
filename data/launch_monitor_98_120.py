"""Build data/references/launch_monitor_98_120_tables.json: published launch-monitor driver references at 98 and 120 mph club speed,
interpolated where stated, plus a READ-ONLY comparison with env/ball_flight_analytic.py (imported, never edited).
Run (venv): python -m data.launch_monitor_98_120"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "data/references/launch_monitor_98_120_tables.json"
MPH = 0.44704; YD = 1.0936

def lerp(x, x0, x1, y0, y1): return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

# --- published rows (transcribed from fetched documents; see sources) ---
OPT_CARRY = {  # TrackMan Driver Fitting Chart, CARRY optimizer, AoA 0 / -5 / +5: ball, launch, spin, carry, total, dyn loft
  95: {0: (138, 12.7, 3114, 219, 244, 15.0)}, 100: {-5: (144, 9.6, 3722, 222, 244, 12.2), 0: (146, 12.1, 3118, 235, 272, 14.3), 5: (148, 14.9, 2538, 247, 272, 16.7)},
  120: {-5: (176, 6.1, 3433, 281, 305, 8.1), 0: (178, 9.3, 2890, 296, 321, 11.0), 5: (179, 12.6, 2343, 310, 350, 14.0)}}
OPT_TOTAL = {95: {0: (140, 10.5, 2565, 213, 262, 12.3)}, 100: {0: (148, 10.0, 2570, 230, 278, 11.7)}, 120: {-5: (178, 4.5, 2929, 273, 322, 6.2), 0: (179, 7.7, 2382, 290, 340, 9.0), 5: (180, 10.3, 1636, 300, 358, 11.3)}}

def interp_row(a, b, x):
    return [round(lerp(x, a[0], b[0], p, q), 2) for p, q in zip(a[1], b[1])]

def sources():
    return [
     dict(id="tm_optimizer_2010", url="https://wishongolf.com/wp-content/uploads/2012/07/TrackMan-Driver-Optimization_2010.pdf", type="vendor (TrackMan) fitting chart, hosted by a third-party fitter; dated 2010",
          verification="fetched (PDF downloaded, text extracted)", note="Theoretical OPTIMIZER output for centre strikes, not measured player averages. Carry optimizer and total optimizer tables, AoA -5/0/+5, 75-120 mph.", unverified=False),
     dict(id="tm_pga_tour_pdf", url="https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf", type="vendor (TrackMan) PGA TOUR averages, metres version; undated (2019-era set per repo notes)",
          verification="fetched (PDF downloaded; driver row read; search excerpt agrees)", note="Driver: 113 mph, AoA -1.3, ball 167, smash 1.48, launch 10.9, spin 2686, carry 251 m (=275 yd). Highest measured club speed in the TrackMan set.", unverified=False),
     dict(id="tm_combine_blogs", url="https://www.trackman.com/blog/club-speed", type="vendor (TrackMan) blog pages quoting 'Combine' male-amateur driver averages (club-speed, ball-speed, launch-angle, spin-rate, smash-factor pages)",
          verification="search_snippet (excerpts of trackman.com/blog/what-is-club-speed, /ball-speed, /launch-angle, /spin-rate, /smash-factor); pages not fully read", note="5 HCP: 101 mph/147/11.2/2987/223 yd; 10 HCP: 95/138/11.9/3192/205; scratch 110/161/11.2/2896/252. Carry column came from a secondary synthesis of the search result, less certain.", unverified=True),
     dict(id="foresight_ref_tables", url="https://help.foresightsports.com/hc/en-us/articles/47208228295187-Ball-Launch-Data-Performance-Reference-Tables", type="vendor (Foresight Sports) help-centre reference tables (page updated 2025-12-09)",
          verification="fetched (page body read)", note="Optimised driver table by club/ball speed (launch 10-14 deg for all speeds, spin and carry ranges) and a 'faster swing speeds' typical table (1w: 112 mph, 165, 11.2 deg, 2685 rpm, 270 yd). The table is described as derived from measured and calculated data; method not given.", unverified=False),
     dict(id="usga_tpx3006", url="https://www.usga.org/content/dam/usga/pdf/Equipment/TPX3006-overall-distance-and-symmetry-test-procedure.pdf", type="governing body (USGA) test procedure; also the 2019 TPX3006 v3.0 PDF and the USGA distance FAQ",
          verification="search_snippet (excerpts of the TPX3006 PDFs and FAQ page; not fully read)", note="Ball test launch conditions: 120 mph, 10 deg, 2520 rpm (42 rps), reference ball speed 175 mph (256 fps); limit 317 yd overall + 3 yd tolerance at 75F/30 inHg/50% RH. Currently in force; the planned 125 mph/11 deg/2220 rpm change was postponed to no earlier than 2030 per a 2026 USGA/R&A joint statement (snippet).", unverified=True),
     dict(id="tm_tour_2023_repo", url="https://www.trackman.com/blog/introducing-updated-tour-averages", type="vendor (TrackMan) 2023 tour averages, via data/references/impact_physics_calibration.json (itself from a snippet)",
          verification="not re-fetched here; repo value, marked search_snippet upstream", note="115 mph, ball 171, smash 1.49, launch 10.4, spin 2545, carry 282 yd, AoA -0.9.", unverified=True),
     dict(id="tutelman_launchopt", url="https://tutelman.com/golf/ballflight/launchOptimize.php", type="independent engineering analysis (Tutelman), model-based best launch vs ball speed",
          verification="search_snippet here (fetched in the earlier impact-physics work)", note="Best launch: 145 mph ball 11 deg, 160 mph 10 deg, 175 mph 8.5 deg (model-based, not measured).", unverified=True),
    ]

def cases():
    rows = {}
    # ---- 98 mph ----
    a95, a100 = OPT_CARRY[95][0], OPT_CARRY[100][0]
    c98 = interp_row((95, a95), (100, a100), 98)
    t98 = interp_row((95, OPT_TOTAL[95][0]), (100, OPT_TOTAL[100][0]), 98)
    fs_ball = round(lerp(98, 97, 103, 140, 150), 1)
    def tabrow(v, r): return dict(club_mph=v, ball_mph=r[0], smash=round(r[0] / v, 3), launch_deg=r[1], spin_rpm=r[2], carry_yd=r[3], total_yd=r[4], dynamic_loft_deg=r[5])
    rows["98"] = dict(
      trackman_optimizer_carry_AoA0=dict(**tabrow(98, c98), interpolation="linear between published 95 and 100 mph rows (AoA 0, carry optimizer); no published 98 mph row. Total column is noisy upstream (244 at 95 -> 272 at 100) so the interpolated total is weak."),
      trackman_optimizer_total_AoA0=dict(**tabrow(98, t98), interpolation="linear between 95 and 100 mph rows (AoA 0, total optimizer)"),
      trackman_optimizer_carry_AoA_m5_p5="no 98 mph row; published AoA +-5 at 100 mph: -5: 144/9.6 deg/3722/222 yd; +5: 148/14.9/2538/247",
      foresight_optimal_table=dict(club_mph=98, ball_mph=fs_ball, launch_range_deg=[10.0, 14.0], spin_range_rpm=[round(lerp(98, 97, 103, 3100, 3000)), round(lerp(98, 97, 103, 2110, 2000))],
              carry_range_yd=[round(lerp(98, 97, 103, 231, 254)), round(lerp(98, 97, 103, 249, 275))], total_range_yd=[round(lerp(98, 97, 103, 250, 273)), round(lerp(98, 97, 103, 272, 299))],
              interpolation="linear between published 97 mph (ball 140) and 103 mph (ball 150) rows; interpolated ball speed 141.7 is the table's ball speed, i.e. smash ~1.45 as implied by that table"),
      trackman_combine_amateur_interp=dict(club_mph=98, ball_mph=round(lerp(98, 95, 101, 138, 147), 1), smash=round(lerp(98, 95, 101, 138, 147) / 98, 3), launch_deg=round(lerp(98, 95, 101, 11.9, 11.2), 2),
              spin_rpm=round(lerp(98, 95, 101, 3192, 2987)), carry_yd=round(lerp(98, 95, 101, 205, 223)),
              interpolation="linear between the 10 HCP (95 mph) and 5 HCP (101 mph) Combine rows; these are DIFFERENT player groups, so treat as indicative; carry from snippet-derived text (unverified)"),
      range_summary=dict(smash=[1.42, 1.49], launch_deg=[11.2, 12.4], spin_rpm=[2990, 3120], carry_yd=[214, 235],
              note="smash 1.42 = Combine interpolation; 1.49 = TrackMan optimizer/tour upper bound; ranges span the sources, they are not a confidence interval"))
    # ---- 120 mph ----
    c120 = OPT_CARRY[120][0]; t120 = OPT_TOTAL[120][0]
    fs120 = dict(club_mph=120, ball_mph=round(lerp(120, 117, 124, 170, 180), 1), launch_range_deg=[10.0, 14.0],
                 spin_range_rpm=[round(lerp(120, 117, 124, 2800, 2700)), round(lerp(120, 117, 124, 1800, 1700))],
                 carry_range_yd=[round(lerp(120, 117, 124, 298, 320)), round(lerp(120, 117, 124, 325, 349))], total_range_yd=[round(lerp(120, 117, 124, 318, 340)), round(lerp(120, 117, 124, 349, 386))],
                 interpolation="linear between published 117 mph (ball 170) and 124 mph (ball 180) rows")
    rows["120"] = dict(
      trackman_optimizer_carry_AoA0=dict(**tabrow(120, c120), interpolation="none (published row)"),
      trackman_optimizer_carry_AoA_m5=dict(**tabrow(120, OPT_CARRY[120][-5]), interpolation="none"),
      trackman_optimizer_carry_AoA_p5=dict(**tabrow(120, OPT_CARRY[120][5]), interpolation="none"),
      trackman_optimizer_total_AoA0=dict(**tabrow(120, t120), interpolation="none (published row)"),
      foresight_optimal_table=fs120,
      usga_ball_test=dict(club_mph=120, ball_mph=175, smash=round(175 / 120, 3), launch_deg=10.0, spin_rpm=2520, total_yd_limit=317, note="a standard test condition (roughly the longest hitters), NOT a player average; ball speed is a 'reference only' value"),
      trackman_pga_tour_nearest_measured=dict(club_mph=113, ball_mph=167, smash=1.48, launch_deg=10.9, spin_rpm=2686, carry_yd=275, aoa_deg=-1.3, note="highest measured club-speed average found; 7 mph below 120, so 120 mph is still an extrapolation of measured averages"),
      range_summary=dict(smash=[1.458, 1.49], launch_deg=[9.3, 11.0], spin_rpm=[2342, 2890], carry_yd=[296, 310],
              note="launch 9.3-11.0 deg: optimizer AoA0 9.3, USGA 10; spin spans USGA 2520 and optimizer 2890 (AoA 0) down to 2343 (AoA +5); the Foresight range is wider (10-14 deg, 1700-2800 rpm) because it is a window, not a point"))
    return rows

def model_runs():
    import env.ball_flight_analytic as bf
    out = []
    def impact_k(vc, n, K, e=0.83, m_club=0.20, mu=0.22):
        # local copy of bf.impact with the roll-off constant K exposed (3.5 in the env file). env/ is NOT modified.
        n = n / np.linalg.norm(n); vn = float(vc @ n); vt = vc - vn * n; vtm = np.linalg.norm(vt)
        bn = (1 + e) * m_club / (m_club + bf.M_BALL) * max(vn, 0.0); Jn = bf.M_BALL * bn
        Jt = min(mu * Jn, bf.M_BALL * vtm / K); d = vt / vtm if vtm > 1e-9 else np.zeros(3)
        return bn * n + (Jt / bf.M_BALL) * d, -(bf.R_BALL * Jt / bf.I_BALL) * np.cross(n, d)
    # (mph, AoA, dynamic loft) conditions taken from the TrackMan carry-optimizer rows (AoA 0 dynamic loft: 98 -> interpolated 14.58 at 98; 14.3 at 100; 11.0 at 120)
    conds = [(98, 0.0, 14.58), (98, 0.0, 12.5), (120, 0.0, 11.0), (120, 2.0, 12.5), (120, -5.0, 8.1), (120, 5.0, 14.0)]
    for mph, att, loft in conds:
        for label, K, e in (("env_default(K=3.5,e=0.83)", 3.5, 0.83), ("R1/R2 patched copy (K=5.6,e=0.845)", 5.6, 0.845)):
            cs = mph * MPH; a = np.radians(att); l = np.radians(loft)
            vc = cs * np.array([np.cos(a), 0, np.sin(a)]); n = np.array([np.cos(l), 0, np.sin(l)])
            vb, w = impact_k(vc, n, K, e=e)
            r = bf.simulate([0, 0, 0.07], vb, w)
            out.append(dict(mph=mph, attack_deg=att, dynamic_loft_deg=loft, variant=label, ball_mph=round(r["ball_speed"] / MPH, 1), smash=round(r["ball_speed"] / cs, 3),
                            launch_deg=round(r["launch"], 2), spin_rpm=round(r["backspin_rpm"]), carry_yd=round(r["carry"] * YD, 1), total_yd=round(r["total"] * YD, 1)))
    return out

def comparison(tables, runs):
    f = lambda m, loft, v: next(r for r in runs if r["mph"] == m and r["dynamic_loft_deg"] == loft and r["attack_deg"] == 0.0 and r["variant"].startswith(v))
    t98 = tables["98"]["trackman_optimizer_carry_AoA0"]; t120 = tables["120"]["trackman_optimizer_carry_AoA0"]; out = {}
    for mph, t, loft in ((98, t98, 14.58), (120, t120, 11.0)):
        d = f(mph, loft, "env_default"); p = f(mph, loft, "R1/R2")
        out[str(mph)] = dict(target=dict(ball_mph=t["ball_mph"], smash=t["smash"], launch_deg=t["launch_deg"], spin_rpm=t["spin_rpm"], carry_yd=t["carry_yd"]),
            env_default=dict(ball_mph=d["ball_mph"], smash=d["smash"], launch_deg=d["launch_deg"], spin_rpm=d["spin_rpm"], carry_yd=d["carry_yd"]),
            patched_K5p6_e0p845=dict(ball_mph=p["ball_mph"], smash=p["smash"], launch_deg=p["launch_deg"], spin_rpm=p["spin_rpm"], carry_yd=p["carry_yd"]),
            spin_ratio_default_over_target=round(d["spin_rpm"] / t["spin_rpm"], 3), spin_ratio_patched_over_target=round(p["spin_rpm"] / t["spin_rpm"], 3),
            K_that_matches_target_spin=round(3.5 * d["spin_rpm"] / t["spin_rpm"], 2), carry_error_default_pct=round(100 * (d["carry_yd"] / t["carry_yd"] - 1), 1),
            carry_error_patched_pct=round(100 * (p["carry_yd"] / t["carry_yd"] - 1), 1), launch_error_default_deg=round(d["launch_deg"] - t["launch_deg"], 2))
    out["recommendations"] = [
      "SPIN: backspin in the env model = v_club*sin(spin loft)/(K*1.4*R) with K hard-coded 3.5 (mu never binds). TrackMan optimizer AoA0 rows (98 and 120 mph) are matched at K ~3.96 at both speeds (spin ratio default/target 1.13 and 1.13), i.e. spin_scale ~0.88; the earlier tour-point fit (K~5.6, spin_scale 0.62) UNDER-spins these rows (0.71x at 98, 0.71x at 120). The two fits disagree because they assume different dynamic/spin loft; fit K on measured spin loft (launch monitor) rather than on a single averaged point. Interim: K in [4.0, 5.6], i.e. spin_scale 0.62-0.88; prefer ~4.0 for the 98-120 mph optimizer-consistent case.",
      "SPIN TARGETS (centre strike, AoA 0, carry-optimal): ~3100 rpm at 98 mph (range 2990-3200 across sources), ~2890 rpm at 120 mph (2520 USGA test, 2343 at AoA +5, 3433 at AoA -5). Spin should FALL with speed only through lower dynamic loft; at fixed loft it rises ~linearly with speed.",
      "SMASH CAP: published values 1.45-1.49 (optimizer 1.46 at 100, 1.48 at 120; TrackMan tour 1.48-1.49; USGA reference 1.458). Env default 1.44-1.47 is acceptable; keep a hard cap at 1.50 (already the recommendation R2). Do not exceed 1.49 for centre strikes.",
      "LAUNCH: env default is 0.4-0.6 deg below the table at the same TrackMan dynamic loft and AoA 0 (11.72 vs 12.35 interp at 98; 8.86 vs 9.3 at 120). Within the likely loft-definition mismatch; low priority; do not re-tune before dynamic loft is measured.",
      "CARRY: env default is 7-8% short at both speeds even before spin is fixed; the K patch only partly closes it (about -3%). Part of the remaining gap is aerodynamics (Cd/Cl), not spin; carry is therefore not a clean spin diagnostic.",
      "The 120 mph reference is an optimizer/test value; no measured population average exists above 115 mph in the sources found. Re-fit when Mason's launch-monitor data exist."]
    return out

def build():
    tables = cases()
    runs = model_runs()
    d = dict(schema_version=1, generated="2026-10-17", scope="Driver launch-monitor reference values at 98 and 120 mph club speed; comparison with env/ball_flight_analytic.py",
      mason_own_numbers="NONE EXIST YET. Mason has not provided launch-monitor data; 120+ mph is his self-reported club speed, unverified. Nothing here is a measurement of Mason.",
      sources=sources(), tables=tables, model_runs=runs, model_comparison=comparison(tables, runs), caveats=[
        "Optimizer tables are theoretical best-case centre-strike outputs, not player averages; measured averages have lower smash and higher spin for amateurs.",
        "No measured published average exists at 120 mph in the sources found (TrackMan PGA tour max 113-115 mph); 120 mph values are optimizer/test-condition values.",
        "TrackMan optimizer rows are 2010 vintage; interpolation to 98 mph is linear between 95 and 100 mph rows.",
        "Foresight table gives ranges and its construction is not documented.", "Model runs use TrackMan dynamic loft as the env face-normal loft; this is an assumption (dynamic loft vs model 'loft' may not be identical)."],
      verification_note="'fetched' = document body read in this job; 'search_snippet' = only a search excerpt seen; unverified flag marks items resting on snippets.")
    OUT.write_text(json.dumps(d, indent=1)); return d

if __name__ == "__main__":
    d = build()
    for r in d["model_runs"]: print(r)
    print("wrote", OUT)

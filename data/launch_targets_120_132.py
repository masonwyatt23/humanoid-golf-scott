"""Build data/references/launch_targets_120_132_limits.json: cited driver target table at 120/130/132 mph club speed
(ball speed, smash, launch, spin, carry, total where sourced) + published smash/spin limits for a gate.
PUBLIC SOURCES ONLY. Nothing here is a measurement of Mason. Every value carries a `basis` tag:
  published = row read from a source; interpolated / extrapolated = computed here (method stated); model = env/ball_flight_analytic.py run (NOT a source); unverified = rests on a search snippet.
Run (venv): python -m data.launch_targets_120_132"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.launch_monitor_98_120 import lerp, OPT_CARRY, MPH, YD
OUT = ROOT / "data/references/launch_targets_120_132_limits.json"

# TrackMan optimizer, carry, AoA 0: 105 mph row (via a fitter's reprint of the TrackMan chart; search snippet) and 120 mph row (wishon PDF, fetched).
TM105 = {-5: (152, 8.7, 3680, 237), 0: (154, 11.2, 3040, 251), 5: (155, 14.5, 2560, 263)}
TM120 = {a: OPT_CARRY[120][a][:4] for a in (-5, 0, 5)}
FS = {117: (170, 2800, 1800, 298, 325, 318, 349), 124: (180, 2700, 1700, 320, 349, 340, 386), 131: (190, 2600, 1600, 342, 372, 378, 401), 138: (200, 2500, 1500, 360, 389, 381, 418)}  # ball, spin hi, spin lo, carry lo/hi, total lo/hi (Foresight table, fetched)

def tm_extrap(v, aoa=0):
    a, b = TM105[aoa], TM120[aoa]
    r = [lerp(v, 105, 120, p, q) for p, q in zip(a, b)]
    return dict(club_mph=v, ball_mph=round(r[0], 1), smash=round(r[0] / v, 3), launch_deg=round(r[1], 1), spin_rpm=round(r[2]), carry_yd=round(r[3]),
                basis="extrapolated" if v > 120 else "published", method=f"linear extrapolation of the TrackMan optimizer AoA {aoa} rows at 105 and 120 mph beyond the last published row (120 mph); chart has no row above 120 mph" if v > 120 else "published row")

def fs_row(v):
    lo, hi = (117, 124) if v <= 124 else ((124, 131) if v <= 131 else (131, 138))
    f = lambda i: lerp(v, lo, hi, FS[lo][i], FS[hi][i])
    return dict(club_mph=v, ball_mph=round(f(0), 1), launch_range_deg=[10.0, 14.0], spin_range_rpm=[round(f(1)), round(f(2))], carry_range_yd=[round(f(3)), round(f(4))], total_range_yd=[round(f(5)), round(f(6))],
                basis="published" if v in FS else "interpolated", method=f"linear between Foresight rows {lo} and {hi} mph" if v not in FS else "published row (club 131 mph, ball 190); interpolated nowhere",
                note="Foresight ball speed implies smash %.3f; this is a window table, not a point estimate" % (f(0) / v))

def model_rows():
    import env.ball_flight_analytic as bf
    def impact_k(vc, n, K, e, m_club=0.20, mu=0.22):
        n = n / np.linalg.norm(n); vn = float(vc @ n); vt = vc - vn * n; vtm = np.linalg.norm(vt)
        bn = (1 + e) * m_club / (m_club + bf.M_BALL) * max(vn, 0.0); Jn = bf.M_BALL * bn
        Jt = min(mu * Jn, bf.M_BALL * vtm / K); d = vt / vtm if vtm > 1e-9 else np.zeros(3)
        return bn * n + (Jt / bf.M_BALL) * d, -(bf.R_BALL * Jt / bf.I_BALL) * np.cross(n, d)
    out = []
    for mph, loft in ((130, 10.0), (130, 9.0), (132, 10.0), (132, 9.0)):
        for label, K, e in (("K=4.0,e=0.845 (recommended interim)", 4.0, 0.845), ("env_default K=3.5,e=0.83", 3.5, 0.83)):
            cs = mph * MPH; l = np.radians(loft)
            vb, w = impact_k(cs * np.array([1.0, 0, 0]), np.array([np.cos(l), 0, np.sin(l)]), K, e)
            r = bf.simulate([0, 0, 0.07], vb, w)
            out.append(dict(basis="model (NOT a source)", club_mph=mph, aoa_deg=0.0, dynamic_loft_deg_assumed=loft, variant=label, ball_mph=round(r["ball_speed"] / MPH, 1), smash=round(r["ball_speed"] / cs, 3),
                            launch_deg=round(r["launch"], 2), spin_rpm=round(r["backspin_rpm"]), carry_yd=round(r["carry"] * YD, 1), total_yd=round(r["total"] * YD, 1)))
    return out

SOURCES = [
 dict(id="tm_optimizer_2010", url="https://wishongolf.com/wp-content/uploads/2012/07/TrackMan-Driver-Optimization_2010.pdf", verification="fetched", unverified=False, note="TrackMan optimizer chart, club speeds 75-120 mph; vendor theoretical optimum, not player averages. Ends at 120 mph."),
 dict(id="tm_optimizer_reprint", url="https://www.dlancegolf.com/fitting-tips/four-keys-for-optimizing-driver-distance/", verification="search_snippet", unverified=True, note="Reprint of the same TrackMan optimizer carry rows incl. 105 mph (154/11.2/3040/251 at AoA 0). The 75/90/120 rows agree with the fetched PDF. Its TOTAL column differs from the PDF (330 vs 321 at 120 mph) so totals are NOT taken from it."),
 dict(id="foresight_ref_tables", url="https://help.foresightsports.com/hc/en-us/articles/47208228295187-Ball-Launch-Data-Performance-Reference-Tables", verification="fetched", unverified=False, note="Optimized driver table to 145 mph club speed (rows 124/131/138 used) and typical tables (1w 112 mph)."),
 dict(id="randa_wld_trackman", url="https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/550ab9f6-5dd3-45b0-b58c-7563d4256c04/R07%20-%20Analysis%20of%20Trackman%20data%20gathered%20at%20World%20Long%20Drive.pdf", verification="search_snippet", unverified=True, note="R&A report: TrackMan World Long Drive men's averages: 145 mph club, 214 ball, smash 1.48, launch 11.2, spin 2789, carry 352 yd; women 116/171/1.47/13.4/2813/282. Same report says PGA Tour smash 1.48."),
 dict(id="golfcom_burke", url="https://golf.com/instruction/driving/long-drive-champ-golfer-trackman-numbers/", verification="search_snippet", unverified=True, note="One practice shot (T. Burke, 2016): club 141.3 mph, ball 211, smash 1.50, AoA ~+8, spin 1850 rpm, 409 yd. Single shot, extreme AoA; an existence proof, not a target."),
 dict(id="tm_smash_blog", url="https://www.trackman.com/blog/smash-factor", verification="fetched", unverified=False, note="Smash near 1.50 expected for driver, PW ~1.25; PGA TOUR driver 1.49, LPGA 1.49; Combine male amateurs: scratch or better 1.49, 5 HCP 1.45, 10 HCP 1.45, avg golfer 1.44, bogey 1.43; 'possible to have a smash factor that is too high with certain clubs'."),
 dict(id="tutelman_smash", url="https://tutelman.com/golf/ballflight/smashfactor.php", verification="search_snippet", unverified=True, note="Physics: smash=(1+COR)/(1+m/M); 200 g head, 46 g ball, COR 0.83 -> 1.482 at 5 deg loft, ~1.465 at 10 deg loft; 1.500 needs ~229 g head."),
 dict(id="tutelman_gear", url="https://www.tutelman.com/golf/ballflight/gearEffect.php", verification="search_snippet", unverified=True, note="Theoretical max smash 1.5 (200 g, COR 0.83, ~0 loft); pros mid/high 1.4x; hackers 1.25 or less."),
 dict(id="tm_pga_tour_pdf", url="https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf", verification="fetched", unverified=False, note="PGA Tour driver 113 mph/167/1.48/10.9/2686/251 m; 3W 107/158/1.48/9.2/3655; hybrid ~1.46; 6i 1.3x; 9i 1.28; PW 1.23 (7i 90 mph/120/1.33/7097)."),
 dict(id="foresight_typical", url="https://help.foresightsports.com/hc/en-us/articles/47208228295187-Ball-Launch-Data-Performance-Reference-Tables", verification="fetched", unverified=False, note="Typical spin by club: 1w 2685, 3w 3801, 5w 4624, 7i 6585, PW 10399 (fast-swing table)."),
 dict(id="rule_cor_usga", url="https://www.usga.org/content/dam/usga/pdf/Equipment/TPX3006-overall-distance-and-symmetry-test-procedure.pdf", verification="search_snippet", unverified=True, note="Ball overall distance test: 120 mph / 10 deg / 2520 rpm, 317 yd limit (+3 tol). Driver COR limit 0.83 per the rules (Tutelman refs)."),
]

def build():
    tm = {str(v): tm_extrap(v) for v in (120, 130, 132)}
    aoa = {str(v): {f"AoA_{a}": tm_extrap(v, a) for a in (-5, 5)} for v in (130, 132)}
    fs = {str(v): fs_row(v) for v in (120, 130, 132)}
    # fallback anchors for 120: published rows
    targets = {}
    for v in (120, 130, 132):
        t = tm[str(v)]
        targets[str(v)] = dict(
            point_target_trackman_AoA0=t,
            point_target_trackman_AoA_variants=aoa.get(str(v)),
            foresight_window=fs[str(v)],
            total_yd=dict(value=None if v > 120 else 340, basis="published (TrackMan TOTAL optimizer, AoA 0, wishon PDF)" if v == 120 else "NOT SOURCED as a point; use Foresight total_range_yd window (published/interpolated); TrackMan chart has no >120 mph row",
                          window_yd=fs[str(v)]["total_range_yd"]),
            smash_gate_ceiling=1.50, smash_expected_range=[1.46, 1.49],
            spin_expected_range_rpm=[fs[str(v)]["spin_range_rpm"][1], t["spin_rpm"] + 500],
            suggested_gate=dict(ball_mph=[round(0.97 * t["ball_mph"], 1), round(1.01 * t["ball_mph"], 1)], launch_deg=[8.0, 14.0], spin_rpm=[fs[str(v)]["spin_range_rpm"][1], 3200], carry_yd=[fs[str(v)]["carry_range_yd"][0] - 20, fs[str(v)]["carry_range_yd"][1] + 10],
                                basis="DERIVED here from the windows above as a sanity band, NOT published; launch 8-14 = TrackMan point (7.8-9.3 at AoA 0) to Foresight upper 14"))
    ev = [
      dict(source="randa_wld_trackman", club_mph=145, ball_mph=214, smash=1.48, launch_deg=11.2, spin_rpm=2789, carry_yd=352, basis="published (snippet-unverified)", note="measured group average; closest measured population above 120 mph"),
      dict(source="golfcom_burke", club_mph=141.3, ball_mph=211, smash=1.50, launch_deg=None, spin_rpm=1850, carry_yd=None, total_yd=409, aoa_deg=8, basis="published (snippet-unverified)", note="single shot"),
      dict(source="tm_pga_tour_pdf", club_mph=113, ball_mph=167, smash=1.48, launch_deg=10.9, spin_rpm=2686, carry_yd=275, basis="published (fetched)", note="highest club speed among tour averages"),
    ]
    limits = dict(
      smash=dict(
        driver=dict(hard_ceiling=1.50, expected_centre_strike_max=1.49, typical_tour=[1.48, 1.49], typical_scratch_amateur=1.49, typical_amateur=[1.43, 1.45], basis="published", sources=["tm_smash_blog", "randa_wld_trackman", "tm_pga_tour_pdf"],
                    physics_note="(1+COR)/(1+m/M) with COR 0.83, 200 g head, 46 g ball = 1.482 at 5 deg loft, ~1.465 at 10 deg loft (Tutelman); 1.500 is an upper bound requiring ~229 g head; measured 1.50 shots exist (single shots, snippet-unverified)",
                    gate_recommendation="FAIL/flag any shot with smash > 1.50; WARN > 1.49; WARN < 1.30 for contact shots (poor strike)"),
        three_wood=dict(typical=1.48, basis="published (fetched TrackMan PGA Tour PDF)", source="tm_pga_tour_pdf"),
        hybrid=dict(typical=1.46, basis="published (fetched TrackMan PGA Tour PDF; ~1.46 hybrid)", source="tm_pga_tour_pdf"),
        iron_6=dict(typical=1.39, basis="published (TrackMan blog tour average)", source="tm_smash_blog"),
        iron_7=dict(typical=1.33, basis="published (PGA Tour PDF)", source="tm_pga_tour_pdf"),
        iron_9=dict(typical=1.28, basis="published (PGA Tour PDF)", source="tm_pga_tour_pdf"),
        pitching_wedge=dict(typical=[1.23, 1.25], basis="published (PGA Tour PDF 1.23; TrackMan blog 'near 1.25')", sources=["tm_pga_tour_pdf", "tm_smash_blog"]),
        note="Max by club type is not published as a rule; the numbers are tour AVERAGES, and a gate ceiling for non-drivers should be set ~0.03-0.05 above the average (derived, not published)."),
      spin_rpm=dict(
        driver=dict(tour_average=[2545, 2686], tour_average_sources="PGA Tour 2686 (113 mph, fetched); 2023 tour 2545 (repo value, snippet); Foresight typical 1w 2685", long_drive_average=2789, burke_single_shot=1850,
                    optimizer_window_at_120_to_132_mph=[1600, 2900], foresight_optimum_range_120=[1757, 2757], usga_ball_test=2520, amateur_combine=[2987, 3192],
                    gate_recommendation="driver at 120-132 mph: PASS 1800-3000 rpm, WARN 1500-1800 or 3000-3500, FAIL < 1200 or > 4000 (derived from windows above; not published thresholds)", basis="published ranges; thresholds DERIVED"),
        three_wood=dict(typical=[3655, 3801], basis="published (PGA Tour PDF; Foresight fast table)"),
        hybrid=dict(typical=4437, basis="published (PGA Tour PDF, partly garbled in extraction: unverified)"),
        iron_7=dict(typical=[6585, 7097], basis="published (Foresight fast table; PGA Tour PDF)"),
        iron_9=dict(typical=[8647, 9018], basis="published"),
        pitching_wedge=dict(typical=[9304, 10399], basis="published")),
      launch_deg=dict(driver_tour=[10.4, 11.2], driver_optimum_window=[10.0, 14.0], note="Foresight 10-14 for all speeds; TrackMan point optimum falls with speed (9.3 at 120, extrapolated ~8 at 130)"))
    d = dict(schema_version=1, generated="2026-10-17", scope="Driver targets at 120/130/132 mph club speed and published smash/spin limits for the gate",
      mason_own_numbers="NONE EXIST YET. 120+ mph is Mason's self-reported club speed (unverified). Nothing here measures Mason. No Instagram-derived or Mason-clip data used.",
      sources=SOURCES, targets=targets, measured_evidence_above_113_mph=ev, model_runs_130_132=model_rows(), limits=limits,
      caveats=["TrackMan optimizer chart ends at 120 mph; the 130 and 132 mph point targets are LINEAR EXTRAPOLATIONS (basis=extrapolated) and give smash 1.49 at 130-132, at the physical ceiling: treat ball speed as upper bound.",
               "Foresight rows are windows (launch 10-14, wide spin/carry ranges) with an implied smash of ~1.45; the two vendors differ by ~4-5% in ball speed at 130 mph (TrackMan-extrap 194 vs Foresight 189). Both are optimizer-type outputs, not measured player averages.",
               "No sourced TOTAL point exists above 120 mph; only the Foresight window (published/interpolated).",
               "No measured population average at 130/132 mph club speed was found. Nearest measured: World Long Drive men's 145 mph (snippet-unverified) and PGA Tour 113 mph.",
               "Unverified = relies on search snippets (see sources[].unverified). Suggested gate bands and thresholds are derived here and are not published limits.",
               "Model rows are env/ball_flight_analytic.py output at an ASSUMED dynamic loft; they show what the model gives, not what is real."])
    OUT.write_text(json.dumps(d, indent=1)); return d

if __name__ == "__main__":
    d = build()
    for k, t in d["targets"].items(): print(k, t["point_target_trackman_AoA0"], t["foresight_window"]["total_range_yd"])
    for r in d["model_runs_130_132"]: print(r)
    print("wrote", OUT)

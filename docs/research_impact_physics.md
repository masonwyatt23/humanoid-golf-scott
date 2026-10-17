# Driver impact physics & ball-model calibration (120–150 mph club speed)

Branch `research-impact-physics`. Machine-readable twin: `data/references/impact_physics_calibration.json` (every value carries source ids → URLs, `confidence`, `unverified`). Written 2026-10-17. Model under test: `env/ball_flight_analytic.py` (read-only; run in a venv, never edited).

**Evidence honesty.** Most sources were read only through search-result excerpts (`search_snippet`); only the two Tutelman pages (gear effect 3, launch optimisation) were fetched in full. Primary papers (Smits & Smith 1994, Bearman & Harvey 1976, Penner 2003) were *not* read in full. Nothing below is a measurement of Mason; his 120 mph is self-reported. There is **no verified published TrackMan mean for club speed >125 mph** here, so 130–150 mph model outputs are extrapolation.

## 1. Published facts (with confidence)

| Topic | Value | Source | Conf. |
|---|---|---|---|
| USGA CT limit | 239 µs (+18 µs tolerance → 257 µs) | [USGA TPX3004](https://www.usga.org/content/dam/usga/pdf/Equipment/TPX3004-procedure-for-measuring-the-flexibility-of-a-golf-clubhead.pdf), [USGA notice 2016](https://www.usga.org/content/dam/usga/pdf/RSI/distance-insights-2021-docs/Notice%20%20-Spring%20Effect%20Interpretation%201-11-16%20Final.pdf) | high |
| Legacy COR limit | 0.822 + 0.008 = 0.830 | [Hireko](https://www.hirekogolf.com/coefficient-of-restitution-cor-characteristic-time-ct), [GOLF.com](https://golf.com/gear/gear-101-ct-test-cor-test-golf-clubs/) | medium |
| Centre-hit smash (200 g head, e=0.83) | 1.482 square; <1.47 at ~10° loft; falls as loft rises | [Tutelman smash](https://www.tutelman.com/golf/ballflight/smashfactor.php) | medium |
| Tour driver 2023 (TrackMan) | 115 mph club, 171 mph ball, smash 1.49, 2,545 rpm, 282 yd carry, AoA −0.9° (launch 10.4° via secondary blog) | [Golf Monthly](https://www.golfmonthly.com/tour/how-far-pga-tour-players-hit-every-club-in-the-bag), [TrackMan AoA](https://www.trackman.com/blog/attack-angle), [Golfing Focus](https://golfingfocus.com/how-far-tour-pros-hit-driver-and-what-it-means-for-your-drives/) | medium (launch: low) |
| Older TrackMan tour set | 113 / 167 mph, 1.48, 10.9°, 2,686 rpm, 38° landing, 275 yd, AoA −1.3° | [PDF](https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf) | medium |
| D-plane | Ball starts mostly along the face (~85/15 face/path for driver); spin axis ⟂ D-plane; spin ∝ face-to-path/spin-loft obliqueness | [Tutelman D-plane](https://www.tutelman.com/golf/biomech/appconcepts1.php), [Nine flights](https://www.tutelman.com/golf/ballflight/ballflight.php), [TrackMan defs](https://support.trackmangolf.com/hc/en-us/articles/5089892383515-Practice-Trackman-Data-Parameter-Definitions) | medium–high |
| Spin loft / launch | spin loft = dynamic loft − AoA; launch = AoA + f·L, f = 0.96 − 0.0071·L (L deg) | [Tutelman 3-D launch](https://tutelman.com/golf/ballflight/3dlaunch.php) | medium |
| Gear effect | horizontal spin = 16.4·Vb(mph)·x(in) rpm; vertical = 25·Vb·y(in) rpm (Ih 4000–5900 g·cm², Iv ½–⅔ Ih). ~2,460 / 3,750 rpm per inch at 150 mph. Bulge/roll offset it | [Tutelman GE3](https://www.tutelman.com/golf/ballflight/gearEffect3.php) (fetched) | high |
| Carry-optimal launch vs ball speed (zero-AoA fit) | 100→17°, 115→15°, 130→13°, 145→11°, 160→10°, 175→8.5°, 190→7° | [Tutelman launch optimise](https://www.tutelman.com/golf/ballflight/launchOptimize.php) (fetched) | medium (simulation-derived, not tour data) |
| Aero | CD rises with spin above Re 5·10⁴ and with Re up to ~2·10⁵ then drops; CL ≈ Re-independent, rises with spin; spin decay law, landing spin ≈ 75 % of launch | [Penner 2003](https://iopscience.iop.org/article/10.1088/0034-4885/66/2/202), [Smits & Smith 1994 abstract](https://doi.org/10.4324/9780203474709-58), [Penner convex](http://www.raypenner.com/golf-convex.pdf) | medium (qualitative) |
| CL fit | CL = 1.99 S − 3.25 S² (S = Rω/V) — **secondary** implementation of Smits & Smith | [golfsim](https://github.com/avrybrdly93/golfsim) | low, unverified |
| Bounce | normal restitution ≈ 0.4 (green, rigid model); Penner's turf-angle β formula does not fit recent data | [arXiv 2302.02758](https://arxiv.org/html/2302.02758v1) | low |

Bearman & Harvey (1976, Aeronautical Quarterly) is cited only via Penner; no URL verified.

Where sources disagree: a high-speed "optimal launch/spin" chart assuming −10° AoA (6.2° / 3,500 rpm at 150 mph ball speed) conflicts with the Tutelman table and with TrackMan's older +5° AoA optimiser (14.5° / 2,560 rpm at 155 mph). Neither is used for calibration. The old rule "spin = 160·V·sin(loft)" gives ~4,600 rpm at tour conditions, far above 2,545 (modern low-spin balls) — **do not use**.

## 2. What the model does (read-only runs)

`impact()` is a two-body model with `e=0.83`, `mu=0.22`, tangential impulse `Jt = min(mu·Jn, M·vt/3.5)`.

**Finding 1 (high): `mu` is dead code for driver impacts.** Sweeping mu 0.08→0.22 gives identical spin (4,084.6 rpm). The roll-off limit always binds, so backspin = vt/(1.4·R) with vt = Vc·sin(spin loft); the only live knob is the literal `3.5`.

Model vs published tour point (115 mph, AoA −0.9°, dyn loft 13.5°):

| Metric | Published | Model |
|---|---|---|
| Spin | 2,545 rpm | **4,085 rpm (+60 %)** |
| Smash | 1.49 | 1.44 |
| Launch | 10.4° | 10.7° |
| Carry | 275–282 yd | **251 yd (−9 to −11 %)** |
| Apex | ~105 ft | 108 ft |
| Landing angle | 38° (2019 set) | 44° |

Slope: ~316 rpm per degree of spin loft at 130 mph; excess spin is what shortens carry.

Other behaviour (130 mph, AoA 0, loft sweep 6→16°): smash 1.48→1.43 (right direction); launch ≈ 0.8·loft (consistent with Tutelman f); carry peaks at ~8° loft (305 yd) — spin 2,584 rpm.

Face-to-path (130 mph): launch direction = 0.80·face, sidespin ≈ 316 rpm per deg FTP (4° → 1,264 rpm) added on top of unchanged backspin. Not verifiable numerically from sources; the D-plane conserves/tilts total spin instead.

Missing: off-centre impacts (gear effect, smash loss), speed dependence of COR, D-plane tilt, impact-location inputs.

Aero: model `cl_of(S)=0.42·S^0.4` equals the secondary Smits–Smith fit at S=0.10 (0.167) but is 12–18 % lower at S=0.15–0.20 (0.197 vs 0.226; 0.221 vs 0.268) — unverified. `cd_of` 0.20–0.29 is inside the generic 0.2–0.3 band (unverified).

## 3. Recommended calibration (not applied; env/ untouched)

1. **Replace `3.5` with a calibrated constant K ≈ 5.6** (or `spin_scale ≈ 0.62`). On a patched copy in /tmp: 2,553 rpm, carry 269 yd (e=0.83) / 274 yd (e=0.86) vs 275–282. Fitted to one averaged point — re-fit on Mason launch-monitor data. (high priority)
2. **Effective e ≈ 0.845** so centre smash lands 1.47–1.49 at tour loft. Do not go to e=0.86: patched copy then shows smash 1.50–1.51 at 140–150 mph/low loft, above a conforming practical ceiling. (high)
3. **Add impact-location inputs**: horizontal spin `+16.4·Vb·dx`, vertical `+25·Vb·dy`, bulge/roll start-line offset, smash loss `∝ r²`. The gear formulas are high confidence; the loss coefficient (0.07–0.14 per inch, grows ~quadratically) is **unverified**. (medium)
4. **D-plane face-to-path**: start line ≈ 0.85·face + 0.15·path; conserve total spin, tilt axis. (medium)
5. **Lift**: adopt CL=1.99S−3.25S² only after checking the primary paper. (low)
6. Roll-out: model rolls 22–27 yd vs ~18 yd tour (mixed measures); fairway en=0.28 / mu 0.45 are unsourced. Leave and mark unverified.
7. **Treat 130–150 mph outputs as extrapolation.** Default model totals (e.g. 150 mph, +5° AoA) of 380–400+ yd have no verified published reference.

## 4. Unverified list
Tour launch 10.4° (secondary); 160·V·sin(loft) spin rule; 400–500 rpm/deg loft; off-centre smash loss per inch; CL fit; CD numeric band; fairway restitution; rollout law; tour spin loft (~14°, not sourced); COR speed dependence; all 130–150 mph "targets"; Bearman & Harvey citation details. Full machine list: `unverified_ids` in the JSON.

## 5. Reproduce
Venv with numpy: `python -c "from env.ball_flight_analytic import *"`; run `impact()`/`simulate()` with club speed `v=[cos a,0,sin a]`, face normal `[cos L,0,sin L]`. Tests: `pytest tests/test_impact_physics_calibration.py`.

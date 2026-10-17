# Power-tier check vs published 130+ mph data, total/carry ratio, and a model-only roll/AoA add-on

Written 2026-10-17 (America/New_York). Public sources only; no Instagram-derived or Mason-clip data. Code: `data/roll_aoa_addon.py` (standalone, no env/ imports), data `data/references/roll_aoa_addon.json`, tests `tests/test_roll_aoa_addon.py`.
Verification tags: **fetched** = page/PDF opened in full this session; **snippet** = search-result excerpt only; *unverified* = not confirmed.

## 1. Power-tier numbers (launch 11.2 deg, spin ~2600 rpm, smash 1.47-1.49) vs published
| Source | Conditions | Club / ball mph | Smash | Launch | Spin rpm | Carry yd | Tag |
|---|---|---|---|---|---|---|---|
| R&A "Analysis of Trackman data gathered at World Long Drive events" (randa.org PDF) | 304 men's drives, 2019 | 145 / 214 | 1.48 | **11.2** | 2789 | 352 mean (median 361) | **fetched** |
| same, PGA Tour row | tour avg | 113 / 167 | 1.48 | 10.9 | 2686 | 275 | **fetched** |
| TrackMan Driver Optimizer chart 2010 (wishongolf.com PDF mirror) CARRY opt, 120 mph | AoA 0 / +5 | 120 / 178-179 | 1.48-1.49 | 9.3 / 12.6 | 2890 / 2343 | 296 / 310 | **fetched** (chart stops at 120 mph) |
| same, TOTAL opt, 120 mph | AoA 0 / +5 | 120 / 179-180 | 1.49-1.50 | 7.7 / 10.3 | 2382 / 1636 | 290 / 300 | **fetched** |
| Foresight "Optimized Driver Launch Data" (help.foresightsports.com) | table | 131 / 190 (smash 1.45) | 1.45 | 10-14 range | 2600-1600 range | 342-372 | **snippet** |
| same | | 145 / 210 | 1.45 | 10-14 | 2400-1400 | 383-408 | **snippet** |
| GOLF.com long-drive champ | single shot | 141.3 / 211 | 1.50 | AoA ~+8 | 1850 | n/a | **snippet** |
| TrackMan PGA Tour averages PDF (support.trackmangolf.com) | tour avg | 113 / 167 | 1.48 | 10.9 | 2686 | 275 | snippet (same numbers as R&A, fetched) |
URLs: randa.org: https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/550ab9f6-5dd3-45b0-b58c-7563d4256c04/R07%20-%20Analysis%20of%20Trackman%20data%20gathered%20at%20World%20Long%20Drive.pdf ; TrackMan chart: https://wishongolf.com/wp-content/uploads/2012/07/TrackMan-Driver-Optimization_2010.pdf ; Foresight: https://help.foresightsports.com/hc/en-us/articles/47208228295187-Ball-Launch-Data-Performance-Reference-Tables ; GOLF.com: https://golf.com/instruction/driving/long-drive-champ-golfer-trackman-numbers/ ; TrackMan PGA avg: https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf

**Verdict: consistent.**
- **Smash 1.47-1.49:** matches the R&A long-drive mean (1.48) and the TrackMan chart (1.48-1.50). Foresight's table implies a lower 1.45 (snippet) - mild disagreement; 1.50 is the practical ceiling (GOLF.com snippet).
- **Launch 11.2 deg:** identical to the R&A long-drive mean (11.2) and inside the TrackMan 120 mph band (7.7-12.6 by AoA/optimizer) and Foresight 10-14.
- **Spin ~2600:** inside every band (TrackMan 1636-2890 at 120 mph; Foresight 1600-2600 at 131 mph). It is 7% below the R&A long-drive mean 2789 and at the *top* of Foresight's 131 mph range, so if anything slightly **high** relative to a total-distance optimum (1600-2400), not low. R&A itself warns spin measurements are noisy.
- **Disagreement to flag (carry, not the power-tier numbers):** the model carry at 130-132 mph (321-331 yd) agrees with TrackMan-chart scaling and R&A (352 at 145 mph; ~2.4 yd/mph) but is **below** Foresight's 342-372 yd at 131 mph (snippet). Sources differ by ~20-40 yd at this speed; the TrackMan chart does not reach 130 mph, so all 130+ TrackMan numbers are extrapolations. Mason's 120+ mph club speed is self-reported, *unverified*.

## 2. Total/carry ratio 1.08-1.10
Published pairs (total/carry): R&A PGA-avg launch simulation 291/272 = **1.07** (fetched); TrackMan carry-optimizer 120 mph: 321/296 = 1.08, 350/310 = 1.13, 305/279 = 1.09 (110 mph +5) (fetched); TrackMan **total**-optimizer 120 mph: 340/290 = 1.17, 358/300 = **1.19**, 110 mph +5: 326/268 = 1.22 (fetched); Foresight 131 mph: 378/342 = 1.105 and 401/372 = 1.078, 124 mph: 340/320 = 1.06 and 386/349 = 1.11 (snippet); a GolfWRX forum post quoting TrackMan tour numbers 269 carry + 25 roll = 294 = 1.09 (snippet, weak). Web rules of thumb: roll 8-12% of driver carry on normal turf, firm ~2x, soft ~0 (ShotTally, snippet, weak); each degree flatter landing = +1.5-2 yd roll (Scott Sackett PDF, snippet); TrackMan says total is a calculated flat/normal-hardness estimate, not measured (golflounge.de, snippet).
**Verdict:** 1.08-1.10 is **supported as the carry-optimized / normal-firmness range** (published 1.06-1.13 for those rows), but it is an **ASSUMPTION for our 350 yd case**: our target (launch 10-11, spin 1600-2400) is a low-spin, flat-landing profile closer to TrackMan's *total* optimizer, which publishes **1.17-1.22** at 110-120 mph. Honest range: **1.07-1.13 normal, up to ~1.2 firm/total-optimized**; use 1.10 only as a central normal-firmness guess. With 296 m (324 yd) carry: 1.08 -> 350 yd, 1.10 -> 356 yd, 1.19 -> 386 yd. Total is condition-dependent; keep reporting **carry** as the primary metric.

## 3. Add-on API (`data/roll_aoa_addon.py`) - MODEL-ONLY, UNCALIBRATED
Not a published model. Structure follows published qualitative facts (flatter landing and lower spin -> more roll; firmness scales roll); coefficients are Data Agent assumptions checked against the pairs above (JSON `validation`). Standalone; Trainer may call it on env output (env/ untouched).
```python
from data.roll_aoa_addon import estimate_roll_yd, estimate_total_from_m, aoa_sensitivity, sensitivity_per_deg
estimate_roll_yd(carry_yd, launch_deg=None, spin_rpm=None, descent_deg=None, firmness="normal"|"soft"|"firm"|"very_firm"|float)
  -> {roll_yd, total_yd, roll_frac, total_over_carry, descent_deg_used, firmness, label}
estimate_total_from_m(carry_m, **same)      # env carry is metres; adds roll_m, total_m
aoa_sensitivity(aoa_list, dynamic_loft_deg=.. | spin_loft_deg=.., ball_mph=190, spin_k=130)  # launch = AoA + SL*(0.96-0.0071*SL); spin = env formula
```
roll_frac = 0.09 x firmness x (1 + 0.045 x (38 - descent)) x (1 + 0.00012 x (2686 - spin)), clipped 0-0.35. Firmness multipliers soft 0.35, normal 1.0, firm 1.6, very_firm 2.0 (assumed from "firm ~2x, soft ~0"). If no descent angle is given it is estimated by a crude heuristic anchored on one point (PGA avg 10.9 deg, 2686 rpm -> 38 deg); **prefer a simulated descent angle** (the env reports none; Trainer could log it).
**Validation vs published pairs:** normal-firmness model ratio 1.08-1.12 for the carry-optimizer/R&A/Foresight rows (published 1.06-1.13); it **under-predicts** TrackMan total-optimizer rows (model 1.12 vs published 1.17-1.22); "firm" gives 1.14-1.20 (over for carry rows, close for total rows).
**Sample (env carry 293 / 296 / 299 m = 320 / 324 / 327 yd, launch 10.4, spin 2400):** soft total 332 / 335 / 339 yd; **normal 353 / 356 / 360 yd**; firm 372 / 376 / 380; very firm 385 / 389 / 393. So a **350 yd total is reachable on normal-to-soft turf only at the top of the carry range, and with ordinary firmness it is met with ~25-30 yd of margin to spare** *(model-only)*; 350 yd **carry** is not supported (best measured 299 m = 327 yd).
**AoA sensitivity (model; dynamic loft 11.5, 190 mph ball):** holding dynamic loft fixed, +1 deg AoA = **+0.14 deg launch, +28 rpm** (spin loft shrinks 1:1, almost cancelling). Holding spin loft fixed (7.5 deg), +1 deg AoA = **+1.0 deg launch, +188 rpm**. Practical reading: raising AoA only lowers spin if the loft delivered at the face drops with it; otherwise launch and spin rise together. Table in JSON for AoA 0-6. This matches the TrackMan chart direction (more AoA at fixed optimizer -> lower spin, higher launch).

## 4. Unverified / caveats
- Roll model coefficients, firmness table, descent heuristic: assumptions, not fit to data beyond the 9 published pairs; Foresight pair launch/spin inputs are range midpoints (12 deg, 2100 rpm), not row data.
- TrackMan chart is a 2010 chart, stops at 120 mph; all 130+ mph TrackMan values are extrapolations. Foresight and ShotTally/Sackett/golflounge/GolfWRX items are search snippets, not fetched pages.
- Foresight vs TrackMan/R&A carry disagreement at 130 mph (~20-40 yd) unresolved.
- Env carry is metres (code reading from earlier docs, to confirm with Trainer); the env has no roll, so any total here is model-only.
- Tutelman launch formula was fetched in earlier repo work, not re-fetched today; the env spin formula is a copy from the repo docs.

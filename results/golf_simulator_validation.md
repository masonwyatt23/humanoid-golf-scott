# Golf simulator validation (model-based, analytic ball model)

Benchmark: **TrackMan PGA Tour driver average** (113 mph club, AoA -1.3 deg, 167 mph ball, smash 1.48, launch 10.9 deg, 2686 rpm, max height 32 yd, land angle 38 deg, carry 275 yd = 251 m).
Sources: https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf; https://www.usga.org/content/dam/usga/pdf/Equipment/Equipment%20Specifications%20Research.pdf

Note: the 282 yd carry in the request belongs to a different 2023-24 row (115 mph / 171 mph / 10.4 deg / 2545 rpm) that we only have from secondary web reports; the primary TrackMan row we could read gives 275 yd for 113 mph. 282 yd is therefore informational only.

## 1. Flight model from published launch conditions (167 mph, 10.9 deg, 2686 rpm)

| metric | model | published | error | tolerance | pass |
|---|---|---|---|---|---|
| carry_yd | 268.30 | 275.00 | -2.4% | 5% | PASS |
| apex_yd | 33.32 | 32.00 | +4.1% | 10% | PASS |
| land_angle_deg | 39.83 | 38.00 | +1.8 | 3 | PASS |
| smash | 1.48 | 1.48 | -0.1% | 3% | PASS |

Model total (carry + bounce/roll, fairway): 295 yd; hang 6.7 s. (TrackMan table above gives carry only; total is not benchmarked.)

## 2. Impact model (club 113 mph, AoA -1.3 deg, dynamic loft 14.00 deg chosen so launch = 10.9 deg)

| metric | model | published | error | tolerance | pass |
|---|---|---|---|---|---|
| ball_mph | 162.45 | 167.00 | -2.7% | 3% | PASS |
| smash | 1.44 | 1.48 | -2.9% | 3% | PASS |
| launch_deg | 10.99 | 10.90 | +0.1 | 1 | PASS |
| backspin_rpm | 4258.58 | 2686.00 | +58.5% | 10% | FAIL |
| carry_yd | 243.36 | 275.00 | -11.5% | 5% | FAIL |
| apex_yd | 35.11 | 32.00 | +9.7% | 10% | PASS |

### 2b. Same impact model with spin calibration spin_scale = 0.62 (Data Agent R1, medium confidence; dynamic loft 14.00 deg for launch 10.9)

Fitted to this single tour-average row, so agreement here is NOT an independent validation; raw spin above is ~60% high, calibrated spin removes that bias at tour conditions only.

| metric | model | published | error | tolerance | pass |
|---|---|---|---|---|---|
| ball_mph | 162.45 | 167.00 | -2.7% | 3% | PASS |
| smash | 1.44 | 1.48 | -2.9% | 3% | PASS |
| launch_deg | 10.99 | 10.90 | +0.1 | 1 | PASS |
| backspin_rpm | 2640.32 | 2686.00 | -1.7% | 10% | PASS |
| carry_yd | 259.54 | 275.00 | -5.6% | 5% | FAIL |
| apex_yd | 31.04 | 32.00 | -3.0% | 10% | PASS |

### 2c. Spin_scale 0.62 AND restitution e = 0.845 (Data Agent R1 + R2, medium confidence; dynamic loft 13.75 deg)

Also tuned on this single tour row (not independent). Shown to separate the two biases: spin (R1) and centre-hit smash (R2).

| metric | model | published | error | tolerance | pass |
|---|---|---|---|---|---|
| ball_mph | 163.97 | 167.00 | -1.8% | 3% | PASS |
| smash | 1.45 | 1.48 | -2.0% | 3% | PASS |
| launch_deg | 10.82 | 10.90 | -0.1 | 1 | PASS |
| backspin_rpm | 2598.18 | 2686.00 | -3.3% | 10% | PASS |
| carry_yd | 262.47 | 275.00 | -4.6% | 5% | PASS |
| apex_yd | 31.16 | 32.00 | -2.6% | 10% | PASS |

Reading: the impact model gets smash/ball speed right but over-predicts backspin (simple center-hit friction model, no gear effect/loft-spin nuance), which lowers carry and raises apex. Use `shot_from_launch` when spin is known; treat `shot_from_club` spin as indicative only.

## 3. Informational (secondary-source row, not pass/fail)

115 mph / 171 mph / 10.4 deg / 2545 rpm -> model carry 276 yd, apex 33 yd (secondary reports quote ~282 yd carry).

## 4. Sensitivities (model-internal sanity, not benchmarks)

- +10 mph ball speed: +19.4 yd carry
- +1000 rpm backspin: -9.6 yd carry

## Scope / honesty

- This validates the ANALYTIC ball model only. The leaderboard's carry/total yards come from the MuJoCo-physics ball (smash ~1.0 artifact, results/smash_anomaly.md) and are not these numbers.
- One benchmark row only: this is a spot check, not a full calibration across clubs or conditions (no wind, altitude, turf variation).

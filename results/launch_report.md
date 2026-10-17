# Launch-monitor-style report (ADDITIVE; gate pass/fail unchanged)

Source: `eval/launch_report.py` over eval_gate JSONs (det policy, 100 eps/seed). Unit/flag logic: `data/launch_output.py` (Data Agent, d6d0f0e). All rows are MODEL-BASED simulation, not measurements of a person.

**Target (published TrackMan driver row)**: 120 mph club -> 178 ball mph, smash 1.483, launch 9.3 deg, spin 2890 rpm, 296 yd carry. The 130 and 132 mph rows are extrapolated upper bounds only (not published), so the 132 mph power tier has no published row to match. Smash/spin thresholds are derived, not published.

Smash column = ball mph / impact club mph. `gate smash_mean` is the gate JSON's smash_factor_mean (mean of per-episode ratios; not a true ratio of the speeds shown).

| gate file | seed | gain | fs | club mph | ball mph | smash | gate smash_mean | launch deg | spin rpm (source) | carry yd | det lat std m | gate | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gate_imit15_dart_s52_seed4000.json | 4000 | - | 2.0 | 120.4 | 119.7 | 0.994 | 1.004 | 12.3 | - (absent) | 124.0 | 1.5 | PASS | WARN smash<1.30 (poor/non-physical contact?) |
| gate_imit15_dart_s53.json | 4000 | - | 2.0 | 120.3 | 119.6 | 0.994 | 1.004 | 12.3 | - (absent) | 123.0 | 1.45 | PASS | WARN smash<1.30 (poor/non-physical contact?) |
| gate_imit19_masonmapped_dart_s51.json | 4000 | - | 2.0 | 75.1 | 67.3 | 0.897 | 0.897 | 13.9 | - (absent) | 64.0 | 0.11 | PASS | WARN smash<1.30 (poor/non-physical contact?) |

Rows below: the gate JSONs are held locally under `results/imit_private/` (not in the repo). Values are copied from the previous report and are **Trainer-reported, file held**; they cannot be regenerated from `main` alone.

| gate file | seed | gain | fs | club mph | ball mph | smash | gate smash_mean | launch deg | spin rpm (source) | carry yd | det lat std m | gate | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gain120/gate_imit18_power_dart_s51.json | 4000 | 1.2 | 2.0 | 132.4 | 195.8 | 1.479 | 1.479 | 12.6 | 2886.0 (hand-set by env impact model (no spin model)) | 323.0 | 2.17 | PASS | Trainer-reported, file held |
| gain102/gate_imit18_power_dart_s51.json | 4000 | 1.02 | 2.0 | 132.4 | 166.6 | 1.258 | 1.258 | 12.6 | 2453.0 (hand-set by env impact model (no spin model)) | 276.0 | 1.68 | PASS | WARN smash<1.30 (poor/non-physical contact?); Trainer-reported, file held |
| gate_imit18_power_dart_s51.json | 4000 | 1.28 | 2.0 | 132.4 | 208.7 | 1.577 | 1.577 | 12.6 | - (absent) | 339.0 | 2.34 | PASS | FAIL smash>1.50; Trainer-reported, file held |
| gate_imit18_power_dart_s52.json | 4000 | 1.28 | 2.0 | 132.4 | 208.8 | 1.577 | 1.577 | 12.6 | - (absent) | 339.0 | 2.34 | PASS | FAIL smash>1.50; Trainer-reported, file held |
| gate_ppo15_stoch_s71.json | 4000 | - | 2.0 | 115.9 | 110.1 | 0.951 | 0.979 | 11.3 | - (absent) | 102.0 | 0.03 | FAIL | WARN smash<1.30 (poor/non-physical contact?); Trainer-reported, file held |
| gate_ppo15_bcreg_s62.json | 4000 | - | 2.0 | 118.4 | 117.3 | 0.991 | 1.001 | 12.0 | - (absent) | 115.0 | 0.49 | FAIL | WARN smash<1.30 (poor/non-physical contact?); Trainer-reported, file held |

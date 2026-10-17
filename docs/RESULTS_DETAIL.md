# Detailed results, status and known limits

Moved verbatim from the previous README so nothing is lost. The top-level [README](../README.md) carries the short, labelled summary; this file carries the full tables and caveats. All numbers come from committed files under `results/`.

## Status table (simulation only)

| Area | State | Verified number / source |
|---|---|---|
| Club-ball contact | Works | 100% true contact in deterministic mode for every left-handed residual-PPO run (`results/gate_*.json`, `results/leaderboard.md`); stochastic mode is lower for some earlier runs |
| Club speed | Works (scripted + residual) | Trained left-handed runs 107-118.5 mph mean peak (123.6 for the flat-launch `left_fast2_s11`) (gate/leaderboard); scripted lofted base 120.3-120.4 mph (`results/TRAINING_NOTES.md` Stage 5). Target 120 mph |
| Deep carry (deterministic) | Works, with a caveat | 96-114 m mean carry (an2: 114.3 m, `results/gate_ppo_resid_v3_left_an2_s0.json`). These runs were trained in the pre-fix strike regime (see Known limits) |
| Lateral gate (carry > 11.98 m, lateral std < 2.73 m, contact >= 99%) | **Fails for every deep-carry trained model** | Lateral std 5.7-8.2 m. Runs that pass the literal gate are flat-launch exploits (e.g. `left_fast2_s11`: 15.2 m carry, -5.8 deg launch) |
| Leaderboard headline (`results/leaderboard.md`) | Best trained model `ppo_v3tiny_s22` (Stage 7, negative result); best overall is the Stage 6 scripted swing | Ranked by contact then mean carry averaged over deterministic + stochastic: 108.5 m for `ppo_v3tiny_s22` (deterministic 117.1 m, stochastic 99.9 m, lateral std 6.1 / 9.2 m). Its lateral spread still fails the gate. **No model meets the showcase criterion.** The leaderboard's own header line still names a legacy scripted baseline as best overall (113.827 m); the same 113.8 m figure is the Stage 6 row |
| Scripted baseline, lofted fix (`configs/fast_scripted_v2_lofted.json`) | Passes in the notes only | Evaluator protocol, 100 eps, seeds 4000/8000: contact 100%, launch 9.3/9.5 deg, carry 70.0/71.9 m, lateral std 0.013 m, 120.3 mph. **No committed gate JSON**; lateral std is tiny because the model has no sidespin. Superseded by Stage 6 above (`results/strike_regime_rerun.md`: 68.9 m carry, 9.0 deg launch, 0.013 m lateral std, 50 eps) |
| **Stage 6 scripted swing (`configs/fast_scripted_v3.json`) - NOT learned** | **Passes all gates** | `results/leaderboard.md` (deterministic = stochastic, zero residual, 50 eps, seed 4000): contact 100%, landed 100%, mean carry 113.8 m, launch 12.2 deg, lateral std 1.66 m, peak club 120.3 mph (max 120.6). Same config in the gate files `results/gate_ppo_v3tiny_s2{1,2,3}.json` (`scripted_zero_residual`, 100 eps): carry 113.0 m, lateral std 2.12 m, 120.3 mph. A hand-tuned config, not a trained policy |
| Trained policy beating scripted | **No** | Stage 7 (`ppo_v3tiny_s21/22/23`: tiny residual PPO on the Stage 6 script) is a recorded negative result: all `gate_pass=false`; deterministic gate carry 86.4 / 105.1 / 93.6 m, lateral std 6.45 / 5.23 / 4.43 m, versus 113.0 m / 2.12 m for the scripted base (`results/gate_ppo_v3tiny_s2*.json`, 100 eps) |
| **No trained model qualifies yet** | Confirmed | `results/leaderboard.md`: no model meets the showcase criterion. Earlier trained-model numbers hold only under their original configs (`results/strike_regime_rerun.md`) |
| Smash factor | **Unverified** | The leaderboard reports scripted ~1.0 (peak ball speed / impact club speed, 1.01 for Stage 6). The ball model has no spin or compliance, so treat smash as a diagnostic, not a validated figure; no real-world comparison exists |
| Model checkpoints | Not published | See `docs/CHECKPOINT_RELEASE.md` for what blocks a Release |
| Real robot / real ball validation | None | Simulation only |


## Known limits

- **Lateral gate fails for deep-carry models.** All trained left-handed runs with 96-114 m carry have lateral std 5.7-8.2 m against a < 2.73 m gate. Runs with tiny lateral spread (an5, an7, an8, fast2) get it from flat or negative launch and carry only 9-15 m.
- **Strike-regime artefact.** Stage 5 notes show negative `loft_deg` means more loft in the v3 model, and that older runs with positive loft or `ball_dz >= 0` struck the club's top edge. Treat all earlier carry/launch numbers (including the table below) as results from that regime, not as physical drives. The Stage 7 `v3tiny` models are the only trained runs on the fixed regime, and they fail the lateral gate.
- **Scripted vs trained.** The Stage 6 scripted swing (`configs/fast_scripted_v3.json`) passes every gate (113.8 m, 12.2 deg, lateral std 1.66 m, 120.3 mph; `results/leaderboard.md`) but is a hand-tuned config, **not learned**. The default scripted swing fails the lateral gate (4.22 m / 3.97 m in the gate files). Trained policies have never beaten their scripted baseline; the Stage 7 residual PPO on the Stage 6 script made it worse (`results/TRAINING_NOTES.md` Stage 7). **No trained model qualifies yet.**
- **Earlier trained-model numbers hold only under their original configs.** Re-running frozen `an2`/`an3`/`fast2` checkpoints under the fixed strike regime (loft -26, ball_dz -0.01) changes carry, launch and lateral std substantially (e.g. `an3_s1` 108.6 m -> 81.1 m, `fast2_s11` 15.2 m -> 33.8 m). These are out-of-distribution diagnostics, not retrained results; see [`results/strike_regime_rerun.md`](../results/strike_regime_rerun.md).
- **Smash factor is unverified.** The reported ~1.0 (scripted) is peak ball speed over club speed in a no-spin, no-compliance ball model; it is not a validated physical figure.
- **Stage 6 gate evidence.** The scripted swing's gate numbers come from the leaderboard (50 eps) and the `scripted_zero_residual` blocks of the v3tiny gate files (100 eps); there is no standalone gate JSON for it.
- **Checkpoints are unpublished,** so the leaderboard and gate cannot be reproduced from this repo alone; `results/` holds the recorded outputs.
- **Deterministic vs stochastic.** The tables below are deterministic unless marked. The leaderboard headline averages both modes (102.9 m for an3_s1), and the carry definition changed between runs (analytic training carry vs MuJoCo physics gate). Compare only within one file.
- Tempo targets from Mason's swings are a loose band (n=11); no speed target is derivable from them.
- Simulation only; no real-robot or real-ball validation.

## Current Performance

Numbers below are copied from the committed `results/leaderboard.md` / `results/leaderboard.json` (50 episodes, seeds 4000-4049, env fingerprint `59bc5ea99d60`, v2 physics; the same rows are unchanged in the current `results/leaderboard.md` (fingerprint `7a2ffa104b56`)). Contact = true club-ball contact. Distance = final ball x in metres (total, including roll); carry = x at landing (0 if the ball never landed).

| Model | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) |
|---|---|---|---|---|---|---|
| ppo_scott_baseline | 30000 | deterministic | 0% | 0.30 | 0.30 | 0.000 |
| ppo_scott_baseline | 30000 | stochastic | 0% | 0.56 | 7.90 | 0.000 |
| ppo_scott_curr | 30000 | deterministic | 100% | 3.01 | 3.01 | 0.000 |
| ppo_scott_curr | 30000 | stochastic | 34% | 5.04 | 13.90 | 0.062 |
| ppo_scott_prev_backup | 30000 | deterministic | 100% | 2.76 | 2.76 | 0.000 |
| ppo_scott_prev_backup | 30000 | stochastic | 38% | 4.86 | 13.62 | 0.021 |
| ppo_scott_final2 | 60000 | deterministic | 48% | 1.80 | 9.80 | 0.091 |
| ppo_scott_final2 | 60000 | stochastic | 60% | 1.96 | 10.37 | 0.128 |
| ppo_scott / ppo_scott_carry1 (best legacy model) | 100000 | deterministic | 98% | 0.47 | 0.59 | 0.102 |
| ppo_scott / ppo_scott_carry1 (best legacy model) | 100000 | stochastic | 66% | 0.88 | 5.93 | 0.237 |

Takeaways for the legacy models above: 100% contact appears only in deterministic mode and carry stays tiny (best mean 0.24 m, stochastic). The residual-PPO runs below are far better. The current `results/leaderboard.md` headline best model is `ppo_resid_v3_left_an3_s1` (ranked by contact averaged over deterministic and stochastic modes, then mean carry; it is not the best on lateral spread or on the gate), not the legacy `ppo_scott_carry1`.

Club speed (from `results/leaderboard.md`, peak club-head linear speed over all physics substeps; 120 mph = 53.64 m/s target): the best legacy model `ppo_scott_carry1` reaches a mean peak of 25.78 m/s and a max of 40.74 m/s (91.1 mph, 75.9% of target) in stochastic mode, with a mean peak ball speed of only 2.45 m/s. In deterministic mode its peak club speed is 0.35 m/s mean / 0.58 m/s max. Single-swing peaks in stochastic mode are not a sustained, controlled swing.

**Early-model club speeds:** the 706,966 m/s peak seen for `ppo_scott_baseline` was real output from an unstable legacy-config simulation (torque_scale 10, out-of-range legacy address pose) that diverged within ~0.05 s (MuJoCo "Nan, Inf or huge value in QACC"), not a metric bug. `eval/flight_tracker.py` now flags episodes with any substep above 100 m/s or non-finite and excludes them from peak stats (raw max is reported, never clipped); the leaderboard shows `ppo_scott_baseline` as n/a (50 sim-unstable episodes excluded).

**Best verified result so far — residual PPO, left-handed, analytic ball flight (`results/gate_ppo_resid_v3_left_an2_s0.json`, `results/gate_ppo_resid_v3_left_an1_s0.json`, `results/leaderboard.md`):** evaluator-protocol gate (`python -m eval.eval_gate <name> 50 4000`: 50 episodes, seeds 4000+, MuJoCo physics with the flight tracker, 450-step flight horizon, **deterministic** policy, v3 env, loft 8 deg). Training notes: `results/TRAINING_NOTES.md` section D.

| Model | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club speed mean (mph) | Peak club max (mph) |
|---|---|---|---|---|---|---|
| scripted zero-residual (no learning) | 100% | 72% | 57.8 | 4.22 | 107.9 | 108.1 |
| ppo_resid_v3_left_an1_s0 | 100% | 100% | 110.3 | 7.53 | 114.5 | 115.4 |
| ppo_resid_v3_left_an2_s0 | 100% | 100% | 114.3 | 7.42 | 114.7 | 115.5 |
| ppo_resid_v3_left_an3_s1 | 100% | 100% | 108.6 | 6.74 | 114.6 | 115.2 |
| ppo_resid_v3_left_an4_s2 (loft 7, native-left Mason style) | 100% | 100% | 96.1 | 6.68 | 111.7 | 112.4 |
| ppo_resid_v3_left_an5_s3 (flat-launch exploit) | 100% | 72% | 9.6 | 0.14 | 117.0 | 117.7 |
| ppo_resid_v3_left_an6_s4 | 100% | 98% | 99.8 | 6.95 | 113.0 | 115.0 |
| ppo_resid_v3_left_an9_s7 | 100% | 100% | 103.3 | 8.17 | 110.4 | 111.7 |
| ppo_resid_v3_left_an7_s5 (flat-launch, leaderboard) | 100% | 66% | 9.0 | 0.26 | 115.3 | 116.9 |
| ppo_resid_v3_left_an8_s6 (flat-launch, leaderboard) | 100% | 82% | 11.4 | 0.10 | 118.5 | 119.2 |
| ppo_resid_v3_left_an10_s8 (leaderboard) | 100% | 94% | 110.0 | 5.67 | 107.0 | 108.4 |
| ppo_resid_v3_left_fast2_s11 (flat-launch, gate JSON) | 100% | 100% | 15.2 | 0.017 | 123.6 | 123.8 |

(All from `results/gate_*.json`, `policy_det` block; same 50 episodes, seeds 4000+. Note the scripted row is the default scripted swing; the an4/an5/an6/an9 gate files use loft 7 and have their own scripted block with 48.1 m carry, 54% landed, 3.97 m lateral std. `gate_pass` is false for every model above.)

an7, an8 and an10 rows come from the committed `results/leaderboard.md`/`.json` (deterministic, 50 episodes, seeds 4000-4049, no gate JSON exists for them). an7 and an8 are flat-launch exploits (mean launch elevation -3.2 and -5.2 degrees) with near-zero lateral spread but only 9-11 m carry, so they fail the carry gate. an10 reaches 110.0 m mean carry (94% landed) with the lowest lateral std of the deep-carry runs, 5.67 m, but it still fails the lateral gate (< 2.73 m); its stochastic carry is 57.1 m with 6.40 m lateral std. Every trained left-handed run in this table fails the gate. Checkpoints are still unpublished.

`left_fast2_s11` (`results/gate_ppo_resid_v3_left_fast2_s11.json`, deterministic, 50 episodes, seed 4000) reaches 123.6 mph mean peak club speed and a 0.017 m lateral std, so it passes the literal gate (carry > 11.98 m, lateral std < 2.73 m, contact >= 99%). But its launch elevation is about -5.8 degrees (100% flat flag), so it is a flat-launch exploit and not a good drive (15.2 m carry). The scripted base in the same protocol carries 30.0 m with 2.92 m lateral std (119.8 mph), i.e. it fails the lateral gate.

**Honest summary (verified against the committed files above):** the best deterministic carry is about 96-114 m at about 111-115 mph peak club speed (an2: 114.3 m / 114.7 mph), but every trained left-handed model **fails** the lateral gate (< 2.73 m): lateral std is 6.7-8.2 m. an5 has lateral std 0.14 m only because it learned a flat, negative-launch strike (carry 9.6 m, 72% landed, so it fails the carry gate too). The default scripted swing also fails the lateral gate (4.22 m / 3.97 m in the gate JSONs). A tuned scripted configuration (`ball_x=0.422`, 5 mm ball-position noise, loft 7, no learning) is reported in `results/TRAINING_NOTES.md` (Address-geometry finding) as passing carry > 11.98 m and lateral std < 2.73 m: 53.1 m carry, 1.98 m lateral std, 107.8 mph, launch about 11 degrees. That result is from the notes only (no committed gate JSON), uses 5 mm noise instead of the default 3 cm, and in the same notes the trained policies do not beat their scripted baseline (an10: lateral 5.74 m vs 2.18 m scripted). Launch is bimodal and set mainly by ball position along the swing arc. Details and an7-an10 numbers (analytic evaluation, not gate protocol) are in `results/TRAINING_NOTES.md`.

Caveats:
- All rows above are **deterministic** (an1/an2 from the committed gate JSONs; an3_s1 from the committed `results/leaderboard.md`/`.json`, same protocol, 50 episodes, seeds 4000+). In stochastic mode an3_s1 has 100% contact, 97.2 m mean carry, 94% landed and 7.49 m lateral std (leaderboard). The leaderboard ranks an3_s1 > an2 > an1 among left-handed models (it has the lowest lateral std, 6.74 m, but an2 has the highest deterministic carry, 114.3 m). The earlier stochastic ladder run (`results/ppo_resid_v3_ladder_s0.json`, v3 env, MuJoCo landing) had 100% contact and a peak club speed max of 50.46 m/s (112.9 mph) but only 0.24 m mean carry and 20% landed, with the scripted swing at 6.6 m. Do not mix these protocols.
- The an1/an2 policies are trained with an **analytic** ball-flight model (drag + Magnus, assumed backspin = clip(1500 + 70 x launch elevation deg, 1000, 5000) rpm, no sidespin). Their training-time carry (about 92-93 m) is analytic. The gate numbers above come from the MuJoCo physics gate. The carry definition changed between runs, so compare only within a single JSON.
- Launch elevation stays near 33 degrees (target 10-15), and smash factor drops from 0.90 (scripted) to about 0.73-0.76 as the policy trades smash for loft. The Mason-style match score is slightly lower than scripted (0.62 vs 0.53-0.55).
- Lateral std is 6.7-7.5 m for an1-an3, so those runs **fail** the teammate gate (carry > 11.98 m AND lateral std < 2.73 m): `gate_pass` is false in every gate JSON and the leaderboard marks an3_s1 FAIL too. Relative to carry, lateral dispersion is about 0.066 (an2) vs 0.073 (scripted).
- Club speed of about 115 mph is the peak head speed in a scripted-swing-plus-residual setup; it is not a human-like or sustained controlled swing and is below the 120 mph target (about 95.5%).
- Everything is simulation only; no real-robot or real-ball validation.
- Details for the older (non-residual) models are in the table above; those carry numbers are not comparable with the gate protocol.

> **Reproducibility caveat:** the v2/v3 environment code (`env/`), `eval/flight_tracker.py`, `eval/leaderboard.py` and training scripts are pushed, but the model checkpoints are not (trained models are not committed; they will be shared via a GitHub Releases note). **Trained model checkpoints are not published yet.** A GitHub Release will be considered only once it is confirmed the models contain no non-commercial data (GolfDB / CMU mocap licensing). The leaderboard therefore can't be re-run end to end from this repo yet; the `results/` files are the recorded outputs.

See [ROADMAP.md](../ROADMAP.md) for next steps.

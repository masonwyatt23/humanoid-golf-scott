# PureGolf / Adam Scott Humanoid Training System

Autonomous pipeline for training a simulated humanoid to swing a golf club in the style of Adam Scott and other pure/textbook swings.

## Current Performance

Numbers below are copied from the committed `results/leaderboard.md` / `results/leaderboard.json` (50 episodes, seeds 4000-4049, env fingerprint `59bc5ea99d60`, v2 physics; the same rows are unchanged in the current `results/leaderboard.md` (fingerprint `99f124d7b5dd`)). Contact = true club-ball contact. Distance = final ball x in metres (total, including roll); carry = x at landing (0 if the ball never landed).

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
| ppo_scott / ppo_scott_carry1 (best by leaderboard) | 100000 | deterministic | 98% | 0.47 | 0.59 | 0.102 |
| ppo_scott / ppo_scott_carry1 (best by leaderboard) | 100000 | stochastic | 66% | 0.88 | 5.93 | 0.237 |

Takeaways for the legacy models above: 100% contact appears only in deterministic mode and carry stays tiny (best mean 0.24 m, stochastic). The residual-PPO runs below are the current best; the leaderboard ranks by contact, then carry.

Club speed (from `results/leaderboard.md`, peak club-head linear speed over all physics substeps; 120 mph = 53.64 m/s target): the best model `ppo_scott_carry1` reaches a mean peak of 25.78 m/s and a max of 40.74 m/s (91.1 mph, 75.9% of target) in stochastic mode, with a mean peak ball speed of only 2.45 m/s. In deterministic mode its peak club speed is 0.35 m/s mean / 0.58 m/s max. Single-swing peaks in stochastic mode are not a sustained, controlled swing.

**Early-model club speeds:** the 706,966 m/s peak seen for `ppo_scott_baseline` was real output from an unstable legacy-config simulation (torque_scale 10, out-of-range legacy address pose) that diverged within ~0.05 s (MuJoCo "Nan, Inf or huge value in QACC"), not a metric bug. `eval/flight_tracker.py` now flags episodes with any substep above 100 m/s or non-finite and excludes them from peak stats (raw max is reported, never clipped); the leaderboard shows `ppo_scott_baseline` as n/a (50 sim-unstable episodes excluded).

**Best verified result so far — residual PPO, left-handed, analytic ball flight (`results/gate_ppo_resid_v3_left_an2_s0.json`, `results/gate_ppo_resid_v3_left_an1_s0.json`, `results/leaderboard.md`):** evaluator-protocol gate (`python -m eval.eval_gate <name> 50 4000`: 50 episodes, seeds 4000+, MuJoCo physics with the flight tracker, 450-step flight horizon, **deterministic** policy, v3 env, loft 8 deg). Training notes: `results/TRAINING_NOTES.md` section D.

| Model | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club speed mean (mph) | Peak club max (mph) |
|---|---|---|---|---|---|---|
| scripted zero-residual (no learning) | 100% | 72% | 57.8 | 4.22 | 107.9 | 108.1 |
| ppo_resid_v3_left_an1_s0 | 100% | 100% | 110.3 | 7.53 | 114.5 | 115.4 |
| ppo_resid_v3_left_an2_s0 | 100% | 100% | 114.3 | 7.42 | 114.7 | 115.5 |
| ppo_resid_v3_left_an3_s1 (leaderboard row; no gate JSON committed) | 100% | 100% | 108.6 | 6.74 | 114.6 | 115.2 |

Caveats:
- All rows above are **deterministic** (an1/an2 from the committed gate JSONs; an3_s1 from the committed `results/leaderboard.md`/`.json`, same protocol, 50 episodes, seeds 4000+). In stochastic mode an3_s1 has 100% contact, 97.2 m mean carry, 94% landed and 7.49 m lateral std (leaderboard). The leaderboard ranks an3_s1 > an2 > an1 among left-handed models (it has the lowest lateral std, 6.74 m, but an2 has the highest deterministic carry, 114.3 m). The earlier stochastic ladder run (`results/ppo_resid_v3_ladder_s0.json`, v3 env, MuJoCo landing) had 100% contact and a peak club speed max of 50.46 m/s (112.9 mph) but only 0.24 m mean carry and 20% landed, with the scripted swing at 6.6 m. Do not mix these protocols.
- The an1/an2 policies are trained with an **analytic** ball-flight model (drag + Magnus, assumed backspin = clip(1500 + 70 x launch elevation deg, 1000, 5000) rpm, no sidespin). Their training-time carry (about 92-93 m) is analytic. The gate numbers above come from the MuJoCo physics gate. The carry definition changed between runs, so compare only within a single JSON.
- Launch elevation stays near 33 degrees (target 10-15), and smash factor drops from 0.90 (scripted) to about 0.73-0.76 as the policy trades smash for loft. The Mason-style match score is slightly lower than scripted (0.62 vs 0.53-0.55).
- Lateral std is 6.7-7.5 m, so all three left-handed runs **fail** the teammate gate (carry > 11.98 m AND lateral std < 2.73 m): `gate_pass` is false in both gate JSONs and the leaderboard marks an3_s1 FAIL too. Relative to carry, lateral dispersion is about 0.066 (an2) vs 0.073 (scripted).
- Club speed of about 115 mph is the peak head speed in a scripted-swing-plus-residual setup; it is not a human-like or sustained controlled swing and is below the 120 mph target (about 95.5%).
- Everything is simulation only; no real-robot or real-ball validation.
- Details for the older (non-residual) models are in the table above; those carry numbers are not comparable with the gate protocol.

> **Reproducibility caveat:** the v2/v3 environment code (`env/`), `eval/flight_tracker.py`, `eval/leaderboard.py` and training scripts are pushed, but the model checkpoints are not (trained models are not committed; they will be shared via a GitHub Releases note). **Trained model checkpoints are not published yet.** A GitHub Release will be considered only once it is confirmed the models contain no non-commercial data (GolfDB / CMU mocap licensing). The leaderboard therefore can't be re-run end to end from this repo yet; the `results/` files are the recorded outputs.

See [ROADMAP.md](ROADMAP.md) for next steps.

## Features

- MuJoCo humanoid + club + ball with proper address initialization
- Synthetic Adam Scott / Scheffler / Rory / average style references
- Multi-swing reference dataset loader
- Curriculum scaffolding (Address → Contact → Style → Ball flight)
- Dense approach + contact + imitation + ball-flight rewards
- PPO training (Stable-Baselines3)
- Style comparison script (`eval/compare_styles.py`)
- Public video proxy for Adam Scott pure swing footage

## Quick Start

```bash
pip install -r requirements.txt
python -m data.generate_synthetic_scott
python -m train.train_ppo --style scott --timesteps 50000
# train_ppo writes models/ppo_scott.zip (models/ is created by training; trained models are gitignored and go to a releases note)
python -m eval.evaluate --model models/ppo_scott --episodes 5
python -m eval.compare_styles
```

## Project Structure

- `data/` — synthetic generators and video processing
- `env/` — MuJoCo environment and model
- `imitation/` — reference dataset and curriculum
- `train/` — PPO training
- `eval/` — evaluation, rendering, style comparison

## Extending with Real PureGolf Content

1. See `python -m data.download_puregolf_proxy` (lists sources + licensing notes; downloads need `--download --i-have-reviewed-tos`; most footage is copyrighted).
2. Place permitted videos in `data/raw_videos/` (gitignored).
3. Run `python -m data.process_video [--capture-fps 250]` (resumable, gap-filling, smoothing).
4. For production quality use WHAM or GVHMR, see `docs/WHAM_GVHMR.md`; save `.npz` to `data/references/`.

5. The ReferenceDataset automatically loads them.

See `docs/NEXT_DATA_SOURCES.md` for the ranked list of real data sources. Tests: `pytest tests`.

### Data licensing notes

- **GolfDB videos are not licensed for commercial use** (research/non-commercial only). Use GolfDB-derived data only for non-commercial research; see `docs/GOLFDB_PLAN.md`.
- **CMU mocap-derived files** (`data/references/cmu_*.npz`) require acknowledgment of the CMU Graphics Lab Motion Capture Database, and may not be resold as a standalone dataset. See `docs/CMU_MOCAP_GOLF.md`.
- Every reference `.npz` carries `license_class` / `commercial_ok` tags; the per-file license column is in `docs/REFERENCE_PATHS.md`.
- Raw videos and footage (including Mason's self-filmed swings) are never committed: `*.mp4`, `*.mov`, `*.avi`, `*.mkv`, `*.webm` and `data/raw_videos/` are gitignored.

Created as part of AshlrAI agentic engineering experiments.

# PureGolf / Adam Scott Humanoid Training System

Autonomous pipeline for training a simulated humanoid to swing a golf club in the style of Adam Scott and other pure/textbook swings.

## Current Performance

Numbers below are copied from the committed `results/leaderboard.md` / `results/leaderboard.json` (50 episodes, seeds 4000-4049, env fingerprint `59bc5ea99d60`, v2 physics). Contact = true club-ball contact. Distance = final ball x in metres (total, including roll); carry = x at landing (0 if the ball never landed).

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

Takeaways: 100% contact has been reached by some models in deterministic mode, but not together with distance. Carry is still tiny (best mean 0.24 m) and the leaderboard ranks by contact, then carry.

Club speed (from `results/leaderboard.md`, peak club-head linear speed over all physics substeps; 120 mph = 53.64 m/s target): the best model `ppo_scott_carry1` reaches a mean peak of 25.78 m/s and a max of 40.74 m/s (91.1 mph, 75.9% of target) in stochastic mode, with a mean peak ball speed of only 2.45 m/s. In deterministic mode its peak club speed is 0.35 m/s mean / 0.58 m/s max. Single-swing peaks in stochastic mode are not a sustained, controlled swing.

**Early-model club speeds:** the 706,966 m/s peak seen for `ppo_scott_baseline` was real output from an unstable legacy-config simulation (torque_scale 10, out-of-range legacy address pose) that diverged within ~0.05 s (MuJoCo "Nan, Inf or huge value in QACC"), not a metric bug. `eval/flight_tracker.py` now flags episodes with any substep above 100 m/s or non-finite and excludes them from peak stats (raw max is reported, never clipped); the leaderboard shows `ppo_scott_baseline` as n/a (50 sim-unstable episodes excluded).

> **Reproducibility caveat:** the v2/v3 environment code (`env/`), `eval/flight_tracker.py`, `eval/leaderboard.py` and training scripts are pushed, but the model checkpoints are not (trained models are not committed; they will be shared via a GitHub Releases note). The leaderboard therefore can't be re-run end to end from this repo yet; the `results/` files are the recorded outputs.

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

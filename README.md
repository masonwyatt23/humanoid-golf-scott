# PureGolf / Adam Scott Humanoid Training System

Autonomous pipeline for training a simulated humanoid to swing a golf club in the style of Adam Scott and other pure/textbook swings.

## Current Performance

- **Contact:** reliable (100%) contact rate is achievable with the dense approach + contact rewards.
- **Distance:** still modest; the ball-velocity (cvel) fix and post-contact velocity bonus (see `ROADMAP.md`) are expected to improve carry, but no post-fix numbers are committed yet.

> No results/metrics files are committed to this repo, so no exact distance figures are quoted here. Reproduce them with `python -m eval.evaluate` (mean distance, contact rate) and `python -m eval.compare_styles`.

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

1. Download reels from @puregolf__ or public Adam Scott slow-mo videos.
2. Place in `data/raw_videos/`.
3. Run `python -m data.process_video` (planned; not yet implemented in this repo).
4. For production quality use WHAM or GVHMR and save `.npz` to `data/references/`.
5. The ReferenceDataset automatically loads them.

Created as part of AshlrAI agentic engineering experiments.

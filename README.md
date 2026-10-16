# PureGolf / Adam Scott Humanoid Training System

Autonomous pipeline for training a simulated humanoid to swing a golf club in the style of Adam Scott and other pure/textbook swings (PureGolf Instagram content or public slow-mo videos).

**Current status**: ~40k-step training achieves **100% contact rate**. Ball distance is still developing; longer runs and curriculum improve carry.

## Features

- MuJoCo humanoid + club + ball environment with proper address initialization
- Synthetic Adam Scott / Scheffler / Rory / average style reference generators
- Multi-swing reference dataset loader
- Curriculum learning (Address → Contact → Style → Ball flight)
- Dense approach + contact + imitation + ball-flight rewards
- PPO training via Stable-Baselines3
- Evaluation and open-loop tracking baselines
- Public video proxy for Adam Scott pure swing footage

## Quick Start

```bash
pip install -r requirements.txt
python -m data.generate_synthetic_scott
python -m train.train_ppo --style scott --timesteps 100000
python -m eval.evaluate --model models/ppo_scott --episodes 5
```

## Project Structure

- `data/` — synthetic generators and video processing
- `env/` — MuJoCo environment and model
- `imitation/` — reference dataset and curriculum
- `train/` — PPO training
- `eval/` — evaluation and rendering

## Extending with Real PureGolf Content

1. Download reels from @puregolf__ or public Adam Scott slow-mo videos.
2. Place in `data/raw_videos/`.
3. Run `python -m data.process_video` (MediaPipe baseline).
4. For production quality use WHAM or GVHMR and save `.npz` to `data/references/`.
5. The ReferenceDataset automatically loads them.

## Next Steps

- Replace simplified humanoid with Unitree G1/H1 MJCF
- Stronger 3D reconstruction (WHAM/GVHMR)
- Longer curriculum training on GPU
- Ball spin / launch metrics

Created as part of AshlrAI agentic engineering experiments.

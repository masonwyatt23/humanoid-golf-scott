"""
Train a PPO policy on the humanoid golf environment with Adam Scott-style imitation.
"""

import argparse
from pathlib import Path
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from env.humanoid_golf_env import HumanoidGolfEnv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", type=str, default="scott", choices=["scott", "scheffler", "rory", "average"])
    parser.add_argument("--timesteps", type=int, default=100_000)
    parser.add_argument("--n_envs", type=int, default=4)
    args = parser.parse_args()

    ref_path = Path(__file__).parent.parent / "data" / "references" / f"{args.style}_swing.npz"
    if not ref_path.exists():
        print(f"Reference not found: {ref_path}")
        print("Generating synthetic references...")
        from data.generate_synthetic_scott import generate_scott_style_swing, save_reference
        data = generate_scott_style_swing(style=args.style)
        save_reference(data, ref_path)

    def make_env():
        return HumanoidGolfEnv(reference_path=str(ref_path))

    env = make_vec_env(make_env, n_envs=args.n_envs)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        tensorboard_log=None,
    )

    print(f"Training on {args.style} style for {args.timesteps} timesteps...")
    model.learn(total_timesteps=args.timesteps)

    save_dir = Path(__file__).parent.parent / "models"
    save_dir.mkdir(exist_ok=True)
    model.save(save_dir / f"ppo_{args.style}")
    print(f"Model saved to {save_dir / f'ppo_{args.style}'}")


if __name__ == "__main__":
    main()

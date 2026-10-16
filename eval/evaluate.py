"""
Evaluate a trained policy and report ball flight + style metrics.
"""

import argparse
from pathlib import Path
import numpy as np

from stable_baselines3 import PPO
from env.humanoid_golf_env import HumanoidGolfEnv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, help="Path to saved model (without .zip)")
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--style", type=str, default="scott")
    args = parser.parse_args()

    ref_path = Path(__file__).parent.parent / "data" / "references" / f"{args.style}_swing.npz"
    env = HumanoidGolfEnv(reference_path=str(ref_path) if ref_path.exists() else None)

    model = PPO.load(args.model)

    distances = []
    contacts = []

    for ep in range(args.episodes):
        obs, _ = env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

        distances.append(info["ball_distance"])
        contacts.append(info["contacted"])
        print(f"Episode {ep+1}: distance={info['ball_distance']:.2f}m, contacted={info['contacted']}")

    print("\n=== Summary ===")
    print(f"Mean distance: {np.mean(distances):.2f}m ± {np.std(distances):.2f}")
    print(f"Contact rate: {np.mean(contacts)*100:.0f}%")


if __name__ == "__main__":
    main()

"""
Compare policies trained on different pure-swing styles.
"""

import argparse
from pathlib import Path
import numpy as np
from stable_baselines3 import PPO
from env.humanoid_golf_env import HumanoidGolfEnv


STYLES = ["scott", "scheffler", "rory", "average"]


def evaluate_style(style: str, episodes: int = 3) -> dict:
    ref_path = Path("data/references") / f"{style}_swing.npz"
    model_path = Path("models") / f"ppo_{style}"
    
    if not model_path.with_suffix(".zip").exists():
        return {"style": style, "status": "no_model"}
    
    env = HumanoidGolfEnv(reference_path=str(ref_path) if ref_path.exists() else None)
    model = PPO.load(str(model_path))
    
    distances = []
    contacts = []
    
    for _ in range(episodes):
        obs, _ = env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, _, term, trunc, info = env.step(action)
            done = term or trunc
        distances.append(info["ball_distance"])
        contacts.append(info["contacted"])
    
    return {
        "style": style,
        "mean_distance": float(np.mean(distances)),
        "std_distance": float(np.std(distances)),
        "contact_rate": float(np.mean(contacts)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=3)
    args = parser.parse_args()
    
    print("Style Comparison\n" + "=" * 40)
    results = []
    for style in STYLES:
        r = evaluate_style(style, args.episodes)
        results.append(r)
        if r.get("status") == "no_model":
            print(f"{style:12s}  (no model trained)")
        else:
            print(f"{style:12s}  dist={r['mean_distance']:.2f}m  contact={r['contact_rate']*100:.0f}%")
    
    print("\nBest distance:", max((r for r in results if "mean_distance" in r), key=lambda x: x["mean_distance"], default=None))


if __name__ == "__main__":
    main()

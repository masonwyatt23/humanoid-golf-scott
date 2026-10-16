"""
Train policies for multiple pure-swing styles in sequence.
"""

import subprocess
import sys
from pathlib import Path


STYLES = ["scott", "scheffler", "rory", "average"]


def train_style(style: str, timesteps: int = 30000):
    print(f"\n=== Training {style} for {timesteps} steps ===")
    cmd = [
        sys.executable, "-m", "train.train_ppo",
        "--style", style,
        "--timesteps", str(timesteps),
        "--n_envs", "1",
    ]
    subprocess.run(cmd, check=True)


def main():
    timesteps = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
    for style in STYLES:
        try:
            train_style(style, timesteps)
        except Exception as e:
            print(f"Failed to train {style}: {e}")
    print("\nMulti-style training complete. Run: python -m eval.compare_styles")


if __name__ == "__main__":
    main()

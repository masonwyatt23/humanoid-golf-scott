"""
Generate synthetic Adam Scott-style golf swing reference motions.

These are kinematic trajectories that capture key characteristics of Scott's swing:
- Smooth, unhurried tempo
- Excellent sequencing (lower body initiates downswing)
- Relatively stable lower body / minimal lateral sway
- Clean plane, delayed wrist release
- Good width and balance

Output format is a .npz compatible with the training pipeline.
"""

import numpy as np
from pathlib import Path
from typing import Dict


def generate_scott_style_swing(duration: float = 1.4, dt: float = 0.01, style: str = "scott") -> Dict[str, np.ndarray]:
    """
    Generate a full swing trajectory.
    style options: "scott", "scheffler", "rory", "average"
    """
    t = np.arange(0, duration, dt)
    n = len(t)

    phase = t / duration

    if style == "scott":
        backswing_time = 0.65
        tempo_ratio = 3.0
        lower_body_stability = 0.85
        wrist_delay = 0.75
        sway = 0.02
    elif style == "scheffler":
        backswing_time = 0.55
        tempo_ratio = 2.2
        lower_body_stability = 0.4
        wrist_delay = 0.65
        sway = 0.12
    elif style == "rory":
        backswing_time = 0.58
        tempo_ratio = 2.6
        lower_body_stability = 0.7
        wrist_delay = 0.70
        sway = 0.04
    else:
        backswing_time = 0.6
        tempo_ratio = 2.5
        lower_body_stability = 0.6
        wrist_delay = 0.6
        sway = 0.06

    joints = np.zeros((n, 11))

    for i, p in enumerate(phase):
        if p < backswing_time:
            bs = p / backswing_time
            joints[i, 0] = -120 * bs
            joints[i, 2] = 80 * bs
            joints[i, 3] = -30 * bs
            joints[i, 5] = -25 * bs * (1 - lower_body_stability)
            joints[i, 6] = 20 * bs
        else:
            ds = (p - backswing_time) / (1 - backswing_time)
            release = np.clip((ds - wrist_delay) / (1 - wrist_delay), 0, 1)
            joints[i, 0] = -120 + 200 * ds
            joints[i, 2] = 80 - 60 * ds
            joints[i, 3] = -30 + 90 * release
            joints[i, 5] = -25 + 50 * ds * (1.2 - lower_body_stability)
            joints[i, 6] = 20 + 40 * ds
            joints[i, 5] += sway * 100 * np.sin(ds * np.pi)

    joints += np.random.randn(*joints.shape) * 1.5

    club_head = np.zeros((n, 3))
    for i in range(n):
        shoulder = joints[i, 0] * np.pi / 180
        elbow = joints[i, 2] * np.pi / 180
        wrist = joints[i, 3] * np.pi / 180
        club_head[i, 0] = 0.3 + 0.58 * np.sin(shoulder + elbow) + 1.12 * np.sin(shoulder + elbow + wrist)
        club_head[i, 2] = 1.0 + 0.58 * np.cos(shoulder + elbow) + 1.12 * np.cos(shoulder + elbow + wrist)

    return {
        "time": t,
        "joints": joints,
        "club_head": club_head,
        "style": style,
        "duration": duration,
        "dt": dt,
    }


def save_reference(data: Dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **{k: v for k, v in data.items() if isinstance(v, np.ndarray)})
    print(f"Saved reference motion to {path}")


if __name__ == "__main__":
    out_dir = Path(__file__).parent.parent / "data" / "references"
    for style in ["scott", "scheffler", "rory", "average"]:
        data = generate_scott_style_swing(style=style)
        save_reference(data, out_dir / f"{style}_swing.npz")
    print("Synthetic reference motions generated.")

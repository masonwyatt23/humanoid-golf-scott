"""
Train a PPO policy on the humanoid golf environment with Adam Scott-style imitation.
"""

import argparse
from pathlib import Path
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from env.humanoid_golf_env import HumanoidGolfEnv
from stable_baselines3.common.callbacks import BaseCallback


class ProgressCallback(BaseCallback):
    """Feeds training progress (0..1) to envs (curriculum) and logs contact/distance."""

    def __init__(self, total, log_every=5000):
        super().__init__()
        self.total, self.log_every, self._next = total, log_every, log_every
        self.recent = []

    def _on_step(self):
        p = self.num_timesteps / self.total
        self.training_env.env_method("set_progress", p)
        for d, i in zip(self.locals["dones"], self.locals["infos"]):
            if d:
                self.recent.append((i.get("true_contact", False), i.get("max_ball_x", 0.0), i.get("carry", 0.0)))
        if self.num_timesteps >= self._next:
            r = self.recent[-100:]
            if r:
                print(f"[progress {p:.2f}] steps={self.num_timesteps} eps={len(self.recent)} contact={np.mean([x[0] for x in r]):.2f} "
                      f"max_ball_x={np.mean([x[1] for x in r]):.2f} carry={np.mean([x[2] for x in r]):.2f}", flush=True)
            self._next += self.log_every
        return True


def evaluate(model, make_env, n=50):
    env = make_env()
    rows = []
    for ep in range(n):
        obs, _ = env.reset(seed=1000 + ep)
        env.set_progress(1.0)
        done = False
        while not done:
            act, _ = model.predict(obs, deterministic=True)
            obs, _, done, trunc, info = env.step(act)
            done = done or trunc
        rows.append(info)
    c = np.array([r["true_contact"] for r in rows], float)
    mx = np.array([r["max_ball_x"] for r in rows])
    cr = np.array([r["carry"] for r in rows])
    cs = np.array([r["impact_club_speed"] for r in rows])
    bs = np.array([r["peak_ball_speed"] for r in rows])
    legacy = np.mean([r["contacted"] for r in rows])
    print(f"EVAL n={n} true_contact_rate={c.mean():.2f} legacy_contacted_rate={legacy:.2f} "
          f"mean_ball_x={mx.mean():.2f} max_ball_x={mx.max():.2f} mean_ball_x_given_contact={(mx[c>0].mean() if c.any() else 0):.2f} "
          f"mean_carry={cr.mean():.2f} max_carry={cr.max():.2f} mean_impact_club_speed={cs.mean():.1f} mean_peak_ball_speed={bs.mean():.2f}")
    return {"n_episodes": n, "true_contact_rate": float(c.mean()), "legacy_contacted_rate": float(legacy),
            "mean_total_distance_x": float(mx.mean()), "max_total_distance_x": float(mx.max()),
            "mean_total_distance_x_given_contact": float(mx[c > 0].mean()) if c.any() else 0.0,
            "mean_carry": float(cr.mean()), "max_carry": float(cr.max()), "landed_fraction": float((cr > 0).mean()),
            "mean_impact_club_speed": float(cs.mean()), "mean_peak_ball_speed": float(bs.mean()), "max_peak_ball_speed": float(bs.max())}



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", type=str, default="scott", choices=["scott", "scheffler", "rory", "average"])
    parser.add_argument("--timesteps", type=int, default=100_000)
    parser.add_argument("--n_envs", type=int, default=4)
    parser.add_argument("--curriculum", action="store_true", help="staged reward: contact first, ball-flight weight ramps up")
    parser.add_argument("--pin_torso", action="store_true")
    parser.add_argument("--address_pose", default="legacy", choices=["legacy", "fixed"])
    parser.add_argument("--torque_scale", type=float, default=10.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--eval_episodes", type=int, default=50)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()

    ref_path = Path(__file__).parent.parent / "data" / "references" / f"{args.style}_swing.npz"
    if not ref_path.exists():
        print(f"Reference not found: {ref_path}")
        print("Generating synthetic references...")
        from data.generate_synthetic_scott import generate_scott_style_swing, save_reference
        data = generate_scott_style_swing(style=args.style)
        save_reference(data, ref_path)

    def make_env():
        return HumanoidGolfEnv(reference_path=str(ref_path), curriculum=args.curriculum, pin_torso=args.pin_torso,
                               address_pose=args.address_pose, torque_scale=args.torque_scale)

    env = make_vec_env(make_env, n_envs=args.n_envs, seed=args.seed)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=0,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        tensorboard_log=None,
        seed=args.seed,
    )

    print(f"Training on {args.style} style for {args.timesteps} timesteps...")
    model.learn(total_timesteps=args.timesteps, callback=ProgressCallback(args.timesteps))
    metrics = evaluate(model, make_env, n=args.eval_episodes)
    import json
    metrics.update(vars(args))
    rd = Path(__file__).parent.parent / "results"
    rd.mkdir(exist_ok=True)
    with open(rd / f"train_{args.style}{args.tag}.json", "w") as f:
        json.dump(metrics, f, indent=2)

    save_dir = Path(__file__).parent.parent / "models"
    save_dir.mkdir(exist_ok=True)
    model.save(save_dir / f"ppo_{args.style}{args.tag}")
    print(f"Model saved to {save_dir / f'ppo_{args.style}{args.tag}'}")


if __name__ == "__main__":
    main()

"""
Evaluate a trained policy and report ball flight, contact, and swing-consistency metrics.

Usage:
    python -m eval.evaluate --model models/ppo_scott --style scott --episodes 20 \
        [--seed 0] [--json eval/results/scott.json] [--stochastic]

Metric definitions (all computed over episodes):
  contact_rate      fraction of episodes where the env flagged contact.
  mean/std_distance ball x-position (m) at episode end (NOT true carry; the env
                    reports final x of the ball body).
  cv_distance       std/|mean| of distance (unitless; lower = more consistent).
                    NaN if mean is ~0.
  path_dispersion   mean over normalized swing time of the 3D std (m) of the club
                    head position across episodes (each trajectory resampled to a
                    common length). Lower = more repeatable club head path.
  distance_*_contact  distance stats restricted to contacted episodes only.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

N_PATH_POINTS = 50


def _resample(traj: np.ndarray, n: int = N_PATH_POINTS) -> np.ndarray:
    """Linearly resample a (T, 3) trajectory to (n, 3) on normalized time."""
    traj = np.asarray(traj, dtype=float)
    if len(traj) == 1:
        return np.repeat(traj, n, axis=0)
    src = np.linspace(0.0, 1.0, len(traj))
    dst = np.linspace(0.0, 1.0, n)
    return np.stack([np.interp(dst, src, traj[:, k]) for k in range(traj.shape[1])], axis=1)


def club_path_dispersion(paths: Sequence[np.ndarray]) -> float:
    """Mean per-timestep 3D std (m) of club head position across episodes."""
    if len(paths) < 2:
        return float("nan")
    stack = np.stack([_resample(p) for p in paths])  # (E, N, 3)
    per_point_std = np.sqrt(np.var(stack, axis=0).sum(axis=-1))  # (N,)
    return float(per_point_std.mean())


def compute_metrics(distances: Sequence[float], contacts: Sequence[bool],
                    club_paths: Optional[Sequence[np.ndarray]] = None) -> Dict[str, float]:
    """Pure-numpy summary of per-episode results (no sim required)."""
    d = np.asarray(distances, dtype=float)
    c = np.asarray(contacts, dtype=bool)
    if d.size == 0:
        raise ValueError("no episodes to summarize")
    mean = float(d.mean())
    std = float(d.std())  # population std, ddof=0
    out = {
        "episodes": int(d.size),
        "contact_rate": float(c.mean()),
        "mean_distance": mean,
        "std_distance": std,
        "max_distance": float(d.max()),
        "cv_distance": std / abs(mean) if abs(mean) > 1e-6 else float("nan"),
        "mean_distance_contact": float(d[c].mean()) if c.any() else float("nan"),
        "std_distance_contact": float(d[c].std()) if c.any() else float("nan"),
        "path_dispersion": club_path_dispersion(club_paths) if club_paths else float("nan"),
    }
    return out


def rollout(model, env, episodes: int, seed: Optional[int] = None,
            deterministic: bool = True) -> Dict[str, list]:
    """Run episodes; record final ball distance, contact flag, and club head path."""
    import mujoco  # noqa: F401  (env already requires it)
    club_id = env.model.geom("club_head").id
    distances, contacts, paths = [], [], []
    true_contacts, carries, max_xs, ball_speeds, club_speeds, joint_trajs = [], [], [], [], [], []
    for ep in range(episodes):
        obs, _ = env.reset(seed=None if seed is None else seed + ep)
        path = [env.data.geom_xpos[club_id].copy()]
        jt = [env.data.qpos[14:25].copy()]
        done, info = False, {}
        while not done:
            action, _ = model.predict(obs, deterministic=deterministic)
            obs, _, terminated, truncated, info = env.step(action)
            path.append(env.data.geom_xpos[club_id].copy())
            jt.append(env.data.qpos[14:25].copy())
            done = terminated or truncated
        distances.append(info["ball_distance"])
        contacts.append(bool(info["contacted"]))
        paths.append(np.array(path))
        true_contacts.append(bool(info.get("true_contact", info["contacted"])))
        carries.append(float(info.get("carry", 0.0)))
        max_xs.append(float(info.get("max_ball_x", info["ball_distance"])))
        ball_speeds.append(float(info.get("peak_ball_speed", float("nan"))))
        club_speeds.append(float(info.get("impact_club_speed", float("nan"))))
        joint_trajs.append(np.array(jt))
    return {"distances": distances, "contacts": contacts, "paths": paths,
            "true_contacts": true_contacts, "carries": carries, "max_xs": max_xs,
            "ball_speeds": ball_speeds, "club_speeds": club_speeds, "joint_trajs": joint_trajs}


def evaluate_model(model_path: str, style: str, episodes: int = 20, seed: Optional[int] = 0,
                   deterministic: bool = True, verbose: bool = False,
                   env_kwargs: Optional[dict] = None) -> Dict[str, float]:
    """Load a PPO model and return metrics. Raises FileNotFoundError if missing."""
    from stable_baselines3 import PPO
    from env.humanoid_golf_env import HumanoidGolfEnv

    zip_path = Path(model_path)
    if zip_path.suffix != ".zip":
        zip_path = zip_path.with_suffix(".zip")
    if not zip_path.exists():
        raise FileNotFoundError(f"model not found: {zip_path}")

    ref = Path(__file__).resolve().parent.parent / "data" / "references" / f"{style}_swing.npz"
    env = HumanoidGolfEnv(reference_path=str(ref) if ref.exists() else None, **(env_kwargs or {}))
    model = PPO.load(str(zip_path))
    res = rollout(model, env, episodes, seed, deterministic)
    if verbose:
        for i, (d, c) in enumerate(zip(res["distances"], res["contacts"]), 1):
            print(f"Episode {i}: distance={d:.2f}m, contacted={c}")
    m = compute_metrics(res["distances"], res["contacts"], res["paths"])
    d = np.asarray(res["distances"], float)
    tc = np.asarray(res["true_contacts"], bool)
    car = np.asarray(res["carries"], float)
    bs = np.asarray(res["ball_speeds"], float)
    m.update({
        "true_contact_rate": float(tc.mean()),
        "median_distance": float(np.median(d)),
        "min_distance": float(d.min()),
        "mean_max_ball_x": float(np.mean(res["max_xs"])),
        "carry_landed_rate": float((car > 0).mean()),
        "mean_carry_landed": float(car[car > 0].mean()) if (car > 0).any() else float("nan"),
        "mean_peak_ball_speed": float(np.nanmean(bs)),
        "max_peak_ball_speed": float(np.nanmax(bs)),
        "mean_impact_club_speed_contact": float(np.nanmean(np.asarray(res["club_speeds"])[tc])) if tc.any() else float("nan"),
        "per_episode": {"distance": res["distances"], "legacy_contact": res["contacts"],
                        "true_contact": res["true_contacts"], "carry": res["carries"],
                        "peak_ball_speed": res["ball_speeds"]},
    })
    try:
        from eval.style_match import style_match_score
        m["style_match_dtw"] = style_match_score(res["joint_trajs"], style)
    except Exception as e:  # reference missing etc.
        m["style_match_dtw"] = None
        m["style_match_error"] = str(e)
    m["style"] = style
    m["model"] = str(zip_path)
    m["deterministic"] = deterministic
    m["env_kwargs"] = env_kwargs or {}
    return m


def format_summary(m: Dict[str, float]) -> str:
    return (
        f"Episodes: {m['episodes']}\n"
        f"Contact rate: {m['contact_rate']*100:.0f}%\n"
        f"Distance: {m['mean_distance']:.2f}m ± {m['std_distance']:.2f} (max {m['max_distance']:.2f}m)\n"
        f"Distance CV: {m['cv_distance']:.3f}\n"
        f"Club path dispersion: {m['path_dispersion']:.4f}m\n"
        f"True (geom) contact rate: {m['true_contact_rate']*100:.0f}%  | legacy flag: {m['contact_rate']*100:.0f}%\n"
        f"Median distance: {m['median_distance']:.2f}m; carry (landed episodes only): {m['carry_landed_rate']*100:.0f}% landed, mean {m['mean_carry_landed']:.2f}m\n"
        f"Peak ball speed: mean {m['mean_peak_ball_speed']:.2f} m/s, max {m['max_peak_ball_speed']:.2f}\n"
        f"DTW style match (joint rad, lower=closer): {m.get('style_match_dtw')}"
    )


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True, help="Path to saved model (with or without .zip)")
    p.add_argument("--episodes", type=int, default=5)
    p.add_argument("--style", default="scott")
    p.add_argument("--seed", type=int, default=0, help="Base seed (episode i uses seed+i)")
    p.add_argument("--stochastic", action="store_true", help="Sample actions instead of deterministic")
    p.add_argument("--json", default=None, help="Optional path to write metrics JSON")
    p.add_argument("--curriculum", action="store_true")
    p.add_argument("--pin_torso", action="store_true")
    p.add_argument("--address_pose", default="legacy", choices=["legacy", "fixed"])
    p.add_argument("--torque_scale", type=float, default=10.0)
    p.add_argument("--tag", default="", help="suffix for results filename")
    args = p.parse_args(argv)
    env_kwargs = dict(curriculum=args.curriculum, pin_torso=args.pin_torso,
                      address_pose=args.address_pose, torque_scale=args.torque_scale)
    if args.episodes < 1:
        p.error("--episodes must be >= 1")

    try:
        m = evaluate_model(args.model, args.style, args.episodes, args.seed,
                           not args.stochastic, verbose=False, env_kwargs=env_kwargs)
    except FileNotFoundError as e:
        raise SystemExit(f"error: {e}")
    print("\n=== Summary ===")
    print(format_summary(m))
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(m, indent=2))
    # always also write to results/eval_<style>_<mode>.json in project root
    out = Path(__file__).resolve().parent.parent / "results" / f"eval_{args.style}{args.tag}_{'stochastic' if args.stochastic else 'det'}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()

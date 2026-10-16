"""Dispersion report: python -m eval.dispersion_report [--episodes 50] [--seed 2000]"""
import argparse, json
from pathlib import Path
from stable_baselines3 import PPO
from env.humanoid_golf_env import HumanoidGolfEnv
from eval.flight_tracker import FlightTracker, dispersion, LATERAL_THRESHOLD_M

ROOT = Path(__file__).resolve().parent.parent
CURR = dict(curriculum=True, pin_torso=True, address_pose="fixed", torque_scale=3.0)
LEGACY = dict(curriculum=False, pin_torso=False, address_pose="legacy", torque_scale=10.0)
# per-model training configs (from the training commands / results/train_scott.json)
CURR60 = dict(CURR, randomize_reset=True, forward_reward=True)  # 60k-step runs (results/train_scott*.json)
MODELS = {"ppo_scott": CURR60, "ppo_scott_final2": CURR60, "ppo_scott_prev_backup": CURR}
REFS = ["scott", "rory", "scheffler", "average"]
# Mason video refs in docs/REFERENCE_PATHS.md rank order (best first); low-quality part3 files excluded per that doc
MASON_REFS = ["mason_swing_part1_s05_refined", "mason_swing_part2_s01_refined", "mason_swing_part1_s02_refined",
              "mason_swing_part1_s06_refined", "mason_swing_part1_s03_refined", "mason_swing_part1_s04_refined",
              "mason_swing_part2_s05_refined", "mason_swing_part2_s02_refined"]
MASON_QUALITY = {"mason_swing_part1_s05_refined": 0.86, "mason_swing_part2_s01_refined": 0.80, "mason_swing_part1_s02_refined": 0.79,
                 "mason_swing_part1_s06_refined": 0.78, "mason_swing_part1_s03_refined": 0.78, "mason_swing_part1_s04_refined": 0.78,
                 "mason_swing_part2_s05_refined": 0.77, "mason_swing_part2_s02_refined": 0.75}  # quality_score per docs/REFERENCE_PATHS.md


def run(name, kw, episodes, seed, det):
    import numpy as np
    from eval.style_match import style_match_stats
    ref = ROOT / "data/references/scott_swing.npz"
    env = HumanoidGolfEnv(reference_path=str(ref), **kw)
    model = PPO.load(str(ROOT / "models" / name))
    ft, shots, jt = FlightTracker(env).install(), [], []
    for ep in range(episodes):
        obs, _ = env.reset(seed=seed + ep); ft.reset(); done = False; info = {}; tr_ = [env.data.qpos[14:25].copy()]
        while not done:
            a, _ = model.predict(obs, deterministic=det)
            obs, _, te, tr, info = env.step(a); ft.step(); tr_.append(env.data.qpos[14:25].copy()); done = te or tr
        shots.append(ft.summary(info)); jt.append(np.array(tr_))
    ft.close()
    d = dispersion(shots)
    d['dtw_to_reference_style_rad'] = {r: style_match_stats(jt, r) for r in REFS}
    from eval.style_match import UPPER_COLS
    d['dtw_mason'] = {r: {"all11": style_match_stats(jt, r), "upper5": style_match_stats(jt, r, UPPER_COLS)} for r in MASON_REFS}
    return d, shots


def main():
    p = argparse.ArgumentParser(); p.add_argument("--episodes", type=int, default=50)
    p.add_argument("--seed", type=int, default=3000); p.add_argument("--tag", default=""); a = p.parse_args()
    out = {"threshold_m": LATERAL_THRESHOLD_M, "episodes": a.episodes, "seed_base": a.seed, "runs": []}
    for name, kw in MODELS.items():
        if not (ROOT / "models" / f"{name}.zip").exists():
            continue
        for det in (True, False):
            d, shots = run(name, kw, a.episodes, a.seed, det)
            out["runs"].append({"model": name, "mode": "deterministic" if det else "stochastic",
                                "env_kwargs": kw, "metrics": d, "shots": shots})
    rd = ROOT / "results"; rd.mkdir(exist_ok=True)
    (rd / f"dispersion_report{a.tag}.json").write_text(json.dumps(out, indent=2))
    L = ["# Dispersion report", "",
         f"{a.episodes} episodes/run, seeds {a.seed}..{a.seed+a.episodes-1}. Tracker: `eval/flight_tracker.py` (minimal equivalent; no original found).",
         f"DTW columns: mean DTW distance (rad, lower=closer) of the Scott-trained policy trajectory to each reference swing; the non-Scott columns are PURE reference-style distances, not evidence the policy imitates that style.", "Frame: x forward, +y = LEFT of target line, -y = RIGHT. Miss = final |y| > {LATERAL_THRESHOLD_M} m. Distance = final ball x (total, not carry). Contact = club-head/ball geom contact.", "",
         "| Model | Mode | Contact | Mean dist (m) | Dist std | Median | Max | Mean y | Lateral std (m) | Left miss | Right miss | In corridor | Carry landed | Peak ball spd mean (m/s) | DTW Scott ref | DTW Rory | DTW Scheffler | DTW Average |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["runs"]:
        m = r["metrics"]
        L.append(f"| {r['model']} | {r['mode']} | {m['contact_rate']*100:.0f}% | {m['mean_distance']:.2f} | {m['std_distance']:.2f} | {m['median_distance']:.2f} | {m['max_distance']:.2f} | {m['mean_y']:+.3f} | {m['lateral_std']:.3f} | {m['left_miss_rate']*100:.0f}% | {m['right_miss_rate']*100:.0f}% | {m['in_corridor_rate']*100:.0f}% | {m['landed_fraction']*100:.0f}% | {m['mean_peak_ball_speed']:.2f} | " + " | ".join(f"{m['dtw_to_reference_style_rad'][k]['mean']:.3f}" for k in REFS) + " |")
    (rd / f"dispersion_report{a.tag}.md").write_text("\n".join(L) + "\n"); print("\n".join(L))

if __name__ == "__main__":
    main()

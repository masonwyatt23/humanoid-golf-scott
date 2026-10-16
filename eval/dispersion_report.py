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
MASON_REFS_ORIG = ["mason_swing_part1_s05_refined", "mason_swing_part2_s01_refined", "mason_swing_part1_s02_refined",
              "mason_swing_part1_s06_refined", "mason_swing_part1_s03_refined", "mason_swing_part1_s04_refined",
              "mason_swing_part2_s05_refined", "mason_swing_part2_s02_refined"]
MASON_QUALITY_ORIG = {"mason_swing_part1_s05_refined": 0.86, "mason_swing_part2_s01_refined": 0.80, "mason_swing_part1_s02_refined": 0.79,
                 "mason_swing_part1_s06_refined": 0.78, "mason_swing_part1_s03_refined": 0.78, "mason_swing_part1_s04_refined": 0.78,
                 "mason_swing_part2_s05_refined": 0.77, "mason_swing_part2_s02_refined": 0.75}  # quality_score per docs/REFERENCE_PATHS.md


def run(name, kw, episodes, seed, det, scripted=False):
    """name = models/<name>.zip (ignored if scripted=True: zero-residual action on the residual env)."""
    import numpy as np
    from eval.style_match import style_match_stats
    from eval.env_factory import make_env, joint_qpos_idx
    env = make_env(kw)
    zero = np.zeros(env.action_space.shape, dtype=np.float32)
    model = None if scripted else PPO.load(str(ROOT / "models" / name))
    qi = joint_qpos_idx(env)
    ft, shots, jt = FlightTracker(env).install(), [], []
    try:
        for ep in range(episodes):
            obs, _ = env.reset(seed=seed + ep); ft.reset(); done = False; info = {}; tr_ = [env.data.qpos[qi].copy()]
            while not done:
                a = zero if scripted else model.predict(obs, deterministic=det)[0]
                obs, _, te, tr, info = env.step(a); ft.step(); tr_.append(env.data.qpos[qi].copy()); done = te or tr
            sh = ft.summary(info); sh["max_ball_x"] = float(info.get("max_ball_x", sh["final_x"]))
            shots.append(sh); jt.append(np.array(tr_))
    finally:
        ft.close()
    d = dispersion(shots)
    d["mean_max_ball_x"] = float(np.mean([s["max_ball_x"] for s in shots]))
    d['dtw_to_reference_style_rad'] = {r: style_match_stats(jt, r) for r in REFS}
    from eval.style_match import UPPER_COLS
    d['dtw_mason_v2'] = {r: {"all11": style_match_stats(jt, r), "upper5": style_match_stats(jt, r, UPPER_COLS)} for r in MASON_V2_REFS}
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


# Mirrored Mason references (docs/REFERENCE_PATHS.md: filter on mirrored=True): the same 8 swings, mirrored files only.
def _mirrored(names):
    import numpy as np
    out = []
    for n in names:
        f = ROOT / "data/references" / f"{n}_mirrored.npz"
        if f.exists() and bool(np.load(f, allow_pickle=True)["mirrored"]):
            out.append(n + "_mirrored")
    return out

MASON_REFS = _mirrored(MASON_REFS_ORIG)
MASON_QUALITY = {n + "_mirrored": q for n, q in MASON_QUALITY_ORIG.items()}


# Native Mason v2 refs (docs/REFERENCE_PATHS.md "v2 additions"): filter on fields, never glob.
def _v2_refs():
    import numpy as np
    order = "p1_s06 p1_s11 p2_s02 p2_s01 p1_s04 p1_s03 p2_s13 p2_s10 p1_s05 p2_s11 p3_s09_unmirrored".split()   # doc's recommended list order
    ok, info = [], {}
    for w in order:
        n = f"mason_v2_{w}"; f = ROOT / "data/references" / f"{n}.npz"
        if not f.exists(): continue
        d = np.load(f, allow_pickle=True)
        # recommended, not partial, license self_owned + commercial_ok; `mirrored` is recorded (p3_s09_unmirrored is the documented
        # exception: it is the caption-flipped clip mirrored back, so mirrored=True is expected there)
        if bool(d["recommended"]) and not bool(d["partial"]) and str(d["license_class"]) == "self_owned" and bool(d["commercial_ok"]):
            ok.append(n)
            info[n] = dict(quality=round(float(d["quality_score"]), 2), view=str(d["view"]), mirrored=bool(d["mirrored"]),
                           handedness=str(d["handedness"]), tempo_ratio=round(float(d["tempo_ratio"]), 1))
    return ok, info

MASON_V2_REFS, MASON_V2_INFO = _v2_refs()

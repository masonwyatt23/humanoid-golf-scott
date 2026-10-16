"""PPO on top of the scripted-swing residual env (v3 model). Writes models/<name>.zip and results/<name>.json"""
import argparse, json, time
from pathlib import Path
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from env.residual_golf_env import ResidualGolfEnv
from train.train_ppo import ProgressCallback

ROOT = Path(__file__).resolve().parent.parent


def run_eval(policy_fn, make_env, n=100, seed0=5000):
    env = make_env(); rows = []
    for ep in range(n):
        obs, _ = env.reset(seed=seed0 + ep); env.set_progress(1.0); done = False
        while not done:
            obs, _, done, trunc, info = env.step(policy_fn(obs)); done = done or trunc
        rows.append(info)
    g = lambda k: np.array([r[k] for r in rows], float)
    c = g("true_contact"); cr = g("carry"); mx = g("max_ball_x"); lat = g("ball_lateral")
    ik = g("impact_club_speed"); bs = g("peak_ball_speed")
    ok = c > 0
    return {"n_episodes": n, "true_contact_rate": float(c.mean()), "landed_fraction": float((cr > 0).mean()),
            "mean_total_distance_x": float(mx.mean()), "max_total_distance_x": float(mx.max()),
            "mean_carry": float(cr.mean()), "max_carry": float(cr.max()),
            "mean_carry_given_landed": float(cr[cr > 0].mean()) if (cr > 0).any() else 0.0,
            "lateral_mean": float(lat.mean()), "lateral_std": float(lat.std()),
            "mean_impact_club_speed": float(ik[ok].mean()) if ok.any() else 0.0, "max_impact_club_speed": float(ik.max()),
            "mean_ball_speed": float(bs.mean()), "max_ball_speed": float(bs.max()),
            "median_smash": float(np.median(bs[ok & (ik > 5)] / ik[ok & (ik > 5)])) if (ok & (ik > 5)).any() else 0.0,
            "mean_launch_elev_deg": float(np.degrees(g("launch_elevation")[ok]).mean()) if ok.any() else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timesteps", type=int, default=60000)
    ap.add_argument("--n_envs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="ppo_resid")
    ap.add_argument("--model_xml", default="humanoid_golf_v3.xml")
    ap.add_argument("--flight_model", action="store_true")
    ap.add_argument("--gate_lo", type=float, default=15.0)
    ap.add_argument("--gate_hi", type=float, default=35.0)
    ap.add_argument("--loft", type=float, default=6.0)
    ap.add_argument("--q_back", type=float, default=2.2)
    ap.add_argument("--t_down", type=float, default=0.12)
    ap.add_argument("--res_scale", type=float, nargs=4, default=[0.2, 0.2, 0.2, 0.1])
    ap.add_argument("--yaw", action="store_true", help="scripted chest yaw backswing/finish (+/-0.35 rad)")
    ap.add_argument("--force_scale", type=float, default=2.0)
    ap.add_argument("--eval_episodes", type=int, default=100)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--log_std_init", type=float, default=-1.5)
    ap.add_argument("--ent", type=float, default=0.0)
    a = ap.parse_args()
    script = dict(q_back=a.q_back, t_down=a.t_down, t_back=0.6)
    if a.yaw: script.update(yaw_back=-0.35, yaw_fin=0.35)
    kw = dict(script=script, residual_scale=tuple(a.res_scale), model_xml=a.model_xml, flight_model=a.flight_model, tee_height=0.04,
              force_scale=a.force_scale, kp=700.0, kd=700.0 / 30, loft_deg=a.loft, curriculum=True, carry_reward=True, forward_reward=True,
              randomize_reset=True, gate_lo=a.gate_lo, gate_hi=a.gate_hi)
    make_env = lambda: ResidualGolfEnv(**kw)
    out = {"args": vars(a)}
    out["scripted_only"] = run_eval(lambda o: np.zeros(5), make_env, a.eval_episodes)
    print("SCRIPTED", json.dumps(out["scripted_only"]), flush=True)
    env = make_vec_env(make_env, n_envs=a.n_envs, seed=a.seed, vec_env_cls=SubprocVecEnv)
    model = PPO("MlpPolicy", env, verbose=0, learning_rate=a.lr, n_steps=512, batch_size=256, n_epochs=10, gamma=0.99,
                ent_coef=a.ent, seed=a.seed, policy_kwargs=dict(log_std_init=a.log_std_init))
    t0 = time.time()
    model.learn(total_timesteps=a.timesteps, callback=ProgressCallback(a.timesteps, log_every=10000))
    out["train_seconds"] = time.time() - t0
    (ROOT / "models").mkdir(exist_ok=True); (ROOT / "results").mkdir(exist_ok=True)
    model.save(ROOT / "models" / a.name)
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_env, a.eval_episodes)
    print("POLICY", json.dumps(out["policy"]), flush=True)
    json.dump(out, open(ROOT / "results" / f"{a.name}.json", "w"), indent=2)


if __name__ == "__main__":
    main()

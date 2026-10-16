"""PPO on top of the scripted-swing residual env (v3 model). Writes models/<name>.zip and results/<name>.json"""
import argparse, json, time
from pathlib import Path
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from env.residual_golf_env import ResidualGolfEnv
from train.train_ppo import ProgressCallback
from stable_baselines3.common.callbacks import BaseCallback


class LadderCallback(BaseCallback):
    """Club-speed ladder (m/s): rung 10,15,...,54. Advance after >=50 episodes at the rung with clean contact >=85% and mean impact >=85% of rung."""
    RUNGS = [10, 15, 20, 25, 30, 35, 40, 45, 50, 54]

    def __init__(self, log):
        super().__init__(); self.i = 0; self.buf = []; self.log = log; self.history = []
        self.log.append(("start", 0, self.RUNGS[0]))

    def _on_training_start(self):
        self.training_env.env_method("set_rung", self.RUNGS[0])

    def _on_step(self):
        for d, inf in zip(self.locals["dones"], self.locals["infos"]):
            if d:
                self.buf.append((bool(inf.get("true_contact", False)), float(inf.get("impact_club_speed", 0.0))))
        if len(self.buf) >= 50 and self.i < len(self.RUNGS) - 1:
            r = self.RUNGS[self.i]; b = self.buf[-50:]
            if np.mean([x[0] for x in b]) >= 0.85 and np.mean([x[1] for x in b]) >= 0.85 * r:
                self.i += 1; self.buf = []
                self.training_env.env_method("set_rung", self.RUNGS[self.i])
                self.history.append((self.num_timesteps, self.RUNGS[self.i]))
                print(f"[ladder] steps={self.num_timesteps} -> rung {self.RUNGS[self.i]} m/s", flush=True)
        return True


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
    ik = g("impact_club_speed"); bs = g("peak_ball_speed"); pk = g("peak_club_speed")
    seq = [r for r in rows if "arm_lead_ms" in r]
    ok = c > 0
    return {"n_episodes": n, "true_contact_rate": float(c.mean()), "landed_fraction": float((cr > 0).mean()),
            "mean_total_distance_x": float(mx.mean()), "max_total_distance_x": float(mx.max()),
            "mean_carry": float(cr.mean()), "max_carry": float(cr.max()),
            "mean_carry_given_landed": float(cr[cr > 0].mean()) if (cr > 0).any() else 0.0,
            "lateral_mean": float(lat.mean()), "lateral_std": float(lat.std()),
            "mean_impact_club_speed": float(ik[ok].mean()) if ok.any() else 0.0, "max_impact_club_speed": float(ik.max()),
            "mean_ball_speed": float(bs.mean()), "max_ball_speed": float(bs.max()),
            "median_smash": float(np.median(bs[ok & (ik > 5)] / ik[ok & (ik > 5)])) if (ok & (ik > 5)).any() else 0.0,
            "peak_club_speed_mean_ms": float(pk.mean()), "peak_club_speed_max_ms": float(pk.max()),
            "peak_club_speed_mean_mph": float(pk.mean() * 2.23694), "peak_club_speed_max_mph": float(pk.max() * 2.23694),
            "impact_club_speed_mean_mph": float(ik[ok].mean() * 2.23694) if ok.any() else 0.0,
            "seq_thorax_before_arm_frac": float(np.mean([r["seq_order_thorax_before_arm"] for r in seq])) if seq else None,
            "seq_arm_before_club_frac": float(np.mean([r["seq_order_arm_before_club"] for r in seq])) if seq else None,
            "seq_arm_lead_ms_mean": float(np.mean([r["arm_lead_ms"] for r in seq])) if seq else None,
            "mean_style_score": float(np.mean([r["style_score"] for r in rows if "style_score" in r])) if any("style_score" in r for r in rows) else None,
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
    ap.add_argument("--ladder", action="store_true", help="club-speed ladder 10..54 m/s in 5 m/s rungs, advance when clean-contact >=85% and mean impact >=85% of rung")
    ap.add_argument("--seq_weight", type=float, default=0.0)
    ap.add_argument("--style_prior", action="store_true")
    ap.add_argument("--ball_dz", type=float, default=0.008)
    ap.add_argument("--handedness", default="right")
    ap.add_argument("--analytic_ball", action="store_true")
    ap.add_argument("--elev_target", type=float, default=12.5)
    ap.add_argument("--style_ref", default=None)
    ap.add_argument("--style_weight", type=float, default=0.0)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--log_std_init", type=float, default=-1.5)
    ap.add_argument("--ent", type=float, default=0.0)
    a = ap.parse_args()
    script = dict(q_back=a.q_back, t_down=a.t_down, t_back=0.6)
    if a.yaw: script.update(yaw_back=-0.35, yaw_fin=0.35)
    kw = dict(script=script, residual_scale=tuple(a.res_scale), model_xml=a.model_xml, flight_model=a.flight_model, tee_height=0.04,
              force_scale=a.force_scale, kp=700.0, kd=700.0 / 30, loft_deg=a.loft, curriculum=True, carry_reward=True, forward_reward=True,
              randomize_reset=True, ball_dz=a.ball_dz, handedness=a.handedness, gate_lo=a.gate_lo, gate_hi=a.gate_hi, seq_weight=a.seq_weight,
              analytic_ball=a.analytic_ball, elev_target_deg=a.elev_target, style_ref=a.style_ref, style_weight=a.style_weight,
              style_prior=a.style_prior, yaw_amp=0.1, wrist_amp=0.0, style_lead=0.05)
    make_env = lambda: ResidualGolfEnv(**kw)
    import subprocess
    out = {"args": vars(a), "git_head": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=str(ROOT)).stdout.strip()}
    out["scripted_only"] = run_eval(lambda o: np.zeros(5), make_env, a.eval_episodes)
    print("SCRIPTED", json.dumps(out["scripted_only"]), flush=True)
    env = make_vec_env(make_env, n_envs=a.n_envs, seed=a.seed, vec_env_cls=SubprocVecEnv)
    model = PPO("MlpPolicy", env, verbose=0, learning_rate=a.lr, n_steps=512, batch_size=256, n_epochs=10, gamma=0.99,
                ent_coef=a.ent, seed=a.seed, policy_kwargs=dict(log_std_init=a.log_std_init))
    t0 = time.time()
    cbs = [ProgressCallback(a.timesteps, log_every=10000)]
    lad = None
    if a.ladder:
        lad = LadderCallback([]); cbs.append(lad)
    model.learn(total_timesteps=a.timesteps, callback=cbs)
    if lad: out["ladder_history"] = lad.history; out["final_rung"] = lad.RUNGS[lad.i]
    out["train_seconds"] = time.time() - t0
    (ROOT / "models").mkdir(exist_ok=True); (ROOT / "results").mkdir(exist_ok=True)
    model.save(ROOT / "models" / a.name)
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_env, a.eval_episodes)
    print("POLICY", json.dumps(out["policy"]), flush=True)
    json.dump(out, open(ROOT / "results" / f"{a.name}.json", "w"), indent=2)


if __name__ == "__main__":
    main()

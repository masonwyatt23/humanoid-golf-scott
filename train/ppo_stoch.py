"""Stage 23 'truly learned' attempt: DART-then-PPO fine-tune with lateral+launch penalty scored on the STOCHASTIC policy, gentle exploration.
Start = DART-distilled BC policy (e.g. imit15_dart_s53, BOOSTED force_scale 2). Gentle exploration: low log_std, small lr, small clip.
Extra episode-end penalty (reward wrapper): -w_lat*|ball y| - w_launch*max(0,|launch_deg-12|-3). BC anchor optional (--lam, default 0.05, weak).
Checkpoint selection: every --sel_every rollouts evaluate the STOCHASTIC policy (sel_eps eps, fixed seeds); score = carry - 10*lat_std - 2*|launch-12|
 with contact>=99% required; init policy is a candidate, so the saved model never scores below start on that selection set.
Reports action departure from script (rms rad vs script target, before/after) -- measured, not claimed.
usage: python -m train.ppo_stoch --init imit15_dart_s53 --name ppo15_stoch_s71 [--steps 150000]"""
import argparse, json, time, hashlib, copy
from pathlib import Path
import numpy as np, torch, gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
from train.ppo_bcreg import Lab, BCReg, action_diff
ROOT = Path(__file__).resolve().parent.parent


class Pen(gym.Wrapper):
    def __init__(self, env, wl, wa):
        super().__init__(env); self.wl, self.wa = wl, wa
    def step(self, a):
        o, r, d, t, i = self.env.step(a)
        if d or t:
            u = self.env.unwrapped; el = np.degrees(u.launch_elevation)
            r = r - self.wl * abs(float(u.ball_lateral)) - self.wa * max(0.0, abs(el - 12.0) - 3.0)
        return o, r, d, t, i


def score(m):
    if m["true_contact_rate"] < 0.99: return -1e9
    return m["mean_carry"] - 10.0 * m["lateral_std"] - 2.0 * abs(m.get("mean_launch_elev_deg", 12.0) - 12.0)


class Sel(BaseCallback):
    def __init__(self, make_eval, every, eps, seed0):
        super().__init__(); self.me, self.every, self.eps, self.s0 = make_eval, every, eps, seed0; self.n = 0; self.best = None; self.hist = []
    def _on_step(self): return True
    def consider(self, tag):
        m = run_eval(lambda o: self.model.predict(o, deterministic=False)[0], self.me, self.eps, self.s0); s = score(m)
        self.hist.append(dict(tag=tag, score=s, carry=m["mean_carry"], lat=m["lateral_std"], contact=m["true_contact_rate"]))
        print("SEL", self.hist[-1], flush=True)
        if self.best is None or s > self.best[0]: self.best = (s, copy.deepcopy(self.model.policy.state_dict()), tag)
    def _on_rollout_end(self):
        self.n += 1
        if self.n % self.every == 0: self.consider(self.n)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--init", required=True); ap.add_argument("--name", required=True); ap.add_argument("--steps", type=int, default=150000)
    ap.add_argument("--lr", type=float, default=2e-6); ap.add_argument("--log_std", type=float, default=-4.0); ap.add_argument("--lam", type=float, default=0.05)
    ap.add_argument("--w_lat", type=float, default=0.5); ap.add_argument("--w_launch", type=float, default=0.3); ap.add_argument("--bc_k", type=int, default=3)
    ap.add_argument("--sel_every", type=int, default=6); ap.add_argument("--sel_eps", type=int, default=30); ap.add_argument("--seed", type=int, default=71); ap.add_argument("--eval_episodes", type=int, default=100)
    a = ap.parse_args(); torch.set_num_threads(1)
    src = json.load(open(ROOT / "results" / f"{a.init}.json")); kw = src["env_kwargs_full"]; buf = []
    make_eval = lambda: ResidualGolfEnv(**kw)
    venv = DummyVecEnv([lambda: Lab(Pen(ResidualGolfEnv(**kw), a.w_lat, a.w_launch), buf, kw["learn_scale"])])
    model = PPO.load(str(ROOT / "models" / a.init), env=venv, learning_rate=a.lr, seed=a.seed, n_steps=512, batch_size=128, n_epochs=3, clip_range=0.05, ent_coef=0.0)
    with torch.no_grad(): model.policy.log_std.fill_(a.log_std)
    out = dict(args=vars(a), init=a.init, tier="force_scale %s BOOSTED; DART-distilled start; PPO fine-tune" % kw.get("force_scale"))
    out["diff_before"] = action_diff(model, kw)
    bc = BCReg(buf, a.lam, np.asarray(kw["learn_scale"], float), a.bc_k); sel = Sel(make_eval, a.sel_every, a.sel_eps, 5000); sel.model = model; sel.consider("init")
    t0 = time.time(); model.learn(total_timesteps=a.steps, callback=[bc, sel]); sel.consider("final"); out["train_seconds"] = time.time() - t0
    out["selection_history"] = sel.hist; out["selected"] = sel.best[2]; model.policy.load_state_dict(sel.best[1])
    model.save(ROOT / "models" / a.name); out["checkpoint_sha256"] = hashlib.sha256((ROOT / "models" / f"{a.name}.zip").read_bytes()).hexdigest()
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_eval, a.eval_episodes)
    out["policy_stochastic"] = run_eval(lambda o: model.predict(o, deterministic=False)[0], make_eval, a.eval_episodes)
    out["diff_after"] = action_diff(model, kw); out["env_kwargs_full"] = kw
    json.dump(out, open(ROOT / "results" / f"{a.name}.json", "w"), indent=2, default=float)
    print("AFTER sel", out["selected"], {k: out["policy"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, "stoch", {k: out["policy_stochastic"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, "diff", out["diff_before"]["rms_rad_all"], "->", out["diff_after"]["rms_rad_all"], flush=True)


if __name__ == "__main__": main()

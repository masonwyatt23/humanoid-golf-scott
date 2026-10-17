"""Stage 26 LEARNED-policy attempt #5 (BOOSTED fs2 v3 body, start = frozen DART base imit15_dart_s53, script-distilled): residual PPO with
 - tiny lr + target_kl trust-region cap (SB3 early-stops the epoch loop when approx KL > target_kl) and clip 0.05,
 - log_std fixed near -8 (sigma ~3e-4 action units * learn_scale ~ 1e-3 rad, i.e. within the ~1 mm strike window) throughout,
 - exploration ONLY in the downswing: outside the downswing (clock < t_hold+t_back+t_pause) the env gets the policy MEAN (the sampled noise is discarded),
 - reward = env reward - w_lat*|ball y| (lateral reduction) - w_launch*launch penalty at episode end,
 - HARD selection: every --sel_every rollouts evaluate (100 eps, stochastic at current log_std AND deterministic) and require contact>=0.99 on both, score = carry - 10*lat_std(stoch+det mean);
   init is a candidate so the saved model never scores below start on that set.
Action departure from the script (rms rad vs script target) before/after is reported.
usage: python -m train.ppo_resid_kl --init imit15_dart_s53 --name ppo15_klres_s101"""
import argparse, json, time, hashlib, copy
from pathlib import Path
import numpy as np, torch, gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
from train.ppo_bcreg import Lab, BCReg, action_diff
from train.ppo_stoch import Pen
ROOT = Path(__file__).resolve().parent.parent


class DownswingOnly(gym.Wrapper):
    """env sees mean action outside the downswing; inside, the sampled action (= mean + policy noise)."""
    def __init__(self, env, holder): super().__init__(env); self.h = holder; self._o = None
    def reset(self, **k): self._o, i = self.env.reset(**k); return self._o, i
    def step(self, a):
        u = self.env.unwrapped; s = u.script; t_top = s["t_hold"] + s["t_back"] + s["t_pause"] - 0.02
        if u.clock < t_top and self.h.get("model") is not None:
            a = self.h["model"].predict(self._o, deterministic=True)[0]
        o, r, d, t, i = self.env.step(a); self._o = o; return o, r, d, t, i


def score(det, sto):
    if det["true_contact_rate"] < 0.99 or sto["true_contact_rate"] < 0.99: return -1e9
    return 0.5 * (det["mean_carry"] + sto["mean_carry"]) - 10.0 * 0.5 * (det["lateral_std"] + sto["lateral_std"])


class Sel(BaseCallback):
    def __init__(self, make_eval, every, eps, seed0):
        super().__init__(); self.me, self.every, self.eps, self.s0 = make_eval, every, eps, seed0; self.n = 0; self.best = None; self.hist = []
    def _on_step(self): return True
    def consider(self, tag):
        d = run_eval(lambda o: self.model.predict(o, deterministic=True)[0], self.me, self.eps, self.s0)
        s = run_eval(lambda o: self.model.predict(o, deterministic=False)[0], self.me, self.eps, self.s0); sc = score(d, s)
        self.hist.append(dict(tag=tag, score=sc, det_carry=d["mean_carry"], det_lat=d["lateral_std"], det_contact=d["true_contact_rate"], stoch_carry=s["mean_carry"], stoch_lat=s["lateral_std"], stoch_contact=s["true_contact_rate"]))
        print("SEL", self.hist[-1], flush=True)
        if self.best is None or sc > self.best[0]: self.best = (sc, copy.deepcopy(self.model.policy.state_dict()), tag)
    def _on_rollout_end(self):
        self.n += 1
        if self.n % self.every == 0: self.consider(self.n)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--init", required=True); ap.add_argument("--name", required=True); ap.add_argument("--steps", type=int, default=150000)
    ap.add_argument("--lr", type=float, default=1e-5); ap.add_argument("--log_std", type=float, default=-8.0); ap.add_argument("--target_kl", type=float, default=0.002); ap.add_argument("--clip", type=float, default=0.05)
    ap.add_argument("--lam", type=float, default=0.05); ap.add_argument("--w_lat", type=float, default=1.0); ap.add_argument("--w_launch", type=float, default=0.3); ap.add_argument("--bc_k", type=int, default=3)
    ap.add_argument("--sel_every", type=int, default=20); ap.add_argument("--sel_eps", type=int, default=100); ap.add_argument("--seed", type=int, default=101); ap.add_argument("--eval_episodes", type=int, default=100)
    a = ap.parse_args(); torch.set_num_threads(1)
    src = json.load(open(ROOT / "results" / f"{a.init}.json")); kw = src["env_kwargs_full"]; buf = []; holder = {}
    make_eval = lambda: ResidualGolfEnv(**kw)
    venv = DummyVecEnv([lambda: Lab(DownswingOnly(Pen(ResidualGolfEnv(**kw), a.w_lat, a.w_launch), holder), buf, kw["learn_scale"])])
    model = PPO.load(str(ROOT / "models" / a.init), env=venv, learning_rate=a.lr, seed=a.seed, n_steps=512, batch_size=128, n_epochs=3, clip_range=a.clip, ent_coef=0.0, target_kl=a.target_kl)
    holder["model"] = model
    with torch.no_grad(): model.policy.log_std.fill_(a.log_std)
    out = dict(args=vars(a), init=a.init, tier="force_scale %s BOOSTED; frozen-DART start (script-distilled); residual PPO, KL-capped, downswing-only exploration" % kw.get("force_scale"))
    out["diff_before"] = action_diff(model, kw)
    bc = BCReg(buf, a.lam, np.asarray(kw["learn_scale"], float), a.bc_k); sel = Sel(make_eval, a.sel_every, a.sel_eps, 5000); sel.model = model; sel.consider("init")
    t0 = time.time(); model.learn(total_timesteps=a.steps, callback=[bc, sel]); sel.consider("final"); out["train_seconds"] = time.time() - t0
    out["selection_history"] = sel.hist; out["selected"] = sel.best[2]; model.policy.load_state_dict(sel.best[1])
    out["selected_log_std"] = float(model.policy.log_std.mean())
    model.save(ROOT / "models" / a.name); out["checkpoint_sha256"] = hashlib.sha256((ROOT / "models" / f"{a.name}.zip").read_bytes()).hexdigest()
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_eval, a.eval_episodes)
    out["policy_stochastic"] = run_eval(lambda o: model.predict(o, deterministic=False)[0], make_eval, a.eval_episodes)
    out["diff_after"] = action_diff(model, kw); out["env_kwargs_full"] = kw
    json.dump(out, open(ROOT / "results" / f"{a.name}.json", "w"), indent=2, default=float)
    print("AFTER sel", out["selected"], {k: out["policy"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, "stoch", {k: out["policy_stochastic"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, "diff", out["diff_before"]["rms_rad_all"], "->", out["diff_after"]["rms_rad_all"], flush=True)


if __name__ == "__main__": main()

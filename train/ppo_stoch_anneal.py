"""Stage 25 'truly learned' attempt #4: DART-then-PPO from imit15_dart_s53 (BOOSTED fs2 v3 body, script-distilled start) with log_std START in [-5,-4.5] annealed to --log_std_end, stronger lr (3e-5) than s71/s81 so weights actually move,
lateral+launch episode-end penalty on the STOCHASTIC policy, selection every --sel_every rollouts on 100 eps (stochastic, at the CURRENT log_std) with contact>=0.99 floor; init is a candidate.
Saved model carries the log_std of the selected checkpoint (the gate's 'stoch' mode uses it). Action departure from script reported (rms rad, before/after).
usage: python -m train.ppo_stoch_anneal --init imit15_dart_s53 --name ppo15_anneal_s91"""
import argparse, json, time, hashlib, copy
from pathlib import Path
import numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
from train.ppo_bcreg import Lab, BCReg, action_diff
from train.ppo_stoch import Pen, score, Sel
ROOT = Path(__file__).resolve().parent.parent


class Anneal(BaseCallback):
    def __init__(self, a, b, total_rollouts): super().__init__(); self.a, self.b, self.n, self.i = a, b, total_rollouts, 0
    def _on_step(self): return True
    def _on_rollout_end(self):
        self.i += 1; v = self.a + (self.b - self.a) * min(1.0, self.i / self.n)
        with torch.no_grad(): self.model.policy.log_std.fill_(v)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--init", required=True); ap.add_argument("--name", required=True); ap.add_argument("--steps", type=int, default=200000)
    ap.add_argument("--lr", type=float, default=3e-5); ap.add_argument("--log_std", type=float, default=-4.7); ap.add_argument("--log_std_end", type=float, default=-6.0); ap.add_argument("--lam", type=float, default=0.02)
    ap.add_argument("--w_lat", type=float, default=0.5); ap.add_argument("--w_launch", type=float, default=0.3); ap.add_argument("--bc_k", type=int, default=3)
    ap.add_argument("--sel_every", type=int, default=16); ap.add_argument("--sel_eps", type=int, default=100); ap.add_argument("--seed", type=int, default=91); ap.add_argument("--eval_episodes", type=int, default=100)
    a = ap.parse_args(); torch.set_num_threads(1)
    src = json.load(open(ROOT / "results" / f"{a.init}.json")); kw = src["env_kwargs_full"]; buf = []
    make_eval = lambda: ResidualGolfEnv(**kw)
    venv = DummyVecEnv([lambda: Lab(Pen(ResidualGolfEnv(**kw), a.w_lat, a.w_launch), buf, kw["learn_scale"])])
    model = PPO.load(str(ROOT / "models" / a.init), env=venv, learning_rate=a.lr, seed=a.seed, n_steps=512, batch_size=128, n_epochs=3, clip_range=0.1, ent_coef=0.0)
    with torch.no_grad(): model.policy.log_std.fill_(a.log_std)
    out = dict(args=vars(a), init=a.init, tier="force_scale %s BOOSTED; DART-distilled start; PPO fine-tune, annealed log_std" % kw.get("force_scale"))
    out["diff_before"] = action_diff(model, kw)
    bc = BCReg(buf, a.lam, np.asarray(kw["learn_scale"], float), a.bc_k); sel = Sel(make_eval, a.sel_every, a.sel_eps, 5000); sel.model = model; sel.consider("init")
    n_roll = a.steps // 512; t0 = time.time(); model.learn(total_timesteps=a.steps, callback=[Anneal(a.log_std, a.log_std_end, n_roll), bc, sel]); sel.consider("final"); out["train_seconds"] = time.time() - t0
    out["selection_history"] = sel.hist; out["selected"] = sel.best[2]; model.policy.load_state_dict(sel.best[1])
    out["selected_log_std"] = float(model.policy.log_std.mean())
    model.save(ROOT / "models" / a.name); out["checkpoint_sha256"] = hashlib.sha256((ROOT / "models" / f"{a.name}.zip").read_bytes()).hexdigest()
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_eval, a.eval_episodes)
    out["policy_stochastic"] = run_eval(lambda o: model.predict(o, deterministic=False)[0], make_eval, a.eval_episodes)
    out["diff_after"] = action_diff(model, kw); out["env_kwargs_full"] = kw
    json.dump(out, open(ROOT / "results" / f"{a.name}.json", "w"), indent=2, default=float)
    print("AFTER sel", out["selected"], "log_std", out["selected_log_std"], {k: out["policy"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, "stoch", {k: out["policy_stochastic"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, "diff", out["diff_before"]["rms_rad_all"], "->", out["diff_after"]["rms_rad_all"], flush=True)


if __name__ == "__main__": main()

"""PPO fine-tune with a behaviour-cloning regulariser (conservative; keeps contact at 100%).
Reward = env reward (carry/contact/launch via shot_pen + strike-quality terms already in env). After each PPO rollout, K Adam steps on
 lam * radian-weighted MSE(policy mean, script target) over the states just visited (the BC anchor). Reports action diff vs script
 (rad, mean over visited states, before/after) so 'departs from the script' is measured, not claimed. Env kwargs from init model's results JSON.
usage: python -m train.ppo_bcreg --init imit15_dart_s53 --name ppo18_bcreg_s61 [--steps 60000]"""
import argparse, json, time, hashlib
from pathlib import Path
import numpy as np, torch, gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
ROOT = Path(__file__).resolve().parent.parent


class Lab(gym.Wrapper):
    """records (obs, script-target/learn_scale) for every visited state"""
    def __init__(self, env, buf, ls):
        super().__init__(env); self.buf = buf; self.ls = np.asarray(ls, float)
    def _lab(self):
        u = self.env.unwrapped; return np.clip(u.targets(u.clock) / self.ls, -1, 1)
    def reset(self, **k):
        self._o, i = self.env.reset(**k); return self._o, i
    def step(self, a):
        self.buf.append((self._o.copy(), self._lab().astype(np.float32)))
        o, r, d, t, i = self.env.step(a); self._o = o; return o, r, d, t, i


class BCReg(BaseCallback):
    def __init__(self, buf, lam, ls, k):
        super().__init__(); self.buf, self.lam, self.k = buf, lam, k; self.ls = torch.tensor(ls, dtype=torch.float32)
        self.opt = None; self.log = []
    def _on_step(self): return True
    def _on_rollout_end(self):
        if not self.buf: return
        pol = self.model.policy
        if self.opt is None: self.opt = torch.optim.Adam(pol.parameters(), lr=3e-6)
        X = torch.tensor(np.array([b[0] for b in self.buf])); Y = torch.tensor(np.array([b[1] for b in self.buf])); self.buf.clear()
        for _ in range(self.k):
            m = pol.get_distribution(X).distribution.mean[:, :4]
            loss = self.lam * 1e3 * (((m - Y) * self.ls) ** 2).mean(); self.opt.zero_grad(); loss.backward(); self.opt.step()
        self.log.append(float(torch.sqrt((((m - Y) * self.ls) ** 2).mean())))


def action_diff(model, kw, eps=30, seed0=7000):
    env = ResidualGolfEnv(**kw); ls = np.asarray(kw["learn_scale"], float); dif = []
    for i in range(eps):
        o, _ = env.reset(seed=seed0 + i); env.set_progress(1.0); d = False
        while not d:
            a = model.predict(o, deterministic=True)[0]; lab = np.clip(env.targets(env.clock) / ls, -1, 1)
            dif.append(((a[:4] - lab) * ls) ** 2); o, _, d, t, _ = env.step(a); d = d or t
    dif = np.array(dif); return dict(rms_rad_per_joint=np.sqrt(dif.mean(0)).tolist(), rms_rad_all=float(np.sqrt(dif.mean())))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--init", required=True); ap.add_argument("--name", required=True); ap.add_argument("--steps", type=int, default=60000)
    ap.add_argument("--lr", type=float, default=3e-6); ap.add_argument("--log_std", type=float, default=-4.5); ap.add_argument("--lam", type=float, default=0.3)
    ap.add_argument("--lat_weight", type=float, default=None); ap.add_argument("--bc_k", type=int, default=5); ap.add_argument("--seed", type=int, default=61); ap.add_argument("--eval_episodes", type=int, default=100)
    a = ap.parse_args(); torch.set_num_threads(1)
    src = json.load(open(ROOT / "results" / f"{a.init}.json")); kw = src["env_kwargs_full"]; buf = []
    if a.lat_weight is not None: kw["lat_weight"] = a.lat_weight
    make_eval = lambda: ResidualGolfEnv(**kw)
    venv = DummyVecEnv([lambda: Lab(ResidualGolfEnv(**kw), buf, kw['learn_scale'])])
    model = PPO.load(str(ROOT / "models" / a.init), env=venv, learning_rate=a.lr, seed=a.seed, n_steps=512, batch_size=128, n_epochs=3, clip_range=0.1, ent_coef=0.0)
    with torch.no_grad(): model.policy.log_std.fill_(a.log_std)
    out = dict(args=vars(a), init=a.init, env_kwargs_full=kw, tier="force_scale %s BOOSTED" % kw.get("force_scale"))
    out["before"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_eval, 40, 5000); out["diff_before"] = action_diff(model, kw)
    print("BEFORE", {k: out["before"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, out["diff_before"]["rms_rad_all"], flush=True)
    cb = BCReg(buf, a.lam, np.asarray(kw["learn_scale"], float), a.bc_k); t0 = time.time()
    model.learn(total_timesteps=a.steps, callback=cb); out["train_seconds"] = time.time() - t0; out["bc_rms_rad_per_rollout"] = cb.log
    model.save(ROOT / "models" / a.name); out["checkpoint_sha256"] = hashlib.sha256((ROOT / "models" / f"{a.name}.zip").read_bytes()).hexdigest()
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_eval, a.eval_episodes)
    out["policy_stochastic"] = run_eval(lambda o: model.predict(o, deterministic=False)[0], make_eval, a.eval_episodes)
    out["diff_after"] = action_diff(model, kw)
    out["env_kwargs_full"] = kw; json.dump(out, open(ROOT / "results" / f"{a.name}.json", "w"), indent=2, default=float)
    print("AFTER", {k: out["policy"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}, "diff_after", out["diff_after"], flush=True)


if __name__ == "__main__": main()

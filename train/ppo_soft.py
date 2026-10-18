"""Stage 27 LEARNED attempts #7/#8: same KL-capped residual PPO (frozen DART start, downswing-only exploration) as ppo_resid_kl but a SOFTER selection rule:
eligible = contact>=0.99 (det AND stoch) and lateral_std<=cap (det AND stoch, 100 eps); score = mean carry + 0.05*club mph (carry/speed bonus).
A NON-init checkpoint is accepted if eligible and score >= init_score - tol; best eligible non-init wins; otherwise init is kept.
usage: python -m train.ppo_soft --init X --name Y --cap 2.0"""
import sys, copy, time, json, hashlib, argparse
import numpy as np, torch
from pathlib import Path
import train.ppo_resid_kl as K
from train.train_residual import run_eval
from train.ppo_bcreg import Lab, BCReg, action_diff
from train.ppo_stoch import Pen
from env.residual_golf_env import ResidualGolfEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
ROOT = K.ROOT

class SoftSel(K.Sel):
    cap = 2.0; tol = 0.5
    def consider(self, tag):
        d = run_eval(lambda o: self.model.predict(o, deterministic=True)[0], self.me, self.eps, self.s0)
        s = run_eval(lambda o: self.model.predict(o, deterministic=False)[0], self.me, self.eps, self.s0)
        ok = min(d["true_contact_rate"], s["true_contact_rate"]) >= 0.99 and max(d["lateral_std"], s["lateral_std"]) <= self.cap
        sc = 0.5*(d["mean_carry"]+s["mean_carry"]) + 0.05*0.5*(d["impact_club_speed_mean_mph"]+s["impact_club_speed_mean_mph"])
        h = dict(tag=tag, score=sc, eligible=bool(ok), det_carry=d["mean_carry"], det_lat=d["lateral_std"], det_contact=d["true_contact_rate"], stoch_carry=s["mean_carry"], stoch_lat=s["lateral_std"], stoch_contact=s["true_contact_rate"], club_mph=d["impact_club_speed_mean_mph"])
        self.hist.append(h); print("SEL", h, flush=True)
        sd = copy.deepcopy(self.model.policy.state_dict())
        if tag == "init": self.init = (sc, sd, tag); self.best = self.init; self.best_ne = None; return
        if ok and sc >= self.init[0] - self.tol and (self.best_ne is None or sc > self.best_ne[0]): self.best_ne = (sc, sd, tag)
        self.best = self.best_ne if self.best_ne else self.init

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--init", required=True); ap.add_argument("--name", required=True); ap.add_argument("--steps", type=int, default=40000)
    ap.add_argument("--lr", type=float, default=2e-5); ap.add_argument("--log_std", type=float, default=-7.0); ap.add_argument("--target_kl", type=float, default=0.004); ap.add_argument("--clip", type=float, default=0.08)
    ap.add_argument("--lam", type=float, default=0.05); ap.add_argument("--w_lat", type=float, default=2.0); ap.add_argument("--w_launch", type=float, default=0.3); ap.add_argument("--bc_k", type=int, default=3)
    ap.add_argument("--sel_every", type=int, default=8); ap.add_argument("--sel_eps", type=int, default=100); ap.add_argument("--seed", type=int, default=121); ap.add_argument("--eval_episodes", type=int, default=100)
    ap.add_argument("--cap", type=float, default=2.0); ap.add_argument("--tol", type=float, default=0.5)
    a = ap.parse_args(); torch.set_num_threads(1)
    src = json.load(open(ROOT/"results"/f"{a.init}.json")); kw = src["env_kwargs_full"]; buf = []; holder = {}
    make_eval = lambda: ResidualGolfEnv(**kw)
    venv = DummyVecEnv([lambda: Lab(K.DownswingOnly(Pen(ResidualGolfEnv(**kw), a.w_lat, a.w_launch), holder), buf, kw["learn_scale"])])
    model = PPO.load(str(ROOT/"models"/a.init), env=venv, learning_rate=a.lr, seed=a.seed, n_steps=512, batch_size=128, n_epochs=3, clip_range=a.clip, ent_coef=0.0, target_kl=a.target_kl)
    holder["model"] = model
    with torch.no_grad(): model.policy.log_std.fill_(a.log_std)
    out = dict(args=vars(a), init=a.init, tier="force_scale %s; frozen-DART start (script-distilled); residual PPO soft selection (cap %.2f, tol %.2f)" % (kw.get("force_scale"), a.cap, a.tol))
    out["diff_before"] = action_diff(model, kw)
    bc = BCReg(buf, a.lam, np.asarray(kw["learn_scale"], float), a.bc_k)
    SoftSel.cap, SoftSel.tol = a.cap, a.tol
    sel = SoftSel(make_eval, a.sel_every, a.sel_eps, 5000); sel.model = model; sel.consider("init")
    t0 = time.time(); model.learn(total_timesteps=a.steps, callback=[bc, sel]); sel.consider("final"); out["train_seconds"] = time.time()-t0
    out["selection_history"] = sel.hist; out["selected"] = sel.best[2]; model.policy.load_state_dict(sel.best[1])
    model.save(ROOT/"models"/a.name); out["checkpoint_sha256"] = hashlib.sha256((ROOT/"models"/f"{a.name}.zip").read_bytes()).hexdigest()
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_eval, a.eval_episodes)
    out["policy_stochastic"] = run_eval(lambda o: model.predict(o, deterministic=False)[0], make_eval, a.eval_episodes)
    out["diff_after"] = action_diff(model, kw); out["env_kwargs_full"] = kw
    json.dump(out, open(ROOT/"results"/f"{a.name}.json", "w"), indent=2, default=float)
    print("AFTER sel", out["selected"], {k: out["policy"][k] for k in ("true_contact_rate","mean_carry","lateral_std")}, "diff", out["diff_before"]["rms_rad_all"], "->", out["diff_after"]["rms_rad_all"], flush=True)
if __name__ == "__main__": main()

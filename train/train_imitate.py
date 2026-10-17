"""v5 imitation stage trainer: one curriculum stage = (script_weight w, learn_scale s).
  target = w * v3_script(t) + s * action     (w=0 -> script-free: the policy outputs every joint target)
1) DISTILL: behaviour-clone the teacher (full v3 script) into the policy: a* = (1-w) * script(t) / s (noisy rollouts for state diversity).
2) RL fine-tune (PPO, small lr/std) on flight reward (carry/launch/lateral via shot_pen) + unified-refset shape tracking (track_weight).
Writes models/<name>.zip, results/<name>.json (args, det + stochastic eval on the training env, learned-fraction stats). Gate: eval.eval_gate <name>.
"""
import argparse, json, time, subprocess
from pathlib import Path
import numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval, ProgressCallback
ROOT = Path(__file__).resolve().parent.parent


def env_kwargs(a):
    cfg = json.load(open(ROOT / a.config)); cfg.pop("description", None); cfg.pop("hypothetical", None)
    kw = dict(script=dict(cfg["script"]), residual_scale=tuple(a.res_scale), flight_model=True, curriculum=True, carry_reward=True,
              forward_reward=True, randomize_reset=True, gate_lo=15.0, gate_hi=35.0, seq_weight=a.seq_weight, style_prior=False, yaw_amp=0.1, wrist_amp=0.0, style_lead=0.05,
              analytic_ball=False, lat_weight=a.lat_weight, lat_angular=a.lat_angular, elev_weight=0.0, carry_cap=a.carry_cap, tempo_scale=0.0, shot_pen=a.shot_pen, act_l2=0.0,
              script_weight=a.stage_w, learn_scale=list(a.learn_scale), track_set="unified_v1", track_weight=a.track_weight)
    for k in ("ball_x", "ball_x_noise", "loft_deg", "ball_dz", "tee_height", "force_scale", "kp", "kd", "handedness", "model_xml", "sh_noise", "el_noise", "contact_damp", "impact_model"):
        if k in cfg: kw[k] = cfg[k]
    return kw


def _collect(model, kw, a, eps, seed0, use_student, noise_hi):
    """Roll out (teacher+noise, or the student mean+noise = DAgger) and label every visited state with the teacher action a* = (1-w)*script(t)/s."""
    env = ResidualGolfEnv(**kw); ls = np.asarray(kw["learn_scale"], float); w = kw["script_weight"]; X, Y = [], []
    rng = np.random.default_rng(seed0)
    for ep in range(eps):
        obs, _ = env.reset(seed=seed0 + ep); env.set_progress(1.0); done = False; nz = rng.uniform(0, noise_hi)
        while not done:
            tgt = np.clip((1.0 - w) * env.targets(env.clock) / ls, -1, 1)
            ideal = np.concatenate([tgt, [0.0]]).astype(np.float32); X.append(obs.copy()); Y.append(ideal)
            base = model.predict(obs, deterministic=True)[0] if use_student else ideal
            act = np.clip(base + rng.normal(0, nz, 5), -1, 1).astype(np.float32); act[4] = 0.0
            obs, _, done, trunc, _ = env.step(act); done = done or trunc
    return X, Y


def _fit(model, X, Y, ls, a, epochs, lr):
    X = torch.tensor(np.array(X)); Y = torch.tensor(np.array(Y)); pol = model.policy; opt = torch.optim.Adam(pol.parameters(), lr=lr); n = len(X)
    lst = torch.tensor(ls, dtype=torch.float32) * torch.tensor(a.w_vec, dtype=torch.float32); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=lr * 0.01)
    for epoch in range(epochs):
        perm = torch.randperm(n)
        for i in range(0, n, 512):
            idx = perm[i:i + 512]; mean = pol.get_distribution(X[idx]).distribution.mean
            loss = 1e3 * (((mean[:, :4] - Y[idx][:, :4]) * lst) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()  # error in RADIANS, extra weight on shoulder/yaw (w_vec)
        sched.step()
    with torch.no_grad(): rm = float(torch.sqrt((((pol.get_distribution(X).distribution.mean[:, :4] - Y[:, :4]) * torch.tensor(ls, dtype=torch.float32)) ** 2).mean()))
    return rm


def distill(model, kw, a):
    ls = np.asarray(kw["learn_scale"], float)
    X, Y = _collect(model, kw, a, a.bc_eps, 10000 + a.seed * 1000, False, a.bc_noise)
    rm = _fit(model, X, Y, ls, a, a.bc_epochs, a.bc_lr); hist = [rm]
    for it in range(a.dagger_iters):   # DAgger: states from the STUDENT (with injected action noise), teacher labels, aggregate, refit
        Xn, Yn = _collect(model, kw, a, a.dagger_eps, 50000 + a.seed * 1000 + it * 100, True, a.dagger_noise)
        X += Xn; Y += Yn; rm = _fit(model, X, Y, ls, a, max(a.bc_epochs // 2, 50), a.bc_lr * 0.5); hist.append(rm)
    return dict(n_samples=len(X), rmse_rad_per_iter=hist, rmse_rad_mean_joint=rm, dagger_iters=a.dagger_iters)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--config", default="configs/fast_scripted_v3.json")
    ap.add_argument("--stage_w", type=float, required=True); ap.add_argument("--learn_scale", type=float, nargs=4, required=True)
    ap.add_argument("--init_model", default=None); ap.add_argument("--res_scale", type=float, nargs=4, default=[0.01, 0.01, 0.01, 0.01])
    ap.add_argument("--bc_eps", type=int, default=200); ap.add_argument("--bc_epochs", type=int, default=400); ap.add_argument("--bc_lr", type=float, default=1e-3); ap.add_argument("--bc_noise", type=float, default=0.01)
    ap.add_argument("--ppo_steps", type=int, default=20000); ap.add_argument("--lr", type=float, default=1e-5); ap.add_argument("--log_std", type=float, default=-8.0)
    ap.add_argument("--dagger_iters", type=int, default=0); ap.add_argument("--dagger_eps", type=int, default=60); ap.add_argument("--dagger_noise", type=float, default=0.01)
    ap.add_argument("--w_vec", type=float, nargs=4, default=[3.0, 1.0, 2.0, 2.0]); ap.add_argument("--lat_weight", type=float, default=0.0); ap.add_argument("--lat_angular", action="store_true")
    ap.add_argument("--n_envs", type=int, default=2); ap.add_argument("--track_weight", type=float, default=2.0); ap.add_argument("--seq_weight", type=float, default=0.0)
    ap.add_argument("--shot_pen", type=float, default=1.0); ap.add_argument("--carry_cap", type=float, default=120.0); ap.add_argument("--eval_episodes", type=int, default=100)
    a = ap.parse_args(); torch.set_num_threads(1)
    kw = env_kwargs(a); make_env = lambda: ResidualGolfEnv(**kw)
    out = {"args": vars(a), "env_kwargs_full": kw, "git_head": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=str(ROOT)).stdout.strip()}
    venv = make_vec_env(make_env, n_envs=a.n_envs, seed=a.seed, vec_env_cls=SubprocVecEnv)
    if a.init_model: model = PPO.load(str(ROOT / "models" / a.init_model), env=venv, learning_rate=a.lr, seed=a.seed)
    else: model = PPO("MlpPolicy", venv, verbose=0, learning_rate=a.lr, n_steps=512, batch_size=256, n_epochs=10, seed=a.seed, policy_kwargs=dict(net_arch=[256, 256], log_std_init=a.log_std))
    t0 = time.time(); out["distill"] = distill(model, kw, a); print("DISTILL", json.dumps(out["distill"]), flush=True)
    with torch.no_grad(): model.policy.log_std.fill_(a.log_std)
    out["after_distill"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_env, 40, 5000)
    print("AFTER_DISTILL_DET", json.dumps({k: out["after_distill"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std", "mean_launch_elev_deg")}), flush=True)
    if a.ppo_steps > 0:
        model.learn(total_timesteps=a.ppo_steps, callback=ProgressCallback(a.ppo_steps, log_every=5000))
    out["train_seconds"] = time.time() - t0; model.save(ROOT / "models" / a.name)
    out["policy"] = run_eval(lambda o: model.predict(o, deterministic=True)[0], make_env, a.eval_episodes)
    out["policy_stochastic"] = run_eval(lambda o: model.predict(o, deterministic=False)[0], make_env, a.eval_episodes)
    e = make_env(); lf, dv = [], []
    for i in range(30):
        o, _ = e.reset(seed=7000 + i); e.set_progress(1.0); d = False
        while not d: o, _, d, t, info = e.step(model.predict(o, deterministic=True)[0]); d = d or t
        lf.append(info.get("learned_norm_frac", 0.0)); dv.append(info.get("traj_rms_dev_from_v3_script_rad", 0.0))
    out["learned"] = dict(script_weight=a.stage_w, action_norm_frac_from_policy=float(np.mean(lf)), traj_rms_dev_from_v3_script_rad=float(np.mean(dv)))
    json.dump(out, open(ROOT / "results" / f"{a.name}.json", "w"), indent=2, default=float)
    print("POLICY", json.dumps({k: out["policy"][k] for k in ("true_contact_rate", "mean_carry", "lateral_std", "mean_launch_elev_deg")}), "STOCH", json.dumps({k: out["policy_stochastic"][k] for k in ("mean_carry", "lateral_std", "mean_launch_elev_deg")}), "LEARNED", out["learned"], flush=True)


if __name__ == "__main__":
    main()

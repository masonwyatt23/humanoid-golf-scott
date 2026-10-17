"""Stage 25: stochastic contact of imit15_dart_s53 vs log_std (BOOSTED fs2, script-distilled)."""
import json, sys, torch, numpy as np
from stable_baselines3 import PPO
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
torch.set_num_threads(1)
kw = json.load(open("results/imit15_dart_s53.json"))["env_kwargs_full"]; out = {}
for ls in [-8, -6, -5, -4.5, -4]:
    m = PPO.load("models/imit15_dart_s53")
    with torch.no_grad(): m.policy.log_std.fill_(ls)
    r = run_eval(lambda o: m.predict(o, deterministic=False)[0], lambda: ResidualGolfEnv(**kw), 100, 5000)
    out[str(ls)] = {k: r[k] for k in ("true_contact_rate", "mean_carry", "lateral_std")}; print(ls, out[str(ls)], flush=True)
json.dump(out, open("results/stoch_probe_s25.json", "w"), indent=1)

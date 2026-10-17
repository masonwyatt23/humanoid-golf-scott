"""RMS action departure of ppo15_klres_s101 from the script (action_diff) and from its init imit15_dart_s53, + parameter diff."""
import json, numpy as np, torch
from stable_baselines3 import PPO
from env.residual_golf_env import ResidualGolfEnv
from train.ppo_bcreg import action_diff
J = json.load(open("results/ppo15_klres_s101.json")); kw = dict(J["env_kwargs_full"], _env="residual"); kw.pop("_env")
kw["residual_scale"] = list(kw["residual_scale"]); kw.setdefault("track_weight", 0.0)
A = PPO.load("models/ppo15_klres_s101.zip", device="cpu"); B = PPO.load("models/imit15_dart_s53.zip", device="cpu")
pa, pb = A.policy.state_dict(), B.policy.state_dict()
mx = max(float((pa[k] - pb[k]).abs().max()) for k in pa if k in pb); print("max |param diff|", mx)
out = {"max_abs_param_diff": mx, "script_diff_klres": action_diff(A, kw), "script_diff_init": action_diff(B, kw)}
env = ResidualGolfEnv(**kw); ls = np.asarray(kw["learn_scale"], float); d2 = []
for i in range(30):
    o, _ = env.reset(seed=7000 + i); env.set_progress(1.0); d = False
    while not d:
        a = A.predict(o, deterministic=True)[0]; b = B.predict(o, deterministic=True)[0]
        d2.append(((a[:4] - b[:4]) * ls) ** 2); o, _, d, t, _ = env.step(a); d = d or t
d2 = np.array(d2); out["klres_vs_init_rms_rad"] = float(np.sqrt(d2.mean())); out["klres_vs_init_per_joint"] = np.sqrt(d2.mean(0)).tolist()
print(json.dumps(out, indent=1)); json.dump(out, open("results/klres_private/departure.json", "w"), indent=1)

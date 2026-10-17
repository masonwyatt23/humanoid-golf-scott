"""Action-noise robustness of an imitation model (deterministic mean + iid Gaussian noise of std sigma in action units, i.e. sigma*learn_scale rad).
python -m eval.noise_robustness <name> [eps] [sigmas...]   -> results/noise_<name>.json   (training-env protocol = v3 config, flight physics)"""
import sys, json, numpy as np
from pathlib import Path
from stable_baselines3 import PPO
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
ROOT = Path(__file__).resolve().parent.parent
name = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 50; sig = [float(x) for x in sys.argv[3:]] or [0.0, 0.005, 0.01, 0.02]
J = json.load(open(ROOT / "results" / f"{name}.json")); kw = dict(J["env_kwargs_full"], track_weight=0.0, track_set=None); kw["residual_scale"] = tuple(kw["residual_scale"])
import os
MASK = np.array([float(x) for x in os.environ.get('NOISE_MASK', '1,1,1,1,1').split(',')])   # per-action-dim noise mask, e.g. NOISE_MASK=0,0,0,1,0 = yaw-only noise
TAG = os.environ.get('NOISE_TAG', '')
model = PPO.load(str(ROOT / "models" / name)); rng = np.random.default_rng(0); out = {}
for s in sig:
    r = run_eval(lambda o: np.clip(model.predict(o, deterministic=True)[0] + rng.normal(0, s, 5) * MASK, -1, 1), lambda: ResidualGolfEnv(**kw), n, 5000)
    out[str(s)] = {k: r[k] for k in ("true_contact_rate", "mean_carry", "lateral_std", "mean_launch_elev_deg", "frac_launch_8_14", "landed_fraction", "peak_club_speed_mean_mph")}
    print(name, "sigma", s, {k: round(v, 2) for k, v in out[str(s)].items()}, flush=True)
json.dump(out, open(ROOT / "results" / f"noise_{name}{TAG}.json", "w"), indent=1)

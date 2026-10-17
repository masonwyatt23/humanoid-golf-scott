"""Mean track_score / key_score (track_time_fix, unified_v1) + carry/lateral/launch of a policy, deterministic, training-env protocol. python -m eval.track_before_after <name> [eps] [seed]"""
import sys, json, numpy as np
from pathlib import Path
from stable_baselines3 import PPO
from env.residual_golf_env import ResidualGolfEnv
ROOT = Path(__file__).resolve().parent.parent
name = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 30; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
J = json.load(open(ROOT / "results" / f"{name}.json")); kw = dict(J["env_kwargs_full"], track_set="unified_v1", track_weight=1.0, track_time_fix=True, key_weight=1.0); kw["residual_scale"] = tuple(kw["residual_scale"])
env = ResidualGolfEnv(**kw); model = PPO.load(str(ROOT / "models" / name), device="cpu"); R = []
for i in range(n):
    o, _ = env.reset(seed=seed + i); env.set_progress(1.0); d = False
    while not d: o, _, te, tr, info = env.step(model.predict(o, deterministic=True)[0]); d = te or tr
    p = info.get("track_parts", {}); R.append([info.get("track_score", np.nan), info.get("key_score", np.nan), p.get("sh", np.nan), p.get("yaw", np.nan), p.get("wr", np.nan), info["carry"], info["ball_lateral"], np.degrees(info["launch_elevation"]), info.get("traj_rms_dev_from_v3_script_rad", np.nan)])
R = np.array(R); print(name, "track %.3f key %.3f | sh %.3f yaw %.3f wr %.3f | carry %.1f lat_std %.2f launch %.1f | rms dev from script %.4f rad" % (*np.nanmean(R[:, :5], 0), R[:, 5].mean(), R[:, 6].std(), R[:, 7].mean(), np.nanmean(R[:, 8])))

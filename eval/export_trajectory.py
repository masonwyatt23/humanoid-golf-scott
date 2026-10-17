"""Export a qpos trajectory of one rollout for the render pipeline. python -m eval.export_trajectory <model_name> <seed> [out.npz]
Saves time (s), qpos (T,nq) sampled every 10 ms of sim time, ball_pos (T,3), joint_names, and metadata JSON (model xml, env kwargs, gate numbers). Deterministic policy, evaluator-protocol env."""
import sys, json, numpy as np, mujoco
from pathlib import Path
from stable_baselines3 import PPO
from env.residual_golf_env import ResidualGolfEnv
ROOT = Path(__file__).resolve().parent.parent
name, seed = sys.argv[1], int(sys.argv[2]); out = sys.argv[3] if len(sys.argv) > 3 else str(ROOT / "results" / "trajectories" / f"{name}_seed{seed}.npz")
J = json.load(open(ROOT / "results" / f"{name}.json")); kw = dict(J["env_kwargs_full"], track_weight=0.0, track_set=None); kw["residual_scale"] = tuple(kw["residual_scale"])
env = ResidualGolfEnv(**kw); model = PPO.load(str(ROOT / "models" / name)); m = env.model
T, Q, B = [], [], []; orig = mujoco.mj_step
def wrapped(mm, d, *a, **k):
    orig(mm, d, *a, **k)
    if len(T) == 0 or d.time - T[-1] >= 0.01 - 1e-9: T.append(float(d.time)); Q.append(d.qpos.copy()); B.append(d.xpos[env._ball_id].copy())
mujoco.mj_step = wrapped
try:
    obs, _ = env.reset(seed=seed); env.set_progress(1.0); done = False
    while not done:
        obs, _, done, tr, info = env.step(model.predict(obs, deterministic=True)[0]); done = done or tr
finally: mujoco.mj_step = orig
jn = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
meta = dict(model=name, seed=seed, model_xml=kw.get("model_xml"), handedness=kw.get("handedness"), script_weight=kw["script_weight"], sample_dt_s=0.01, true_contact=bool(info["true_contact"]),
            carry_m=float(info["carry"]), lateral_m=float(info["ball_lateral"]), launch_deg=float(np.degrees(info["launch_elevation"])), peak_club_mph=float(info["peak_club_speed"] * 2.23694),
            qpos_layout="MuJoCo qpos (freejoint ball: qpos[0:7]=ball pos+quat; see joint_names for the rest)", note="Policy outputs all 4 joint PD targets (script_weight 0); evaluator-protocol physics, v3 config")
np.savez_compressed(out, time=np.array(T), qpos=np.array(Q), ball_pos=np.array(B), joint_names=np.array(jn), metadata=json.dumps(meta))
print(out, len(T), "frames", meta)

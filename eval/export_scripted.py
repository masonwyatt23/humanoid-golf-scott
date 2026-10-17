"""Export qpos + body poses of one scripted-config rollout. python -m eval.export_scripted cfg.json seed out_stem
Writes <stem>.npz (time, qpos, body_xpos, body_xquat, ball_pos, joint_names, body_names, metadata) and <stem>_bodymap.json."""
import sys, json, numpy as np, mujoco
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
cfgf, seed, stem = sys.argv[1], int(sys.argv[2]), sys.argv[3]
cfg = json.load(open(cfgf)); desc = cfg.pop("description", ""); cfg.pop("hypothetical", None)
kw = dict(B0); kw.update(cfg); kw["script"] = dict(B0["script"], **cfg["script"])
env = make_env(kw); m = env.model
T, Q, X, R, B = [], [], [], [], []; orig = mujoco.mj_step
def w(mm, d, *a, **k):
    orig(mm, d, *a, **k)
    if not T or d.time - T[-1] >= 0.01 - 1e-9: T.append(float(d.time)); Q.append(d.qpos.copy()); X.append(d.xpos.copy()); R.append(d.xquat.copy()); B.append(d.xpos[env._ball_id].copy())
mujoco.mj_step = w
try:
    obs, _ = env.reset(seed=seed); done = False; z = np.zeros(env.action_space.shape, dtype=np.float32)
    while not done:
        obs, _, te, tr, info = env.step(z); done = te or tr
finally: mujoco.mj_step = orig
jn = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]; jn = [j or f"free_{i}" for i, j in enumerate(jn)]
bn = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(m.nbody)]
meta = dict(config=cfgf, description=desc, model_xml=kw["model_xml"], seed=seed, episode=0, sample_dt_s=0.01, handedness=kw["handedness"], true_contact=bool(info["true_contact"]),
            ball_final_x=float(info["max_ball_x"]), peak_club_mph=float(info["peak_club_speed"] * 2.23694), launch_deg=float(np.degrees(info["launch_elevation"])),
            note="HYPOTHETICAL power tier; scripted v4 swing, zero residual. chest_yaw is a +-60deg stand-in for pelvis yaw (no pelvis-yaw DOF).")
np.savez_compressed(stem + ".npz", time=np.array(T), qpos=np.array(Q), body_xpos=np.array(X), body_xquat=np.array(R), ball_pos=np.array(B), joint_names=np.array(jn), body_names=np.array(bn), metadata=json.dumps(meta))
bm = dict(note="body index -> name (axis 1 of body_xpos/body_xquat, wxyz quats, world frame); joints list gives qpos address/type/range. 'pelvis_standin_joint' is the chest_yaw joint (rotates torso about vertical).",
          bodies=[dict(index=i, name=bn[i], parent=bn[int(m.body_parentid[i])]) for i in range(m.nbody)],
          joints=[dict(name=jn[i], qpos_adr=int(m.jnt_qposadr[i]), type=int(m.jnt_type[i]), range_rad=[float(x) for x in m.jnt_range[i]], body=bn[int(m.jnt_bodyid[i])]) for i in range(m.njnt)],
          pelvis_standin_joint="chest_yaw", spine_joints=[j for j in jn if any(s in j for s in ("chest","spine","waist"))], metadata=meta)
json.dump(bm, open(stem + "_bodymap.json", "w"), indent=1); print(stem, len(T), "frames", meta)

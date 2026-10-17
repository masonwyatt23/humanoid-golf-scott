"""Build evaluation envs/policies from a config dict stored in the leaderboard cache.

kw["_env"] == "residual": ResidualGolfEnv (scripted swing + PPO residual), kwargs rebuilt exactly as train/train_residual.py main()
does from the results/<name>.json `args`.  Otherwise HumanoidGolfEnv (legacy train_ppo envs).
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
# train_residual.py argparse defaults, used ONLY for keys absent from a results JSON "args" (older runs)
RESID_DEFAULTS = dict(model_xml="humanoid_golf_v3.xml", flight_model=False, gate_lo=15.0, gate_hi=35.0, loft=6.0, q_back=2.2,
                      t_down=0.12, res_scale=[0.2, 0.2, 0.2, 0.1], yaw=False, force_scale=2.0, seq_weight=0.0, style_prior=False,
                      handedness="right")


def resid_kw_from_args(args: dict, ball_dz_if_absent: float = 0.0) -> dict:
    a = dict(RESID_DEFAULTS); a.update(args)
    ball_dz = a.get("ball_dz", ball_dz_if_absent)   # flag did not exist in older runs: env default 0.0 then (see leaderboard note)
    script = dict(q_back=a["q_back"], t_down=a["t_down"], t_back=0.6)
    script.update(json.loads(a["script_extra"])) if a.get("script_extra") else None
    if a["yaw"]:
        script.update(yaw_back=-0.35, yaw_fin=0.35)
    extra = {k: a[k] for k in ("ball_x", "ball_x_noise", "sh_noise", "el_noise", "tempo_scale", "contact_damp", "script_weight", "learn_scale", "flight_steps", "elbow_base") if k in a}   # address-position args (an8+); absent -> env defaults (0.43 / 0.03)
    if a.get("impact_model"): extra["impact_model"] = json.loads(a["impact_model"])
    return dict(**extra, _env="residual", script=script, residual_scale=list(a["res_scale"]), model_xml=a["model_xml"], flight_model=a["flight_model"],
                tee_height=0.04, force_scale=a["force_scale"], kp=700.0, kd=700.0 / 30, loft_deg=a["loft"], curriculum=True, carry_reward=True,
                forward_reward=True, randomize_reset=True, ball_dz=ball_dz, handedness=a["handedness"], gate_lo=a["gate_lo"], gate_hi=a["gate_hi"],
                seq_weight=a["seq_weight"], style_prior=a["style_prior"], yaw_amp=0.1, wrist_amp=0.0, style_lead=0.05)


def make_env(kw: dict):
    kw = dict(kw)
    if kw.pop("_env", None) == "residual":
        from env.residual_golf_env import ResidualGolfEnv
        kw["residual_scale"] = tuple(kw["residual_scale"])
        return ResidualGolfEnv(**kw)
    from env.humanoid_golf_env import HumanoidGolfEnv
    return HumanoidGolfEnv(reference_path=str(ROOT / "data/references/scott_swing.npz"), **kw)


# ref-column joint names (data/process_video.py JOINT_NAMES): lets us read the same 11 joints from ANY model layout
JOINT_NAMES = ["right_shoulder_pitch", "right_shoulder_roll", "right_elbow", "right_wrist", "left_shoulder_pitch",
               "right_hip_pitch", "right_knee", "right_ankle", "left_hip_pitch", "left_knee", "left_ankle"]


def joint_qpos_idx(env):
    return np.array([int(env.model.jnt_qposadr[env.model.joint(n).id]) for n in JOINT_NAMES])

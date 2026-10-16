"""Unitree G1 (29-DoF, MuJoCo Menagerie, BSD-3) + driver club golf env with actuator-tier knobs.

Honest scope: pelvis is a vertical-axis yaw hinge (stand-in for planted-foot hip yaw of both legs, torque = 2x hip-yaw);
all leg joints are held rigid by PD; the robot cannot fall. Club: 0.27 kg (shaft+grip 0.07, head 0.20), 1.15 m, left hand
soft-tied to the shaft 12 cm below the right hand. Ball on an invisible tee (held until first club contact).

Tiers (torque N*m, speed rad/s). 'stock' = Menagerie/Unitree numbers as used in scripts/g1_club_speed_feasibility.py.
'elite' = HYPOTHETICAL robot (NOT an existing product): hips/waist 250 N*m & 45 rad/s (pelvis proxy = 2 hips = 500),
shoulders/elbow 75 N*m & 55 rad/s, wrists 30 N*m (speed 55 rad/s assumed).
Torque-speed curve: torque scales linearly to 0 at the rated speed (in the direction of motion).
"""
import numpy as np
import mujoco
from pathlib import Path
from gymnasium import spaces
import gymnasium as gym

MENAG = "/workspace/menagerie"
CLUB_LEN, GRIP_SEP, SHAFT_M, HEAD_M = 1.15, 0.12, 0.07, 0.20
DT = 0.0005
CTRL_DT = 0.02
SUBSTEPS = int(round(CTRL_DT / DT))

ARM = ["shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow", "wrist_roll", "wrist_pitch", "wrist_yaw"]


def tier_limits(tier):
    if tier == "stock":
        hip, waist, sh, wr_r, wr_py = (176, 32), (88, 32), (25, 37), (25, 37), (5, 22)
        wp = (50, 32)
    elif tier == "elite":  # HYPOTHETICAL
        hip, waist, sh, wr_r, wr_py = (500, 45), (250, 45), (75, 55), (30, 55), (30, 55)
        wp = (250, 45)
    else:
        raise ValueError(tier)
    L = {"pelvis_yaw": hip, "waist_yaw_joint": waist, "waist_roll_joint": wp, "waist_pitch_joint": wp}
    for side in ("left", "right"):
        for j in ("shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow"):
            L[f"{side}_{j}_joint"] = sh
        L[f"{side}_wrist_roll_joint"] = wr_r
        L[f"{side}_wrist_pitch_joint"] = wr_py
        L[f"{side}_wrist_yaw_joint"] = wr_py
    return L


def build_model():
    spec = mujoco.MjSpec.from_file(f"{MENAG}/unitree_g1/scene.xml")
    for k in list(spec.keys):
        spec.delete(k)
    spec.option.timestep = DT
    pel = spec.body("pelvis")
    for j in list(pel.joints):
        spec.delete(j)
    pel.add_joint(name="pelvis_yaw", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 0, 1], range=[-1.6, 1.6], limited=True,
                  damping=1.0, armature=0.5)
    for g in spec.geoms:
        if g.name != "floor":
            g.contype = 0; g.conaffinity = 0
    rw = spec.body("right_wrist_yaw_link")
    club = rw.add_body(name="club", pos=[0.10, 0, 0])
    club.add_geom(name="shaft", type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0, 0, 0.20 - CLUB_LEN, 0, 0, 0.20], size=[0.008, 0, 0],
                  mass=SHAFT_M, contype=0, conaffinity=0, rgba=[.2, .2, .2, 1])
    club.add_geom(name="head", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[0.03, 0, 0.20 - CLUB_LEN], size=[0.04, 0.05, 0.03], mass=HEAD_M,
                  contype=2, conaffinity=2, solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001], rgba=[.7, .7, .75, 1])
    club.add_site(name="grip_left", pos=[0, 0, -GRIP_SEP])
    club.add_site(name="clubhead", pos=[0.03, 0, 0.20 - CLUB_LEN])
    lw = spec.body("left_wrist_yaw_link")
    lw.add_site(name="lhand", pos=[0.10, 0, 0])
    eq = spec.add_equality(name="left_grip", type=mujoco.mjtEq.mjEQ_CONNECT, objtype=mujoco.mjtObj.mjOBJ_SITE, name1="lhand", name2="grip_left")
    eq.solref = [0.01, 1]
    ball = spec.worldbody.add_body(name="ball", pos=[0.5, 0.0, 0.07])
    ball.add_freejoint()
    ball.add_geom(name="ball_geom", type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[0.021, 0, 0], mass=0.046, contype=3, conaffinity=3,
                  solref=[0.002, 1], solimp=[0.95, 0.99, 0.001, 0.5, 2], friction=[0.5, 0.01, 0.001])
    spec.add_actuator(name="pelvis_yaw", target="pelvis_yaw", trntype=mujoco.mjtTrn.mjTRN_JOINT, gear=[1, 0, 0, 0, 0, 0])
    model = spec.compile()
    # all actuators become direct torque motors (ctrl = N*m); PD + limits are computed in python
    model.actuator_gainprm[:, 0] = 1.0
    model.actuator_biasprm[:, :] = 0.0
    model.actuator_forcerange[:] = 0.0
    model.actuator_forcelimited[:] = 0
    model.actuator_ctrllimited[:] = 0
    model.actuator_gear[:, 0] = 1.0
    # joint-level actuatorfrcrange from Menagerie would clip; disable (we apply tier limits ourselves)
    model.jnt_actfrclimited[:] = 0
    return model

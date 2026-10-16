"""IK for G1 golf key poses (address, top-of-backswing, impact). Writes env/g1_poses.json"""
import sys, json, numpy as np, mujoco
sys.path.insert(0, '.')
from scipy.optimize import least_squares
from env.g1_golf_env import build_model, ARM

m = build_model(); d = mujoco.MjData(m)
J = lambda n: m.joint(n)
qadr = lambda n: int(m.jnt_qposadr[J(n).id])
free = ["waist_pitch_joint", "waist_roll_joint"] + [f"{s}_{a}_joint" for s in ("right", "left") for a in ARM]
rng_ = {n: m.jnt_range[J(n).id] for n in free}
head = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "clubhead")
gl = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "grip_left")
lh = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "lhand")
cl = m.body("club").id
BALL = np.array([0.5, 0.0, 0.07])

def fk(q, fixed):
    d.qpos[:] = m.qpos0
    for n, v in fixed.items(): d.qpos[qadr(n)] = v
    for n, v in zip(free, q): d.qpos[qadr(n)] = v
    mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d)

def cost(q, fixed, head_t, face_w, shaft_w, q0):
    fk(q, fixed)
    R = d.xmat[cl].reshape(3, 3)
    r = [ (d.site_xpos[head] - head_t) * 10.0,
          (d.site_xpos[lh] - d.site_xpos[gl]) * 6.0,
          face_w * (R[:, 0] - np.array([0, 1, 0])),
          shaft_w * (R[:, 2] - np.array([0, 0, 1])),
          0.05 * (q - q0) ]
    return np.concatenate(r)

def solve(fixed, head_t, face_w=2.0, shaft_w=2.0, q0=None, seeds=6):
    q0 = np.zeros(len(free)) if q0 is None else q0
    lo = np.array([rng_[n][0] for n in free]); hi = np.array([rng_[n][1] for n in free])
    best = None; rs = np.random.default_rng(0)
    for s in range(seeds):
        x0 = np.clip(q0 + (0 if s == 0 else rs.normal(0, 0.4, len(free))), lo + 1e-3, hi - 1e-3)
        r = least_squares(cost, x0, bounds=(lo, hi), args=(fixed, head_t, face_w, shaft_w, q0))
        if best is None or r.cost < best.cost: best = r
    fk(best.x, fixed)
    return best.x, dict(head_err=float(np.linalg.norm(d.site_xpos[head] - head_t)), hand_err=float(np.linalg.norm(d.site_xpos[lh] - d.site_xpos[gl])),
                        shaft_z=float(d.xmat[cl].reshape(3, 3)[2, 2]), face_y=float(d.xmat[cl].reshape(3, 3)[1 - 1, 0] * 0 + d.xmat[cl].reshape(3, 3)[1, 0]))

if __name__ == "__main__":
    out = {}
    head_addr = BALL + np.array([0.0, -0.10, 0.0])     # 4 cm gap between face and ball at address
    head_imp = BALL + np.array([0.0, -0.066, 0.0])     # face touching the ball at impact
    qa, ea = solve({"pelvis_yaw": 0.0, "waist_yaw_joint": 0.0}, head_addr)
    out["address"] = dict(zip(free, qa.tolist()), pelvis_yaw=0.0, waist_yaw_joint=0.0); print("address", ea)
    # impact: body already rotated toward target (pelvis +0.5, waist +0.6): arms adapt
    for py, wy in [(0.5, 0.6), (0.3, 0.4)]:
        qi, ei = solve({"pelvis_yaw": py, "waist_yaw_joint": wy}, head_imp, q0=qa)
        print("impact", py, wy, ei)
        out[f"impact_{py}_{wy}"] = dict(zip(free, qi.tolist()), pelvis_yaw=py, waist_yaw_joint=wy, **{"_err": ei})
    # top of backswing: body turned away (pelvis -0.7, waist -0.9), head behind/above right shoulder
    head_top = np.array([-0.1, -0.6, 1.25])
    qt, et = solve({"pelvis_yaw": -0.7, "waist_yaw_joint": -0.9}, head_top, face_w=0.0, shaft_w=0.0, q0=qa)
    print("top", et); out["top"] = dict(zip(free, qt.tolist()), pelvis_yaw=-0.7, waist_yaw_joint=-0.9)
    json.dump(out, open("env/g1_poses.json", "w"), indent=1)

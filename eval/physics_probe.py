"""No-training physics probes: (1) prescribed (kinematic) swing -> ball speed vs club speed,
(2) torque-limited dynamic swing -> achievable club speed. Writes results/physics_probe.json"""
import json, sys, numpy as np, mujoco
from env.humanoid_golf_env import HumanoidGolfEnv

def make(xml, dt=None, **kw):
    e = HumanoidGolfEnv(pin_torso=True, address_pose="fixed", model_xml=xml, **kw)
    if dt: e.model.opt.timestep = dt
    return e

def prescribed(xml, dt, omega, q0=0.9, flight=False):
    e = make(xml, dt, flight_model=flight); e.reset(seed=0)
    m, d = e.model, e.data
    d.qpos[14] = q0; mujoco.mj_forward(m, d)
    t = 0.0; maxclub = 0.0; hit = False; impact_cs = 0.0; air = False; carry = 0.0; apex = 0.0; bv0 = None
    n = int(6.0 / m.opt.timestep) if flight else int(0.8 / m.opt.timestep)
    for k in range(n):
        q = q0 - omega * t
        d.qpos[7:14] = e._root_pin; d.qvel[6:12] = 0
        d.qpos[14] = q; d.qvel[12] = -omega if q > -1.2 else 0.0
        d.qpos[16] = np.deg2rad(20); d.qvel[14] = 0
        d.qpos[15] = 0; d.qvel[13] = 0; d.qpos[17] = 0; d.qvel[15] = 0   # hold roll + wrist rigid
        if q <= -1.2: d.qvel[12] = 0
        if flight: e._apply_aero()
        mujoco.mj_step(m, d); t += m.opt.timestep
        cs = e._club_speed()
        bz = d.xpos[e._ball_id][2]; apex = max(apex, bz)
        if hit and bv0 is None and t > 0.02 + (0.9 - 0) / omega * 0 and np.linalg.norm(d.qvel[0:3]) > 1: pass
        if hit and bz > 0.06: air = True
        if hit and air and carry == 0.0 and bz < 0.03: carry = float(d.xpos[e._ball_id][0]); break
        if not hit:
            if e._check_contact(): hit = True; impact_cs = max(maxclub, cs)
            maxclub = cs
    bv = d.qvel[0:3].copy()
    return dict(model=xml, dt=m.opt.timestep, omega=omega, contact=bool(hit), impact_club_speed=float(impact_cs),
                ball_speed=float(np.linalg.norm(bv)), smash=float(np.linalg.norm(bv) / impact_cs) if impact_cs > 0.5 else None,
                launch_elev_deg=float(np.degrees(np.arctan2(bv[2], np.hypot(bv[0], bv[1])))), ball_vx=float(bv[0]), carry=carry, apex=float(apex), total_x=float(d.xpos[e._ball_id][0]))

def dynamic(xml, dt, torque, ball=True, smoothing=0.0):
    """best of a small open-loop sweep: backswing B steps then full forward torque."""
    best = None
    for B in [3, 6, 10, 14, 18, 24]:
        for hold in [15, 20, 30]:
            e = make(xml, dt, torque_scale=torque); e.reset(seed=0)
            if not ball: e.data.qpos[0] = 5.0
            e.data.qvel[:] = 0
            peak = 0.0; ics = 0.0
            for t in range(120):
                a = np.zeros(11); a[0] = 1.0 if t < B else -1.0 if t < B + hold else 0
                a[2] = -1.0 if t < B else 0.5; a[3] = 0.0
                _, _, done, _, info = e.step(a)
                peak = max(peak, e._club_speed())
            row = dict(model=xml, dt=e.model.opt.timestep, torque_scale=torque, B=B, hold=hold, peak_club_speed=float(peak),
                       contact=bool(info["true_contact"]), impact_club_speed=float(info["impact_club_speed"]),
                       ball_speed=float(info["peak_ball_speed"]))
            key = row["ball_speed"] if ball else row["peak_club_speed"]
            if best is None or key > best["_k"]: best = dict(row, _k=key)
    return best

if __name__ == "__main__":
    out = {"prescribed": [], "dynamic_free_air": [], "dynamic_with_ball": []}
    for xml, dt in [("humanoid_golf.xml", 0.002), ("humanoid_golf.xml", 0.0005), ("humanoid_golf_v2.xml", 0.0005), ("humanoid_golf_v2.xml", 0.0002)]:
        for om in [6, 12, 20, 30, 40]:
            r = prescribed(xml, dt, om, flight=(xml == "humanoid_golf_v2.xml" and dt == 0.0005)); out["prescribed"].append(r); print("P", r, flush=True)
    for xml, dt in [("humanoid_golf.xml", 0.002), ("humanoid_golf_v2.xml", 0.0005)]:
        for tq in [3, 10]:
            r = dynamic(xml, dt, tq, ball=False); out["dynamic_free_air"].append(r); print("DF", r, flush=True)
            r = dynamic(xml, dt, tq, ball=True); out["dynamic_with_ball"].append(r); print("DB", r, flush=True)
    json.dump(out, open("results/physics_probe.json", "w"), indent=1)

"""Wrist PD step/ramp-response probe (read-only use of env/; light, no training).
python -m data.wrist_pd_lag_probe [--out data/references/wrist_pd_lag_probe.json]
Drives ResidualGolfEnv's own PD (kp, kd, gear, forcerange, 20 ms control / 0.5 ms physics) with other targets held, and logs commanded vs achieved
right_wrist. Static analysis lines (inertia, lag constant) are computed from the model. All numbers UNVERIFIED beyond this sim; not a hardware claim."""
import argparse, json
import numpy as np, mujoco
from env.residual_golf_env import ResidualGolfEnv

KW = dict(flight_model=False, tee_height=0.04, kp=700.0, kd=700.0 / 30, handedness="left", randomize_reset=False, ball_dz=-0.008, ball_x=0.396)


def make(xml, fs, grip=False):
    return ResidualGolfEnv(model_xml=xml, force_scale=fs, grip=grip, residual_scale=(0, 0, 0, 0), **KW)


def drive(env, wrist_fn, T, hold=(0.0, 0.35, 0.0)):
    """wrist_fn(t)->wrist target (rad); returns arrays t, cmd, ach, ctrl_sat, torque."""
    env.reset(seed=0)
    ai, lim = env._act["right_wrist"], env.model.actuator_forcerange[env._act["right_wrist"], 1]
    env.targets = lambda t: np.array([hold[0], hold[1], wrist_fn(t), hold[2]])
    R = []
    for _ in range(int(T / 0.02)):
        t0 = env.clock
        env.step(np.zeros(5, np.float32))
        R.append((env.clock, env._tgt[2], env.data.qpos[env._qa["right_wrist"]], abs(env.data.ctrl[ai]) >= 0.999 * lim, env.data.qfrc_actuator[env._da["right_wrist"]]))
    return np.array(R, float)


def summarize(R, tgt_final):
    cmd, ach = R[:, 1], R[:, 2]
    i90 = np.argmax(np.abs(ach) >= 0.9 * abs(tgt_final)) if np.any(np.abs(ach) >= 0.9 * abs(tgt_final)) else -1
    return dict(final_cmd=round(float(cmd[-1]), 3), final_ach=round(float(ach[-1]), 3), max_abs_err=round(float(np.max(np.abs(cmd - ach))), 3),
                sat_frac=round(float(R[:, 3].mean()), 2), t90_s=(round(float(R[i90, 0] - R[0, 0] + 0.02), 3) if i90 >= 0 else None))


def static_info(xml, fs):
    env = make(xml, fs); m = env.model; ai = env._act["right_wrist"]
    jid = m.actuator_trnid[ai, 0]; dof = m.jnt_dofadr[jid]
    mujoco.mj_forward(m, env.data)
    return dict(gear=float(m.actuator_gear[ai, 0]), forcerange=[float(x) for x in m.actuator_forcerange[ai]], max_torque_Nm=float(m.actuator_gear[ai, 0] * m.actuator_forcerange[ai, 1]),
                joint_damping=float(m.dof_damping[dof]), armature=float(m.dof_armature[dof]),
                dt_physics=float(m.opt.timestep), dt_control=0.02, kp=env.kp, kd=env.kd,
                ctrl_to_torque="ctrl=(kp*err-kd*qd)/gear, force=ctrl (gain 1) clipped to forcerange, torque=gear*force; target-position PD, not raw torque")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="data/references/wrist_pd_lag_probe.json"); a = ap.parse_args()
    out = {"status": "UNVERIFIED sim probe; env/ read-only", "models": {}}
    for name, xml, fss in (("v3", "humanoid_golf_v3.xml", (1.0, 2.0)), ("v4_power", "humanoid_golf_v4_power.xml", (1.0, 2.0))):
        for fs in fss:
            key = f"{name}_fs{fs:g}"; e = {"static": static_info(xml, fs), "cases": {}}
            T0 = 0.8  # settle time at the start value before any ramp (so the initial offset does not pollute the lag metric)
            ramp = lambda a0, a1, dur: (lambda t: a0 if t < T0 else a0 + (a1 - a0) * min((t - T0) / dur, 1.0))
            for lbl, fn, T in (("step_0_to_-0.09", lambda t: -0.09, 0.4), ("step_0_to_-0.33", lambda t: -0.33, 0.4),
                               ("settled_-0.5_ramp_to_-0.09_in_0.095s", ramp(-0.5, -0.09, 0.095), T0 + 0.4),
                               ("settled_-0.5_ramp_to_-0.33_in_0.095s", ramp(-0.5, -0.33, 0.095), T0 + 0.4),
                               ("settled_0_ramp_to_-0.977_in_0.095s", ramp(0.0, -0.977, 0.095), T0 + 0.4),
                               ("settled_-0.5_ramp_to_-0.09_in_0.2s", ramp(-0.5, -0.09, 0.2), T0 + 0.5)):
                env = make(xml, fs)
                R = drive(env, fn, T); c = summarize(R, float(R[-1, 1])); e["cases"][lbl] = c
                if lbl.startswith("settled"):
                    dur = float(lbl.split("in_")[1].rstrip("s")); k = int(np.argmin(np.abs(R[:, 0] - (T0 + dur))))
                    c["at_ramp_end_cmd"] = round(float(R[k, 1]), 3); c["at_ramp_end_ach"] = round(float(R[k, 2]), 3)
                    c["lag_at_ramp_end_rad"] = round(float(R[k, 2] - R[k, 1]), 3)
                    c["max_abs_err_during_ramp"] = round(float(np.max(np.abs(R[(R[:, 0] > T0) & (R[:, 0] <= T0 + dur + 0.02), 1] - R[(R[:, 0] > T0) & (R[:, 0] <= T0 + dur + 0.02), 2]))), 3)
                    c.pop("max_abs_err"); c.pop("t90_s")
            out["models"][key] = e
    # diagnostic fix sweep (v3 fs2): lead the command by L seconds and/or change kp/kd; metric = achieved-minus-intended wrist at ramp end (-0.5 -> -0.09 in 0.095 s)
    sweep = {}
    for kp, kd in ((700.0, 700.0 / 30), (1400.0, 700.0 / 30), (1400.0, 40.0)):
        for L in (0.0, 0.04, 0.06, 0.08):
            env = make("humanoid_golf_v3.xml", 2.0); env.kp, env.kd = kp, kd
            T0 = 0.8; fn = lambda t, L=L: -0.5 + 0.41 * float(np.clip((t + L - T0) / 0.095, 0.0, 1.0))
            R = drive(env, fn, T0 + 0.3)
            k = int(np.argmin(np.abs(R[:, 0] - (T0 + 0.095 + 0.02))))
            sweep[f"kp{kp:g}_kd{kd:.1f}_lead{L:g}"] = dict(ach_at_impact=round(float(R[k, 2]), 3), intended=-0.09, err=round(float(R[k, 2] + 0.09), 3), peak_past_intended=round(float(np.max(R[:, 2]) + 0.09), 3))
    out["fix_sweep_v3_fs2"] = sweep
    json.dump(out, open(a.out, "w"), indent=1)
    for k, v in out["models"].items():
        print(k, "max torque", v["static"]["max_torque_Nm"])
        for c, s in v["cases"].items(): print("  ", c, s)


if __name__ == "__main__":
    main()

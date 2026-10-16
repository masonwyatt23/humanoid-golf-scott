"""
Scripted-swing + residual-policy golf env (PD targets).

A scripted backswing/downswing trajectory (shoulder pitch, elbow, wrist, chest yaw) is tracked by joint PD
controllers (torque limited by the actuator forcerange in the XML). The policy outputs RESIDUALS added to
the scripted joint targets plus a tempo factor that speeds up/slows down the swing clock. The observation
contains the swing phase (progress of the scripted swing in [0,1]).

Action (5): [d_shoulder, d_elbow, d_wrist, d_chest_yaw, tempo] in [-1,1]
  residual_scale rad per unit (default 0.4 / 0.4 / 0.4 / 0.25), tempo -> clock speed 1 + 0.3*a.
"""
import numpy as np
import mujoco
from gymnasium import spaces
from env.humanoid_golf_env import HumanoidGolfEnv

DEFAULT_SCRIPT = dict(q_back=2.0, elbow_back=0.5, t_hold=0.10, t_back=0.55, t_pause=0.05, t_down=0.22,
                      q_fin=-1.2, t_follow=0.25, wrist_cock=0.0, yaw_back=0.0, yaw_fin=0.0)


def _smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


class ResidualGolfEnv(HumanoidGolfEnv):
    def __init__(self, script=None, residual_scale=(0.4, 0.4, 0.4, 0.25), kp=700.0, kd=40.0, grip=False, force_scale=1.0, style_prior=False, yaw_amp=0.6, wrist_amp=0.8, yaw_sign=1.0, wrist_sign=1.0, style_lead=0.0, seq_weight=0.0, **kw):
        kw.setdefault("pin_torso", True)
        kw.setdefault("address_pose", "fixed")
        kw.setdefault("model_xml", "humanoid_golf_v3.xml")
        super().__init__(**kw)
        self.script = dict(DEFAULT_SCRIPT, **(script or {}))
        s = self.script
        self.T = s["t_hold"] + s["t_back"] + s["t_pause"] + s["t_down"] + s["t_follow"]
        self.swing_steps = int(np.ceil(self.T / 0.02))
        self.max_steps = self.swing_steps + 200  # extra time for the ball to fly and land (episode ends earlier on landing)
        self.res_scale = np.array(residual_scale)
        self.kp, self.kd = kp, kd
        self.action_space = spaces.Box(-1.0, 1.0, shape=(5,), dtype=np.float32)
        m = self.model
        self._jn = ["right_shoulder_pitch", "right_elbow", "right_wrist", "chest_yaw"]
        self._qa = {n: int(m.jnt_qposadr[m.joint(n).id]) for n in self._jn}
        self._da = {n: int(m.jnt_dofadr[m.joint(n).id]) for n in self._jn}
        self._act = {m.actuator(i).name: i for i in range(m.nu)}
        self._gear = m.actuator_gear[:, 0]
        self._hold = [n for n in self._act if n not in self._jn and n != "left_shoulder_pitch"]
        self.style = None
        if style_prior:
            from env.style_prior import StylePrior
            self.style = StylePrior()
        self.yaw_amp, self.wrist_amp, self.yaw_sign, self.wrist_sign = yaw_amp, wrist_amp, yaw_sign, wrist_sign
        self.style_lead = style_lead  # seconds: yaw/wrist targets are read this far ahead to offset PD lag
        self.clock = 0.0
        self._tgt = np.zeros(4)
        self._contact_step = None
        self.grip = grip
        if force_scale != 1.0:
            self.model.actuator_forcerange[:] *= force_scale
        self.model.eq_active0[:] = 1 if grip else 0

    # scripted joint targets at swing time t
    def targets(self, t):
        s = self.script
        t1 = s["t_hold"]; t2 = t1 + s["t_back"]; t3 = t2 + s["t_pause"]; t4 = t3 + s["t_down"]; t5 = t4 + s["t_follow"]
        el0 = np.deg2rad(20.0)
        if t < t2:
            b = _smooth((t - t1) / s["t_back"])
            sh = s["q_back"] * b; el = el0 + (s["elbow_back"] - el0) * b; wr = s["wrist_cock"] * b; yaw = s["yaw_back"] * b
        elif t < t3:
            sh, el, wr, yaw = s["q_back"], s["elbow_back"], s["wrist_cock"], s["yaw_back"]
        else:
            # downswing: ease-in so the arm accelerates through the ball (impact near end of t_down)
            u = np.clip((t - t3) / s["t_down"], 0.0, 1.0) ** 1.5 if t < t4 else 1.0
            if t < t4:
                sh = s["q_back"] + (s["q_fin"] - s["q_back"]) * u * 1.0
                el = s["elbow_back"] + (el0 - s["elbow_back"]) * min(u * 1.5, 1.0)
                wr = s["wrist_cock"] * (1 - min(u * 1.5, 1.0)); yaw = s["yaw_back"] + (s["yaw_fin"] - s["yaw_back"]) * u
            else:
                sh, el, wr, yaw = s["q_fin"], el0, 0.0, s["yaw_fin"]
        if self.style is not None:
            t = t + self.style_lead
            # CMU sequencing prior: thorax-yaw and wrist-hinge curve shapes
            if t < t1:
                seg, u = "back", 0.0
            elif t < t2:
                seg, u = "back", (t - t1) / s["t_back"]
            elif t < t3:
                seg, u = "back", 1.0
            elif t < t4:
                seg, u = "down", (t - t3) / s["t_down"]
            else:
                seg, u = "follow", (t - t4) / s["t_follow"]
            yaw = self.yaw_sign * self.yaw_amp * self.style.value("thorax", seg, u)
            wr = self.wrist_sign * self.wrist_amp * self.style.value("wrist", seg, u)
        return np.array([sh, el, wr, yaw])

    def _pd(self):
        d = self.data
        ctrl = np.zeros(self.model.nu)
        for k, n in enumerate(self._jn):
            q, qd = d.qpos[self._qa[n]], d.qvel[self._da[n]]
            i = self._act[n]
            ctrl[i] = (self.kp * (self._tgt[k] - q) - self.kd * qd) / self._gear[i]
        for n in self._hold:
            i = self._act[n]
            jid = self.model.actuator_trnid[i, 0]
            q = d.qpos[self.model.jnt_qposadr[jid]]; qd = d.qvel[self.model.jnt_dofadr[jid]]
            kp, kd = (600.0, 40.0) if n == 'right_shoulder_roll' else (100.0, 10.0)
            ctrl[i] = (kp * (0.0 - q) - kd * qd) / self._gear[i]
        return ctrl

    def _substep_ctrl(self):
        return self._pd()  # PD evaluated at the physics rate (zero-order hold at 50 Hz is unstable)

    def _action_to_ctrl(self, action):
        a = np.clip(np.asarray(action, dtype=float), -1, 1)
        tg = self.targets(self.clock) + self.res_scale * a[:4]
        tg[3] *= self.hand_sign  # chest yaw is a vertical-axis rotation: mirrored for left-handers
        self._tgt = tg
        self.clock += 0.02 * (1.0 + 0.3 * a[4])
        self.phase = float(min(1.0, self.clock / self.T))
        return self._pd()

    def _phase_value(self):
        return float(min(1.0, self.clock / self.T))

    def set_rung(self, v):
        """club-speed ladder: gate opens linearly(smoothstep) between v-15 and v m/s."""
        self.gate_hi = float(v); self.gate_lo = float(v) - 15.0

    def _seq_stats(self):
        """Kinematic-sequence features from per-step |angular speed| of thorax (chest yaw), arm (shoulder pitch), club body.
        Pelvis has no DOF in this model so it is not scored. Reference (Cheetham 2008 via docs/research_data_sources.md):
        peak order pelvis<thorax<arm<club, thorax/arm lead ~68/65 ms before the club peak; ratios club/arm ~2.3."""
        if len(self._seq) < 5:
            return {}
        a = np.array(self._seq)  # columns: t, thorax, arm, club
        i0 = int(np.argmax(a[:, 2]))  # restrict to window ending at the club peak
        ic = int(np.argmax(a[:, 3])); ia = int(np.argmax(a[:, 2])); it = int(np.argmax(a[:, 1]))
        t = a[:, 0]
        return {"seq_order_arm_before_club": bool(t[ia] <= t[ic]), "seq_order_thorax_before_arm": bool(t[it] <= t[ia]),
                "arm_lead_ms": float((t[ic] - t[ia]) * 1000), "thorax_lead_ms": float((t[ic] - t[it]) * 1000),
                "club_over_arm_peak_ratio": float(a[ic, 3] / max(a[ia, 2], 1e-6)),
                "peak_club_angvel_degs": float(np.degrees(a[ic, 3]))}

    def _compute_reward(self):
        # speed-gated, carry-driven reward (contact bonus only pays for a real strike)
        r = 0.003 * min(self._club_speed(), 60.0)
        if self.true_contact and not getattr(self, "_paid_contact", False):
            self._paid_contact = True
            r += 1.0 + 5.0 * self._gate()
        if self.true_contact:
            if self._contact_step is None:
                self._contact_step = self.episode_steps
            r += 0.02 * self._gate() * min(float(np.linalg.norm(self._ball_lin_vel())), 60.0)
            if self.episode_steps - self._contact_step == 3:  # launch quality shortly after separation: ~15 deg elevation, on-target azimuth
                v = self._ball_lin_vel(); sp = float(np.linalg.norm(v))
                if sp > 5.0:
                    elev = np.arctan2(v[2], np.hypot(v[0], v[1])); az = np.arctan2(v[1], max(v[0], 1e-6))
                    r += self._gate() * (2.0 * np.exp(-((elev - 0.26) ** 2) / 0.04) + 2.0 * np.exp(-(az ** 2) / 0.01))
        return float(r)

    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        self.clock = 0.0
        self.phase = 0.0
        self._contact_step = None
        self._seq = []
        return obs, info

    def step(self, action):
        obs, r, term, trunc, info = super().step(action)
        info["phase"] = self.phase
        d = self.data
        self._seq.append([self.clock, abs(d.qvel[self._da["chest_yaw"]]), abs(d.qvel[self._da["right_shoulder_pitch"]]),
                          float(np.linalg.norm(d.cvel[self._club_body_id][:3]))])
        if self.true_contact and (self._landed or (self.episode_steps > 10 and np.linalg.norm(self._ball_lin_vel()) < 0.2)):
            term = True
        if (not self.true_contact) and self.clock > self.T + 0.3:
            term = True
        if term or trunc:
            g = self._gate()
            st = self._seq_stats()
            info.update(st)
            if self.seq_weight > 0 and st and self.true_contact:
                # sequencing bonus (gated on a real strike): thorax peaks before arm, arm before club, arm lead near 65 ms (+-30)
                ok = 0.5 * st["seq_order_thorax_before_arm"] + 0.5 * st["seq_order_arm_before_club"]
                lead = np.exp(-((st["arm_lead_ms"] - 65.0) ** 2) / (2 * 30.0 ** 2))
                r += self.seq_weight * g * (ok + lead)
            if self.true_contact:
                r += g * min(self.carry, 150.0) / 5.0 - 0.2 * min(abs(self.ball_lateral), 20.0)
                if not self._landed:
                    r -= 1.0
            else:
                r -= 2.0
        return obs, r, term, trunc, info

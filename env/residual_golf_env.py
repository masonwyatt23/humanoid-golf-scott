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
from pathlib import Path
import mujoco
from gymnasium import spaces
from env.humanoid_golf_env import HumanoidGolfEnv

DEFAULT_SCRIPT = dict(q_back=2.0, elbow_back=0.5, t_hold=0.10, t_back=0.55, t_pause=0.05, t_down=0.22,
                      q_fin=-1.2, t_follow=0.25, wrist_cock=0.0, yaw_back=0.0, yaw_fin=0.0,
                      yaw_ff=0.0, wr_rel_start=0.0, wr_rel_end=0.667, wr_end=0.0, el_end=None)  # wrist release window (fraction of downswing), wrist angle after release, elbow at end of downswing (None = 20 deg)


def _smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


class ResidualGolfEnv(HumanoidGolfEnv):
    def __init__(self, script=None, residual_scale=(0.4, 0.4, 0.4, 0.25), kp=700.0, kd=40.0, grip=False, force_scale=1.0, style_prior=False, yaw_amp=0.6, wrist_amp=0.8, yaw_sign=1.0, wrist_sign=1.0, style_lead=0.0, seq_weight=0.0, flight_steps=450, lat_weight=0.2, elev_weight=0.0, az_weight=2.0, carry_cap=150.0, lat_angular=False, elev_low_mult=1.0, analytic_ball=False, elev_target_deg=12.5, style_ref=None, style_weight=0.0, **kw):
        kw.setdefault("pin_torso", True)
        kw.setdefault("address_pose", "fixed")
        kw.setdefault("model_xml", "humanoid_golf_v3.xml")
        super().__init__(**kw)
        self.script = dict(DEFAULT_SCRIPT, **(script or {}))
        s = self.script
        self.T = s["t_hold"] + s["t_back"] + s["t_pause"] + s["t_down"] + s["t_follow"]
        self.swing_steps = int(np.ceil(self.T / 0.02))
        self.max_steps = self.swing_steps + flight_steps  # extra time for the ball to fly and land (episode ends earlier on landing)
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
        self.seq_weight = seq_weight
        self._club_body_id = int(self.model.geom_bodyid[self._club_geom])
        self._seq = []
        self._contact_step = None
        self.grip = grip
        self.carry_cap = carry_cap
        self.elev_low_mult = elev_low_mult  # penalty multiplier when launch is BELOW the target (kills the flat-launch exploit)
        self.lat_angular = lat_angular  # penalise lateral/carry in percent (angular miss) instead of metres, so short flat shots cannot hide dispersion
        self.lat_weight, self.elev_weight, self.az_weight = lat_weight, elev_weight, az_weight
        self.analytic_ball = analytic_ball  # score carry from analytic flight (drag+Magnus) of the MuJoCo launch vector, end episode 3 steps after contact
        self.elev_target = np.deg2rad(elev_target_deg)
        self._an = None
        self._y_off = 0.0
        self.style_weight = style_weight
        self._qtraj = []
        self._ref_shape = self._load_style_ref(style_ref) if (style_ref and style_weight > 0) else None
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
                el1 = el0 if s["el_end"] is None else s["el_end"]
                el = s["elbow_back"] + (el1 - s["elbow_back"]) * min(u * 1.5, 1.0)
                rr = np.clip((u - s["wr_rel_start"]) / max(s["wr_rel_end"] - s["wr_rel_start"], 1e-3), 0.0, 1.0)
                wr = s["wrist_cock"] + (s["wr_end"] - s["wrist_cock"]) * rr; yaw = s["yaw_back"] + (s["yaw_fin"] - s["yaw_back"]) * u
            else:
                sh, el, wr, yaw = s["q_fin"], (el0 if s["el_end"] is None else s["el_end"]), s["wr_end"], s["yaw_fin"]
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
        if s["yaw_ff"] != 0.0:  # feed-forward face-angle correction from the observed ball y offset (launch azimuth was 0.93-correlated with it)
            yaw = yaw + s["yaw_ff"] * self._y_off * _smooth((t - t1) / s["t_back"])
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

    @staticmethod
    def _resamp(x, n=25):
        x = np.asarray(x, float)
        if len(x) < 3: return np.zeros(n)
        y = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
        r = y.max() - y.min()
        return (y - y.min()) / r if r > 1e-6 else np.zeros(n)

    def _load_style_ref(self, path):
        """Mason reference(s) -> mean normalised trail-shoulder-pitch shapes for backswing (start->top) and downswing (top->impact).
        STYLE ONLY: 2D-proxy angles from single-view video; tempo/speed from the reference are never used.
        path may be a file, a list of files, or "mason_v2_recommended" (native left-handed, recommended, not partial, not mirrored,
        self_owned/commercial_ok, handedness left). v2 files use anatomical columns (right_* = LEAD arm for a lefty) so the trail
        (club) arm is col 4; v1/mirrored files use trail/lead roles (col 0). Ref pitch is 0 hanging, negative going up -> negated."""
        import glob
        if isinstance(path, str) and path == "mason_v2_recommended":
            files = []
            for f in sorted(glob.glob(str(Path(__file__).resolve().parent.parent / "data/references/mason_v2_*.npz"))):
                d = np.load(f, allow_pickle=True)
                if (bool(d["recommended"]) and not bool(d["partial"]) and not bool(d["mirrored"]) and str(d["license_class"]) == "self_owned"
                        and bool(d["commercial_ok"]) and str(d["handedness"]) == "left"):
                    files.append(f)
            path = files
        paths = [path] if isinstance(path, (str, Path)) else list(path)
        bs, ds = [], []
        for f in paths:
            d = np.load(f, allow_pickle=True)
            anat = "joint_convention" in d.files and "anatomical" in str(d["joint_convention"])
            col = -np.asarray(d["joints"][:, 4 if anat else 0], float); t = np.asarray(d["time"], float)
            t0 = float(d["t_start_in_video"]); i_top = int(np.argmin(abs(t - (float(d["t_top"]) - t0)))); i_imp = int(np.argmin(abs(t - (float(d["t_impact"]) - t0))))
            mov = np.where(abs(col - col[0]) > 5.0)[0]; i0 = max(int(mov[0]) - 3, 0) if len(mov) else 0
            bs.append(self._resamp(col[i0:i_top + 1])); ds.append(self._resamp(col[i_top:i_imp + 1]))
        self.style_files = [Path(f).name for f in paths]
        return dict(back=np.mean(bs, 0), down=np.mean(ds, 0), n=len(paths))

    def _style_score(self):
        s = self.script; q = np.array(self._qtraj)  # columns: clock, shoulder pitch
        if len(q) < 10 or self._ref_shape is None: return 0.0
        t_top = s["t_hold"] + s["t_back"] + s["t_pause"]
        b = q[(q[:, 0] >= s["t_hold"]) & (q[:, 0] <= t_top), 1]; dn = q[q[:, 0] >= t_top, 1]
        e = np.mean((self._resamp(b) - self._ref_shape["back"]) ** 2) + np.mean((self._resamp(dn) - self._ref_shape["down"]) ** 2)
        return float(np.exp(-e / 0.1))

    def _lat_pen(self):
        lat = abs(self.ball_lateral)
        if self.lat_angular:
            return min(lat / max(self.carry, 30.0), 0.3) * 100.0
        return min(lat, 20.0)

    def _elev_pen(self):
        v = self._ball_lin_vel() if self._an is None else None
        e = self._an["launch"] if self._an is not None else float(np.degrees(self.launch_elevation))
        dev = e - np.degrees(self.elev_target)
        return min(abs(dev), 40.0) / 10.0 * (self.elev_low_mult if dev < 0 else 1.0)

    def _lockout(self):
        sc = self.script
        return self.clock < sc["t_hold"] + sc["t_back"] + sc["t_pause"] - 0.02

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
            if self._sep_v is not None and not getattr(self, "_launch_paid", False):  # launch quality AT SEPARATION (substep-level), target elevation / on-target azimuth
                self._launch_paid = True
                v = self._sep_v; sp = float(np.linalg.norm(v))
                if sp > 5.0:
                    elev = np.arctan2(v[2], np.hypot(v[0], v[1])); az = np.arctan2(v[1], max(v[0], 1e-6))
                    r += self._gate() * (2.0 * np.exp(-((elev - self.elev_target) ** 2) / 0.04) + self.az_weight * np.exp(-(az ** 2) / (0.01 if self.az_weight <= 2.0 else 0.003)))
        return float(r)

    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        self.clock = 0.0
        self.phase = 0.0
        self._contact_step = None
        self._seq = []
        self._an = None
        self._launch_paid = False
        self._qtraj = []
        self._y_off = float(self.data.qpos[1])
        return obs, info

    def step(self, action):
        obs, r, term, trunc, info = super().step(action)
        info["phase"] = self.phase
        d = self.data
        self._qtraj.append([self.clock, float(d.qpos[self._qa["right_shoulder_pitch"]])])
        self._seq.append([self.clock, abs(d.qvel[self._da["chest_yaw"]]), abs(d.qvel[self._da["right_shoulder_pitch"]]),
                          float(np.linalg.norm(d.cvel[self._club_body_id][:3]))])
        if self.analytic_ball and self.true_contact and self._an is None and self._sep_v is not None:
            from env.ball_flight_analytic import simulate
            v = self._sep_v.copy(); sp = float(np.linalg.norm(v))
            elev = np.degrees(np.arctan2(v[2], np.hypot(v[0], v[1])))
            rpm = float(np.clip(1500.0 + 70.0 * elev, 1000.0, 5000.0))  # ASSUMED backspin from launch elevation (no measured spin)
            w0 = np.array([0.0, -rpm * 2 * np.pi / 60.0, 0.0])
            if sp > 1.0 and v[0] > 0:
                res = simulate([0, 0, 0.07], v, w0, dt=0.005, t_max=12.0)
                c = res["carry"] if res["carry"] is not None else 0.0
                self._an = dict(carry=float(c), lat=float(res["lat_carry"] or 0.0), apex=float(res["apex"]), spin=rpm, launch=float(res["launch"]), hang=float(res["hang"] or 0.0))
            else:
                self._an = dict(carry=0.0, lat=0.0, apex=0.0, spin=rpm, launch=float(elev), hang=0.0)
            self.carry = self._an["carry"]; self.ball_lateral = self._an["lat"]; self._landed = self._an["carry"] > 0
            self.launch_elevation = float(np.radians(elev)); info["launch_elevation"] = self.launch_elevation; info["sep_speed"] = sp; info["carry"] = self.carry; info["ball_lateral"] = self.ball_lateral; info["carry_analytic"] = self.carry; info["apex_analytic"] = self._an["apex"]; info["spin_rpm_assumed"] = rpm
            term = True
        if (not self.analytic_ball) and self.true_contact and (self._landed or (self.episode_steps > 10 and np.linalg.norm(self._ball_lin_vel()) < 0.2)):
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
            if self.true_contact and self._ref_shape is not None:
                sc = self._style_score(); info["style_score"] = sc; r += self.style_weight * g * sc
            if self.true_contact:
                r += g * min(self.carry, self.carry_cap) / 5.0 - self.lat_weight * self._lat_pen() - self.elev_weight * self._elev_pen()
                if not self._landed:
                    r -= 1.0
            else:
                r -= 2.0
        return obs, r, term, trunc, info

"""
MuJoCo humanoid golf environment with imitation support.
"""

import numpy as np
import mujoco
import gymnasium as gym
from gymnasium import spaces
from pathlib import Path
from typing import Optional, Dict


class HumanoidGolfEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array"], "render_fps": 50}

    def __init__(
        self,
        reference_path: Optional[str] = None,
        render_mode: Optional[str] = None,
        target_distance: float = 15.0,
        curriculum: bool = False,
        pin_torso: bool = False,
        address_pose: str = "legacy",
        torque_scale: float = 10.0,
        randomize_reset: bool = False,
        forward_reward: bool = False,
        carry_reward: bool = False,
        ball_damping: float = 0.0,
        action_smoothing: float = 0.0,
        shoulder_range_deg: float = 0.0,
        gate_lo: float = 2.0,
        gate_hi: float = 8.0,
        model_xml: str = "humanoid_golf.xml",
        flight_model: bool = False,
        tee_height: float = 0.0,
        loft_deg: float = None,
        handedness: str = "right",
        ball_x: float = 0.43,
        ball_dz: float = 0.0,
    ):
        """
        curriculum: if True use the staged reward (contact first, ball-flight weight
            ramped 0->1 via set_progress()). False = legacy reward (backwards compatible).
        pin_torso: if True the root/torso is held at a fixed address pose each physics
            step (arm-swing-only task). Default False = original free-floating torso.
        address_pose: "legacy" (original, values are radians-vs-degrees buggy) or
            "fixed" (in-range joint angles, torso lowered so the club sole sits at the ball).
        """
        super().__init__()
        self.render_mode = render_mode
        self.target_distance = target_distance
        self.curriculum = curriculum
        self.pin_torso = pin_torso
        self.ball_x0 = ball_x   # fixed-pose ball x (m)
        self.ball_dz = ball_dz  # extra ball height above the tee-relative default (m): raises ball relative to the club arc
        assert handedness in ("right", "left")
        self.handedness = handedness
        self.hand_sign = 1.0 if handedness == "right" else -1.0  # left-handed = mirror about the x-z plane (y -> -y); see docs/HANDEDNESS.md
        self.tee_height = tee_height  # ball centre raised by this much and held (invisible tee) until first club contact; torso raised equally
        self.flight_model = flight_model  # drag + Magnus on the airborne ball (Cd .26, Cl=min(1.7 S,.3), rho 1.19)
        # carry_reward: ball-flight reward = carry (first landing) + launch elevation + ball speed,
        #   all scaled by a smooth club-speed gate at impact (0 below gate_lo m/s, 1 above gate_hi m/s).
        self.carry_reward = carry_reward
        self.gate_lo, self.gate_hi = gate_lo, gate_hi
        self.action_smoothing = action_smoothing  # ctrl = s*prev_ctrl + (1-s)*new (0 = off)
        self._ctrl_prev = np.zeros(self.model.nu if hasattr(self,'model') else 11)
        self.randomize_reset = randomize_reset  # small ball-x / pose noise on reset (fixed pose only)
        self.forward_reward = forward_reward    # contact-gated forward-direction reward + lateral penalty
        self.torque_scale = torque_scale  # ctrl = action * torque_scale (legacy 10 -> up to 500Nm at shoulder)
        self.address_pose = address_pose
        self.progress = 0.0  # 0..1 training progress, set via set_progress()

        model_path = Path(__file__).parent / "models" / model_xml
        self.model = mujoco.MjModel.from_xml_path(str(model_path))
        self.data = mujoco.MjData(self.model)
        self.substeps = int(round(0.02 / self.model.opt.timestep))  # control dt fixed at 20 ms
        if ball_damping > 0:  # linear+angular drag on the ball's freejoint so rolling does not dominate
            self.model.dof_damping[0:6] = ball_damping
        if shoulder_range_deg > 0:  # limit right shoulder pitch to +-range
            jid = self.model.joint("right_shoulder_pitch").id
            r = np.deg2rad(shoulder_range_deg)
            self.model.jnt_range[jid] = [-r, r]

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(self.model.nu,), dtype=np.float32)

        obs_dim = self.model.nq + self.model.nv + 3 + 3 + 3 + 1
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)

        self.reference = None
        self.ref_idx = 0
        if reference_path:
            self.load_reference(reference_path)

        self.phase = 0.0
        self.contacted = False
        self.episode_steps = 0
        self.max_steps = 200
        self._ball_id = self.model.body("ball").id
        if loft_deg is not None:  # club face loft: rotation of the head box about y (positive = face tilts up)
            a = np.deg2rad(loft_deg)
            self.model.geom_quat[self.model.geom("club_head").id] = [np.cos(a / 2), 0.0, np.sin(a / 2), 0.0]
        self._q_sp = int(self.model.jnt_qposadr[self.model.joint('right_shoulder_pitch').id])
        self._q_el = int(self.model.jnt_qposadr[self.model.joint('right_elbow').id])
        self._club_geom = self.model.geom("club_head").id
        self._ball_geom = self.model.geom("ball_geom").id
        self._club_body = int(self.model.geom_bodyid[self._club_geom])
        self._reset_metrics()

    # ---- curriculum / metrics helpers -------------------------------------
    def set_progress(self, p: float):
        """Training progress in [0,1]; drives the curriculum ball-flight weight."""
        self.progress = float(np.clip(p, 0.0, 1.0))

    def curriculum_weights(self) -> Dict[str, float]:
        """Contact-focused at p=0; ball-flight weight ramps linearly 0->1 over
        progress 0.2..0.8 (contact weight kept, never removed)."""
        ramp = float(np.clip((self.progress - 0.2) / 0.6, 0.0, 1.0))
        return {"contact": 1.0, "imitation": 1.0 - 0.5 * ramp, "ball": ramp}

    def _reset_metrics(self):
        self.true_contact = False
        self.impact_club_speed = 0.0
        self.peak_ball_speed = 0.0
        self.peak_ball_vx = 0.0
        self.peak_club_speed = 0.0   # max club-head speed over the episode (m/s), pre- or post-contact
        self.ball_speed = 0.0          # post-contact peak speed (alias of peak_ball_speed once in contact)
        self.ball_lateral = 0.0        # ball y at episode end/latest (m), + = left of target line
        self.launch_direction = 0.0    # azimuth of peak-speed ball velocity, atan2(vy,vx) rad (0 = on target line)
        self.launch_elevation = 0.0
        self._best_v = 0.0
        self._prev_club_speed = 0.0
        self._carry_paid = False
        self.carry_gate = 0.0
        self.max_ball_x = 0.0
        self.carry = 0.0
        self._airborne = False
        self._landed = False
        self._flew = False

    def _check_contact(self) -> bool:
        d = self.data
        for i in range(d.ncon):
            g1, g2 = d.contact[i].geom1, d.contact[i].geom2
            if {g1, g2} == {self._club_geom, self._ball_geom}:
                return True
        return False

    def _apply_aero(self):
        d = self.data
        d.xfrc_applied[self._ball_id, :] = 0.0
        v = d.qvel[0:3]
        sp = float(np.linalg.norm(v))
        if sp < 0.5 or d.xpos[self._ball_id][2] < 0.03:
            return
        rho, r = 1.19, 0.02135
        A = np.pi * r * r
        w = d.cvel[self._ball_id][:3]  # angular velocity
        S = float(np.linalg.norm(w)) * r / sp
        cl = min(1.7 * S, 0.30)
        q = 0.5 * rho * A * sp
        f = -0.26 * q * v
        wn = np.linalg.norm(w)
        if wn > 1e-6:
            f = f + cl * q * np.cross(w / wn, v)
        d.xfrc_applied[self._ball_id, :3] = f

    def _ground_contact(self) -> bool:
        d = self.data; g = self.model.geom("ground").id
        for i in range(d.ncon):
            if {d.contact[i].geom1, d.contact[i].geom2} == {g, self._ball_geom}:
                return True
        return False

    def _club_speed(self) -> float:
        v = np.zeros(6)
        mujoco.mj_objectVelocity(self.model, self.data, mujoco.mjtObj.mjOBJ_GEOM,
                                 self._club_geom, v, 0)
        return float(np.linalg.norm(v[3:]))

    def _ball_lin_vel(self) -> np.ndarray:
        # ball has the first freejoint: qvel[0:3] is linear velocity (world frame).
        # NOTE: data.cvel rows are [angular, linear]; cvel[3:6] is linear (MuJoCo: cvel = [rot:lin]).
        return self.data.qvel[0:3].copy()

    def load_reference(self, path: str):
        data = np.load(path)
        self.reference = {
            "joints": data["joints"],
            "club_head": data["club_head"] if "club_head" in data.files else None,  # CMU mocap has no club target
            "dt": float(data["dt"]) if "dt" in data else 0.01,
        }

    def _get_obs(self) -> np.ndarray:
        qpos = self.data.qpos.copy()
        qvel = self.data.qvel.copy()

        ball_pos = self.data.xpos[self.model.body("ball").id]
        ball_vel = self.data.cvel[self.model.body("ball").id][3:6]

        club_id = self.model.geom("club_head").id
        club_pos = self.data.geom_xpos[club_id]

        obs = np.concatenate([
            qpos,
            qvel,
            ball_pos,
            ball_vel,
            club_pos,
            [self.phase],
        ]).astype(np.float32)
        return obs

    def _compute_reward_curriculum(self) -> float:
        w = self.curriculum_weights()
        ball_pos = self.data.xpos[self._ball_id]
        ball_v = self._ball_lin_vel()
        club_pos = self.data.geom_xpos[self._club_geom]
        dist = np.linalg.norm(club_pos - ball_pos)
        r = 0.0
        # contact-focused terms (always on)
        r += w["contact"] * 1.5 * np.exp(-dist * 3.0)
        if dist < 0.2:
            r += w["contact"] * 3.0 * (1.0 - dist / 0.2)
        if self.true_contact and not getattr(self, "_paid_contact", False):
            self._paid_contact = True
            r += w["contact"] * 10.0
        # imitation (radians now; reference is stored in degrees)
        if self.reference is not None and self.ref_idx < len(self.reference["joints"]):
            tj = np.deg2rad(self.reference["joints"][self.ref_idx])
            cj = self.data.qpos[14:14 + len(tj)]
            r += w["imitation"] * 2.0 * np.exp(-np.mean((cj - tj) ** 2) / 0.5)
        # ball-flight terms (ramped): only after real contact; per-step, bounded
        if self.true_contact and not self.carry_reward:
            speed = np.linalg.norm(ball_v)
            fwd = max(0.0, ball_v[0])
            launch = np.arctan2(max(ball_v[2], 0.0), max(abs(ball_v[0]), 1e-6))
            r += w["ball"] * (0.15 * min(speed, 30.0)            # ball speed
                              + 0.15 * min(fwd, 30.0)            # forward speed
                              + 0.5 * min(self.max_ball_x, 30.0) / 30.0 * 5   # distance
                              + 0.5 * np.exp(-((launch - 0.3) ** 2) / 0.1))   # ~17deg launch
            # peak post-contact ball speed along the target (+x) direction, gated on contact
            r += w["ball"] * 0.5 * min(max(self.peak_ball_vx, 0.0), 30.0)
            # small penalty (once, at the end of the episode) for contact with a weak strike
        if self.carry_reward:
            r += self._carry_terms(w)
        if self.forward_reward and self.true_contact:
            bv = self._ball_lin_vel()
            sp = float(np.linalg.norm(bv[:2]))
            direction_cos = bv[0] / (sp + 1e-6)          # 1 = straight down target line
            r += 0.3 * min(max(bv[0], 0.0), 30.0) * max(direction_cos, 0.0)
            r -= 0.5 * min(abs(self.data.xpos[self._ball_id][1]), 5.0)   # lateral deviation penalty
            r -= 0.3 * min(sp, 30.0) * max(0.0, 1.0 - direction_cos)     # off-line speed
        if self.true_contact and self.episode_steps >= self.max_steps and self.peak_ball_vx < 3.0:
            r -= 2.0 * max(w["ball"], 0.25)
        if self.data.xpos[self.model.body("torso").id][2] < 0.5 and not self.pin_torso:
            r -= 10.0
        return float(r)

    def _gate(self) -> float:
        x = np.clip((self.impact_club_speed - self.gate_lo) / (self.gate_hi - self.gate_lo), 0.0, 1.0)
        return float(x * x * (3 - 2 * x))  # smoothstep

    def _carry_terms(self, w) -> float:
        ramp = 0.3 + 0.7 * w["ball"]          # never fully off: contact-first, flight weight grows
        club_pos = self.data.geom_xpos[self._club_geom]
        ball_pos = self.data.xpos[self._ball_id]
        r = 0.0
        # dense pre-contact signal: club speed when near the ball (gives gradient toward a fast swing)
        if not self.true_contact and np.linalg.norm(club_pos - ball_pos) < 0.35:
            r += ramp * 0.05 * min(self._club_speed(), 15.0)
        if self.true_contact:
            g = self._gate()
            self.carry_gate = g
            bv = self._ball_lin_vel()
            r += ramp * g * 0.1 * min(float(np.linalg.norm(bv)), 40.0)               # ball speed
            if self._airborne and not self._landed:
                r += ramp * g * 0.1 * min(max(bv[2], 0.0), 15.0)                      # vz while airborne
            elev = self.launch_elevation
            r += ramp * g * 0.2 * np.exp(-((elev - 0.35) ** 2) / 0.08) * (self.ball_speed > 1.0)  # ~20deg launch
            if self._landed and not self._carry_paid:
                self._carry_paid = True
                r += ramp * g * 3.0 * min(self.carry, 60.0)                           # first-landing carry
        return float(r)

    def _compute_reward(self) -> float:
        if self.curriculum:
            return self._compute_reward_curriculum()
        reward = 0.0

        if self.reference is not None and self.ref_idx < len(self.reference["joints"]):
            target_joints = self.reference["joints"][self.ref_idx]
            current_joints = self.data.qpos[14:14+len(target_joints)]
            joint_err = np.mean((current_joints - target_joints) ** 2)
            reward += 2.0 * np.exp(-joint_err / 200.0)

            if self.reference.get("club_head") is not None:
                target_club = self.reference["club_head"][self.ref_idx]
                club_id = self.model.geom("club_head").id
                current_club = self.data.geom_xpos[club_id]
                club_err = np.sum((current_club - target_club) ** 2)
                reward += 1.5 * np.exp(-club_err / 0.5)

        ball_pos = self.data.xpos[self.model.body("ball").id]
        ball_vel = self.data.cvel[self.model.body("ball").id][3:6]

        club_id = self.model.geom("club_head").id
        club_pos = self.data.geom_xpos[club_id]
        club_ball_dist = np.linalg.norm(club_pos - ball_pos)
        reward += 1.5 * np.exp(-club_ball_dist * 3.0)

        if club_ball_dist < 0.2:
            reward += 3.0 * (1.0 - club_ball_dist / 0.2)

        if not self.contacted and np.linalg.norm(ball_vel) > 0.5:
            self.contacted = True
            reward += 10.0

        dist_to_target = abs(ball_pos[0] - self.target_distance)
        reward += 0.1 * max(0, 20 - dist_to_target)

        if ball_vel[0] > 0:
            reward += 0.05 * ball_vel[0]

        torso_height = self.data.xpos[self.model.body("torso").id][2]
        if torso_height < 0.5:
            reward -= 10.0

        return reward

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)

        self.data.qpos[0] = 0.35
        self.data.qpos[1] = 0.0
        self.data.qpos[2] = 0.021 + self.tee_height + self.ball_dz
        self.data.qpos[3] = 1.0

        self.data.qpos[7] = 0.0
        self.data.qpos[8] = 0.0
        self.data.qpos[9] = 1.05
        self.data.qpos[10] = 1.0

        if self.address_pose == "fixed":
            self.data.qpos[9] = 0.86 + self.tee_height   # torso lowered so club-head centre is ~2cm above ground (was 0.10m: club passed OVER the ball)
            self.data.qpos[0] = self.ball_x0   # ball ahead of club head (head front edge ~0.38) so address is not interpenetrating
            self.data.qpos[self._q_sp] = 0.0                  # shoulder pitch (rad)
            self.data.qpos[self._q_el] = np.deg2rad(20.0)     # elbow (rad)
        else:
            # legacy: values are interpreted as RADIANS by MuJoCo (-10 rad, 60 rad)
            # and are far outside the joint ranges.
            self.data.qpos[14] = -10.0
            self.data.qpos[16] = 60.0
        if self.randomize_reset:
            self.data.qpos[0] += self.np_random.uniform(-0.03, 0.03)      # ball x
            self.data.qpos[1] += self.hand_sign * self.np_random.uniform(-0.02, 0.02)      # ball y (mirrored for left-handers)
            self.data.qpos[self._q_sp] += self.np_random.uniform(-0.05, 0.05)     # shoulder pitch (rad)
            self.data.qpos[self._q_el] += self.np_random.uniform(-0.1, 0.1)       # elbow (rad)
        self._ctrl_prev = np.zeros(self.model.nu if hasattr(self,'model') else 11)
        self._ball_z0 = 0.021 + self.tee_height + self.ball_dz
        self._place_left_arm()
        self._root_pin = self.data.qpos[7:14].copy()

        mujoco.mj_forward(self.model, self.data)

        self.phase = 0.0
        self.ref_idx = 0
        self.contacted = False
        self._paid_contact = False
        self._reset_metrics()
        self.episode_steps = 0

        return self._get_obs(), {}

    def _place_left_arm(self):
        """v3 two-handed grip: put the passive left arm where its hand meets the right wrist (once, cached)."""
        m, d = self.model, self.data
        try:
            lp, le = m.joint('left_shoulder_pitch'), m.joint('left_elbow')
        except KeyError:
            return
        if not hasattr(self, '_left_ik'):
            mujoco.mj_forward(m, d)
            tgt = d.xpos[m.body('right_wrist').id].copy()
            hb = m.body('left_hand').id
            qa, qe = int(m.jnt_qposadr[lp.id]), int(m.jnt_qposadr[le.id])
            best = (1e9, 0.0, 0.0)
            for a in np.linspace(-1.2, 1.2, 97):
                for b in np.linspace(0.0, 2.0, 81):
                    d.qpos[qa], d.qpos[qe] = a, b
                    mujoco.mj_kinematics(m, d)
                    err = np.linalg.norm(d.xpos[hb] - tgt)
                    if err < best[0]:
                        best = (err, a, b)
            self._left_ik = best
            d.qpos[qa], d.qpos[qe] = 0.0, 0.0
        err, a, b = self._left_ik
        d.qpos[int(m.jnt_qposadr[lp.id])] = a
        d.qpos[int(m.jnt_qposadr[le.id])] = b
        mujoco.mj_forward(m, d)

    def _substep_ctrl(self):
        return None  # hook: subclasses may recompute ctrl every physics substep (PD at sim rate)

    def _phase_value(self):
        return min(1.0, self.episode_steps / self.max_steps)

    def _action_to_ctrl(self, action):
        return np.clip(action, -1, 1) * self.torque_scale

    def step(self, action):
        ctrl = self._action_to_ctrl(action)
        if self.action_smoothing > 0:
            ctrl = self.action_smoothing * self._ctrl_prev + (1 - self.action_smoothing) * ctrl
        self._ctrl_prev = ctrl.copy()
        self.data.ctrl[:] = ctrl

        for _ in range(self.substeps):
            if self.flight_model:
                self._apply_aero()
            if self.tee_height > 0 and not self.true_contact:
                self.data.qpos[2] = self._ball_z0; self.data.qvel[0:6] = 0.0
            sc = self._substep_ctrl()
            if sc is not None:
                self.data.ctrl[:] = sc
            if self.pin_torso:
                self.data.qpos[7:14] = self._root_pin
                self.data.qvel[6:12] = 0.0
            mujoco.mj_step(self.model, self.data)
            self.peak_club_speed = max(self.peak_club_speed, self._club_speed())
            if not self.true_contact:
                cs_now = self._club_speed()
                if self._check_contact():
                    self.true_contact = True
                    # speed just before/at first contact (post-contact speed is already reduced)
                    self.impact_club_speed = max(self._prev_club_speed, cs_now)
                self._prev_club_speed = cs_now
        bp = self.data.xpos[self._ball_id]
        self.max_ball_x = max(self.max_ball_x, float(bp[0]))
        self.peak_ball_speed = max(self.peak_ball_speed, float(np.linalg.norm(self._ball_lin_vel())))
        self.ball_lateral = float(bp[1])
        bv = self._ball_lin_vel()
        if self.true_contact and np.linalg.norm(bv) > self._best_v:
            self._best_v = float(np.linalg.norm(bv))
            self.ball_speed = self._best_v
            self.launch_direction = float(np.arctan2(bv[1], max(abs(bv[0]), 1e-6) * np.sign(bv[0] if bv[0] != 0 else 1)))
            self.launch_elevation = float(np.arctan2(bv[2], np.hypot(bv[0], bv[1]) + 1e-9))
        if self.true_contact:
            self.peak_ball_vx = max(self.peak_ball_vx, float(self._ball_lin_vel()[0]))
            if bp[2] > 0.06:
                self._airborne = True
            if self.tee_height > 0 and bp[2] > 0.10:
                self._flew = True  # tee mode: only shots that get >10 cm high count as flights
            if self.tee_height > 0 and getattr(self, "_flew", False) and not self._landed and self._ground_contact():
                self._landed = True
                self.carry = float(bp[0])  # tee mode: first ground touch after the strike
            if self.tee_height <= 0 and self._airborne and not self._landed and bp[2] < 0.03:
                self._landed = True
                self.carry = float(bp[0])

        if np.any(np.isnan(self.data.qpos)) or np.any(np.isinf(self.data.qpos)):
            return self._get_obs(), -100.0, True, False, {"ball_distance": 0.0, "contacted": False, "phase": self.phase}

        self.episode_steps += 1
        self.phase = self._phase_value()
        if self.reference is not None:
            self.ref_idx = min(len(self.reference["joints"]) - 1, self.episode_steps)

        obs = self._get_obs()
        reward = self._compute_reward()

        torso_height = self.data.xpos[self.model.body("torso").id][2]
        terminated = (torso_height < 0.4 and not self.pin_torso) or self.episode_steps >= self.max_steps
        truncated = False

        info = {
            "ball_distance": float(self.data.xpos[self.model.body("ball").id][0]),
            "contacted": self.contacted,          # legacy heuristic (see README/notes: unreliable)
            "true_contact": self.true_contact,    # club_head<->ball geom contact
            "max_ball_x": self.max_ball_x,
            "carry": self.carry if self._landed else 0.0,
            "airborne": self._airborne,
            "impact_club_speed": self.impact_club_speed,
            "peak_ball_speed": self.peak_ball_speed,
            "ball_speed": self.ball_speed,
            "ball_lateral": self.ball_lateral * self.hand_sign,   # golfer frame: sign flipped for left-handers
            "launch_direction": self.launch_direction * self.hand_sign,
            "launch_elevation": self.launch_elevation,
            "carry_gate": self.carry_gate,
            "peak_club_speed": self.peak_club_speed,
            "phase": self.phase,
        }

        return obs, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            renderer = mujoco.Renderer(self.model, height=480, width=640)
            renderer.update_scene(self.data)
            return renderer.render()
        return None

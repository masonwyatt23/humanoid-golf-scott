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
        self.torque_scale = torque_scale  # ctrl = action * torque_scale (legacy 10 -> up to 500Nm at shoulder)
        self.address_pose = address_pose
        self.progress = 0.0  # 0..1 training progress, set via set_progress()

        model_path = Path(__file__).parent / "models" / "humanoid_golf.xml"
        self.model = mujoco.MjModel.from_xml_path(str(model_path))
        self.data = mujoco.MjData(self.model)

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(11,), dtype=np.float32)

        obs_dim = 25 + 23 + 3 + 3 + 3 + 1
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
        self.max_ball_x = 0.0
        self.carry = 0.0
        self._airborne = False
        self._landed = False

    def _check_contact(self) -> bool:
        d = self.data
        for i in range(d.ncon):
            g1, g2 = d.contact[i].geom1, d.contact[i].geom2
            if {g1, g2} == {self._club_geom, self._ball_geom}:
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
            "club_head": data["club_head"],
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
        if self.true_contact:
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
        if self.true_contact and self.episode_steps >= self.max_steps and self.peak_ball_vx < 3.0:
            r -= 2.0 * max(w["ball"], 0.25)
        if self.data.xpos[self.model.body("torso").id][2] < 0.5 and not self.pin_torso:
            r -= 10.0
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
        self.data.qpos[2] = 0.021
        self.data.qpos[3] = 1.0

        self.data.qpos[7] = 0.0
        self.data.qpos[8] = 0.0
        self.data.qpos[9] = 1.05
        self.data.qpos[10] = 1.0

        if self.address_pose == "fixed":
            self.data.qpos[9] = 0.88   # torso lowered so club-head centre is ~2cm above ground (was 0.10m: club passed OVER the ball)
            self.data.qpos[0] = 0.45   # ball ahead of club head (head front edge ~0.38) so address is not interpenetrating
            self.data.qpos[14] = 0.0                  # shoulder pitch (rad)
            self.data.qpos[16] = np.deg2rad(20.0)     # elbow (rad)
        else:
            # legacy: values are interpreted as RADIANS by MuJoCo (-10 rad, 60 rad)
            # and are far outside the joint ranges.
            self.data.qpos[14] = -10.0
            self.data.qpos[16] = 60.0
        self._root_pin = self.data.qpos[7:14].copy()

        mujoco.mj_forward(self.model, self.data)

        self.phase = 0.0
        self.ref_idx = 0
        self.contacted = False
        self._paid_contact = False
        self._reset_metrics()
        self.episode_steps = 0

        return self._get_obs(), {}

    def step(self, action):
        self.data.ctrl[:] = np.clip(action, -1, 1) * self.torque_scale

        for _ in range(10):
            if self.pin_torso:
                self.data.qpos[7:14] = self._root_pin
                self.data.qvel[6:12] = 0.0
            mujoco.mj_step(self.model, self.data)
            if not self.true_contact and self._check_contact():
                self.true_contact = True
                self.impact_club_speed = self._club_speed()
        bp = self.data.xpos[self._ball_id]
        self.max_ball_x = max(self.max_ball_x, float(bp[0]))
        self.peak_ball_speed = max(self.peak_ball_speed, float(np.linalg.norm(self._ball_lin_vel())))
        if self.true_contact:
            self.peak_ball_vx = max(self.peak_ball_vx, float(self._ball_lin_vel()[0]))
            if bp[2] > 0.06:
                self._airborne = True
            if self._airborne and not self._landed and bp[2] < 0.03:
                self._landed = True
                self.carry = float(bp[0])

        if np.any(np.isnan(self.data.qpos)) or np.any(np.isinf(self.data.qpos)):
            return self._get_obs(), -100.0, True, False, {"ball_distance": 0.0, "contacted": False, "phase": self.phase}

        self.episode_steps += 1
        self.phase = min(1.0, self.episode_steps / self.max_steps)
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
            "phase": self.phase,
        }

        return obs, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            renderer = mujoco.Renderer(self.model, height=480, width=640)
            renderer.update_scene(self.data)
            return renderer.render()
        return None

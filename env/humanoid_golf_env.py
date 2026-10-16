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
    ):
        super().__init__()
        self.render_mode = render_mode
        self.target_distance = target_distance

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
        ball_vel = self.data.cvel[self.model.body("ball").id][3:6]  # linear velocity

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

    def _compute_reward(self) -> float:
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
        ball_vel = self.data.cvel[self.model.body("ball").id][3:6]  # linear velocity

        club_id = self.model.geom("club_head").id
        club_pos = self.data.geom_xpos[club_id]
        club_ball_dist = np.linalg.norm(club_pos - ball_pos)
        reward += 2.5 * np.exp(-club_ball_dist * 4.0)

        if club_ball_dist < 0.25:
            reward += 4.0 * (1.0 - club_ball_dist / 0.25)

        if not self.contacted and np.linalg.norm(ball_vel) > 0.3:
            self.contacted = True
            reward += 15.0

        if self.contacted and ball_vel[0] > 1.0:
            reward += 0.5 * ball_vel[0]

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

        self.data.qpos[14] = -10.0
        self.data.qpos[16] = 60.0

        mujoco.mj_forward(self.model, self.data)

        self.phase = 0.0
        self.ref_idx = 0
        self.contacted = False
        self.episode_steps = 0

        return self._get_obs(), {}

    def step(self, action):
        self.data.ctrl[:] = np.clip(action, -1, 1) * 10.0

        for _ in range(10):
            mujoco.mj_step(self.model, self.data)

        if np.any(np.isnan(self.data.qpos)) or np.any(np.isinf(self.data.qpos)):
            return self._get_obs(), -100.0, True, False, {"ball_distance": 0.0, "contacted": False, "phase": self.phase}

        self.episode_steps += 1
        self.phase = min(1.0, self.episode_steps / self.max_steps)
        if self.reference is not None:
            self.ref_idx = min(len(self.reference["joints"]) - 1, self.episode_steps)

        obs = self._get_obs()
        reward = self._compute_reward()

        torso_height = self.data.xpos[self.model.body("torso").id][2]
        terminated = torso_height < 0.4 or self.episode_steps >= self.max_steps
        truncated = False

        info = {
            "ball_distance": float(self.data.xpos[self.model.body("ball").id][0]),
            "contacted": self.contacted,
            "phase": self.phase,
        }

        return obs, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            renderer = mujoco.Renderer(self.model, height=480, width=640)
            renderer.update_scene(self.data)
            return renderer.render()
        return None

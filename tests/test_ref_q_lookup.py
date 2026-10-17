import numpy as np
import pytest
from eval.env_factory import JOINT_NAMES, joint_qpos_idx


def _env():
    pytest.importorskip("mujoco")
    from env.humanoid_golf_env import HumanoidGolfEnv
    e = HumanoidGolfEnv(); e.reset(seed=0); return e


def test_ref_q_matches_name_lookup_not_just_slice():
    e = _env(); qi = joint_qpos_idx(e)
    e.data.qpos[qi] = np.arange(11) * 0.01 + 0.1
    assert np.allclose(e._ref_q(11), np.arange(11) * 0.01 + 0.1)


def test_ref_joints_same_order_as_env_factory():
    assert list(_env().REF_JOINTS)[:11] == list(JOINT_NAMES)[:11]


def test_rollout_uses_ref_q_not_positional_slice():
    import inspect, eval.evaluate as ev
    src = inspect.getsource(ev.rollout)
    assert "_ref_q" in src and "qpos[14:25]" not in src

"""Evaluate a saved residual policy (or scripted-only) for 100 randomized episodes. python -m eval.eval_residual <model.zip|scripted> [flags]"""
import sys, json, numpy as np
from stable_baselines3 import PPO
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
if __name__ == "__main__":
    path = sys.argv[1]; kw = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    base = dict(script=dict(q_back=2.2, t_down=0.12, t_back=0.6), flight_model=True, tee_height=0.04, force_scale=2.0, kp=700.0, kd=700.0/30,
                loft_deg=6.0, randomize_reset=True, curriculum=True, carry_reward=True, forward_reward=True, residual_scale=(0.2,0.2,0.2,0.1))
    base.update(kw); mk = lambda: ResidualGolfEnv(**base)
    if path == "scripted": pol = lambda o: np.zeros(5)
    else:
        m = PPO.load(path); pol = lambda o: m.predict(o, deterministic=True)[0]
    print(json.dumps(run_eval(pol, mk, 100)))

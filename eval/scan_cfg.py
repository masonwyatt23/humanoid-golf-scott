"""Parallel scan of scripted (zero-residual) configs. python -m eval.scan_cfg '<json grid>' [episodes] [seed0]
grid = {"script.t_down":[..], "loft_deg":[..], "ball_x":[..], ...}; keys prefixed script. go into the script dict. Prints metrics (analytic, separation-velocity launch)."""
import sys, json, itertools, numpy as np
from multiprocessing import Pool
BASE = dict(script=dict(q_back=2.2, t_down=0.095, t_back=0.6), flight_model=True, tee_height=0.04, force_scale=2.0, kp=700.0, kd=700.0/30, loft_deg=9.0,
            randomize_reset=True, curriculum=True, carry_reward=True, forward_reward=True, residual_scale=(0.1, 0.08, 0.05, 0.05), ball_dz=0.008,
            analytic_ball=True, handedness="left", ball_x=0.39, ball_x_noise=0.003)
def run(args):
    cfg, n, seed0 = args
    from env.residual_golf_env import ResidualGolfEnv
    from train.train_residual import run_eval
    kw = json.loads(json.dumps(BASE)); kw["script"] = dict(BASE["script"])
    for k, v in cfg.items():
        if k.startswith("script."): kw["script"][k[7:]] = v
        else: kw[k] = v
    kw["residual_scale"] = tuple(kw["residual_scale"])
    r = run_eval(lambda o: np.zeros(5), lambda: ResidualGolfEnv(**kw), n, seed0=seed0)
    return cfg, {k: round(r[k], 2) for k in ["true_contact_rate", "mean_carry", "lateral_mean", "lateral_std", "mean_launch_elev_deg", "median_smash", "peak_club_speed_mean_mph"]}
if __name__ == "__main__":
    grid = json.loads(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 30; s0 = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    keys = list(grid); cfgs = [dict(zip(keys, v)) for v in itertools.product(*[grid[k] for k in keys])]
    with Pool(6) as p:
        for cfg, m in p.imap(run, [(c, n, s0) for c in cfgs]):
            print(json.dumps(cfg), json.dumps(m), flush=True)

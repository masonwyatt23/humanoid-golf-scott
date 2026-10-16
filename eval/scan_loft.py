import sys, json, numpy as np, time
from env.residual_golf_env import ResidualGolfEnv
from train.train_residual import run_eval
for L in [6,10,14,18,22]:
    kw = dict(script=dict(q_back=2.2, t_down=0.12, t_back=0.6), flight_model=True, tee_height=0.04, force_scale=2.0, kp=700.0, kd=700.0/30, loft_deg=float(L),
          randomize_reset=True, curriculum=True, carry_reward=True, forward_reward=True, residual_scale=(0.2,0.2,0.2,0.1), ball_dz=0.008, analytic_ball=True)
    t=time.time(); r=run_eval(lambda o: np.zeros(5), lambda: ResidualGolfEnv(**kw), 40)
    print(L,{k:round(r[k],2) for k in ['true_contact_rate','landed_fraction','mean_carry','max_carry','mean_carry_given_landed','lateral_mean','lateral_std','mean_impact_club_speed','mean_ball_speed','mean_launch_elev_deg']},round(time.time()-t),'s',flush=True)

"""Diagnose launch/landing for scripted (zero-residual) swing: launch vector, club vel at contact, why episodes end."""
import sys, json, numpy as np, mujoco
from env.residual_golf_env import ResidualGolfEnv
kw = dict(script=dict(q_back=2.2, t_down=0.12, t_back=0.6), flight_model=True, tee_height=0.04, force_scale=2.0, kp=700.0, kd=700.0/30,
          loft_deg=6.0, randomize_reset=True, curriculum=True, carry_reward=True, forward_reward=True, residual_scale=(0.2,0.2,0.2,0.1), ball_dz=0.008)
kw.update(json.loads(sys.argv[1]) if len(sys.argv) > 1 else {})
env = ResidualGolfEnv(**kw); rows = []
for ep in range(int(sys.argv[2]) if len(sys.argv) > 2 else 30):
    env.reset(seed=5000+ep); env.set_progress(1.0); done=False; rec=None; n=0
    while not done:
        _,_,done,tr,info = env.step(np.zeros(5)); done = done or tr; n+=1
        if env.true_contact and rec is None: rec = dict(step=n); rec['hv']=None
        if rec is not None and env._contact_step is not None and env.episode_steps-env._contact_step==3:
            v=env._ball_lin_vel(); rec['v']=v.copy()
            gid=env._club_geom; vel=np.zeros(6); mujoco.mj_objectVelocity(env.model,env.data,mujoco.mjtObj.mjOBJ_GEOM,gid,vel,0); rec['hv']=vel[3:].copy()
            rec['hz']=float(env.data.geom_xpos[gid][2]); rec['bz']=float(env.data.xpos[env.model.body("ball").id][2])
    bp=env.data.xpos[env.model.body("ball").id].copy()
    rows.append(dict(rec=rec,steps=n,carry=info['carry'],landed=env._landed,maxx=info['max_ball_x'],bpos=bp,elev=info['launch_elevation'],impact=info['impact_club_speed']))
for r in rows[:12]:
    rc=r['rec']; v=rc.get('v') if rc else None
    print('steps',r['steps'],'landed',r['landed'],'carry',round(r['carry'],1),'maxx',round(r['maxx'],1),'end',r['bpos'].round(2),'imp',round(r['impact'],1),
          'launch v',None if v is None else v.round(1),'elev',round(np.degrees(r['elev']),1),'head v',None if rc is None or rc.get('hv') is None else rc['hv'].round(1),'dz(head-ball)',None if rc is None or 'hz' not in rc else round(rc['hz']-rc['bz'],3))

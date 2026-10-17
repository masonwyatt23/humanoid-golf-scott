"""Diagnostic: ball speed / launch / backspin at club-ball separation, det policy, 6 episodes (seeds 4000-4005) for a few models. python -m eval.measure_sep_spin (needs models/). Output results/ball_spin_measured.json (tiny N, diagnostic only)."""
import sys, json, numpy as np
sys.path.insert(0,'.')
from pathlib import Path
from stable_baselines3 import PPO
from eval.env_factory import make_env
import eval.leaderboard as L
RES=Path('results')
out={}
for name in ('imit16_fs1_dart_s51','imit15_dart_s52','imit9_w000_s51','imit18_power_dart_s51','ppo_v4power48_s71'):
    steps,kw,src=L.config_for([name]); env=make_env(kw); model=PPO.load(f'models/{name}',device='cpu')
    R=[]
    for ep in range(6):
        obs,_=env.reset(seed=4000+ep); done=False; got=None
        while not done:
            a=model.predict(obs,deterministic=True)[0]; obs,_,te,tr,info=env.step(a); done=te or tr
            if got is None and getattr(env,'_sep_v',None) is not None:
                d=env.data; w=d.xmat[env._ball_id].reshape(3,3)@d.qvel[env._ball_dof+3:env._ball_dof+6]
                v=np.array(env._sep_v); R.append((float(np.linalg.norm(v)),float(np.degrees(np.arctan2(v[2],np.hypot(v[0],v[1])))),float(-w[1]*60/(2*np.pi)),float(w[2]*60/(2*np.pi)),float(np.linalg.norm(w)*60/(2*np.pi)))); got=1
    R=np.array(R); out[name]=dict(n=len(R),ball_mps=R[:,0].mean(),launch=R[:,1].mean(),backspin_rpm=R[:,2].mean(),sidespin_rpm_mean_abs=np.abs(R[:,3]).mean(),spin_total=R[:,4].mean())
    print(name,{k:round(float(v),1) for k,v in out[name].items()},flush=True)
json.dump(out,open('results/ball_spin_measured.json','w'),indent=1,default=float)

import sys,json,numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
cfg=json.load(open("configs/fast_scripted_v4_power_hypothetical.json")); cfg.pop("description",None); cfg.pop("hypothetical",None); kw=dict(B0); kw.update(cfg); kw["script"]=dict(B0["script"],**cfg["script"])
env=make_env(kw); u=env.unwrapped if hasattr(env,'unwrapped') else env
seed=int(sys.argv[1]); sh=json.load(open(f"results/shots_v4power_{seed}.json")); rows=[]
for i in range(100):
    env.reset(seed=seed+i); q=env.data.qpos
    rows.append((i,q[0]-env.ball_x0,q[1],q[env._q_sp],q[env._q_el],sh[i]['final_y'],sh[i]['total_dist'],sh[i]['launch_elev_deg']))
R=np.array(rows)
print("cols: ep dx y sp el final_y dist launch")
bad=(abs(R[:,5])>8)|(R[:,6]<200)
for r in R[bad]: print(np.round(r,4))
print("normal ranges dx",R[~bad,1].min(),R[~bad,1].max(),"sp",R[~bad,3].min(),R[~bad,3].max(),"el",R[~bad,4].min(),R[~bad,4].max())
# correlation of dist with sp and el
for k,n in ((1,'dx'),(3,'sp'),(4,'el')): print(n,np.corrcoef(R[:,k],R[:,6])[0,1].round(2))
print("el-bin: n, mean dist, n(dist<200), n(|y|>8)")
for lo in np.arange(0.24,0.46,0.02):
    m=(R[:,4]>=lo)&(R[:,4]<lo+0.02)
    if m.sum(): print(round(lo,2),m.sum(),R[m,6].mean().round(0),(R[m,6]<200).sum(),(abs(R[m,5])>8).sum())

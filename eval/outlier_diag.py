"""Which reset perturbations cause low-launch outliers? python -m eval.outlier_diag '{overrides}' [n] [seed0]"""
import sys, json, numpy as np
from eval.scan_cfg import BASE
from env.residual_golf_env import ResidualGolfEnv
cfg=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}; n=int(sys.argv[2]) if len(sys.argv)>2 else 100; s0=int(sys.argv[3]) if len(sys.argv)>3 else 5000
kw=json.loads(json.dumps(BASE)); kw["script"]=dict(BASE["script"]); kw.update(dict(loft_deg=-26,ball_dz=-0.01,sh_noise=0.05,el_noise=0.1))
for k,v in cfg.items():
    if k.startswith("script."): kw["script"][k[7:]]=v
    else: kw[k]=v
kw["residual_scale"]=tuple(kw["residual_scale"]); env=ResidualGolfEnv(**kw); R=[]
for i in range(n):
    env.reset(seed=s0+i); env.set_progress(1.0)
    d=env.data; x=d.qpos[0]-0; p=(d.qpos[0],d.qpos[1],d.qpos[env._q_sp],d.qpos[env._q_el])
    done=False
    while not done: _,_,done,t,info=env.step(np.zeros(5)); done=done or t
    R.append(list(p)+[np.degrees(info["launch_elevation"]),info["carry"]])
R=np.array(R); el=R[:,4]; out=el<7
print("n",n,"outliers(<7deg)",out.sum(),"median",np.median(el))
for j,nm in enumerate(["ball_x","ball_y","sh","el"]):
    print(nm,"corr w/ elev %.2f"%np.corrcoef(R[:,j],el)[0,1],"outlier mean %.4f vs rest %.4f"%(R[out,j].mean() if out.any() else 0,R[~out,j].mean()))

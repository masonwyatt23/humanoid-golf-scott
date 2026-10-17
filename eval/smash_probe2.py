"""v4 contact calibration probe (opt-in contact_damp/ball_friction). python -m eval.smash_probe2 '{"contact_damp":0.22,...}' [eps]
Reports smash (ball peak speed / impact club speed), backspin rpm ~10 ms after separation (|omega|), launch elev, carry, lateral, mph."""
import sys, json, numpy as np
from eval.scan_cfg import BASE
from env.residual_golf_env import ResidualGolfEnv
cfg=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}; n=int(sys.argv[2]) if len(sys.argv)>2 else 20
kw=json.loads(json.dumps(BASE)); kw["script"]=dict(BASE["script"]); kw["script"]["yaw_ff"]=0.0
kw.update(loft_deg=-31,ball_dz=-0.008,sh_noise=0.05,el_noise=0.1,analytic_ball=False,flight_model=True)
for k,v in cfg.items():
    if k.startswith("script."): kw["script"][k[7:]]=v
    else: kw[k]=v
kw["residual_scale"]=tuple(kw["residual_scale"]); e=ResidualGolfEnv(**kw); m=e.model
bj=m.body(m.geom_bodyid[e._ball_geom]).jntadr[0]; va=m.jnt_dofadr[bj]; R=[]
for i in range(n):
    e.reset(seed=5000+i); e.set_progress(1.0); d=False; sp=None; k0=None
    while not d:
        _,_,d,t,info=e.step(np.zeros(5)); d=d or t
        if e._sep_v is not None and k0 is None: k0=e.episode_steps
        if k0 is not None and e.episode_steps==k0+2 and sp is None: sp=np.linalg.norm(e.data.qvel[va+3:va+6])*60/(2*np.pi)
    if info["impact_club_speed"]>5: R.append([info["peak_ball_speed"]/info["impact_club_speed"],sp or 0,np.degrees(info["launch_elevation"]),info["carry"],info["ball_lateral"],info["max_ball_x"],info["impact_club_speed"]*2.23694,info["peak_ball_speed"]])
R=np.array(R); f=lambda j:"%.2f"%R[:,j].mean()
print(json.dumps(cfg),"smash",f(0),"(std %.2f)"%R[:,0].std(),"spin_rpm",f(1),"(std %.0f)"%R[:,1].std(),"launch",f(2),"carry",f(3),"total",f(5),"lat_std %.2f"%R[:,4].std(),"club_mph",f(6),"ball m/s",f(7))

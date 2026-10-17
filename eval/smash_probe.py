"""Smash-factor probe: ball speed / club speed at impact vs contact damping ratio (solref[1]) of ball+head geoms. Diagnostic only; does not change env files."""
import sys, json, numpy as np
from eval.scan_cfg import BASE
from env.residual_golf_env import ResidualGolfEnv
kw=json.loads(json.dumps(BASE)); kw["script"]=dict(BASE["script"]); kw["script"]["yaw_ff"]=0.0
kw.update(loft_deg=-31,ball_dz=-0.008,sh_noise=0.05,el_noise=0.1,analytic_ball=False,flight_model=True); kw["residual_scale"]=tuple(kw["residual_scale"])
e=ResidualGolfEnv(**kw); m=e.model
print("masses: head",m.geom_mass[e._club_geom] if hasattr(m,'geom_mass') else None,"ball",m.body_mass[m.geom_bodyid[e._ball_geom]],"club body",m.body_mass[e._club_body])
for damp in [1.0,0.5,0.3,0.15]:
    for g in (e._club_geom,e._ball_geom): m.geom_solref[g]=[0.002,damp]
    sm=[];bs=[]
    for i in range(10):
        e.reset(seed=5000+i); e.set_progress(1.0); d=False
        while not d: _,_,d,t,info=e.step(np.zeros(5)); d=d or t
        if info["impact_club_speed"]>5: sm.append(info["peak_ball_speed"]/info["impact_club_speed"]); bs.append(info["peak_ball_speed"])
    print("dampratio",damp,"smash %.2f"%np.mean(sm),"ball speed %.1f m/s"%np.mean(bs))

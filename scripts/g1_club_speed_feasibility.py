"""Torque+speed-limited upper bound for G1 club-head speed (simple random-search bang-bang, zero gravity,
pelvis on a vertical yaw hinge standing in for both hip-yaw motors). Approximate; see docs/research_real_humanoids.md."""
import sys, numpy as np, mujoco
sys.argv=sys.argv[:1]; sys.path.insert(0,"scripts")
from g1_with_club import build, MENAG
def make():
    spec=mujoco.MjSpec.from_file(f"{MENAG}/unitree_g1/scene.xml")
    return spec
import g1_with_club as g
def build_fixed():
    # same as g.build() but replace freejoint by a yaw hinge on pelvis, gravity off
    spec=mujoco.MjSpec.from_file(f"{MENAG}/unitree_g1/scene.xml")
    pel=spec.body("pelvis")
    for j in pel.joints: spec.delete(j)
    pel.add_joint(name="pelvis_yaw",type=mujoco.mjtJoint.mjJNT_HINGE,axis=[0,0,1],range=[-1.2,1.2],limited=True)
    rw=spec.body("right_wrist_yaw_link")
    c=rw.add_body(name="club",pos=[0.10,0,0])
    c.add_geom(name="shaft",type=mujoco.mjtGeom.mjGEOM_CAPSULE,fromto=[0,0,0.20-g.CLUB_LEN,0,0,0.20],size=[0.008,0,0],mass=g.SHAFT_M,contype=0,conaffinity=0)
    c.add_geom(name="head",type=mujoco.mjtGeom.mjGEOM_BOX,pos=[0.03,0,0.20-g.CLUB_LEN],size=[0.05,0.05,0.02],mass=g.HEAD_M,contype=0,conaffinity=0)
    c.add_site(name="clubhead",pos=[0.03,0,0.20-g.CLUB_LEN])
    for k in list(spec.keys): spec.delete(k)
    spec.option.gravity=[0,0,0]
    return spec.compile()
m=build_fixed(); d=mujoco.MjData(m)
m.opt.timestep=0.001; m.actuator_gainprm[:,0]=0; m.actuator_biasprm[:,:]=0
sid=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_SITE,"clubhead")
# (joint, torque limit N m, speed limit rad/s)  -- torque: menagerie actuatorfrcrange (Unitree); speed: unitree_rl_mjlab motor limits
J={"pelvis_yaw":(176,32),"waist_yaw_joint":(88,32),"right_shoulder_pitch_joint":(25,37),"right_shoulder_roll_joint":(25,37),
   "right_shoulder_yaw_joint":(25,37),"right_elbow_joint":(25,37),"right_wrist_roll_joint":(25,37),
   "right_wrist_pitch_joint":(5,22),"right_wrist_yaw_joint":(5,22)}
ids={n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n) for n in J}
qa={n:m.jnt_qposadr[i] for n,i in ids.items()}; da={n:m.jnt_dofadr[i] for n,i in ids.items()}
rngs={n:m.jnt_range[i] for n,i in ids.items()}
def run(p,ts,tq=1.0,sp=1.0,T=0.45):
    d.qpos[:]=m.qpos0; d.qvel[:]=0; d.qfrc_applied[:]=0
    for n in J: d.qpos[qa[n]]=p[n][0]
    mujoco.mj_forward(m,d); best=0.0
    for k in range(int(T/m.opt.timestep)):
        t=k*m.opt.timestep; d.qfrc_applied[:]=0
        for n,(tl,vl) in J.items():
            q=d.qpos[qa[n]];qd=d.qvel[da[n]];tgt=p[n][1]
            if t<ts[n]: 
                tau=0.0   # zero gravity: joint waits at backswing pose until onset
            else:
                s=np.sign(tgt-q); tau=s*tl*tq
                if s*qd>0: tau*=max(0.0,1.0-s*qd/(vl*sp))   # linear torque-speed curve: torque -> 0 at rated no-load speed
                # decelerate when about to hit target
                if abs(tgt-q)<0.5*qd*qd/(tl*tq/ max(1e-3,0.5)) and s*qd>0: tau=-s*tl*tq*0.5
            d.qfrc_applied[da[n]]=tau
        mujoco.mj_step(m,d)
        if not np.all(np.isfinite(d.qvel)): return 0.0
        if any(abs(d.qvel[da[n]])>1.25*J[n][1]*sp for n in J): return 0.0   # reject trials violating joint speed limits (coupling)
        v=np.linalg.norm(d.cvel[m.site_bodyid[sid]][3:]+np.cross(d.cvel[m.site_bodyid[sid]][:3],d.site_xpos[sid]-d.subtree_com[m.site_bodyid[sid]]*0)) if False else 0
        vel=np.zeros(6); mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_SITE,sid,vel,0)
        sv=np.linalg.norm(vel[3:])
        if d.site_xpos[sid][2]<0.35 and abs(vel[5])<0.4*sv: best=max(best,sv)   # only count 'usable' speed: head near ground level, mostly horizontal
    return best
def search(tq,sp,n=700,seed=0):
    rng=np.random.default_rng(seed); bestv=0;bestp=None
    def rnd():
        p={};ts={}
        for nme in J:
            lo,hi=rngs[nme]; p[nme]=(rng.uniform(lo,hi),rng.uniform(lo,hi)); ts[nme]=rng.uniform(0,0.2)
        return p,ts
    for i in range(n):
        p,ts=rnd(); v=run(p,ts,tq,sp)
        if v>bestv: bestv,bestp=v,(p,ts)
    # hill-climb
    p,ts=bestp
    for i in range(500):
        p2={k:(np.clip(a+rng.normal(0,.15),*rngs[k]),np.clip(b+rng.normal(0,.15),*rngs[k])) for k,(a,b) in p.items()}
        ts2={k:float(np.clip(t+rng.normal(0,.02),0,.25)) for k,t in ts.items()}
        v=run(p2,ts2,tq,sp)
        if v>bestv: bestv,p,ts=v,p2,ts2
    return bestv
if __name__=="__main__":
    for tq,sp in [(1,1),(2,1),(3,1),(2,1.5),(3,1.5),(4,1.5),(4,2)]:
        print(f"torque x{tq} speed x{sp}: best peak club-head speed {search(tq,sp):.1f} m/s",flush=True)

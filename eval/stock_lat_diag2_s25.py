"""Stage 25: STOCK fs1 scripted: lateral vs start conditions (elbow, shoulder, ball y, strike-height). usage: '{ov}' eps seed"""
import sys, json, numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
from eval.flight_tracker import FlightTracker
cfg = json.load(open("configs/fast_scripted_v3_fs1_elbowfull.json")); cfg.pop("description")
ov = json.loads(sys.argv[1]); kw = dict(B0); kw.update(cfg); kw.update(ov); kw["script"] = {**B0["script"], **cfg["script"], **ov.get("script", {})}
env = make_env(kw); ft = FlightTracker(env).install(); zero = np.zeros(env.action_space.shape, dtype=np.float32); R = []
u = env.unwrapped
for ep in range(int(sys.argv[2])):
    env.reset(seed=int(sys.argv[3]) + ep); ft.reset(); el = float(u.data.qpos[u._q_el]); sp = float(u.data.qpos[u._q_sp]); yo = float(getattr(u, "_y_off", np.nan)); done = False
    while not done:
        _, _, te, tr, info = env.step(zero); ft.step(); done = te or tr
    s = ft.summary(info); R.append((el, sp, yo, s["final_y"], s["launch_elev_deg"], s["impact_club_speed"], s["carry"], s["true_contact"]))
A = np.array(R, float); lat = A[:, 3]
print("lat std", lat.std(), "mean", lat.mean(), "pcts", np.percentile(lat, [0, 5, 25, 50, 75, 95, 100]).round(2))
for i, n in enumerate(["elbow0", "shoulder0", "ball_y", None, "launch", "club", "carry"]):
    if n: print(n, "corr w lat", round(float(np.corrcoef(A[:, i], lat)[0, 1]), 3))
print("mean lat by elbow tercile", [round(float(lat[(A[:, 0] >= a) & (A[:, 0] <= b)].mean()), 2) for a, b in zip(np.percentile(A[:, 0], [0, 33, 67]), np.percentile(A[:, 0], [33, 67, 100]))])
print("lat std after removing linear fit on elbow+shoulder+ball_y:", float(np.std(lat - np.c_[A[:, [0, 1, 2]], np.ones(len(A))] @ np.linalg.lstsq(np.c_[A[:, [0, 1, 2]], np.ones(len(A))], lat, rcond=None)[0])))
o = np.argsort(-np.abs(lat))[:6]
print("outliers (elbow0, sh0, ball_y, lat, launch, club, carry):"); print(A[o][:, :7].round(3))
print("median-ish (|lat|<0.5) elbow range", A[np.abs(lat) < 0.5][:, 0].min().round(3), A[np.abs(lat) < 0.5][:, 0].max().round(3), "ball_y range", A[np.abs(lat) < 0.5][:, 2].min().round(4), A[np.abs(lat) < 0.5][:, 2].max().round(4))
idx = np.argsort(A[:, 2]); print("ball_y -> lat (sorted):"); print(" ".join(f"{A[i,2]*1000:.0f}:{A[i,3]:.1f}" for i in idx))

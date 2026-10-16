"""Per-shot distribution for a scripted config JSON (analytic, separation-velocity launch). python -m eval.shot_dist configs/x.json [episodes] [seed0] ['{overrides}']"""
import sys, json, numpy as np
from env.residual_golf_env import ResidualGolfEnv
cfg = json.load(open(sys.argv[1])); cfg.pop("description", None)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 100; s0 = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
if len(sys.argv) > 4:
    ov = json.loads(sys.argv[4]); sc = ov.pop("script", {}); cfg["script"].update(sc); cfg.update(ov)
cfg["residual_scale"] = tuple(cfg["residual_scale"]); env = ResidualGolfEnv(**cfg); rows = []
for i in range(n):
    env.reset(seed=s0 + i); env.set_progress(1.0); d = False
    while not d: _, _, d, t, info = env.step(np.zeros(5)); d = d or t
    rows.append([np.degrees(info["launch_elevation"]), info["carry"], info["ball_lateral"], info["impact_club_speed"], env.data.qpos[0], env.data.qpos[1]])
a = np.array(rows); el, ca, la = a[:, 0], a[:, 1], a[:, 2]
print("n", n, "elev pct (5,25,50,75,95):", np.percentile(el, [5, 25, 50, 75, 95]).round(1), "frac elev<3:", round((el < 3).mean(), 2), "frac elev in [5,20]:", round(((el >= 5) & (el <= 20)).mean(), 2), "frac >25:", round((el > 25).mean(), 2))
print("carry mean", ca.mean().round(1), "median", np.median(ca).round(1), "frac>=30:", round((ca >= 30).mean(), 2), "| lat mean", la.mean().round(2), "std", la.std().round(2), "| lat std within elev 5-20:", la[(el >= 5) & (el <= 20)].std().round(2) if ((el >= 5) & (el <= 20)).sum() > 3 else None, "| MAD*1.48", round(1.4826*np.median(abs(la-np.median(la))),2), "| impact mph", (a[:, 3].mean()*2.23694).round(1))

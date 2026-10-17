"""Effect of opt-in script wr_lead on achieved-vs-commanded wrist at impact (scripted, zero residual, masonmapped config, force_scale 2 BOOSTED).
Impact step = first step with true_contact. usage: python -m eval.wr_lead_test [n]"""
import json, sys, numpy as np
from pathlib import Path
from env.residual_golf_env import ResidualGolfEnv
ROOT = Path(__file__).resolve().parent.parent
cfg = json.load(open(ROOT / "configs/fast_scripted_v3_masonmapped.json")); cfg.pop("description", None)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 30; res = {}
for lead in (0.0, 0.03, 0.06, 0.09):
    sc = dict(cfg["script"]); sc["wr_lead"] = lead
    kw = {k: cfg[k] for k in cfg if k != "script"}; kw["script"] = sc; kw["flight_model"] = True
    env = ResidualGolfEnv(**kw); rows = []
    for ep in range(n):
        env.reset(seed=4000 + ep); env.set_progress(1.0); done = False; imp = None; k = 0
        while not done:
            _, _, done, t, info = env.step(np.zeros(5, np.float32)); done = done or t; k += 1
            if imp is None and info.get("true_contact"):
                j = env._jn.index("right_wrist"); imp = (float(env._tgt[j]), float(env.data.qpos[env._qa["right_wrist"]]))
        rows.append(dict(cmd=imp[0] if imp else np.nan, ach=imp[1] if imp else np.nan, contact=float(info["true_contact"]), carry=float(info["carry"]), club=float(info["peak_club_speed"]) * 2.23694, lat=float(info["ball_lateral"])))
    g = lambda k: np.array([r[k] for r in rows], float)
    res[str(lead)] = dict(contact=g("contact").mean(), cmd_wrist_at_impact=float(np.nanmean(g("cmd"))), achieved_wrist_at_impact=float(np.nanmean(g("ach"))),
        lag_err_rad=float(np.nanmean(g("ach") - g("cmd"))), abs_err_rad=float(np.nanmean(abs(g("ach") - g("cmd")))), carry=g("carry").mean(), club_mph=g("club").mean())
    print(lead, res[str(lead)], flush=True)
json.dump(res, open(ROOT / "results/wr_lead_test.json", "w"), indent=2)

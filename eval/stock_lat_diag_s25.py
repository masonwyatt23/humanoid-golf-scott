"""Stage 25: STOCK fs1 q_back 2.3 scripted: what drives lateral? per-shot correlations. usage: stock_lat_diag_s25 '{ov}' eps seed"""
import sys, json, numpy as np
import eval.dispersion_report as dr
from eval.eval_scripted_cfg import base as B0
cfg = json.load(open("configs/fast_scripted_v3_fs1_elbowfull.json")); cfg.pop("description")
ov = json.loads(sys.argv[1]); kw = dict(B0); kw.update(cfg); kw.update(ov); kw["script"] = {**B0["script"], **cfg["script"], **ov.get("script", {})}
dr.REFS = []; d, shots = dr.run("x", kw, int(sys.argv[2]), int(sys.argv[3]), True, scripted=True)
print(sorted(shots[0].keys()))
lat = np.array([s["final_y"] if "final_y" in s else s.get("lateral", np.nan) for s in shots]); print("lat std", lat.std())
for k in shots[0]:
    try:
        v = np.array([float(s[k]) for s in shots])
        if v.std() > 0 and np.isfinite(v).all(): print(k, round(float(np.corrcoef(v, lat)[0, 1]), 3), round(v.std(), 4))
    except Exception: pass

"""Evaluator-protocol eval of a scripted config file with overrides, compact print. python -m eval.eval_v4 configs/x.json '{overrides}' eps seed [tag]"""
import sys, json, math
import eval.dispersion_report as dr
from eval.eval_scripted_cfg import base as BASE0
cfgf, ov, n, seed = sys.argv[1], json.loads(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
cfg = json.load(open(cfgf)); cfg.pop("description", None); cfg.pop("hypothetical", None)
kw = dict(BASE0); kw.update(cfg); kw.update(ov)
if "script" in cfg: kw["script"] = {**BASE0["script"], **cfg["script"], **ov.get("script", {})}
dr.REFS = []
d, shots = dr.run("x", kw, n, seed, True, scripted=True)
keys = ['launch_elev_mean_deg','launch_elev_std_deg','launch_flat_frac','contact_rate','mean_carry','mean_distance','landed_fraction','lateral_std','peak_club_mph_mean']
out = {k: (None if isinstance(d[k], float) and not math.isfinite(d[k]) else round(float(d[k]), 2)) for k in keys}
print("RESULT", sys.argv[5] if len(sys.argv) > 5 else "", seed, json.dumps(out), flush=True)

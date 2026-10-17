"""Stage19 task4: is lateral std just the ball_y start noise? corr(start y, final lateral) and std(lateral - start_y). python -m eval.lat_probe cfg.json [n] [json-overrides]"""
import sys, json, numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
cfg = json.load(open(sys.argv[1])); cfg.pop("description", None); cfg.pop("hypothetical", None)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 40; ov = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
kw = dict(B0); kw.update(cfg); kw.update(ov); kw["script"] = {**B0["script"], **cfg.get("script", {})}
env = make_env(kw); Y = []; L = []
for i in range(n):
    env.reset(seed=4000 + i); y0 = float(env.data.qpos[1]) * env.hand_sign; d = False
    while not d: _, _, te, tr, info = env.step(np.zeros(5, np.float32)); d = te or tr
    Y.append(y0); L.append(info["ball_lateral"])
Y, L = np.array(Y), np.array(L)
print(sys.argv[1], ov, "n=%d std(y0)=%.4f std(lat)=%.4f corr=%.2f std(lat-y0)=%.4f mean(lat-y0)=%.4f  ball_y_noise=%s" % (n, Y.std(), L.std(), np.corrcoef(Y, L)[0, 1], (L - Y).std(), (L - Y).mean(), kw.get("ball_y_noise")))

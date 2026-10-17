"""Grid over script params at v3 (fs2, elbow_base 0.48): contact/launch/lat + trail-arm key_score (key_arm=trail, both wrist signs) and lead-arm key_score.  python -m eval.mason_grid '<json list of script overrides>' [eps] [extra-kw-json]"""
import sys, json, numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
cfg = json.load(open("configs/fast_scripted_v3_elbow48.json")); cfg.pop("description", None); cfg.pop("hypothetical", None)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 20; extra = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
for ov in json.loads(sys.argv[1]):
    res = []
    for arm, ws in (("trail_mapped", 1.0), ("trail", 1.0)):
        kw = dict(B0); kw.update(cfg); kw["script"] = {**B0["script"], **cfg["script"], **ov}; kw.update(extra); kw.update(key_weight=1.0, key_arm=arm, key_wrist_sign=ws, track_set=None)
        env = make_env(kw); R = []
        for i in range(n):
            env.reset(seed=4000 + i); d = False
            while not d: _, _, te, tr, info = env.step(np.zeros(5, np.float32)); d = te or tr
            R.append([info.get("key_score", 0), np.degrees(info["launch_elevation"]) if info["true_contact"] else np.nan, info["ball_lateral"], info["carry"], float(info["true_contact"]), info["peak_club_speed"] * 2.23694])
        R = np.array(R); res.append(R)
    a, b = res
    print(json.dumps(ov), "| key(trail_mapped) %.2f key(raw trail) %.2f | contact %.2f launch %.1f carry %.0f lat_sd %.2f mph %.0f" % (a[:, 0].mean(), b[:, 0].mean(), a[:, 4].mean(), np.nanmean(a[:, 1]), a[:, 3].mean(), np.nanstd(a[:, 2]), a[:, 5].mean()), flush=True)

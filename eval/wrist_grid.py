"""Grid over script wrist params at elbow_base 0.48 (v3): launch/lat/dist + track/key scores (track_time_fix). python -m eval.wrist_grid '<json list of script-override dicts>' [eps]"""
import sys, json, numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
cfg = json.load(open("configs/fast_scripted_v3_elbow48.json")); cfg.pop("description", None); cfg.pop("hypothetical", None)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
for ov in json.loads(sys.argv[1]):
    kw = dict(B0); kw.update(cfg); kw["script"] = {**B0["script"], **cfg["script"], **ov}; kw.update(track_set="unified_v1", track_weight=1.0, track_time_fix=True, key_weight=1.0)
    env = make_env(kw); R = []
    for i in range(n):
        env.reset(seed=4000 + i); d = False
        while not d: _, _, te, tr, info = env.step(np.zeros(5, np.float32)); d = te or tr
        p = info.get("track_parts", {}); R.append([info.get("track_score", 0), info.get("key_score", 0), p.get("wr", 0), np.degrees(info["launch_elevation"]), info["ball_lateral"], info["carry"], float(info["true_contact"]), info["peak_club_speed"] * 2.23694])
    R = np.array(R); print(json.dumps(ov), "track %.3f key %.3f wr %.3f | launch %.1f (sd %.1f) lat_sd %.2f carry %.0f contact %.2f mph %.0f" % (R[:, 0].mean(), R[:, 1].mean(), R[:, 2].mean(), R[:, 3].mean(), R[:, 3].std(), R[:, 4].std(), R[:, 5].mean(), R[:, 6].mean(), R[:, 7].mean()), flush=True)

"""Stage21 random search: trail-elbow 1.126/0.853 (+/-), mapped wrist top -0.6; find true contact with launch>=10. python -m eval.wrist_search N seed"""
import sys, json, numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
cfg = json.load(open("configs/fast_scripted_v3_elbow48.json")); cfg.pop("description", None); cfg.pop("hypothetical", None)
FIX = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
N = int(sys.argv[1]); rng = np.random.default_rng(int(sys.argv[2])); best = []
for k in range(N):
    ov = {"el_end": 0.853, "elbow_back": 1.126, "wrist_cock": -0.6, "q_fin": float(rng.uniform(-0.75, -0.2)), "wr_end": float(rng.uniform(-0.55, 0.1)),
          "t_down": float(rng.choice([0.07, 0.09, 0.12])), "wr_lead": float(rng.choice([0, 0.03])), "wr_rel_start": float(rng.choice([0.3, 0.6]))}
    ov.update(FIX)
    ex = {"ball_dz": float(rng.choice([0.0, 0.02, 0.04])), "loft_deg": float(rng.choice([-31, -45]))}
    for kk in ("ball_dz", "loft_deg"):
        if kk in ov: ex[kk] = ov.pop(kk)
    kw = dict(B0); kw.update(cfg); kw["script"] = {**B0["script"], **cfg["script"], **ov}; kw.update(ex); kw.update(key_weight=1.0, key_arm="trail_mapped", track_set=None)
    env = make_env(kw); R = []
    for i in range(4):
        env.reset(seed=4000 + i); d = False
        while not d: _, _, te, tr, info = env.step(np.zeros(5, np.float32)); d = te or tr
        R.append([float(info["true_contact"]), np.degrees(info["launch_elevation"]) if info["true_contact"] else np.nan, info["carry"], info.get("key_score", 0)])
    R = np.array(R); c = R[:, 0].mean(); la = np.nanmean(R[:, 1]) if c > 0 else np.nan
    print(json.dumps({**ov, **ex}), "contact %.2f launch %.1f carry %.0f key %.2f" % (c, la, R[:, 2].mean(), R[:, 3].mean()), flush=True)

"""Diagnostic: replay a wrist target (top, impact) as a position command on right_wrist inside the v3/v4 swing; log commanded vs achieved angle and saturated-step fraction.
python -m eval.wrist_replay  (prints a table). Cases: as-stored (cocked negative: top -0.703, impact -0.977), sign-flipped (+0.703,+0.977), current script (top -0.5, impact -0.01)."""
import json, sys, numpy as np
from eval.eval_scripted_cfg import base as B0
from eval.env_factory import make_env
def run(cfgf, ov, top, imp, n=10):
    cfg = json.load(open(cfgf)); cfg.pop("description", None); cfg.pop("hypothetical", None); kw = dict(B0); kw.update(cfg); kw.update(ov); kw["script"] = {**B0["script"], **cfg["script"]}
    env = make_env(kw); s = env.script; orig = env.targets; m = env.model; ai = env._act["right_wrist"]; lim = m.actuator_forcerange[ai, 1]
    t_top = s["t_hold"] + s["t_back"] + s["t_pause"]; t_imp = t_top + s["t_down"]
    def tg(t):
        a = np.array(orig(t), float)
        if t < s["t_hold"]: w = 0.0
        elif t < s["t_hold"] + s["t_back"]: w = top * ((t - s["t_hold"]) / s["t_back"])
        elif t < t_top: w = top
        elif t < t_imp: w = top + (imp - top) * ((t - t_top) / s["t_down"])
        else: w = imp
        a[2] = w; return a
    env.targets = tg; R = []
    for i in range(n):
        env.reset(seed=4000 + i); d = False; cmd = []; ach = []; sat = []; tt = []
        while not d:
            _, _, te, tr, info = env.step(np.zeros(5, np.float32)); d = te or tr
            cmd.append(tg(env.clock)[2]); ach.append(env.data.qpos[env._qa["right_wrist"]]); sat.append(abs(env.data.ctrl[ai]) >= 0.999 * lim); tt.append(env.clock)
            if env.true_contact: break
        tt = np.array(tt); cmd = np.array(cmd); ach = np.array(ach); sat = np.array(sat); dn = (tt >= t_top) & (tt <= t_imp + 0.02); bk = (tt >= s["t_hold"]) & (tt < t_top)
        R.append([ach[bk][-1] if bk.any() else np.nan, ach[-1], np.abs(cmd - ach)[dn].max() if dn.any() else np.nan, sat[bk].mean() if bk.any() else np.nan, sat[dn].mean() if dn.any() else np.nan, float(info["true_contact"]), np.degrees(info["launch_elevation"]) if info["true_contact"] else np.nan, info["peak_club_speed"] * 2.23694])
    R = np.nanmean(np.array(R), 0); return R
rows = []
for name, cfgf, ov in (("v3 fs2", "configs/fast_scripted_v3.json", {}), ("v3 fs1", "configs/fast_scripted_v3.json", {"force_scale": 1.0}), ("v4_power", "configs/fast_scripted_v4_power_hypothetical.json", {})):
    for cn, top, imp in (("current script", -0.5, -0.01), ("as-stored (-0.703,-0.977)", -0.703, -0.977), ("sign-flipped (+0.703,+0.977)", 0.703, 0.977)):
        R = run(cfgf, ov, top, imp); print("%-9s %-28s ach@top %.2f ach@end %.2f max|cmd-ach| downswing %.2f rad | sat frac backswing %.2f downswing %.2f | contact %.2f launch %.1f mph %.0f" % (name, cn, *R[:5], *R[5:7], R[7]), flush=True)

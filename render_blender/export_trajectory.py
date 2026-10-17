"""Export a recorded MuJoCo scripted-v3 swing for Blender: per-sample world pose of every body (+ ball, club head) and the ball flight.
    python -m render_blender.export_trajectory [--seed 4000] [--out render_blender/swing_v3.npz]
REAL: body poses, ball motion and launch are from the MuJoCo sim (zero-residual scripted v3 config, evaluator env). Sampled every 10 substeps (200 Hz).
Ball flight after the episode ends is the analytic drag+Magnus model (env/ball_flight_analytic.py) from the sim's separation velocity; spin is ASSUMED."""
import argparse, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=4000); ap.add_argument("--out", default=str(ROOT / "render_blender/swing_v3.npz"))
    ap.add_argument("--cfg", default=str(ROOT / "configs/fast_scripted_v3.json")); a = ap.parse_args()
    import mujoco
    from eval.eval_scripted_cfg import base
    from eval.env_factory import make_env
    from eval.flight_tracker import FlightTracker
    cfg = json.loads(Path(a.cfg).read_text()); kw = dict(base)
    for k, v in cfg.items():
        if k == "script": kw["script"].update(v) if False else kw.__setitem__("script", {**kw["script"], **v})
        elif k not in ("description",): kw[k] = v
    env = make_env(kw); ft = FlightTracker(env).install()
    m = env.model; rec = {"t": [], "xpos": [], "xquat": [], "ball": []}; n = [0]
    orig = mujoco.mj_step
    def wrapped(mm, d, *args, **k):
        orig(mm, d, *args, **k); n[0] += 1
        if n[0] % 10 == 0:
            rec["t"].append(d.time); rec["xpos"].append(d.xpos.copy()); rec["xquat"].append(d.xquat.copy()); rec["ball"].append(d.xpos[env._ball_id].copy())
    mujoco.mj_step = wrapped   # installed after tracker so tracker's wrapper still runs (wrapped calls it as `orig`)
    try:
        obs, _ = env.reset(seed=a.seed); ft.reset(); n[0] = 0
        for k in rec: rec[k].clear()
        done = False; info = {}; z = np.zeros(env.action_space.shape, np.float32)
        while not done:
            obs, _, te, tr, info = env.step(z); ft.step(); done = te or tr
        s = ft.summary(info)
    finally:
        mujoco.mj_step = orig; ft.close()
    names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(m.nbody)]
    t = np.array(rec["t"]); ball = np.array(rec["ball"])
    # impact time = first sample where ball displaced > 5 mm from its initial position
    disp = np.linalg.norm(ball - ball[0], axis=1); ii = int(np.argmax(disp > 0.005)) if (disp > 0.005).any() else -1
    out = dict(t=t, xpos=np.array(rec["xpos"]), xquat=np.array(rec["xquat"]), ball=ball, body_names=np.array(names), impact_idx=ii,
               club_head_pos=None)
    gid = m.geom("club_head").id
    out["club_head_geom_offset"] = m.geom_pos[gid]; out["club_head_body"] = names[m.geom_bodyid[gid]]
    out["club_shaft_fromto"] = np.array([0, 0, 0, 0, 0, -1.1])
    ex = {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in s.items() if isinstance(v, (int, float, bool, np.floating))}
    sepv = ft.v_sep if ft.v_sep is not None else ft._last_v
    out["v_sep"] = np.array(sepv if sepv is not None else [np.nan] * 3)
    np.savez(a.out, **out)
    Path(a.out).with_suffix(".json").write_text(json.dumps(dict(seed=a.seed, summary=ex, samples=len(t), impact_idx=ii, bodies=names, v_sep=out["v_sep"].tolist()), indent=1))
    print("saved", a.out, len(t), "samples; impact idx", ii, {k: ex.get(k) for k in ("impact_club_speed", "peak_ball_speed", "carry", "launch_elev_deg", "true_contact")})
main()

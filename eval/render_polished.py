"""
Polished showcase video from results/leaderboard.json:  results/videos/showcase_polished.mp4  (+ showcase_polished.json)

    python -m eval.render_polished [--pick best_qualifying] [--swings 12] [--seed 5000] [--K 6]

Slides: title card -> leaderboard (deterministic) -> leaderboard (stochastic) -> segment per model (side-on | down-the-line,
slow motion, live overlay of measured club mph / carry / lateral / launch) -> end card with caveats.

* Trained model: --pick best_qualifying. If NO trained model meets the leaderboard criterion, a clearly labeled FALLBACK PREVIEW of the
  best trained model is rendered (red banner 'DOES NOT YET QUALIFY' + the failing criteria computed from the data). Never a 'good drive'.
* Scripted segments ('SCRIPTED (not learned)'): the zero-residual scripted row with the highest det carry among those satisfying the criterion (all scripted rows still appear on the leaderboard slides); if none does, the
  trainer-config 0.422 scripted baseline is shown, labeled as not qualifying when it fails.
* Qualification is recomputed here from leaderboard.json with the leaderboard's own criterion (qualify_criterion): 100% contact in both
  modes, det mean carry >= carry_m_min, det lateral std <= lateral_std_m_max, det mean launch >= launch_elev_deg_min.
* Every number on slides/banners is read from results/leaderboard.json (all-episode stats, 50 eps) or measured live on the rendered swing.
* Swing selection: tracker pass over N deterministic seeds, lower median by carry among true-contact+landed swings; that seed is rendered and
  the overlay shows what was measured on the RENDERED swing (strikes of learned policies are not bit-reproducible once rendering/instrumentation
  is attached, so the rendered swing can differ from the selection pass; both numbers are in showcase_polished.json).
"""
import argparse, datetime, json, subprocess, sys, os, shutil
from pathlib import Path
import numpy as np
from eval import render_showcase as rs

ROOT, FPS, W, H = rs.ROOT, rs.FPS, 1280, 480


def ensure_gl():
    if os.environ.get("_RS_GL"): return
    r = subprocess.run([sys.executable, "-c", "import mujoco;from env.humanoid_golf_env import HumanoidGolfEnv as E;e=E();mujoco.Renderer(e.model,64,64)"],
                       cwd=ROOT, env={**os.environ, "MUJOCO_GL": "egl"}, capture_output=True)
    if r.returncode == 0:
        os.environ["MUJOCO_GL"] = "egl"; os.environ["_RS_GL"] = "egl"; return
    env = {**os.environ, "MUJOCO_GL": "glfw", "_RS_GL": "glfw"}
    os.execvpe("xvfb-run", ["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", sys.executable, "-m", "eval.render_polished", *sys.argv[1:]], env)


def qualification(m, crit):
    d, s = m["modes"].get("deterministic", {}), m["modes"].get("stochastic", {})
    if not d or not s or "error" in d or "error" in s:
        return False, ["evaluation error"]
    fails = []
    if not (d["contact_rate"] >= 1.0 and s["contact_rate"] >= 1.0): fails.append(f"contact det/stoch {d['contact_rate']*100:.0f}%/{s['contact_rate']*100:.0f}% (need 100% both)")
    if d["mean_carry"] < crit["carry_m_min"]: fails.append(f"det carry {d['mean_carry']:.1f} m < {crit['carry_m_min']:.0f}")
    if d["lateral_std"] > crit["lateral_std_m_max"]: fails.append(f"det lateral std {d['lateral_std']:.2f} m > {crit['lateral_std_m_max']}")
    if not d["launch_elev_mean_deg"] >= crit["launch_elev_deg_min"]: fails.append(f"det launch {d['launch_elev_mean_deg']:.1f} deg < {crit['launch_elev_deg_min']:.0f}")
    return not fails, fails


def card(lines, colors=None, size=0.8):
    import cv2
    img = np.zeros((H, W, 3), np.uint8); img[:] = (12, 16, 24)
    y = 60
    for i, t in enumerate(lines):
        sz, th = (size * 1.6, 3) if i == 0 else (size, 1)
        col = (colors or {}).get(i, (255, 255, 255) if i else (0, 220, 255))
        cv2.putText(img, t, (40, y), cv2.FONT_HERSHEY_SIMPLEX, sz, col, th, cv2.LINE_AA)
        y += int(46 * sz / 0.8) if i else 70
    return img


def table_slide(title, rows, mode, crit, note):
    import cv2
    img = np.zeros((H, W, 3), np.uint8); img[:] = (12, 16, 24)
    cv2.putText(img, title, (20, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 220, 255), 2, cv2.LINE_AA)
    cols = [("model", 20), ("kind", 440), ("contact", 500), ("carry m", 590), ("landed", 680), ("lat std m", 760), ("miss L/R", 860), ("launch deg", 960), ("peak mph", 1070), ("qual.", 1170)]
    for c, x in cols: cv2.putText(img, c, (x, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)
    y = 94
    for name, kind, m, q in rows:
        d = m["modes"][mode]
        disp = (name[name.index("[") + 1:].rstrip("]") if "[" in name else name); vals = [disp[:58], kind, f"{d['contact_rate']*100:.0f}%", f"{d['mean_carry']:.1f}", f"{d['landed_fraction']*100:.0f}%", f"{d['lateral_std']:.2f}",
                f"{d['left_miss_rate']*100:.0f}/{d['right_miss_rate']*100:.0f}%", f"{d['launch_elev_mean_deg']:.1f}" + (" FLAT" if d.get("launch_flat_flag") else ""), f"{d['peak_club_mph_mean']:.1f}", "YES" if q else "no"]
        col = (120, 255, 120) if q else (255, 255, 255)
        for (c, x), v in zip(cols, vals): cv2.putText(img, v, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col if c in ("model", "qual.") else (230, 230, 230), 1, cv2.LINE_AA)
        y += 29
    for i, t in enumerate(note): cv2.putText(img, t, (20, H - 54 + 20 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 120), 1, cv2.LINE_AA)
    return img


def wrap(t, n=105):
    out, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + [cur]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", default="best_qualifying", choices=["best_qualifying", "best", "best_left"])
    ap.add_argument("--swings", type=int, default=12); ap.add_argument("--seed", type=int, default=5000); ap.add_argument("--K", type=int, default=6)
    ap.add_argument("--out", default="results/videos/showcase_polished.mp4")
    a = ap.parse_args(); ensure_gl()
    from stable_baselines3 import PPO
    from eval.env_factory import make_env
    from eval.flight_tracker import FlightTracker
    import cv2
    lb = json.loads((ROOT / "results/leaderboard.json").read_text()); crit = lb["qualify_criterion"]; models = lb["models"]
    by = {m["names"][0]: m for m in models}; label = lambda m: "/".join(m["names"])
    q = {m["names"][0]: qualification(m, crit) for m in models}
    trained = [m for m in models if not m.get("scripted")]; scripted = [m for m in models if m.get("scripted")]
    # --- trained model pick
    pk = {"best_qualifying": lb.get("best_qualifying"), "best": lb.get("best_model"), "best_left": lb.get("best_left")}[a.pick]
    fallback = pk is None
    if fallback: pk = lb["best_model"]
    lm = by[pk[0]]; ok_l, fail_l = q[pk[0]]
    # --- scripted segments: those that qualify; else the 0.422 trainer-cfg baseline (labeled)
    sq = [m for m in scripted if q[m["names"][0]][0]]
    seg_s = [max(sq, key=lambda m: m["modes"]["deterministic"]["mean_carry"])] if sq else [m for m in scripted if "ball_x 0.422" in m["names"][0]][:1]
    when = datetime.date.today().isoformat()
    w = rs.Writer(ROOT / a.out); hold = lambda img, s: [w.write(img) for _ in range(int(s * FPS))]
    meta = dict(date=when, pick=a.pick, fallback_preview=fallback, learned=label(lm), learned_qualifies=ok_l, learned_failed_criteria=fail_l,
                scripted_segments=[label(m) for m in seg_s], scripted_qualify={label(m): q[m["names"][0]] for m in scripted}, criterion=crit,
                leaderboard_env_fingerprint=lb.get("env_fingerprint"), segments=[])
    # title card
    t = ["Humanoid Golf - residual-PPO vs scripted swing", "Left-handed setup (v3 humanoid, MuJoCo)", f"Rendered {when}   |   data: results/leaderboard.json ({lb['episodes']} episodes/mode, seeds {lb['seed_base']}+)"]
    cols = {}
    if fallback:
        t += ["FALLBACK PREVIEW: no trained model meets the showcase criterion", "Learned segment = best trained model, shown for transparency - NOT a good drive"]; cols = {3: (255, 70, 70), 4: (255, 70, 70)}
    hold(card(t, cols, 0.6), 4)
    # leaderboard slides
    rank = [r.split("/")[0] for r in lb["ranking"]][:4]
    rows = [(label(by[n]), "LEARNED", by[n], q[n][0]) for n in rank if n in by]
    rows += [(label(m), "SCRIPTED", m, q[m["names"][0]][0]) for m in scripted]
    if lm["names"][0] not in rank: rows.insert(0, (label(lm), "LEARNED", lm, ok_l))
    crit_txt = f"Criterion: contact 100% both modes, det carry >= {crit['carry_m_min']:.0f} m, det lateral std <= {crit['lateral_std_m_max']} m, launch >= {crit['launch_elev_deg_min']:.0f} deg. Ranking = contact then carry (not distance)."
    n1 = [crit_txt, "Top trained models by leaderboard ranking + all zero-residual SCRIPTED rows (not learned). All-episode means; carry/launch from flight tracker."]
    hold(table_slide(f"Leaderboard - DETERMINISTIC policy ({lb['episodes']} eps)", rows, "deterministic", crit, n1), 7)
    hold(table_slide(f"Leaderboard - STOCHASTIC policy ({lb['episodes']} eps)", rows, "stochastic", crit, n1 + ["Scripted rows are zero-residual (no sampling), so det = stoch."]), 7)
    # segments
    segs = [("LEARNED", lm, ok_l, fail_l)] + [("SCRIPTED (not learned)", m, *q[m["names"][0]]) for m in seg_s]
    for kind, m, okq, fails in segs:
        name = m["names"][0]; d = m["modes"]["deterministic"]; sc = m.get("scripted", False)
        title = f"{kind} ({label(m)})" if kind == "LEARNED" else f"{kind}"
        hold(card([title, f"model: {label(m)}", f"Deterministic, {lb['episodes']} eps: carry {d['mean_carry']:.1f} m mean | lateral std {d['lateral_std']:.2f} m | miss L/R {d['left_miss_rate']*100:.0f}%/{d['right_miss_rate']*100:.0f}%",
                   f"launch {d['launch_elev_mean_deg']:.1f} deg | peak club {d['peak_club_mph_mean']:.1f} mph | landed {d['landed_fraction']*100:.0f}%" + ("   (FLAT launch)" if d.get("launch_flat_flag") else ""),
                   ("QUALIFIES under the criterion" if okq else "DOES NOT YET QUALIFY: " + "; ".join(fails))] + [x for x in wrap("Swing shown: ONE deterministic swing, lower median by carry of %d (seeds %d..); live overlay = that swing's own measurement." % (a.swings, a.seed), 100)],
                  {4: (120, 255, 120) if okq else (255, 70, 70)}, 0.6), 4.5)
        env = make_env(m["env_kwargs"]); pol = rs.ZeroPolicy(env) if sc else PPO.load(str(ROOT / "models" / m["names"][0]))
        res = []
        for i in range(a.swings):
            ft = FlightTracker(env).install()
            try:
                obs, _ = env.reset(seed=a.seed + i); ft.reset(); done = False; info = {}
                while not done:
                    obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); done = te or tr
            finally:
                ft.close()
            res.append((a.seed + i, ft.summary(info)))
        good = sorted([r for r in res if r[1]["true_contact"] and r[1]["carry"] > 0], key=lambda r: r[1]["carry"])
        seed, sh = good[(len(good) - 1) // 2]
        ban = [f"{title}" + ("" if okq else "  -  DOES NOT YET QUALIFY") , f"All-episode (det): carry {d['mean_carry']:.1f} m | lat std {d['lateral_std']:.2f} m | L/R miss {d['left_miss_rate']*100:.0f}/{d['right_miss_rate']*100:.0f}% | launch {d['launch_elev_mean_deg']:.1f} deg | {d['peak_club_mph_mean']:.1f} mph",
               f"This swing: seed {seed}, median-by-carry of {a.swings} (overlay below = this swing only)"]
        if not okq: ban.insert(2, "Fails: " + "; ".join(fails))
        ft = FlightTracker(env).install()
        try:
            rec = rs.Recorder(env, a.K, "", w); rec.banner = ban; rec.ft = ft
            rec.banner_color = (120, 255, 120) if okq else (255, 70, 70)
            if kind != "LEARNED": rec.banner_color = (0, 220, 255) if okq else (255, 170, 60)
            rec.install()
            try:
                obs, _ = env.reset(seed=seed); ft.reset(); done = False; info = {}
                while not done:
                    obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); done = te or tr
            finally:
                rec.uninstall()
            rec.frame(hold=int(3 * FPS)); rec.r.close()
        finally:
            ft.close()
        sw = ft.summary(info)
        meta["segments"].append(dict(kind=kind, model=label(m), qualifies=okq, failed=fails, seed=seed, selection_pass_carry=sh["carry"],
                                     rendered=dict(carry=sw["carry"], lateral_y=sw["final_y"], launch_deg=sw["launch_elev_deg"], peak_club_mph=rec.peak_club * 2.23694, impact_club_mps=sw["impact_club_speed"]),
                                     all_swings=[dict(seed=s_, carry=x["carry"], y=x["final_y"], launch=x["launch_elev_deg"]) for s_, x in res]))
    # end card
    e = ["Caveats", f"- {lb['episodes']} episodes per mode, seeds {lb['seed_base']}+; flight tracker = MuJoCo ball only (no spin / sidespin model), so lateral spread is optimistic.",
         "- Carry is the first-landing distance; launch = ball velocity at club-ball separation; club speed = peak club-head geom speed (validated < 100 m/s).",
         "- 'LEARNED' = PPO policy (+ residual on a scripted swing). 'SCRIPTED (not learned)' = zero residual, no learning. Scripted rows never count as learned.",
         "- Learned strikes are regime-sensitive: one swing is not the average; see the leaderboard slides for all-episode stats. Address-noise outliers exist.",
         "- DTW style scores (leaderboard.md) are 2D-proxy, tempo +-15% indicative only; Mason v3 slow-mo refs are loose-tempo extras."]
    if fallback: e.insert(1, "THIS IS A FALLBACK PREVIEW: no trained model qualifies - the learned segment is not a good drive.")
    hold(card(sum([wrap(x, 108) for x in e], []), {1: (255, 70, 70)} if fallback else {}, 0.55), 8)
    w.close(); meta["frames"] = w.frames; meta["duration_s"] = w.frames / FPS; meta["slowdown"] = rec.slow
    (ROOT / a.out).with_suffix(".json").write_text(json.dumps(meta, indent=1, default=float)); print(json.dumps({k: v for k, v in meta.items() if k != "segments"}, indent=1, default=float))
    for s_ in meta["segments"]: print(s_["kind"], s_["model"], s_["qualifies"], s_["seed"], {k: round(v, 2) for k, v in s_["rendered"].items()})


if __name__ == "__main__":
    main()

"""Power-tier PREVIEW video for ppo_v4power_s61 (NOT the main showcase).  python -m eval.render_power_preview
Output: results/videos/showcase_power_preview.mp4 (+ .json).  Reuses PRec / style_scene / card from render_polished.
Numbers on cards come from results/gate_<name>_seed{4000,8000,9000}.json (eval_gate, 100 eps, flight_steps 900); live overlay = rendered swing.
Segments: (A) representative swing = median-by-carry of N swings from seeds 8000.. ; (B) the seed-9000 lateral outlier (largest |y| of seeds 9000..9099)."""
import argparse, json, datetime
import numpy as np
from eval import render_showcase as rs
from eval import render_polished as rp
from eval.render_polished import ROOT, FPS, card, wrap, PRec, style_scene, actuator_tags


def run_seed(env, pol, seed, FT):
    ft = FT(env).install()
    try:
        obs, _ = env.reset(seed=seed); ft.reset(); done = False; info = {}
        while not done:
            obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); done = te or tr
    finally:
        ft.close()
    return ft.summary(info)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--name", default="ppo_v4power_s61"); ap.add_argument("--swings", type=int, default=12)
    ap.add_argument("--out", default="results/videos/showcase_power_preview.mp4"); a = ap.parse_args(); rp.ensure_gl()
    from stable_baselines3 import PPO
    from eval.env_factory import make_env, joint_qpos_idx
    from eval.flight_tracker import FlightTracker
    G = {s: json.loads((ROOT / f"results/gate_{a.name}_seed{s}.json").read_text()) for s in (4000, 8000, 9000)}
    kw = G[8000]["env_kwargs"]; tags = actuator_tags(kw)
    env = make_env(kw); pol = PPO.load(str(ROOT / "models" / a.name))
    # A: representative swing
    res = [(8000 + i, run_seed(env, pol, 8000 + i, FlightTracker)) for i in range(a.swings)]
    good = sorted([r for r in res if r[1]["true_contact"] and r[1]["carry"] > 0], key=lambda r: r[1]["carry"]); seedA, shA = good[(len(good) - 1) // 2]
    # B: seed-9000 outlier
    sc9 = [(9000 + i, run_seed(env, pol, 9000 + i, FlightTracker)) for i in range(100)]
    seedB, shB = max(sc9, key=lambda r: abs(r[1]["final_y"]))
    n_out = sum(abs(r[1]["final_y"]) > 10 for r in sc9)
    print("A", seedA, shA["carry"], shA["final_y"], "| B", seedB, shB["carry"], shB["final_y"], "n|y|>10 =", n_out, flush=True)
    g = lambda s, m: G[s]["policy_" + m]
    gl = lambda s: f"seed {s}: det carry {g(s,'det')['mean_carry']:.1f} m ({g(s,'det')['mean_carry_yd']:.0f} yd), lat std {g(s,'det')['lateral_std']:.2f} m (stoch {g(s,'stoch')['lateral_std']:.2f}), landed {g(s,'det')['landed_fraction']*100:.0f}%, {g(s,'det')['peak_club_mph_mean']:.1f} mph -> " + ("PASS" if G[s]["gate_pass"] else "FAIL")
    sz = G[8000]["scripted_zero_residual"]; s9 = G[9000]["scripted_zero_residual"]
    title = "POWER TIER PREVIEW: scripted + yaw residual (effectively scripted)"
    sub = "HYPOTHETICAL ACTUATORS force_scale 2 - fails seed-9000 lateral (17 m)"
    w = rs.Writer(ROOT / a.out); hold = lambda img, s: [w.write(img) for _ in range(int(s * FPS))]
    RED, ORG = (255, 70, 70), (255, 170, 60)
    hold(card([title, sub, f"model: {a.name} (PPO, yaw-only residual +-0.05 rad on the scripted swing, 30k steps)", "NOT the main showcase (that is imit3_w050_s51, 50% learned / 50% scripted).",
               "Style profile / person claims: none. Simulation only."], {0: ORG, 1: RED}, 0.6), 5)
    hold(card(["Gate results (eval_gate, 100 eps/seed, flight_steps 900, headline tier)", gl(4000), gl(8000), gl(9000),
               f"Zero-residual SCRIPT (not learned) lateral std: seed 8000 {sz['lateral_std']:.2f} m, seed 9000 {s9['lateral_std']:.2f} m  ->  policy ~= script",
               f"Seed 9000: {n_out}/100 swings in my scan miss by >10 m laterally; the same outlier hits the script."], {0: ORG, 3: RED}, 0.5), 9)
    meta = dict(date=datetime.date.today().isoformat(), model=a.name, tags=tags, segments=[])
    for lab, seed, sh, note in [("A: representative swing", seedA, shA, f"median-by-carry of {a.swings} swings from seeds 8000.. (seed 8000 passes the headline)"),
                                ("B: seed-9000 lateral OUTLIER", seedB, shB, "largest |lateral| of seeds 9000..9099 - the reason this model FAILS the headline")]:
        ban = [f"{title}", sub, f"{lab}: seed {seed}; {note}", "Learned part = chest-yaw residual only; swing is scripted. Not a learned drive."]
        ft = FlightTracker(env).install(); style_scene(env)
        rec = PRec(env, w, ban, ORG if lab[0] == "A" else RED, ft, "SCRIPTED + yaw residual (effectively scripted)", tags); rec.install()
        try:
            obs, _ = env.reset(seed=seed); ft.reset(); done = False; info = {}
            while not done:
                obs, _, te, tr, info = env.step(pol.predict(obs)[0]); ft.step(); done = te or tr
        finally:
            rec.uninstall()
        rec.frame(hold=int(3 * FPS)); rec.r.close(); sw = ft.summary(info); ft.close()
        hold(card([f"{lab} (seed {seed}) - measured on the rendered swing", f"carry {sw['carry']:.1f} m / {sw['carry_yd']:.0f} yd | total {sw['total_yd']:.0f} yd | lateral y {sw['final_y']:+.2f} m (+left)",
                   f"launch {sw['launch_elev_deg']:.1f} deg | peak club {rec.peak_club*2.23694:.1f} mph", "HYPOTHETICAL ACTUATORS: " + "; ".join(tags)], {3: RED}, 0.55), 4)
        meta["segments"].append(dict(label=lab, seed=seed, selection_pass=dict(carry=sh["carry"], y=sh["final_y"]), rendered=dict(carry=sw["carry"], carry_yd=sw["carry_yd"], total_yd=sw["total_yd"], lateral_y=sw["final_y"], launch_deg=sw["launch_elev_deg"], peak_club_mph=rec.peak_club * 2.23694)))
    e = ["Caveats", "- Power tier uses force_scale 2 (boosted actuators): hypothetical hardware, not a human-achievable swing; ~132 mph club speed.",
         "- Policy ~= zero-residual script on every seed; only a +-0.05 rad yaw residual is learned. Do not read as learning a golf swing.",
         "- Headline gate FAILS on seed 9000 (lateral std ~17 m vs 2.73 m limit, landed 99%); seeds 4000 and 8000 pass.",
         "- Flight = MuJoCo ball + simple impact model (smash ~1.47); spin model ~60% high vs tour data. Simulation only."]
    hold(card(sum([wrap(x, 100) for x in e], []), {1: RED}, 0.55), 8)
    w.close(); meta["duration_s"] = w.frames / FPS; (ROOT / a.out).with_suffix(".json").write_text(json.dumps(meta, indent=1, default=float)); print(json.dumps(meta, indent=1, default=float))


if __name__ == "__main__":
    main()

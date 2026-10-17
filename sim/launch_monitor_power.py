"""Launch-monitor style per-shot report for the HYPOTHETICAL power tier (imit18_power_dart_s51, ppo_v4power48_s71): MODEL-BASED.
python -m sim.launch_monitor_power [shots=20]  ->  results/launch_monitor_power_tier.{json,md}
Per shot (det policy, seeds 4000+i): club speed (impact / peak), ball speed and launch angles at club-ball separation, backspin/sidespin MuJoCo produced
(power-tier env sets them via its hand-set impact_model, spin_k 130, gain 1.28), the MuJoCo carry/total/lateral, then the SAME launch fed to
sim/golf_simulator.shot_from_launch (analytic drag+Magnus, validated vs TrackMan) -> model carry/total/apex/lateral/landing angle, and a 'smash-capped' variant (ball speed = min(ball, 1.48 x impact club speed)).
Nothing here is a real-world measurement; force_scale 2 / power-tier actuators are hypothetical-strength (not human- or robot-attainable)."""
import sys, json, os
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
MPS = 2.23694; YD = 1.09361


def rollout(name, n):
    from stable_baselines3 import PPO
    from eval.env_factory import make_env
    from eval.flight_tracker import FlightTracker
    import eval.leaderboard as L
    from sim.golf_simulator import shot_from_launch
    steps, kw, src = L.config_for([name]); env = make_env(kw); model = PPO.load(str(ROOT / "models" / name), device="cpu")
    ft = FlightTracker(env).install(); rows = []
    for ep in range(n):
        obs, _ = env.reset(seed=4000 + ep); ft.reset(); done = False; info = {}; got = None
        while not done:
            obs, _, te, tr, info = env.step(model.predict(obs, deterministic=True)[0]); ft.step(); done = te or tr
            if got is None and getattr(env, "_sep_v", None) is not None:
                d = env.data; w = d.xmat[env._ball_id].reshape(3, 3) @ d.qvel[env._ball_dof + 3:env._ball_dof + 6]; v = np.array(env._sep_v)
                got = dict(ball_mps=float(np.linalg.norm(v)), el=float(np.degrees(np.arctan2(v[2], np.hypot(v[0], v[1])))), az=float(np.degrees(np.arctan2(v[1], v[0]))),
                           back=float(-w[1] * 60 / (2 * np.pi)), side=float(w[2] * 60 / (2 * np.pi)))
        sh = ft.summary(info)
        if got is None or not sh["true_contact"]: rows.append(dict(shot=ep, contact=False)); continue
        bm = got["ball_mps"] * MPS; ic = sh["impact_club_speed"] * MPS; pc = sh["peak_club_speed"] * MPS
        m1 = shot_from_launch(bm, got["el"], got["back"], got["az"], got["side"], club_mph=ic)
        cap = min(bm, 1.48 * ic); m2 = shot_from_launch(cap, got["el"], got["back"], got["az"], got["side"], club_mph=ic)
        rows.append(dict(shot=ep, contact=True, club_impact_mph=ic, club_peak_mph=pc, ball_mph=bm, smash=bm / ic, launch_deg=got["el"], launch_dir_deg=got["az"],
                         backspin_rpm=got["back"], sidespin_rpm=got["side"], mj_carry_yd=sh["carry"] * YD, mj_total_yd=sh["total_yd"], mj_lateral_yd=sh["final_y"] * YD,
                         model_carry_yd=m1.carry_yd, model_total_yd=m1.total_yd, model_apex_yd=m1.apex_yd, model_lateral_yd=m1.lateral_total_yd, model_land_angle_deg=m1.land_angle_deg,
                         smashcap_ball_mph=cap, smashcap_carry_yd=m2.carry_yd, smashcap_total_yd=m2.total_yd))
    ft.close(); return rows


def main(n=20):
    out = {"label": "MODEL-BASED launch-monitor view of simulated shots (hypothetical power tier: force_scale 2 / power XML; not attainable by a human or real robot)", "shots_per_model": n, "models": {}}
    md = ["# Launch-monitor view: power tier (MODEL-BASED, simulation)", "", out["label"], "",
          "MuJoCo columns come from the evaluator rollout (det policy, seeds 4000+). Model columns re-fly the same ball speed / launch / spin with sim/golf_simulator (analytic ball-flight model). 'smash-capped' = ball speed limited to 1.48 x impact club speed.", ""]
    for name in ("imit18_power_dart_s51", "ppo_v4power48_s71"):
        rows = rollout(name, n); ok = [r for r in rows if r["contact"]]; out["models"][name] = rows
        mean = lambda k: float(np.mean([r[k] for r in ok]))
        md += [f"## {name}  (power tier, hypothetical-strength actuators; {len(ok)}/{n} contact)", "",
               "| shot | club mph (impact/peak) | ball mph | smash | launch deg | dir deg | backspin rpm | sidespin rpm | MuJoCo carry/total yd | MuJoCo lat yd | model carry/total yd | model apex yd | model lat yd | land angle deg | smash-capped carry yd |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in ok:
            md.append(f"| {r['shot']} | {r['club_impact_mph']:.1f} / {r['club_peak_mph']:.1f} | {r['ball_mph']:.1f} | {r['smash']:.2f} | {r['launch_deg']:.1f} | {r['launch_dir_deg']:+.2f} | {r['backspin_rpm']:.0f} | {r['sidespin_rpm']:+.0f} | {r['mj_carry_yd']:.0f} / {r['mj_total_yd']:.0f} | {r['mj_lateral_yd']:+.1f} | {r['model_carry_yd']:.0f} / {r['model_total_yd']:.0f} | {r['model_apex_yd']:.0f} | {r['model_lateral_yd']:+.1f} | {r['model_land_angle_deg']:.0f} | {r['smashcap_carry_yd']:.0f} |")
        md += [f"| **mean** | {mean('club_impact_mph'):.1f} / {mean('club_peak_mph'):.1f} | {mean('ball_mph'):.1f} | {mean('smash'):.2f} | {mean('launch_deg'):.1f} | {mean('launch_dir_deg'):+.2f} | {mean('backspin_rpm'):.0f} | {mean('sidespin_rpm'):+.0f} | {mean('mj_carry_yd'):.0f} / {mean('mj_total_yd'):.0f} | {mean('mj_lateral_yd'):+.1f} | {mean('model_carry_yd'):.0f} / {mean('model_total_yd'):.0f} | {mean('model_apex_yd'):.0f} | {mean('model_lateral_yd'):+.1f} | {mean('model_land_angle_deg'):.0f} | {mean('smashcap_carry_yd'):.0f} |", ""]
        print(name, "mean MuJoCo carry yd", round(mean('mj_carry_yd')), "model", round(mean('model_carry_yd')), "capped", round(mean('smashcap_carry_yd')), flush=True)
    md += ["Reading: smash ~1.55-1.6 exceeds the ~1.48-1.50 legal-driver ceiling because the power-tier env multiplies the contact ball velocity by impact_model gain 1.28; backspin ~3080 rpm is set by the same hand-set model (spin_k 130 x ball speed x sin(launch+2 deg)), not produced by contact. Club speed ~132 mph (peak, `t_down` 0.06 s) is a hypothetical-strength value. TrackMan PGA Tour averages for reference: club 113 mph, ball 167 mph, smash 1.48, launch 10.9 deg, ~2686 rpm, ~275 yd carry."]
    json.dump(out, open(ROOT / "results" / "launch_monitor_power_tier.json", "w"), indent=1, default=float)
    open(ROOT / "results" / "launch_monitor_power_tier.md", "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20)

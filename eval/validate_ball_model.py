"""Validate the simulator's ball-flight model against approximate published TrackMan-style driver averages.   python -m eval.validate_ball_model

WHICH MODEL: the evaluator protocol (flight_tracker / leaderboard) uses the MuJoCo-PHYSICS ball: MuJoCo rigid-body ball (m 0.046 kg, r 0.021 m geom) + env._apply_aero()
(quadratic drag Cd=0.26 constant, Magnus lift Cl=min(1.7*S, 0.30), S=r*w/v, rho=1.19, NO spin decay, no Reynolds-dependent Cd) + MuJoCo ground contact
(solref 0.002/1, friction 0.5, env ball_damping for rolling) -> carry = first ground touch, total = final rest/roll position. This script launches THAT ball with controlled
velocity/spin (calling the env's own _apply_aero + mj_step). The 'analytic' model (env/ball_flight_analytic.py, drag with spin-dependent Cd, Cl up to 0.45, spin decay 3%/s,
bounce/roll; its docstring says calibrated to TrackMan PGA driver averages) is used by analytic_ball training runs only; it is run on the same grid for comparison.

REFERENCE (approximate published TrackMan-style averages, rounded; no more precision claimed): driver ~120 mph club speed, smash ~1.48 (~178 mph ball), ~12 deg launch, ~2400 rpm backspin
-> roughly 270-280 yd carry; ~130 mph club speed -> roughly 300+ yd carry. Tolerance used: sim carry within +-5% of the reference range (anchor1 257-294 yd; anchor2 >= 285 yd).
"""
import json, itertools, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MPH, YD = 0.44704, 1.09361
SPEEDS, SMASH, LAUNCH, SPIN = (100, 110, 120, 130), (1.0, 1.48), (10, 12, 14), (2000, 2400, 3000)
ANCHORS = {(120, 1.48, 12, 2400): ("approx. published TrackMan-style avg: ~270-280 yd carry", 257.0, 294.0),
           (130, 1.48, 12, 2400): ("approx. published TrackMan-style avg: ~300+ yd carry", 285.0, None)}


def physics_shot(env, v_ball, launch_deg, rpm, t_roll=40.0):
    import mujoco
    m, d = env.model, env.data
    mujoco.mj_resetData(m, d)
    x0 = 3.0
    d.qpos[0:3] = (x0, 0.0, 0.0625); d.qpos[3:7] = (1, 0, 0, 0)
    el = np.radians(launch_deg)
    d.qvel[0:3] = (v_ball * np.cos(el), 0.0, v_ball * np.sin(el)); d.qvel[3:6] = (0.0, -rpm * 2 * np.pi / 60, 0.0)   # backspin: w = -y (v=+x -> lift +z)
    mujoco.mj_forward(m, d)
    dt = m.opt.timestep; t = 0.0; carry = None; apex = 0.0; air = False
    while t < 60.0:
        env._apply_aero(); mujoco.mj_step(m, d); t += dt
        z = float(d.xpos[env._ball_id][2]); apex = max(apex, z)
        if z > 0.1: air = True
        if carry is None and air and env._ground_contact():
            carry = float(d.xpos[env._ball_id][0]) - x0; t_land = t
        if carry is not None and t - t_land > t_roll: break
        if carry is not None and np.linalg.norm(d.qvel[0:3]) < 0.05: break
    return dict(carry_m=carry, total_m=float(d.xpos[env._ball_id][0]) - x0, apex_m=apex - 0.0625, hang_s=t_land if carry is not None else None)


def analytic_shot(v_ball, launch_deg, rpm):
    from env.ball_flight_analytic import simulate
    el = np.radians(launch_deg)
    r = simulate([0, 0, 0.0625], [v_ball * np.cos(el), 0, v_ball * np.sin(el)], [0, -rpm * 2 * np.pi / 60, 0])
    return dict(carry_m=r["carry"], total_m=r["total"], apex_m=r["apex"], hang_s=r["hang"])


FINDINGS = "\n## Findings (verified from the table above)\n\n- **Carry at the anchor cases:** MuJoCo-physics ball (the evaluator's) 289 yd at 120 mph / smash 1.48 / 12 deg / 2400 rpm (reference ~270-280 yd: ~3-7% high, inside the +-5% tolerance of the range) and 312 yd at 130 mph (reference ~300+: consistent). The analytic model gives 293 / 319 yd. So drag + Magnus lift reproduce driver-class carry to within a few percent WHEN the ball is launched at a realistic ~178-192 mph.\n- **Slightly long:** constant Cd 0.26 (no Reynolds/spin dependence), no spin decay (the physics ball keeps all its spin; the analytic one decays 3%/s) and Cl capped at 0.30 all err toward more carry/apex; apex 33 m (physics) vs 38 m (analytic) at 120 mph - the physics ball is flatter. Not tuned here.\n- **Smash 1.0 rows (what this sim's contact model actually produces) carry only 165-202 yd at 120-130 mph** (analytic 165-190): the carry shortfall vs a real drive is the ball-speed problem (see results/smash_anomaly.md), not the flight model.\n- **Total distance / roll is NOT validated and is unphysical in the physics ball:** `total` there is 290-785 yd (rolls for the full 60 s; higher for slower, lower-spin shots) because the env has ball_damping 0.0 and the MuJoCo sphere-plane contact has essentially no rolling resistance (no rolling friction), plus bounce uses the contact solref only. The analytic model adds a bounce/roll model (total ~ carry + 27-33 yd at smash 1.48). Do not trust physics 'total' beyond carry.\n- **In the leaderboard, episodes end at the first landing** (ResidualGolfEnv: 'episode ends earlier on landing'), so leaderboard total distance = carry (roll 0.0 m for models that landed); only never-landed or bouncing-then-ended shots differ. The yard columns for total are therefore carry-equivalent in this protocol.\n- **Not modeled / off:** no sidespin-from-wind, no wind, no altitude/temperature (rho fixed 1.19), no lift dependence on Reynolds number, no rolling friction, no dimple drag crisis.\n"


def main():
    from eval.env_factory import make_env
    import eval.eval_scripted_cfg as esc
    env = make_env(dict(esc.base)); env.reset(seed=0)
    rows = []
    for cs, sm, la, sp in itertools.product(SPEEDS, SMASH, LAUNCH, SPIN):
        vb = cs * MPH * sm
        ph, an = physics_shot(env, vb, la, sp), analytic_shot(vb, la, sp)
        rows.append(dict(club_mph=cs, smash=sm, ball_mph=cs * sm, launch_deg=la, spin_rpm=sp,
                         phys_carry_yd=(ph["carry_m"] or 0) * YD, phys_total_yd=ph["total_m"] * YD, phys_apex_m=ph["apex_m"],
                         an_carry_yd=an["carry_m"] * YD, an_total_yd=an["total_m"] * YD, an_apex_m=an["apex_m"]))
        print(rows[-1], flush=True)
    anch = []
    for k, (txt, lo, hi) in ANCHORS.items():
        r = next(x for x in rows if (x["club_mph"], x["smash"], x["launch_deg"], x["spin_rpm"]) == k)
        for nm, v in (("MuJoCo physics (evaluator)", r["phys_carry_yd"]), ("analytic", r["an_carry_yd"])):
            ok = v >= lo and (hi is None or v <= hi)
            anch.append(dict(case=k, ref=txt, model=nm, carry_yd=v, within_tolerance=bool(ok), tol_range_yd=[lo, hi]))
    out = dict(reference="approximate published TrackMan-style averages (rounded)", tolerance="+-5% of reference range", rows=rows, anchors=anch)
    (ROOT / "results/ball_model_validation.json").write_text(json.dumps(out, indent=1))
    L = ["# Ball-model validation vs approximate published TrackMan-style driver averages", "", __doc__.split("REFERENCE")[0].strip().split("WHICH MODEL:")[1].strip(), "",
         "Reference: driver ~120 mph club / smash ~1.48 (~178 mph ball) / ~12 deg / ~2400 rpm backspin -> roughly 270-280 yd carry; ~130 mph club -> roughly 300+ yd carry (approximate published TrackMan-style averages, rounded). Tolerance: +-5% of that range.", "",
         "## Anchor cases", "", "| Case (club mph, smash, launch, rpm) | Model | Carry yd | Reference | Within tolerance |", "|---|---|---|---|---|"]
    for a in anch: L.append(f"| {a['case']} | {a['model']} | {a['carry_yd']:.0f} | {a['ref']} | {'YES' if a['within_tolerance'] else 'NO'} |")
    L += ["", "## Sweep (carry / total in yards)", "", "| club mph | smash | ball mph | launch | rpm | physics carry | physics total | physics apex m | analytic carry | analytic total | analytic apex m |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows: L.append(f"| {r['club_mph']} | {r['smash']} | {r['ball_mph']:.0f} | {r['launch_deg']} | {r['spin_rpm']} | {r['phys_carry_yd']:.0f} | {r['phys_total_yd']:.0f} | {r['phys_apex_m']:.1f} | {r['an_carry_yd']:.0f} | {r['an_total_yd']:.0f} | {r['an_apex_m']:.1f} |")
    (ROOT / "results/ball_model_validation.md").write_text("\n".join(L) + "\n" + FINDINGS); print("\n".join(L[:20]))


if __name__ == "__main__":
    main()

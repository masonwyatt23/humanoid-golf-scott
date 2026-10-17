"""Old vs fixed strike regime (results/strike_regime_rerun.md/.json).  python -m eval.strike_regime_rerun [--episodes 50] [--seed 4000]

What the 'fix' is (git 7da7be9 / ffc6271, results/TRAINING_NOTES.md 'Stage 5'): NOT an env-physics change but a CONFIG sign/offset fix for the v3 XML:
negative loft_deg = lofted face (positive loft closes the face), and ball_dz -0.01 puts the strike mid-face; the old configs (loft +7..+9, ball_dz +0.008)
struck the top/crown edge ('edge-strike', bimodal flat vs ~35 deg launch). Env code since c7ba7dd only added address-noise params (ball_y/sh/el noise, defaults unchanged),
yaw_ff, separation-velocity launch -> env fingerprint changed, leaderboard cache re-evaluated.

OLD  = the model with its own training config (leaderboard.json, same protocol).
NEW  = the SAME checkpoint run under the fixed regime: only loft_deg=-26 and ball_dz=-0.01 overridden (everything else = its training config). These policies were
       NOT trained under this regime -> out-of-distribution; this is a diagnostic, not a retrained model.
Scripted: OLD = trainer's pre-fix scripted (loft +8, ball_dz 0.008, ball_x .396, wr_end -0.01, yaw_ff -3: TRAINING_NOTES item 3/4) re-measured here; NEW = configs/fast_scripted_v2_lofted.json.
"""
import argparse, json
from pathlib import Path
import eval.dispersion_report as dr
import eval.eval_scripted_cfg as esc

ROOT = Path(__file__).resolve().parent.parent


def row(d):
    return dict(contact=d["contact_rate"], carry=d["mean_carry"], landed=d["landed_fraction"], lat_std=d["lateral_std"], left=d["left_miss_rate"], right=d["right_miss_rate"],
                launch=d["launch_elev_mean_deg"], flat=d["launch_flat_frac"], mph=d["peak_club_mph_mean"], mph_max=d["peak_club_mph_max"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--episodes", type=int, default=50); ap.add_argument("--seed", type=int, default=4000); a = ap.parse_args()
    dr.REFS = []; dr.MASON_V2_REFS = []; dr.MASON_REFS = []
    lb = json.loads((ROOT / "results/leaderboard.json").read_text()); by = {m["names"][0]: m for m in lb["models"]}
    out = []
    def go(label, kind, kw, name=None, scripted=False):
        r = {}
        for mode, det in (("deterministic", True), ("stochastic", False)):
            if scripted and not det: r[mode] = r["deterministic"]; continue
            d, _ = dr.run(name or "x", kw, a.episodes, a.seed, det, scripted=scripted); r[mode] = row(d)
        out.append(dict(label=label, kind=kind, **r)); print(label, r["deterministic"], flush=True)
    for n in ("ppo_resid_v3_left_an3_s1", "ppo_resid_v3_left_an2_s0", "ppo_resid_v3_left_fast2_s11"):
        m = by[next(k for k in by if k.startswith(n))]; kw = m["env_kwargs"]
        out.append(dict(label=f"{n} OLD regime (own config; loft {kw.get('loft_deg')}, ball_dz {kw.get('ball_dz')})", kind="LEARNED", source="leaderboard.json",
                        **{md: row(m["modes"][md]) for md in ("deterministic", "stochastic")}))
        go(f"{n} NEW regime (loft -26, ball_dz -0.01; OOD)", "LEARNED", dict(kw, loft_deg=-26.0, ball_dz=-0.01), name=n)
    old = dict(esc.base, script=dict(q_back=2.2, t_down=0.095, t_back=0.6, wr_end=-0.01, yaw_ff=-3.0), ball_x=0.396, ball_x_noise=0.003, loft_deg=8.0, ball_dz=0.008)
    go("scripted fast OLD regime (loft +8, ball_dz +0.008, yaw_ff -3; trainer pre-fix cfg)", "SCRIPTED (not learned)", old, scripted=True)
    new = dict(esc.base, **{k: v for k, v in json.loads((ROOT / "configs/fast_scripted_v2_lofted.json").read_text()).items() if k != "description"})
    go("scripted fast NEW regime (configs/fast_scripted_v2_lofted.json)", "SCRIPTED (not learned)", new, scripted=True)
    (ROOT / "results/strike_regime_rerun.json").write_text(json.dumps(dict(episodes=a.episodes, seed=a.seed, rows=out), indent=1))
    L = ["# Strike regime: old vs fixed (verified, this evaluator)", "", __doc__.split("Scripted:")[0].strip(), "",
         f"Protocol: {a.episodes} episodes/mode, seeds {a.seed}+, flight tracker (MuJoCo ball, no spin), flat = launch < 5 deg. Scripted rows are zero-residual (det = stoch).", "",
         "| Row | Kind | Mode | Contact | Carry m | Landed | Lat std m | Miss L/R | Launch deg (flat frac) | Peak mph mean/max |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out:
        for md in ("deterministic", "stochastic"):
            x = r[md]; L.append(f"| {r['label']} | {r['kind']} | {md[:3]} | {x['contact']*100:.0f}% | {x['carry']:.1f} | {x['landed']*100:.0f}% | {x['lat_std']:.3f} | {x['left']*100:.0f}/{x['right']*100:.0f}% | {x['launch']:.1f} ({x['flat']*100:.0f}%) | {x['mph']:.1f}/{x['mph_max']:.1f} |")
    L += ["", "Scripted NEW trainer-reported (TRAINING_NOTES Stage 5, 100 eps, evaluator protocol): launch 9.3/9.5 deg, carry 70.0/71.9 m, landed 98/99%, lat std 0.013 m, 120.3 mph. Scripted OLD trainer-reported: launch mean 11.5, 62% flat, lat std 6.3 m, landed 58%, 120.4 mph.",
          "", "Caveat: README numbers for LEARNED models stay valid ONLY for their own (old-regime) training config; the NEW-regime rows show what those frozen policies do under the fixed config, not retrained results."]
    (ROOT / "results/strike_regime_rerun.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()

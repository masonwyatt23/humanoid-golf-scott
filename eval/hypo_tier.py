"""HYPOTHETICAL TIER (force_scale > 1) 3-seed headline-gate table, built from results/gate_<name>_seed<seed>.json (seed 4000 file = ..._seed4000.json).
Kept SEPARATE from the learned-vs-scripted leaderboard.  'Effectively scripted' = on every recorded seed the policy's det carry is within 1% and lateral std within 15%
(or 0.3 m) of the zero-residual script recorded in the same gate file.  Nothing is guessed: every cell is read from the JSON."""
import glob, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TOL_CARRY, TOL_LAT_REL, TOL_LAT_ABS = 0.01, 0.15, 0.3


def tier():
    by = {}
    fs = sorted(glob.glob(str(ROOT / "results/gate_*_seed*.json")) + glob.glob(str(ROOT / "results/imit_private/gate_*.json")) + glob.glob(str(ROOT / "results/power48_private/gate_*.json")))   # *_private = Trainer's GATE_OUT dirs; seed-4000 file there has no _seed suffix
    for f in fs:
        d = json.loads(Path(f).read_text()); kw = d.get("env_kwargs", {})
        if not (kw.get("force_scale", 1.0) or 1.0) > 1.0 or "policy_det" not in d: continue
        by.setdefault(d["name"], {})[d["seed"]] = d
    rows = []
    for n, S in sorted(by.items()):
        eff = all(abs(d["policy_det"]["mean_carry"] - d["scripted_zero_residual"]["mean_carry"]) <= TOL_CARRY * d["scripted_zero_residual"]["mean_carry"]
                  and abs(d["policy_det"]["lateral_std"] - d["scripted_zero_residual"]["lateral_std"]) <= max(TOL_LAT_ABS, TOL_LAT_REL * d["scripted_zero_residual"]["lateral_std"])
                  for d in S.values() if "scripted_zero_residual" in d)
        res = (json.loads((ROOT / f"results/{n}.json").read_text()).get("args", {}).get("res_scale") if (ROOT / f"results/{n}.json").exists() else None)
        kw = next(iter(S.values()))["env_kwargs"]
        rows.append(dict(name=n, seeds=S, effectively_scripted=eff, res_scale=res, force_scale=kw.get("force_scale"), flight_steps=kw.get("flight_steps"),
                         all3=all(s in S and S[s]["gate_pass"] for s in (4000, 8000, 9000))))
    return rows


def noise_cell(name):
    """Quick noise screen (N=10 det eps, Gaussian sigma on every obs+action) from results/leaderboard.json; 'not measured' if absent."""
    try: L = json.loads((ROOT / "results/leaderboard.json").read_text())
    except Exception: return "not measured"
    for m in L["models"]:
        if name in m["names"] and m.get("noise_robust"):
            cl = m["modes"]["deterministic"]["mean_carry"]; nr = m["noise_robust"]
            return " / ".join(f"{nr[k]['mean_carry']:.0f} ({nr[k]['mean_carry']/cl*100:.0f}%)" if nr.get(k) and "mean_carry" in nr[k] else "-" for k in ("0.005", "0.01")) + " " + ("PASS" if all(nr.get(k) and nr[k]["contact_rate"] >= 1 and nr[k]["mean_carry"] >= 0.8 * cl for k in ("0.005", "0.01")) else "FAIL")
    return "not measured"


def md():
    R = tier()
    L = ["## HYPOTHETICAL TIER (force_scale > 1): 3-seed headline gate, kept separate from learned vs scripted", "",
         "**force_scale 2 (hypothetical-strength actuators)**: boosted actuator force caps; not human- or robot-attainable. Source: `results/gate_<name>_seed<seed>.json` (eval_gate, headline tier: det AND stoch contact>=99%, lateral std<=2.73 m, launch 5-20 deg, carry>=min_carry, landed>=90%). "
         "'Effectively scripted' = policy det carry within 1% and lateral std within 15% (or 0.3 m) of the zero-residual script in the same file on every seed; such rows are NOT learned drives. A model counts as passing only if ALL of seeds 4000/8000/9000 pass.", "",
         "| model | label | force_scale | flight_steps | residual cap (res_scale) | seed | episodes | det carry m / yd | det lat std m | stoch lat std m | landed (det) | launch deg | club mph | script lat std m | noise quick (carry m, % of clean; sigma 0.005 / 0.01) | headline |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R:
        sw = next(iter(r["seeds"].values()))["env_kwargs"].get("script_weight")
        lab = "SCRIPT-FREE IMITATION OF THE SCRIPT (learned policy = 100% of joint targets, distilled from the v3 script; force_scale 2, hypothetical-strength actuators)" if (sw == 0 and r["name"].startswith("imit")) and not r["effectively_scripted"] else "EFFECTIVELY SCRIPTED (force_scale 2, hypothetical-strength actuators)" if r["effectively_scripted"] else "POLICY DIFFERS FROM SCRIPT (hypothetical actuators; learned fraction: see leaderboard row)"
        for s, d in sorted(r["seeds"].items()):
            p, st, z = d["policy_det"], d["policy_stoch"], d.get("scripted_zero_residual", {})
            L.append(f"| {r['name']} | {lab} | {r['force_scale']:g} | {r['flight_steps']} | {r['res_scale']} | {s} | {d['episodes']} | {p['mean_carry']:.1f} / {p['mean_carry']*1.09361:.0f} | {p['lateral_std']:.2f} | {st['lateral_std']:.2f} | {p['landed_fraction']*100:.0f}% | {p['launch_elev_mean_deg']:.1f} | {p['peak_club_mph_mean']:.1f} | {z.get('lateral_std', float('nan')):.2f} | {noise_cell(r['name'])} | {'PASS' if d['gate_pass'] else 'FAIL'} (min_carry {d['min_carry']}) |")
    L += ["", "3/3-seed pass: " + (", ".join(f"{r['name']}: {'YES' if r['all3'] else 'NO'}" for r in R) or "no rows"), ""]
    return L


if __name__ == "__main__":
    print("\n".join(md()))

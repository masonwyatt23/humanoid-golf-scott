"""Evaluator-protocol check (same code path as eval.leaderboard / dispersion_report.run: MuJoCo physics, flight tracker,
carry = first landing after flight, episode ends on landing/stop/max_steps) for a residual model vs zero-residual baseline.
python -m eval.eval_gate <name> [episodes] [seed]  ->  results/gate_<name>.json.  GATE: carry > 11.98 m AND lateral std < 2.73 m (teammate baseline numbers)."""
import sys, json
from pathlib import Path
import eval.dispersion_report as dr
from eval.env_factory import resid_kw_from_args
ROOT = Path(__file__).resolve().parent.parent
if __name__ == "__main__":
    name = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 50; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    dr.REFS = []
    args = json.load(open(ROOT / "results" / f"{name}.json"))["args"]
    J = json.load(open(ROOT / "results" / f"{name}.json"))
    if "env_kwargs_full" in J:   # v5 imitation runs store the exact env kwargs (script extras, address, impact model, script_weight/learn_scale)
        kw = dict(J["env_kwargs_full"], _env="residual", track_weight=0.0, track_set=None); kw["residual_scale"] = list(kw["residual_scale"])
    else:
        kw = resid_kw_from_args(args)
    out = {"name": name, "episodes": n, "seed": seed, "env_kwargs": kw}
    for label, scripted, det in [("policy_det", False, True), ("policy_stoch", False, False), ("scripted_zero_residual", True, True)]:
        d, _ = dr.run(name, kw, n, seed, det, scripted=scripted)
        out[label] = {k: d[k] for k in d if not k.startswith("dtw")}
        print(label, {k: round(v, 3) for k, v in out[label].items() if isinstance(v, float) and k in ("contact_rate", "mean_carry", "landed_fraction", "lateral_std", "mean_y", "peak_club_mph_mean", "mean_distance")}, flush=True)
    p, s = out["policy_det"], out["scripted_zero_residual"]
    out["gate_pass"] = bool(p["mean_carry"] > 11.98 and p["lateral_std"] < 2.73 and p["contact_rate"] >= 0.99)
    print("GATE (carry>11.98 & lat_std<2.73 & contact>=99%):", out["gate_pass"])
    json.dump(out, open(ROOT / "results" / f"gate_{name}.json", "w"), indent=1, default=float)

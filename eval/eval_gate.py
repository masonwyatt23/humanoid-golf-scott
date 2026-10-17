"""Evaluator-protocol check (same code path as eval.leaderboard / dispersion_report.run: MuJoCo physics, flight tracker,
carry = first landing after flight, episode ends on landing/stop/max_steps) for a residual model vs zero-residual baseline.
python -m eval.eval_gate <name> [episodes] [seed]  ->  results/gate_<name>.json.  GATE: carry > 11.98 m AND lateral std < 2.73 m (teammate baseline numbers).

WHAT 11.98 m MEANS (investigated 2026-10-17; units are metres, 11.98 m = 13.1 yd; NOT a units or final-x-vs-carry mismatch): the two numbers are a *different-protocol baseline* inherited from a teammate evaluator with a
4-s flight horizon and loft 6 (results/TRAINING_NOTES.md line ~63): with that horizon most balls never 'landed', so their mean carry/lateral were measured on ~1/3 of shots at ~12 m. This evaluator uses a
450-step flight horizon (balls land, carry 70-114 m), so carry > 11.98 m is a very weak floor (a flat -5.8 deg 'exploit' with 15.2 m carry passes it) and an absolute lateral std < 2.73 m is stricter than the
teammate number implied because lateral spread grows with distance. The meaningful, stricter criterion used for the showcase is in eval/leaderboard.py (det carry >= 30 m, lateral std <= 2.73 m, 100% contact,
launch >= 5 deg / not flat). gate_pass here is kept unchanged for continuity with committed gate JSONs; `gate_note` and `launch_not_flat` are added to the output for context.
EVAL_WORKERS=N env var runs episodes in N parallel processes (same per-episode seeds; results statistically equal, not bit-identical)."""
import sys, json, os
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
        d, _ = dr.run(name, kw, n, seed, det, scripted=scripted, workers=int(os.environ.get("EVAL_WORKERS", "1")))
        out[label] = {k: d[k] for k in d if not k.startswith("dtw")}
        print(label, {k: round(v, 3) for k, v in out[label].items() if isinstance(v, float) and k in ("contact_rate", "mean_carry", "landed_fraction", "lateral_std", "mean_y", "peak_club_mph_mean", "mean_distance")}, flush=True)
    p, s = out["policy_det"], out["scripted_zero_residual"]
    out["gate_pass"] = bool(p["mean_carry"] > 11.98 and p["lateral_std"] < 2.73 and p["contact_rate"] >= 0.99)
    out["launch_not_flat"] = bool(not p.get("launch_flat_flag", False))
    out["gate_note"] = "carry>11.98 m is a legacy 4-s-horizon baseline (~1/3 of shots landed at ~12 m); weak floor under the 450-step horizon. Showcase criterion (carry>=30, launch not flat, ...) lives in eval/leaderboard.py. See eval_gate.py docstring."
    print("GATE (carry>11.98 & lat_std<2.73 & contact>=99%):", out["gate_pass"])
    json.dump(out, open(ROOT / "results" / f"gate_{name}.json", "w"), indent=1, default=float)

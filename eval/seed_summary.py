"""Mean/min/max ACROSS TRAINING SEEDS of gate JSONs (opt-in loop reporting; touches no leaderboard file).
python -m eval.seed_summary <name_prefix> [dir ...]   e.g. imit9_w000 results/imit_private
Reads gate_<prefix>_s<SEED>[_seed<EVALSEED>].json; for each eval seed aggregates over training seeds: det/stoch carry, lateral std, launch, landed, pass rate.
Writes results/seed_summary_<prefix>.json and .md"""
import sys, re, json, glob, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
pre = sys.argv[1]; dirs = sys.argv[2:] or [str(ROOT / "results")]
rows = {}
for d in dirs:
    for f in glob.glob(str(Path(d) / f"gate_{pre}_s[0-9]*.json")):
        m = re.match(rf"gate_{re.escape(pre)}_s(\d+)(?:_seed(\d+))?\.json$", Path(f).name)
        if not m: continue
        j = json.load(open(f)); es = int(m.group(2) or 4000)
        rows.setdefault(es, {})[int(m.group(1))] = j
out = {"prefix": pre, "eval_seeds": {}}; L = [f"| eval seed | n train seeds | pass rate | carry mean/min | lat std mean/max | launch mean/min | landed mean/min |", "|---|---|---|---|---|---|---|"]
for es in sorted(rows):
    js = rows[es]; g = lambda mode, k: np.array([j[mode][k] for j in js.values()], float)
    r = {"train_seeds": sorted(js), "pass_rate": float(np.mean([j["gate_pass"] for j in js.values()]))}
    for mode in ("policy_det", "policy_stoch"):
        if all(mode in j for j in js.values()):
            r[mode] = {k: dict(mean=float(g(mode, k).mean()), min=float(g(mode, k).min()), max=float(g(mode, k).max())) for k in ("mean_carry", "lateral_std", "launch_elev_mean_deg", "landed_fraction")}
    out["eval_seeds"][str(es)] = r; d = r["policy_det"]
    L.append(f"| {es} | {len(js)} | {r['pass_rate']:.2f} | {d['mean_carry']['mean']:.1f}/{d['mean_carry']['min']:.1f} | {d['lateral_std']['mean']:.2f}/{d['lateral_std']['max']:.2f} | {d['launch_elev_mean_deg']['mean']:.1f}/{d['launch_elev_mean_deg']['min']:.1f} | {d['landed_fraction']['mean']:.2f}/{d['landed_fraction']['min']:.2f} |")
(ROOT / "results" / f"seed_summary_{pre}.json").write_text(json.dumps(out, indent=1)); (ROOT / "results" / f"seed_summary_{pre}.md").write_text("\n".join(L) + "\n"); print("\n".join(L))

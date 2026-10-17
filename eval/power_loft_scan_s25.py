"""Stage 25: HYPOTHETICAL power tier (v4_power, fs2 BOOSTED), impact gain 1.20 preset, scripted zero residual: loft scan toward launch ~7.8 deg. args: name grid eps seed"""
import subprocess, json, sys, os
name, grid, n, seed = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3], sys.argv[4]
base = "configs/fast_scripted_v4_power_elbowrange.json"; IM = {"gain": 1.20, "dz0": 0.017, "k_off": 0.4, "spin_k": 130, "k_side": 3500}; rows = {}
for k, ov in grid.items():
    o = {"impact_model": IM}; o.update(ov)
    r = subprocess.run([sys.executable, "-m", "eval.eval_v4", base, json.dumps(o), n, seed, k], capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=".", OMP_NUM_THREADS="1"))
    l = [x for x in r.stdout.splitlines() if x.startswith("RESULT")]
    rows[k] = json.loads(l[0].split(f" {seed} ", 1)[1]) if l else {"error": r.stderr[-200:]}
    print(k, {a: rows[k].get(a) for a in ("contact_rate", "mean_carry", "lateral_std", "launch_elev_mean_deg", "peak_club_mph_mean")}, flush=True)
    json.dump(dict(note="HYPOTHETICAL power tier, impact gain 1.20, scripted zero residual, 100 eps? see n", n=n, rows=rows), open(f"results/{name}.json", "w"), indent=1)

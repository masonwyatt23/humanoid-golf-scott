"""Stage 25: STOCK fs1 q_back 2.3 scripted: lateral-fix scan (yaw_ff, loft, ball_dz...). args: name json_grid eps seed. -> results/<name>.json (script only, not learned)"""
import subprocess, json, sys, os
name, grid, n, seed = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3], sys.argv[4]
base = "configs/fast_scripted_v3_fs1_elbowfull.json"; rows = {}
for k, ov in grid.items():
    o = {"script": {"q_back": 2.3}, "loft_deg": -41}; o["script"].update(ov.get("script", {})); o.update({a: b for a, b in ov.items() if a != "script"})
    r = subprocess.run([sys.executable, "-m", "eval.eval_v4", base, json.dumps(o), n, seed, k], capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=".", OMP_NUM_THREADS="1"))
    l = [x for x in r.stdout.splitlines() if x.startswith("RESULT")]
    rows[k] = json.loads(l[0].split(f" {seed} ", 1)[1]) if l else {"error": r.stderr[-200:]}
    print(k, {a: rows[k].get(a) for a in ("contact_rate", "mean_carry", "lateral_std", "launch_elev_mean_deg", "peak_club_mph_mean")}, flush=True)
    json.dump(dict(note="STOCK force_scale 1 scripted zero residual", cfg=o, rows=rows), open(f"results/{name}.json", "w"), indent=1)

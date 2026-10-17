"""Stage 24 scan 3: STOCK fs1; longer backswing q_back with retuned loft_deg / ball_dz / t_down (contact+launch recovery). 40 eps seed 4000. -> results/stock_speed_scan3_s24.json"""
import subprocess, json, sys, os
base = "configs/fast_scripted_v3_fs1_elbowfull.json"
grid = {}
for qb in (2.3, 2.4, 2.5):
    for loft in (-36, -41):
        grid[f"q_back {qb} loft {loft}"] = {"script": {"q_back": qb}, "loft_deg": loft}


rows = {}
for k, ov in grid.items():
    r = subprocess.run([sys.executable, "-m", "eval.eval_v4", base, json.dumps(ov), "40", "4000", k], capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=".", OMP_NUM_THREADS="1"))
    line = [l for l in r.stdout.splitlines() if l.startswith("RESULT")]
    rows[k] = json.loads(line[0].split(" 4000 ", 1)[1]) if line else {"error": r.stderr[-200:]}
    print(k, {a: rows[k].get(a) for a in ("contact_rate","mean_carry","lateral_std","launch_elev_mean_deg","peak_club_mph_mean")}, flush=True)
    json.dump(dict(note="STOCK force_scale 1, scripted zero residual, 40 eps seed 4000, eval.eval_v4", rows=rows), open("results/stock_speed_scan3_s24.json", "w"), indent=1)

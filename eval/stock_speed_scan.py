"""Stage 24: STOCK (force_scale 1) scripted scan of NON-timing levers (chest yaw range, backswing q_back, wrist cock/release window, t_back) on configs/fast_scripted_v3_fs1_elbowfull.json. Output results/stock_speed_scan_s24.json"""
import subprocess, json, sys, os
base = "configs/fast_scripted_v3_fs1_elbowfull.json"
grid = {
 "base": {},
 "yaw_fin -0.4": {"script": {"yaw_fin": -0.4}}, "yaw_fin 0.4": {"script": {"yaw_fin": 0.4}},
 "yaw_back 0.5": {"script": {"yaw_back": 0.5}}, "yaw_back -0.5": {"script": {"yaw_back": -0.5}},
 "q_back 2.6": {"script": {"q_back": 2.6}}, "q_back 3.0": {"script": {"q_back": 3.0}},
 "wrist_cock 0.6": {"script": {"wrist_cock": 0.6}}, "wrist_cock 1.0": {"script": {"wrist_cock": 1.0}},
 "wr_rel 0.3-0.9": {"script": {"wr_rel_start": 0.3, "wr_rel_end": 0.9}},
 "wr_rel 0.0-0.4": {"script": {"wr_rel_end": 0.4}},
 "t_back 0.9": {"script": {"t_back": 0.9}},
}
rows = {}
for k, ov in grid.items():
    r = subprocess.run([sys.executable, "-m", "eval.eval_v4", base, json.dumps(ov), "40", "4000", k], capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=".", OMP_NUM_THREADS="1"))
    line = [l for l in r.stdout.splitlines() if l.startswith("RESULT")]
    rows[k] = json.loads(line[0].split(" 4000 ", 1)[1]) if line else {"error": r.stderr[-200:]}
    print(k, rows[k], flush=True)
    json.dump(dict(note="STOCK force_scale 1, scripted zero residual, 40 eps seed 4000, eval.eval_v4; non-timing levers", rows=rows), open("results/stock_speed_scan_s24.json", "w"), indent=1)

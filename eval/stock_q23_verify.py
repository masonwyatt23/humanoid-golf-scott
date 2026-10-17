"""Stage 24: STOCK fs1 scripted (zero residual) q_back 2.3 loft -41, 100 eps x seeds 4000/8000/9000 -> results/stock_q23_verify_s24.json (script-only, not a learned policy)"""
import subprocess, json, sys, os
base="configs/fast_scripted_v3_fs1_elbowfull.json"; ov={"script":{"q_back":2.3},"loft_deg":-41}; rows={}
for s in (4000,8000,9000):
    r=subprocess.run([sys.executable,"-m","eval.eval_v4",base,json.dumps(ov),"100",str(s),f"q2.3_loft-41_s{s}"],capture_output=True,text=True,env=dict(os.environ,PYTHONPATH=".",OMP_NUM_THREADS="1"))
    l=[x for x in r.stdout.splitlines() if x.startswith("RESULT")]
    rows[s]=json.loads(l[0].split(f" {s} ",1)[1]) if l else {"error":r.stderr[-300:]}
    json.dump(dict(note="STOCK force_scale 1, scripted zero residual, 100 eps",rows=rows),open("results/stock_q23_verify_s24.json","w"),indent=1)

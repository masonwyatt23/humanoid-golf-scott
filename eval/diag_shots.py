"""Per-shot dump of a scripted config. python -m eval.diag_shots cfg.json eps seed out.json"""
import sys, json
import eval.dispersion_report as dr
from eval.eval_scripted_cfg import base as B0
cfg=json.load(open(sys.argv[1])); cfg.pop("description",None); cfg.pop("hypothetical",None)
kw=dict(B0); kw.update(cfg); kw["script"]=dict(B0["script"],**cfg["script"]); dr.REFS=[]
d,shots=dr.run("x",kw,int(sys.argv[2]),int(sys.argv[3]),True,scripted=True)
json.dump(shots,open(sys.argv[4],"w"),default=float); print(list(shots[0].keys()))

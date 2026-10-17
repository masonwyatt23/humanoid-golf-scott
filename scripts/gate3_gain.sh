#!/bin/bash
# usage: scripts/gate3_gain.sh <model> <impact_gain> -- 3-seed headline gate with OPT-IN impact_gain override (Stage 23); HYPOTHETICAL power tier only
cd /workspace/artifacts/humanoid-golf-scott; D=results/imit_private/gain$(echo $2 | tr -d .); mkdir -p $D
for s in 4000 8000 9000; do GATE_OVERRIDE="{\"impact_gain\":$2}" GATE_OUT=$D PYTHONPATH=. OMP_NUM_THREADS=1 /workspace/golfvenv/bin/python -m eval.eval_gate $1 100 $s > logs/gate_$1_g$2_$s.log 2>&1; done

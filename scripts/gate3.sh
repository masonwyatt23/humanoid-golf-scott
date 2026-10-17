#!/bin/bash
# usage: scripts/gate3.sh <model> -- 3-seed gate into private dir; nohup-safe
cd /workspace/artifacts/humanoid-golf-scott; mkdir -p results/imit_private
for s in 4000 8000 9000; do GATE_OUT=results/imit_private PYTHONPATH=. OMP_NUM_THREADS=1 /workspace/golfvenv/bin/python -m eval.eval_gate $1 100 $s > logs/gate_$1_$s.log 2>&1; done

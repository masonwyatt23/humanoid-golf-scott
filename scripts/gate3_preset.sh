#!/bin/bash
# usage: scripts/gate3_preset.sh <model> <configs/preset_*.json> -- 3-seed headline gate with an OPT-IN versioned preset (gate_override read from the preset file). Output: results/imit_private/<preset>/
cd /workspace/artifacts/humanoid-golf-scott
P=$2; N=$(/workspace/golfvenv/bin/python -c "import json,sys;print(json.load(open('$P'))['preset'])"); OV=$(/workspace/golfvenv/bin/python -c "import json;print(json.dumps(json.load(open('$P'))['gate_override']))")
D=results/imit_private/$N; mkdir -p $D
for s in 4000 8000 9000; do GATE_OVERRIDE="$OV" GATE_OUT=$D PYTHONPATH=. OMP_NUM_THREADS=1 /workspace/golfvenv/bin/python -m eval.eval_gate $1 100 $s > logs/gate_$1_${N}_$s.log 2>&1; done

# Roadmap

Highest-value next steps, in rough priority order:

1. **Unitree G1 model** — replace the generic humanoid (`env/models/humanoid_golf.xml`) with a Unitree G1 MJCF for a realistic, transferable embodiment.
2. **WHAM / GVHMR pose extraction** — extract real swing references from video (e.g. Adam Scott footage) into `.npz` files in `data/references/`; add the missing `data/process_video.py`.
3. **Longer curriculum training** — run extended PPO training through the stages in `imitation/curriculum.py` (Address → Contact → Style → Ball flight) to raise carry distance while keeping contact at 100%.
4. **Ball spin metrics** — track spin, launch angle and carry in the env and `eval/` scripts, and commit results files so README figures are verifiable.

# ROADMAP

Highest-value next steps for the humanoid golf system:

1. **Unitree G1 / H1 model** — Replace the simplified humanoid with a real humanoid MJCF for better morphology match and eventual sim-to-real.
2. **WHAM / GVHMR reconstruction** — Swap MediaPipe for high-quality monocular 3D mesh recovery from PureGolf and Adam Scott videos.
3. **Curriculum training at scale** — Run the staged curriculum (contact → style → ball flight) for 500k–2M steps on GPU with many parallel environments.
4. **Ball spin and launch metrics** — Add clubface angle, path, and spin estimation so policies can be evaluated like Trackman data.
5. **Proper IK retargeting** — Map reconstructed human motion onto the humanoid with contact-aware optimization.
6. **Multi-style policies** — Train and compare Scott, Scheffler, and Rory styles side-by-side with the compare_styles script.
7. **Transfer to ashlrai org** — Move the repository into the AshlrAI GitHub organization once admin access is available.

## Recent changes (commit 6bf1217)

- **cvel fix:** `ball_vel` was read from `data.cvel[ball][:3]`, which is the *angular* part of MuJoCo's `cvel`. It now uses `[3:6]` (linear velocity) in both the observation and the reward.
- **Post-contact velocity bonus:** once contact is registered, the reward adds `0.5 * ball_vel[0]` when forward ball velocity exceeds 1.0 m/s. This replaces the earlier `0.05 * ball_vel[0]` term and the distance-to-target shaping term.
- **Stronger contact rewards:** club-ball proximity term raised to `2.5*exp(-4d)`, near-ball bonus radius widened to 0.25 m (peak 4.0), contact detection threshold lowered to 0.3 m/s, and the one-time contact bonus raised from 10 to 15.

Note: the earlier "0.74 m" carry figure (commit 6adb62d message) predates the cvel fix, and no results files are committed, so it has not been re-measured. Re-run `python -m eval.evaluate` and commit the output to confirm current numbers.

Current milestone: **100% contact rate** reported, with distance still modest and expected to improve after the cvel fix.

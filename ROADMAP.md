# ROADMAP

Highest-value next steps for the humanoid golf system:

1. **Unitree G1 / H1 model** — Replace the simplified humanoid with a real humanoid MJCF for better morphology match and eventual sim-to-real.
2. **WHAM / GVHMR reconstruction** — Swap MediaPipe for high-quality monocular 3D mesh recovery from PureGolf and Adam Scott videos.
3. **Curriculum training at scale** — Run the staged curriculum (contact → style → ball flight) for 500k–2M steps on GPU with many parallel environments.
4. **Ball spin and launch metrics** — Add clubface angle, path, and spin estimation so policies can be evaluated like Trackman data.
5. **Proper IK retargeting** — Map reconstructed human motion onto the humanoid with contact-aware optimization.
6. **Multi-style policies** — Train and compare Scott, Scheffler, and Rory styles side-by-side with the compare_styles script.
7. **Transfer to ashlrai org** — Move the repository into the AshlrAI GitHub organization once admin access is available.

Current reliable milestone: **100% contact rate** with improving carry (latest: 0.74 m). The system is ready for the next scaling steps.

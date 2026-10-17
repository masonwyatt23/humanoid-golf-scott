# Evaluation protocol (as implemented; read from code, 2026-10-17)

Status: written by the Golf Style Evaluator from the code in this tree. It describes what the code does, not what was intended. To be reconciled with the Trainer. All numbers are from MuJoCo simulation.

## 1. Shared episode rollout (`eval/dispersion_report.py::_chunk`, used by both the gate and the leaderboard)
- Env built by `eval.env_factory.make_env(kw)`; model loaded from `models/<name>.zip` (SB3 PPO, CPU). `scripted=True` means a zero-residual action on the same residual env (the scripted swing alone).
- Episode `i` starts with `env.reset(seed = seed_base + i)`; per-episode seeds do not depend on the number of workers, so serial and parallel runs agree.
- `det` = `model.predict(obs, deterministic=True)`; `stoch` = `deterministic=False` (sampled actions). Both are always run.
- Ball physics and flight: MuJoCo ball with `eval/flight_tracker.py::FlightTracker` (substep club speed, separation-velocity launch, sequencing proxy). The episode ends on landing/stop or when `max_steps = swing_steps + flight_steps`. `flight_steps` defaults to 450 in `env/residual_golf_env.py`; the power-tier envs set 900 (recorded in each run's `env_kwargs`).
- Carry = ball x at first landing after flight, 0 if it never landed (so the mean carry includes zeros; `landed_fraction` is reported). Total = final x minus start x.
- **Lateral definition:** `lateral_std` = population standard deviation (`np.std`) of the final ball y over all episodes of that run (`flight_tracker.py` ~l.197; final y, not y at landing, and not normalised by distance). `mean_y` is its mean; +y = left. `left/right_miss` = |final y| > 0.5 m. Because it is a std over final y, a few outliers dominate it at N=50-100, and it grows with carry.
- Launch angle = mean `launch_elev_deg` (separation-velocity based); `launch_flat_flag` marks flat/exploit launches.

## 2. Env kwargs source
- If `results/<name>.json` has `env_kwargs_full` (all v5 imitation runs: imit*), those kwargs are used verbatim (`residual_scale`, `script_weight`, `learn_scale`, `force_scale`, address distribution, impact model, `flight_steps`, ...). Otherwise `eval.env_factory.resid_kw_from_args(args)` rebuilds them from the run's `args` (older runs; missing flags fall back to env defaults, and the leaderboard says so in its provenance column). `track_weight` and `track_set` are forced off for evaluation.
- `GATE_OVERRIDE` (JSON env var) overrides kwargs for a gate run (e.g. a different `elbow_base`); it is recorded in the output's `env_kwargs`. Gate numbers produced with an override are not comparable to plain gate numbers.
- Reference-joint lookup is by joint name (`env._ref_q`, `HumanoidGolfEnv.REF_JOINTS`), not by positional qpos slice.

## 3. `eval/eval_gate.py` (headline gate)
`python -m eval.eval_gate <name> [episodes=50] [seed=4000] [min_carry=11.98]` (env `EVAL_WORKERS=N`, `GATE_OUT=<dir>`).
- Runs three evaluations of the same N episodes: `policy_det`, `policy_stoch`, `scripted_zero_residual`. The runs used for the committed gates are N=100 and seeds 4000, 8000, 9000 (episode seeds seed..seed+99).
- Output: `results/gate_<name>.json` for seed 4000 (no suffix), `results/gate_<name>_seed<seed>.json` otherwise (Trainer's copies sit in `results/imit_private/`). Note that the seed-4000 file has no seed in its name; the repo copies a `_seed4000` duplicate where needed.
- `tier(m, carry_min, lo, hi)`: contact_rate >= 0.99 AND lateral_std <= 2.73 m AND lo <= mean launch <= hi AND mean carry >= carry_min AND landed_fraction >= 0.90.
- `gate_pass` (HEADLINE) = tier(det, min_carry, 5-20 deg) AND tier(stoch, same). `gate_pass_showcase30` = same with carry >= 30 m and launch 8-14 deg. `gate_pass_legacy` = det carry > 11.98 m, lateral < 2.73, contact >= 99% (old teammate baseline; a very weak floor under the 450-step horizon).
- "Full 3-seed headline" = `gate_pass` true on every one of seeds 4000/8000/9000. A single-seed pass is not reported as a headline.

## 4. `eval/leaderboard.py` (leaderboard protocol)
`python -m eval.leaderboard --workers 2` (defaults: **50 episodes**, seed base 4000, i.e. seeds 4000..4049; workers capped at 2).
- Every model is run det and stoch with the env kwargs of section 2; results cached in `results/leaderboard_cache.json` (git-ignored) keyed by checkpoint md5 + env fingerprint + episodes + seed + config hash.
- Qualification (`qualify_criterion` in leaderboard.json): contact 100% in BOTH modes, det mean carry >= 30 m, det lateral std <= 2.73 m, det launch not flat (>= 5 deg).
- **Differences from the headline gate:** N=50 vs 100 and a single seed base vs three seeds; contact must be 100% in both modes (gate: >= 99%); the lateral and carry criteria are checked in det only (gate: det AND stoch); no landed >= 90% or launch <= 20 deg test (a flat/lofted flag instead). A model can therefore pass the gate and fail the leaderboard, or the reverse (example: imit16_fs1_dart_s51 passes all three gate seeds but fails the leaderboard on 98% stochastic contact and det lateral std 3.15 m at N=50).
- Rows are labelled with motor strength (`force_scale`: stock = 1, "2x ... hypothetical-strength actuators", power tier) and learned/scripted/blend labels from `script_weight`. The headline names the best stock-motor trained model separately from the best force_scale>1 model.

## 5. Quick noise gate
- `NOISE_SIGMAS = (0.005, 0.01)`, `NOISE_EPS = 10` det episodes, seeds from the seed base. Gaussian noise of that sigma is added to every observation and every action (action clipped to [-1, 1]), seeded per episode (`default_rng(10000 + seed + ep)`).
- Only for models passing a quick contact/carry screen. Noise PASS = contact stays 100% AND mean carry >= 80% of the clean det mean carry. N=10 so it is noisy; always labelled "quick".

## 6. Not part of the protocol / caveats
- Style columns (DTW to references, `track_score`, key_score) are NOT performance measures. The arm columns (cols 0-3) of `dtw_mason_v2` and the shoulder/wrist parts of `track_score` use the lead/trail arm mapping the Trainer found wrong: VOID (see leaderboard.md).
- Launch-monitor numbers (`sim/golf_simulator.py`) and course estimates (`sim/course.py`) are analytic/model-based, not from the MuJoCo rollout.
- `force_scale > 1` results are hypothetical-strength actuators, not human- or robot-attainable.

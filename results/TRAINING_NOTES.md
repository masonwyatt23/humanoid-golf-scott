# Training notes (local; verified against results/*.json and logs/*.log, 2026-10-16)

Models live in `models/*.zip` (gitignored, local only). Eval = 100 randomized-reset episodes unless noted.
"Scripted-only" = same env with zero residual (no learning), reported in each JSON.

## A. Residual PPO on v3 (`train/train_residual.py`, `env/residual_golf_env.py`)
Common (from each JSON `args`): `--model_xml humanoid_golf_v3.xml --flight_model`, loft 6°, q_back 2.2, t_down 0.12,
gate 15→35 m/s (smoothstep), force_scale 2.0, grip=False, ball_dz 0.008 (ladder run; earlier runs predate the flag, value then = default of that time: unknown), lr 3e-4, ent 0, handedness right (ladder run only; earlier = right by default).
Reward gate: contact bonus 1+5·gate, launch-quality bonus, terminal gate·carry/5 − 0.2|lateral|.
NOTE: the "carry" metric definition changed mid-session (ball must exceed 0.10 m height, then touch ground). Total-distance numbers from earlier runs were computed with older logic; r2 JSON was re-evaluated? — unknown. Compare carry/total only within the same row's JSON.

| file | steps | n_envs | seed | residual scale | log_std_init | reward | policy: contact / landed / impact m/s mean (max) / total dist / carry mean (max) / lateral mean±std | scripted-only carry / impact |
|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_s0.zip (results/ppo_resid_v3_s0.json, ..._v1reward.json identical copy) | 60k | 8 | 0 | 0.4,0.4,0.4,0.25 | default (not recorded; arg absent) | v1 (early-contact bonus; reward-hacked) | 100% / 0.83 / 1.5 (3.4) / 1.2 m / 0.84 (8.5) / +0.55±5.0 | 10.3 m / 26.6 |
| ppo_resid_v3_r2_s0.zip | 60k | 8 | 0 | 0.2,0.2,0.2,0.1 | -1.5 | gated (v2) | 100% / 0.22 / 30.3 (48.2) / 44.0 m / 0.32 (8.2) / -0.69±11.05 | 10.3 / 26.6 |
| ppo_resid_v3_r3_s0.zip | 100k | 4 | 0 | 0.2,0.2,0.2,0.1 | -1.5 | gated (v2) | 100% / 0.35 / 30.5 (48.6) / 46.4 m / 1.12 (73.0) / -1.0±7.25 | 11.0 / 26.6 |
| ppo_resid_v3_ladder_s0.zip | 150k | 6 | 0 | 0.2,0.2,0.2,0.1 | -1.5 | gated + speed ladder + seq_weight 1.0 | 100% / 0.20 / 31.9 (49.8) / 57.3 m (max 120.1) / 0.24 (5.6) / -0.25±4.93 | 6.6 / 27.1 |

Exact commands (reconstructed from JSON args; the shell history itself was not saved):
- r2: `python -m train.train_residual --timesteps 60000 --flight_model --n_envs 8 --name ppo_resid_v3_r2_s0 --seed 0 --res_scale 0.2 --log_std_init -1.5` (res_scale/arg spelling as in train_residual.py; the JSON shows the resulting values)
- r3: same with `--timesteps 100000 --n_envs 4 --name ppo_resid_v3_r3_s0`
- ladder: `python -m train.train_residual --timesteps 150000 --flight_model --n_envs 6 --ladder --seq_weight 1.0 --name ppo_resid_v3_ladder_s0 --seed 0`
- s0 (v1 reward): 60k, 8 envs, seed 0, res 0.4; the reward code was later changed, so this exact run is not reproducible from current HEAD (git history only).
- `logs/resid_v3_r3_s1.log` = a seed-1 run killed early (to keep one job at a time); no model/results saved.

Honest read: impact speed mean ~30–32 m/s (above the 30 m/s milestone) with 100% clean contact, but mean carry is ~0–1 m: launch elevation/dispersion under randomization is unresolved, and the ladder policy's carry (0.24) is *worse* than its scripted baseline (6.6). Best-by-carry is therefore still the scripted swing, not a trained policy; no `models/best_*.zip` was created because no trained model improved carry.

## B. Original-model PPO (`train/train_ppo.py`, legacy env) — all weak; ball hardly moves
Common: curriculum on, pin_torso, address_pose fixed. Fields from JSON `args`.
| file | steps | envs | seed | extra flags | result (100 eps unless noted) |
|---|---|---|---|---|---|
| ppo_scott_baseline.zip | 30k | 4 | ? unknown | original legacy reward, no curriculum | true contact 0% (legacy "100% contact" flag was a bug); ball ~0.35 m (from log; no JSON) |
| ppo_scott_curr.zip | ~30k | 4 | unknown | curriculum, fixed pose, pin_torso | 100% contact, 8.67 m rolling, carry 0 (teammate-reported ~10.7 m is a different eval; not reproduced) |
| ppo_scott_prev_backup.zip | 30k | 4 | 0 | torque_scale 3 | 50 eps: contact 100%, dist 1.92 m, ball peak 0.41 m/s |
| ppo_scott_final2.zip = ppo_scott_prev2_backup.zip | 60k | 4 | 1 | torque_scale 3, randomize_reset, forward_reward | contact 92%, dist 2.40 m (max 12.0), lateral -0.30±1.60 |
| ppo_scott_carry1.zip = ppo_scott.zip (same size/time ±1 min) | 100k | 4 | 2 | torque_scale 4, randomize_reset, forward_reward, carry_reward, ball_damping 0.05, action_smoothing 0.3, shoulder_range 150° | contact 92%, dist 0.47 m, carry max 0.62, impact speed 0.09 m/s, lateral 0.006±0.06 |
Model XML for B: original `env/models/humanoid_golf.xml` (the `--model_xml` flag is not yet in train_ppo.py). Caveat: results/train_scott.json was re-modified in the working tree after my run (not by me, to my knowledge) — treat as unverified.

## C. Not models
Physics probes: `results/physics_probe.json`. G1+club: scripted-swing core only, untuned (stock peak ≈ 17–28 m/s, elite ≈ 19–27 m/s head speed, contact rare); no G1 policy trained. Elite tier is hypothetical.

## D. Stage 3 (2026-10-16 AM): lockout + analytic carry + left-handed + mirrored Mason style
Code state: units patch applied (ae3cb82); contact lockout, analytic ball, style/lat/elev/az weights in e394f9f and later commits (each run's JSON stores `git_head` for runs after this stage began).
### Diagnosis of "balls don't land / launch" (eval/diag_launch.py, eval/scan_loft.py)
1. **Fake contacts**: with reset randomization the club touched the ball at address/backswing in most episodes (impact speed 0.0, ball pushed a few metres). That produced the old "100% contact" with ~0 impact and "carry" of a few m. Fix: `_lockout()` keeps the ball pinned and ignores contact until `t_hold+t_back+t_pause-0.02` s (default in ResidualGolfEnv). With it, every strike is a real hit: impact 48.2 m/s (108 mph) scripted.
2. **Episode ended before landing**: max_steps was swing+200 steps (4 s); high launches (30–40°) were still airborne. Fixed: `flight_steps` default 450 (episode still ends on landing). NOTE this changes the evaluator's scripted baseline (see below).
3. **Flat/low strikes** never exceed 0.10 m height, so the "landed after flight" rule counts them as carry 0 (they roll ~150 m). Launch is bimodal under randomization (≈0–3° vs 30–40°) depending on where in the arc the face meets the ball; loft barely moves the flat mode.
4. Scripted loft scan (analytic carry, 40 eps, loft deg → mean carry m / mean launch elev): 6→26/7°, 10→66/24°, 14→89/34°, 18→91/33°, 22→99/31°.
### Analytic ball (`analytic_ball=True`)
At 3 steps after first true contact the MuJoCo ball velocity is passed to `env/ball_flight_analytic.py` (verbatim copy of teammate prototype /workspace/sim_proto/ball_flight.py; drag+Magnus, dt 0.005, t_max 12 s) with an ASSUMED backspin = clip(1500+70*elev_deg, 1000, 5000) rpm (not measured; no sidespin). Carry/lateral/apex come from that; the episode terminates there (short, fast episodes). Reported `carry`/`ball_lateral` in these runs are therefore ANALYTIC and not comparable to MuJoCo-landing carry. Lateral is in golfer frame (sign flipped for left-handers).
### Runs (all: v3 XML, left-handed, loft 8°, q_back 2.2, t_down 0.12, 150k steps, 6 envs, lr 3e-4, log_std_init -1.5, seq_weight 1.0, style_ref = mason_swing_part1_s05_refined_mirrored.npz, style_weight 1.0, force_scale 2, gate 15→35, no speed ladder (scripted already 48 m/s))
| model | seed | res_scale | lat_w | elev_w | az_w | policy (100 eps, analytic): contact / landed / carry mean (max) / lateral mean±std / impact m/s (mph) / launch elev / style | scripted zero-residual same env |
|---|---|---|---|---|---|---|---|
| ppo_resid_v3_left_an1_s0 | 0 | .2 .2 .2 .1 | 0.2 | 0 | 2 | 100% / 100% / 93.1 (142) / +0.63±6.61 / 51.0 (114.0) / 34.6° / 0.55 | carry 49.3, lat −0.20±5.11, 48.2 (107.9), elev 16.3°, style 0.62 |
| ppo_resid_v3_left_an2_s0 | 0 | .1 .1 .1 .03 | 1.0 | 1.0 | 3 | 100% / 100% / 91.8 (141) / +0.12±6.53 / 51.3 (114.7) / 33.5° / 0.53 | same |
(an3 below if finished.) Commands: `python -m train.train_residual --timesteps 150000 --flight_model --n_envs 6 --seq_weight 1.0 --name <name> --seed <s> --loft 8 --analytic_ball --elev_target 12.5 --handedness left --style_ref data/references/mason_swing_part1_s05_refined_mirrored.npz --style_weight 1.0 [--res_scale ... --lat_weight .. --elev_weight .. --az_weight ..]`
### Evaluator-protocol gate (`python -m eval.eval_gate <name> 50 4000`, MuJoCo physics, flight tracker, flight horizon 450 steps, deterministic) 
| model | contact | landed | carry m | lateral std m | peak club mph |
|---|---|---|---|---|---|
| scripted zero residual (loft 8, left) | 100% | 72% | 57.8 | 4.22 | 107.9 |
| left_an1_s0 | 100% | 100% | 110.3 | 7.53 | 114.5 |
| left_an2_s0 | 100% | 100% | 114.3 | 7.42 | 114.7 |
Teammate gate (carry > 11.98 m AND lateral std < 2.73 m, from their 4-s-horizon, loft-6 evaluator): carry passes by ~10x, lateral std FAILS in absolute metres, but that gate compares across different horizons: with a 4-s horizon most balls never "land", so their carry/lateral were measured on ~1/3 of shots at ~12 m. Lateral std grows with distance; relative dispersion (lateral std / mean carry) is 0.073 (scripted, 4.22/57.8) vs 0.066 (an2, 7.42/114.3). `models/best_carry_analytic.zip` = left_an2_s0 (best carry; does NOT pass the absolute lateral gate).
Caveats: launch elevation stays ~33° (policy prefers high launch; the analytic spin assumption rewards it) – not the 10–15° target; smash drops 0.90→0.73 (policy trades smash for loft). Mason style score (shape match of trail-shoulder-pitch, 2D proxy) is neutral/slightly lower (0.62→0.53–0.55).

### CORRECTION (found 05:55 ET): lat_weight / elev_weight were NOT active in runs an1–an4
A string replace in `ResidualGolfEnv` silently failed, so the terminal reward used a fixed `-0.2*|lateral|` and no elevation penalty in left_an1, an2, an3 and an4 (the `--lat_weight/--elev_weight` values in the table above and below were recorded in args but had no effect; `--az_weight` and `--carry_cap` DID work). Fixed in the commit "FIX: lat_weight/elev_weight...". That explains why launch elevation stayed ~30–36° and lateral std did not improve. Effective differences between an1–an4 are therefore: res_scale, az_weight, seed, loft, style ref, carry_cap only.
Extra runs:
| model | seed | loft | res_scale | style_ref | az_w | carry_cap | policy (100 eps analytic): landed / carry mean (max) / lat mean±std / impact m/s (mph) / elev / style | scripted same env | evaluator-protocol gate (50 eps, seed 4000, det): carry / landed / lat std / mph |
|---|---|---|---|---|---|---|---|---|---|
| left_an3_s1 | 1 | 8 | .1 .1 .1 .03 | mirrored p1_s05 | 3 | 150 | 100% / 87.9 (142) / +0.85±5.91 / 51.3 (114.8) / 30.0° / 0.52 | 49.3 | 108.6 / 100% / 6.74 / 114.6 |
| left_an4_s2 | 2 | 7 | .1 .1 .1 .03 | native-left mason_v2_p1_s06 (trail col 4) | 3 | 70 | 100% / 78.8 (117) / +0.48±5.87 / 49.8 (111.5) / 36.2° / 0.88 | carry 43.0, lat −0.28±3.61, elev 14.4°, style 0.91 | 96.1 / 100% / 6.68 / 111.7 (scripted: 48.1 carry, 54% landed, lat std 3.97) |
All an* runs: 150k steps, 6 envs, lr 3e-4, log_std_init -1.5, seq_weight 1, force_scale 2, gate 15→35, `--analytic_ball --elev_target 12.5 --handedness left`. Absolute lateral gate (<2.73 m) still FAILS for all; the zero-residual scripted swing also fails it at these carries (3.6–5.1 m analytic).
Style ref note (mason_v2): v2 files use anatomical columns (right_* = LEAD arm for a lefty), so the trail/club arm shoulder pitch is col 4 (valid up to impact only). Loader `style_ref=mason_v2_recommended` averages the 10 flagged files (recommended, not partial, not mirrored, self_owned, commercial_ok, handedness left); excluded: unknown-license files, `*_unmirrored`, partials. Style is shape-only (normalised backswing/downswing trail-shoulder-pitch).

### Runs an5, an6 (weights fixed; verified from results/*.json and results/gate_*.json)
Common: v3 XML, left, loft 7, 150k steps, 6 envs, lr 3e-4, log_std_init -1.5, seq_weight 1, style_ref mason_v2_p1_s06.npz (style_weight 1), res_scale 0.1 0.08 0.05 0.03, az_weight 3, `--analytic_ball --elev_target 12.5`.
| model | seed | lat_w | elev_w | carry_cap | policy analytic (100 eps): carry mean / lat mean±std / elev / peak club m/s (mph) / landed | evaluator-protocol gate (50 eps det): carry / landed / lat std / mph |
|---|---|---|---|---|---|---|
| left_an5_s3 | 3 | 1.0 (m) | 3.0 | 70 | 19.4 / +0.02±0.01 / −2.8° / 52.4 (117.2) / 100% | 9.6 / 72% / 0.14 / 117.0 |
| left_an6_s4 | 4 | 0.5 (% angular, `--lat_angular`) | 2.0 | 100 | 89.1 / +0.55±6.63 / 34.0° / 50.5 (112.9) / 100% | 99.8 / 98% / 6.95 / 113.0 |
Reading: an5 found a degenerate flat/negative-launch optimum (lateral metres penalty is ~0 for short flat shots, i.e. the metre-based lateral penalty can be gamed by not flying). an6's angular penalty removed that exploit but the policy returned to the high-launch mode (34°, smash 0.73) with lateral std ~6.6. Neither passes the gate (an5 fails carry>11.98 under evaluator protocol and launch ≥5°; an6 fails lateral). Launch is bimodal: clean strike (scripted: 14°, smash 0.90) vs heel/toe-like high strike (30–40°, smash ~0.7) that the carry reward prefers.

### Address-geometry finding (08:40 ET; scripted zero-residual, loft 7, left, tee 0.04, ball_dz 0.008; 60 eps analytic unless noted)
Launch elevation and dispersion are governed by WHERE along the swing arc the face meets the ball (ball_x), not by loft or tee height (tee_height also raises the torso, so elevation is identical for tee 0.04 and 0.06):
| ball_x (m) | x-noise | carry (analytic) | elev | lateral std | smash |
|---|---|---|---|---|---|
| 0.36–0.415 (20 eps, ±3 mm) | | 83–93 | 27–38° | 5–9.4 | 0.71–0.93 | (high, erratic mode)
| 0.42 | ±5 mm | 70.5 | 20.3° | 3.65 | 0.92 |
| 0.422 | ±5 mm | 60.5 | 14.7° | 2.09 | 0.91 |
| 0.425 (20 eps, ±3 mm) | | 25.1 | 2.8° | 0.0 | 0.91 | (flat mode)
| 0.43–0.44 (20 eps, ±3 mm) | | 2–9 | 0–0.5° | 0.0 | 0.89–0.92 |
The transition from 15° to ~0° happens within ~5 mm of ball position, i.e. the swing arc's low point is just past the ball and the head is descending steeply at contact — with the default ±3 cm x-noise the strike lands in different regimes, which is the dispersion source (and why policies flatten to the stable flat mode). A physically sensible fix is ball placement (a slightly more rearward/consistent ball position, ~1 cm tolerance is unrealistic for a human but plausible for a robot with a placement guide) and ultimately a shallower arc (more wrist release / lower shaft lean), not tee height. Loft 9 at 0.42 gives 35° (too high).
Evaluator-protocol check of scripted zero-residual at `ball_x=0.422, ball_x_noise=0.005, loft 7` (`python -m eval.eval_scripted_cfg '{"ball_x":0.422,"ball_x_noise":0.005}' 50 4000`, MuJoCo, 450-step horizon): contact 100%, carry 53.1 m, landed 80%, launch 11.0° mean (std 11.3, 42% flat), lateral mean −0.20 / std 1.98 m, peak club 48.2 m/s = 107.8 mph, smash median 0.92. This PASSES carry>11.98 & lat std<2.73 with zero learning (but not 120 mph, and noise is ±5 mm instead of ±3 cm).

### Runs an7–an10 (analytic eval, 100 eps, deterministic; verified from results JSON). Common: left, loft 7, v3, mason_v2_p1_s06 style, seq_weight 1, `--analytic_ball --elev_target 12.5`, az_weight 3
| model | seed | steps | ball_x / x-noise | res_scale | lat_w (ang.) | elev_w × low_mult | carry_cap | other | contact | landed | carry mean | lateral mean/std | elev | peak club m/s (mph) | scripted-only same env |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left_an7_s5 | 5 | 120k | .43/.03 | .04 .04 .03 .02 | 1.0 | 2×1 | 45 | | 100% | 100% | 19.9 | −0.04/0.01 | −1.8° | 51.5 (115.2) | carry 43.0, lat 3.61 |
| left_an8_s6 | 6 | 120k | .40/.015 | .1 .08 .05 .05 | 1.0 | 4×1 | 70 | | 100% | 100% | 24.4 | −0.02/0.01 | −1.3° | 53.0 (118.5) | carry 88.6, lat 7.36 |
| left_an9_s7 | 7 | 120k | .43/.015 | .1 .08 .05 .05 | 1.0 | 4×3 | 60 | ent .005, log_std_init −1 | 100% | 100% | 85.3 | +1.59/6.61 | 33.9° | 49.4 (110.5) | — |
| left_an10_s8 | 8 | 120k | .422/.005 | .1 .08 .05 .05 | 1.0 | 3×2 | 70 | ent .003 | 100% | 100% | 92.7 | +1.46/5.74 | 34.4° | 47.9 (107.2) | carry 61.3, lat 2.18, elev 14.5°, 107.8 mph |
Evaluator-protocol gate (50 eps, seed 4000, det): an9 carry 103.3 / landed 100% / lat std 8.17 / 110.4 mph (FAIL lateral); an7/an8: not gate-run (MuJoCo-protocol carry for flat shots is ~10 m and they fail launch ≥5°).
Key observation (an10): the stochastic policy (eval with sampling) reproduces the training numbers (carry ~60, elev 22°, 40 eps) while the DETERMINISTIC policy flips to the high regime (carry 91, elev 35°, lat std 4.9). The strike regime is discontinuous in the action (≈5 mm of effective arc position), so the mean action is not a good proxy for the sampled policy. And in an10 the trained policy is WORSE than its own scripted baseline on lateral (5.7 vs 2.18) and elevation (34° vs 14.5°), i.e. residual PPO is not improving the best address-tuned scripted swing yet.
Flat-mode policies at other ball positions (deterministic, ±5 mm noise, 30 eps; ball_x → carry analytic / lat std / elev / mph): an8_s6: 0.30 → 33.1/0.03/−2.2°/117.0; 0.33 → 31.1/0.03/−0.3°/117.3; 0.35 → 29.4/0.02/−2.4°/117.7; 0.37 → 26.6/0.02/−1.5°/118.1; 0.39 → 24.0/0.01/−1.5°/118.4. an7_s5 similar (24–30 m, lat ≤0.66, 114–115 mph). These satisfy contact 100%, carry ≥ ~30 m (an8 at bx ≤ 0.33), lat std ≤2.73, but NOT launch ≥5° (negative launch; the analytic "carry" for a ball launched slightly downward from a 6 cm tee is first-bounce distance and should not be read as flight carry).

### Scripted-swing speed/launch scan (no learning; left, tee 0.04, force_scale 2, q_back 2.2; 20–30 eps; analytic) — 09:30 ET
Shorter scripted downswing (`t_down`) raises club speed: t_down 0.12 → 107.8 mph; 0.10 → 117.7; 0.095 → 119.8; 0.09 → 122.8 mph (force_scale 2.5/3 at 0.12 changes nothing: 108.05/108.07 mph, so speed is set by t_down/q_back, not torque cap). But a faster swing makes the strike flatter (dynamic loft falls): at t_down 0.09 launch is −4 to −6° for loft 7 at any ball_x 0.28–0.415; raising loft restores it but with a sharp regime cliff: t_down 0.09, bx 0.40: loft 13 → 0.0° (lat 2.36), loft 16 → 5.0° (lat 4.13, carry 49, 122.8 mph), loft 17 → 16.8° (lat 5.6), loft 20 → 32° (lat 9.9). Rule observed everywhere: launch ≥ ~5° comes with lateral std ≳ 3 m; flat launch comes with lateral ≈ 0.
Best scripted candidate (t_down 0.095, loft 9, ball_x 0.39): 30 eps looked passing (carry 40.5, lat 2.46, 5.4°, 119.8 mph) but 100-episode checks do NOT hold the lateral gate: noise ±3 mm seeds 5000/9000: carry 44.8/48.2, lat std 3.03/3.97, elev 6.8/8.9°, 119.8 mph, contact/landed 100%; noise ±5 mm: carry 44.3/46.0, lat 3.05/4.57. Evaluator protocol (50 eps, seed 4000, ±3 mm): contact 100%, MuJoCo carry 31.9 m, landed 98%, launch (separation) mean 0.2° with 86% flat flag, lateral std 9.0 m (one 61 m outlier), 119.8 mph, smash 0.83. => no config passes all of launch≥5°, lat≤2.73, 120 mph yet. The passing scripted config remains t_down 0.12, loft 7, ball_x 0.422, ±5 mm (107.8 mph, carry 53 m, lat 1.98, launch ~11°).

### an11 and fast1
- left_an11_s9 (warm start from an8_s6, ball_x .40 ±5 mm, lat_w 1.5 ang., elev_w 5×3, carry_cap 80, lr 1e-4, 100k planned): KILLED at ~30k steps (training carry stuck ~25 m, i.e. still the flat mode); no model/results saved (log `logs/resid_v3_left_an11_s9.log` only).
- left_fast1_s10: base scripted t_down 0.095, loft 9, ball_x 0.39 ±5 mm, `--res_scale 0.02 0.02 0.01 0.02`, lr 1e-4, log_std_init −2, 100k steps, 6 envs, seed 10, seq_weight 0.5, style p1_s06 weight 0.5, elev_target 10, lat_w 1.5 (angular), elev_w 2 × low_mult 2, az 3, carry_cap 50. Policy (100 eps, analytic): contact 100%, landed 100%, carry 28.6, lateral +0.01/0.02, launch −4.6°, 54.6 m/s = 122.2 mph, smash 0.89. Scripted base in same env: carry 44.3, lat −0.25/3.05, launch 7.1°, 119.8 mph. => even ±0.02 rad residuals flip the strike into the flat regime; the reward then preferred it (flat: lateral penalty 0 vs scripted ≈10 pts; elevation penalty only ≈6). Reward-balance issue, addressed in fast2 (elev_w 6, lat_w 1).

### left_fast2_s11 (10:00 ET) — base scripted t_down 0.095, loft 9, ball_x 0.39 ±5 mm; res_scale 0.02 0.02 0.01 0.02; lr 1e-4; log_std_init −2; 100k steps; 6 envs; seed 11; seq_weight 0.5; style p1_s06 w 0.5; elev_target 10; lat_w 1.0 (angular); elev_w 6 × low_mult 2; az 3; carry_cap 50; `--analytic_ball`
Policy (100 eps analytic): contact 100%, landed 100%, carry 31.3, lateral −0.03/0.04, launch −5.3°, peak club 55.2 m/s = 123.6 mph, smash 0.89.
Evaluator-protocol gate (50 eps, seed 4000, det): contact 100%, landed 100%, MuJoCo carry 15.2 m, lateral −0.01/0.017, launch (separation) −5.8° (100% flat flag), 123.6 mph; scripted base in same protocol: carry 30.0, lat std 2.92, 119.8 mph. Passes the teammate's literal gate (carry>11.98 & lat<2.73 & contact≥99%) but FAILS launch ≥5° (negative). Saved as `models/best_gate_flat_123mph.zip` (gitignored) — LABEL: passes carry/lateral/speed, not launch; do not present as a good drive.
Conclusion: in this env the strike regime is a cliff in effective arc position: faster swings (t_down ≤0.095) are flat/negative unless loft is raised, and raising loft/moving the ball so that launch ≥5° brings lateral std ≥~3 m (scripted) – every learned residual (even ±0.02 rad) converges to the flat, laterally-perfect regime or the high, laterally-scattered one, never the narrow band between. Likely causes to fix next: (1) swing arc/low point (club descends steeply at the ball; add wrist release/hand-path control and shaft lean to the script rather than shoulder-only pendulum), (2) reward is computed from launch 3 steps after contact (ball may still be in face contact) – use separation velocity as the evaluator does, (3) discontinuity makes PPO's mean action unreliable (stochastic ≠ deterministic eval).

## Stage 4 (10:15–13:00 ET): shallower-arc scripted swing, separation-velocity launch, per-shot analysis
Code (commits after c19a62a): scripted wrist release/elbow params (`wr_rel_start`, `wr_rel_end`, `wr_end`, `el_end`), yaw feed-forward from ball-y offset (`yaw_ff`), ball separation velocity captured at substep level (`_sep_v`; used for the launch bonus, analytic flight and reported launch/elevation instead of +3 steps), tools `eval/scan_cfg.py` (parallel grid), `eval/shot_dist.py` (per-shot distribution), `configs/fast_scripted_v1.json`.
Findings (all scripted zero-residual, left, `t_down` 0.095 ≈ 120 mph, 24–100 eps):
1. Wrist release is a strong, monotonic-ish launch control but extremely sensitive: `wr_end` +0.05/+0.1 rad → launch −7°/−10°; 0 → ~0°; −0.01 → 18°; −0.05 → 35°; −0.1 → 48° (bx 0.40); ±0.3 rad misses the ball entirely (0% contact). Negative values also add ~2–5 mph (up to 125 mph at −0.1).
2. Launch azimuth correlates 0.93 with the ball y offset (±2 cm). Feed-forward yaw (`yaw_ff` −3 rad/m on chest yaw, ramped over the backswing) cuts lateral std 6.1 → ~3.1 m (100 eps, wr_end −0.01, ball_x 0.40, loft 9; yaw_ff −1.5/+1.5/+3 were 4.2–7.5, 3 seeds non-monotonic).
3. With wr_end −0.01, yaw_ff −3, ball_x 0.396, loft 8 (±3–5 mm x-noise), mean metrics over 4 seeds × 100 eps: contact 100%, carry 38–50 m, mean launch 9–13.5°, lateral std 2.05–2.62 m, peak club 120.4 mph (53.8 m/s), smash ~0.9. Variants loft 7.5/7.0 at ball_x 0.395–0.396 similar (launch 6–9°, lat 2.0–2.7).
4. BUT per-shot distribution (eval/shot_dist, seed 5000, 100 eps): launch percentiles 5/25/50/75/95 = −2.4/−1.0/0.2/28.3/34.6°; 59% of shots <3°, 32% >25°, 0% between 5 and 20°; carry median 10.9 m, only 41% ≥30 m. The "means" in item 3 are averages of two regimes (flat with ~0 lateral, high with large lateral) — NOT a pass. Evaluator protocol (MuJoCo, 50 eps seed 4000): launch mean 11.5°, 62% flat flag, lateral std 6.3 m, landed 58%, left/right miss 34%/50%, 120.4 mph.
5. The regime split persists with ZERO ball-x noise (ball_x 0.392–0.4: 46–92% flat, rest ~34°), so it is not just x-placement: it follows the other reset randomization (shoulder pitch ±0.05, elbow ±0.1, ball y ±2 cm; regime correlation with initial shoulder pitch −0.31, elbow −0.24, y −0.11, x 0.0). Strike height/position on the face switches discontinuously between "ball struck low on the face (flat)" and "struck high (34°)" with no intermediate loft.
Earlier-stage means in this notes file that were computed from means over mixed regimes (e.g. scripted t_down 0.095/loft 9/ball_x 0.39 "carry 40, lat 2.46, 5.4°") should be read with this caveat. The only per-shot-consistent passing config remains t_down 0.12/loft 7/ball_x 0.422 ±5 mm (107.8 mph; its launch is also bimodal in the evaluator protocol: 42% flat flag).
Not done: tiny-residual PPO and stochastic-vs-deterministic split on the new base (stopped because the base itself is bimodal; PPO would again optimise the mixture). `train_residual` evaluates deterministic only; `eval/eval_gate.py` has deterministic only — stochastic eval of an10 was done ad hoc (carry 59.7/elev 22° vs det 91.4/35°).

## Stage 5: root cause of the flat/high bimodality, and a passing scripted base (verified)
Contact probe (club-local contact pos/normal at first touch): with loft +8 and ball_dz 0.005-0.007 the ball touches the very top edge of the face (local z 0.025-0.027 of half-height 0.03); at ball_dz 0.010 it hits the head's top surface (normal local -z) => constant ~35 deg "launch". The head passes ~2-3 cm below the ball centre, so the old "high regime" was a crown/edge mis-hit and the "flat regime" a top-edge clip. Not a physical drive.
Fix: in the v3 model **negative loft_deg = more loft** (positive loft closes the face: loft +8..+28 at ball_dz -0.01 gives launch -6..-16 deg). With ball_dz -0.01, launch is smooth in loft: 0 -> 0.2, -4 -> 2.0, -8 -> 3.7, -12 -> 5.3, -16 -> 7.0, -20 -> 8.5, -26 -> 10.8 deg (analytic, sep-velocity, 30 eps). yaw_ff = 0 gives lateral std ~0 (yaw_ff -3 was compensating the old edge strike).
Config configs/fast_scripted_v2_lofted.json (t_down 0.095, q_back 2.2, wr_end -0.01, yaw_ff 0, ball_x 0.396 +-3 mm, ball_dz -0.01, address noise sh 0.05/el 0.1). Zero residual, left-handed.
Analytic ball (separation velocity, assumed spin), 100 eps each, seeds 5000/6000/7000, contact 100%, 120.4 mph (53.8 m/s) peak club speed:
- loft -26, full noise: median launch 10.8 deg, p5 7.1; carry 137-140 m; lat std 0.01-0.01 (one seed 1.24 w/o sh noise); carry>=30 m in 96-99% of shots.
- loft -22, full noise: median launch 9.2 deg, carry 125-128 m, lat std 0.01-1.37, carry>=30 95-99%.
Evaluator protocol (eval.eval_scripted_cfg, MuJoCo flight tracker, no spin model), 100 eps, seeds 4000/8000:
- loft -26: contact 100%, launch 9.3/9.5 deg (std 2.7/2.4), mean carry 70.0/71.9 m, landed 98/99%, lateral std 0.013 m, 120.3 mph (53.8 m/s).
- loft -22: contact 100%, launch 7.5/7.8 deg, carry 50.6/51.1 m, landed 96/97%, lateral std 0.011/0.28 m, 120.4 mph.
Caveats: lateral std is tiny because the model has no sidespin and the swing is deterministic in the lateral plane; ~4-9% of shots are low-launch (2-5 deg) outliers from address noise; carry in the analytic metric depends on assumed spin. Residual PPO was NOT run on this base (it already meets all criteria; earlier PPO never beat scripted). All old results using positive loft/ball_dz>=0 should be treated as edge-strike artefacts.

## Stage 6: outlier cause, carry vs launch/loft tradeoff (evaluator protocol = PRIMARY), config v3
Outlier diagnosis (eval/outlier_diag.py, 200 eps): low-launch shots correlate with elbow reset noise (r=0.50) and shoulder noise (0.26), not ball x/y: address pose shifts head height, and at ball_dz -0.01/loft -26 the strike sits near the lower-face cliff (ball_dz -0.014 => only 36% good shots; -0.02 => all negative launch).
Evaluator-protocol lateral spread comes from contact-generated sidespin/backspin in MuJoCo (corr with spin wz 0.74, wx -0.71; uncorrelated with ball y) and grows as the ball is struck higher on the face (dz -0.003: lat std 7-10 m; -0.01: 0.01 m). Window: dz ~ -0.008 trades outliers vs lateral.
Evaluator protocol (eval.eval_scripted_cfg, 100 eps, seed 4000 unless noted; t_down .095, yaw_ff 0, ball_x .396+-3mm, default sh/el noise), peak club 120.3 mph (53.8 m/s), contact 100%:
loft -26 dz -.003: launch 10.0, carry 86.0, lat 7.0 | -30/-.003: 11.7, 119.5, 10.7 | -34/-.003: 13.7, 144.3, 7.0
loft -28 dz -.009: 10.6, 86.0, 0.21 (landed 99%) | -28/-.007: 10.9, 90.8, 1.39
loft -30 dz -.009: 11.1, 94.4, 0.20 (landed 96%, flat 4%) | -30/-.007: 11.8, 109.2 (s8000 105.3, s9000 102.0), lat 2.09/2.46/1.48
loft -32 dz -.009: 11.3, 104.8, 0.06 (landed 91%, flat 9%) | -32/-.007: 12.7, 125.8, lat 2.77 (fails)
loft -30 dz -.008: s4000 launch 11.7, carry 105.0, lat 1.42; s8000 102.7, 0.38
loft -31 dz -.008 (**configs/fast_scripted_v3.json**): s4000 launch 12.17 (std 1.37), carry 113.0 (median 109.0), lat 2.12, landed 100%; s8000 launch 12.21, carry 110.6, lat 1.60, landed 100%, flat 0%, 120.3 mph.
MuJoCo flight has no designed spin model so these carries are conservative relative to the analytic ones (secondary).

## Stage 7: tiny-residual PPO on configs/fast_scripted_v3.json (ppo_v3tiny_s21/22/23) — NEGATIVE result
Config (all 3 seeds identical except --seed 21/22/23): 60k steps, n_envs 2, lr 1e-4, log_std_init -2, res_scale 0.01 x4, analytic_ball training env (episode ends at ball separation; launch/carry from separation velocity, ASSUMED spin) + flight_model for the gate eval, left-handed, loft -31, ball_dz -0.008, ball_x .396 +-3 mm, t_down .095, script wr_end -0.01 yaw_ff 0, sh/el address noise 0.05/0.1, reward: lat_angular lat_weight .2, elev_target 11 elev_weight .5, carry_cap 160. Checkpoints models/ppo_v3tiny_s21..23.zip (gitignored; NOT promoted to best_*; none passes). Logs: logs/v3tiny_s2*.log. (First launch without OMP_NUM_THREADS=1 was killed: load avg 34, ~10x slower.)
Evaluator protocol (eval.eval_gate, MuJoCo flight, 100 eps, seed 4000) = PRIMARY; contact 100% everywhere:
| model | mode | carry m | landed | lat std m | launch mean (std) | flat-launch frac | mph |
| scripted v3 (zero residual) | det | 113.0 | 100% | 2.11 | 12.17 (1.37) | 0% | 120.3 |
| s21 | det / stoch | 86.4 / 92.1 | 88% / 91% | 6.45 / 9.88 | 8.7 (7.0) / 9.1 (7.0) | 21% / 18% | 119.0 / 119.1 |
| s22 | det / stoch | 105.1 / 96.0 | 94% / 91% | 5.23 / 8.35 | 10.9 (4.0) / 9.3 (7.0) | 11% / 16% | 118.4 / 118.7 |
| s23 | det / stoch | 93.6 / 96.0 | 87% / 93% | 4.43 / 5.69 | 9.8 (5.7) / 10.4 (5.3) | 16% / 11% | 118.9 / 119.2 |
All gate_pass=False (results/gate_ppo_v3tiny_s2*.json; literal carry>11.98 passes but lateral std <2.73 fails). Analytic metric (secondary, assumed spin, 100 eps, seed 5000, det): scripted carry 153.9, lat 0.04, launch p5/50/95 9.9/12.8/13.6, 100% in 8-14; policies: s21 carry 121.0, 80% in 8-14 (p5 -12.1); s22 140.6, 92% (p5 0.5); s23 131.8, 87% (p5 0.3); stochastic slightly worse (78/84/82% in 8-14). 
Why they fail: even a 0.01-rad residual pushes some shots off the narrow mid-face window (the strike window is only a few mm; the dz -0.014 cliff is nearby), producing 11-21% flat/negative-launch shots that the scripted base never has, plus lateral std 4-6 m (sidespin from off-centre contact; the analytic reward cannot see this since it has no contact-generated spin) and ~1.4 mph less club speed. The analytic training reward is blind to the failure mode that the evaluator penalises, and mean reward is dominated by the 85-90% good shots, so PPO has no gradient toward removing the bad ones. Scripted v3 is strictly better on every metric; stochastic vs deterministic differ by only a few points (stochastic worse on lateral).
Conclusion/next step: use configs/fast_scripted_v3.json as the delivered base (zero residual). A residual is only worth retrying if trained on the MuJoCo-flight (evaluator) reward incl. a per-shot penalty for launch outside 8-14 / lateral > 2.7 and a KL/L2 penalty to zero action, or limited to pre-impact joint offsets that cannot move the strike height (e.g. chest yaw only). Not run (time).

## Stage 8: learned residual that qualifies in BOTH deterministic and stochastic evaluator eval; smash-factor anomaly
**Root cause of ppo_v3tiny failure (found in code review):** the 5th action (tempo) scaled the swing clock by 1+0.3*a[4] regardless of residual_scale, so even a "tiny" policy changed swing timing by several % (strike height is a few-mm window) and stochastic noise (std e^-2=0.14 -> ~4% clock jitter) made it worse. Fix: new env args `tempo_scale` (default 0.3 = old behaviour), `shot_pen`, `act_l2`, `lat_limit`; trainer flags --tempo_scale --shot_pen --act_l2; env_factory passes tempo_scale to eval.
**Runs** (30k steps, n_envs 2, lr 1e-4, log_std_init -3, MuJoCo-flight reward (NOT analytic): carry reward cap 120, per-shot penalty shot_pen 1.0 x [(distance outside 8-14 deg)/5 + max(0,|lat|-2.7)/2.7], act_l2 0.01, lat/elev weights 0, base = configs/fast_scripted_v3.json, left-handed, address noise on):
- ppo_v3flt_yaw_s31 / _s32: residual restricted to chest yaw only (--res_scale 0 0 0 0.05, --tempo_scale 0).
- ppo_v3flt_all_s33: all 4 joints 0.01 + tempo_scale 0.02.
Evaluator protocol (eval.eval_gate, 100 eps, seed 4000; contact 100%, 120.3 mph = 53.8 m/s for all):
| model | mode | carry m | landed | lat std m | launch mean (std) deg | flat frac | gate |
| scripted v3 | det | 113.0 | 100% | 2.12 | 12.17 (1.37) | 0 | pass |
| yaw_s31 | det / stoch | 112.6 / 113.0 | 100/100% | 1.99 / 1.98 | 12.17 (1.36) / 12.17 (1.36) | 0 / 0 | PASS |
| yaw_s32 | det / stoch | 112.6 / 112.3 | 100/100% | 2.09 / 2.01 | 12.17 (1.37) / 12.17 (1.36) | 0 / 0 | PASS |
| all_s33 | det / stoch | 105.0 / 103.0 | 99/95% | 10.23 / 8.49 | 10.9 (5.5) / 10.0 (6.4) | 6% / 12% | fail |
Checkpoints: models/best_learned_yaw_s31.zip (primary), best_learned_yaw_s32.zip (gitignored); gate JSONs results/gate_ppo_v3flt_*.json. HONEST CAVEAT: the yaw-only policies are statistically indistinguishable from the scripted base (carry 112.6 vs 113.0, lateral 1.99 vs 2.12 is within seed noise); they qualify because the residual cannot move strike height, not because PPO found a better swing. Any residual touching shoulder/elbow/wrist/tempo (s33, ppo_v3tiny) degrades the shot.
**Smash factor ~1.0 (eval/smash_probe.py, 10 eps, diagnostic only):** not a code bug. Head 0.20 kg, ball 0.046 kg, but both geoms use solref "0.002 1" (damping ratio 1 = critically damped contact => restitution ~0, a plastic collision), and the head is driven by a stiff position-servo arm (effective mass >> ball), so ball speed ~= club speed. Varying solref[1] of both geoms: damp 1.0 -> smash 1.00 (53.8 m/s ball); 0.5 -> 1.10; 0.3 -> 1.29; 0.15 -> 1.77 (95 m/s). A realistic ~1.45-1.5 would need damp ~0.2 plus retuning; NOT applied since it changes ball speed (and every verified carry). The analytic ball model is fed the MuJoCo separation velocity, so inherits the same ~1.0 smash. Consequence: all carries here (~113 m at 120 mph) are for a ball hit at 53.8 m/s; real 120 mph drives launch at ~80 m/s.

## Stage 9: v4 (OPT-IN) calibrated club-ball contact + HYPOTHETICAL ~128 mph tier
All new behaviour is opt-in (env args `contact_damp`, `ball_friction`, `impact_model`; defaults None) so every v3 number stays valid: configs/fast_scripted_v3.json re-run via eval/eval_v4.py (100 eps, seed 4000): launch 12.17, carry 113.2 m, lat 2.05, 120.3 mph (vs 113.0/2.12 in Stage 6; small diff = harness merge details, same config).
**Smash audit** (eval/smash_probe2.py; Stage 8 explained the ~1.0): MuJoCo contact solref damping ratio 1 => no restitution. Opt-in `contact_damp` (solref[1] of ball+head): 0.30 -> smash 1.29 (std 0.07, stable); 0.22 -> 1.35; 0.19 -> 1.45 but erratic (std 0.16, lateral blow-ups: contact too soft for dt 0.5 ms); so a stable damp 0.3 is used plus a calibrated restitution-like `impact_model.gain` applied to ball velocity at separation (gain 1.28 -> mean smash 1.46, std 0.17 over 60 eps).
**impact_model** (applied at first substep after face separation; also used by the analytic ball): `k_off` smash drops with strike offset from face centre (dy/3cm, (dz-dz0)/2cm; measured sweet spot dz0=-0.019, dy sd 13 mm, dz sd 3 mm); `spin_k` backspin rpm = spin_k*|v|*sin(launch+2deg) (spin_k 130 -> ~2300-2500 rpm; plain MuJoCo friction gave only ~400-600 rpm), set about world -y (converted to the body frame); `k_side` sidespin rpm per metre of horizontal face offset (3500 -> lateral std ~2 m). Spin is an assumed model, not measured from contact. Note: the evaluator's own smash_factor/v_sep are sampled before this post-contact adjustment so its smash column is not meaningful for v4 (use the probe).
**v4 base** configs/fast_scripted_v4_hypothetical.json — HYPOTHETICAL elite tier, NOT realistic hardware or a real human (65 ms downswing, ball ~83 m/s): t_down 0.065 (0.09->123 mph, 0.085->124.6, 0.08->125.9, 0.075->126.9, 0.07->127.8, 0.065->128.3 mph club), loft -31, ball_dz -0.008 kept (launch stayed ~10.9-11.1, no re-scan needed; loft/dz window unchanged), contact_damp 0.3, impact_model gain 1.28, k_off 0.4, spin_k 130, k_side 3500, dz0 -0.019.
Evaluator protocol (PRIMARY; eval.eval_v4, 100 eps), contact 100%, 128.3 mph (57.4 m/s):
| seed | launch deg (std) | carry m | TOTAL distance m (incl. roll) | landed | lat std m |
| 4000 | 10.86 (1.9) | 243.0 | 261.2 | 94% | 2.32 |
| 8000 | 10.97 (1.8) | 251.4 | 269.6 | 94% | 1.94 |
| 9000 | 10.85 (2.0) | 236.5 | 263.7 | 91% | 2.47 |
Probe (60 eps): smash 1.46, spin 2486 rpm (sd 500), launch 11.1, ball speed 83.5 m/s. Analytic (secondary) not re-derived; its flight uses the same separation velocity and now the modelled spin.
Residual PPO, yaw-only (res_scale 0 0 0 0.05, tempo_scale 0, 30k steps, flight reward + shot_pen/act_l2 as Stage 8): ppo_v4yaw_s41/42/43, gate JSONs results/gate_ppo_v4yaw_s4*.json, evaluator protocol 100 eps seed 4000:
| model | det carry/total | stoch carry/total | lat std det/stoch | launch | landed | gate |
| scripted v4 | 242.3 / 260.4 | - | 2.31 | 10.85 | 94% | pass |
| s41 | 242.7 / 260.9 | 242.9 / 261.0 | 2.31 / 2.31 | 10.85 | 94% | PASS |
| s42 | 243.0 / 261.1 | 246.1 / 261.2 | 2.37 / 2.36 | 10.86 | 94/95% | PASS |
| s43 | 242.6 / 260.8 | 242.9 / 261.0 | 2.31 / 2.38 | 10.86 | 94% | PASS |
Checkpoint models/best_v4yaw_s41.zip (gitignored). As before the policy is statistically identical to the script (no improvement; yaw-only is simply harmless).
**Realism caveats (important):** (1) ~260 m total (~285 yd) is near the very top of PGA Tour driver data (~295 yd total at ~175 mph ball speed), here with a hypothetical 128 mph club head, so it is plausible for that input but NOT 300+ m; reaching 300 m total would need ~135+ mph club speed or lower drag. (2) 128 mph in a 65 ms downswing is beyond human and current humanoid hardware. (3) Spin is a hand-set model (spin_k) not contact-derived; Magnus uses Cl=min(1.7S,.3), Cd=0.26 constant, no spin decay, no Reynolds-dependent drag crisis, not calibrated to TrackMan; no wind/altitude. (4) Smash 1.46 comes from a velocity gain on top of a damped soft contact, not an emergent coefficient of restitution; the off-centre smash drop is a simple quadratic and ignores gear effect/MOI. (5) landed 91-94%: ~6% of flights are not counted as landed within the tracker horizon (very long/high shots); carry mean covers landed shots only. (6) Lateral spread comes mainly from the k_side model.

## Stage 10: imitation annealing (v5) — auto_loop rows (appended automatically)
Env opt-ins: script_weight, learn_scale (target = w*v3_script + learn_scale*a), track_set/track_weight (unified_v1 normalised-shape tracking: Mason shoulder pitch, MultiSense/CMU thorax rotation + CMU wrist hinge, manifest train weights). Columns: learned = fraction of target-norm from policy / RMS deviation of joint-target trajectory from the v3 script (rad); carry/total from evaluator-protocol gate (100 eps, seed 4000).
| run | script weight | learned frac / traj dev | carry / total det | carry / total stoch | lat std det / stoch | launch det / stoch | contact | mph | gate |
| imit_w075_s53 | 0.75 | 0.25 / 0.006 | det 159.1 / 159.1 | stoch 157.0 / 157.0 | 27.52 / 26.48 | 40.0 / 39.4 | 1.00 | 141.0 | FAIL |
| imit_w075_s51 | 0.75 | 0.25 / 0.007 | det 165.8 / 165.8 | stoch 165.8 / 165.8 | 25.13 / 24.39 | 38.0 / 37.1 | 1.00 | 141.1 | FAIL |
| imit_w075_s52 | 0.75 | 0.25 / 0.002 | det 158.9 / 158.9 | stoch 159.2 / 159.2 | 27.47 / 24.91 | 39.7 / 39.4 | 1.00 | 141.9 | FAIL |
| imit_w075_s52 | 0.75 | 0.25 / 0.002 | det 163.9 / 163.9 | stoch 162.6 / 162.6 | 24.14 / 22.61 | 37.9 / 36.8 | 1.00 | 140.8 | FAIL |
| imit_w075_s51 | 0.75 | 0.25 / 0.002 | det 165.0 / 165.0 | stoch 163.6 / 163.6 | 21.93 / 19.82 | 36.3 / 36.4 | 1.00 | 139.7 | FAIL |
| imit_w075_s53 | 0.75 | 0.25 / 0.002 | det 162.8 / 162.8 | stoch 163.8 / 163.8 | 25.14 / 26.13 | 38.0 / 38.0 | 1.00 | 140.6 | FAIL |
CORRECTION: the 6 rows above named imit_w075_s5x (FAIL, launch ~38 deg, lateral ~25 m) are INVALID: eval.eval_gate rebuilt the env from train_residual-style args and silently dropped the v3 address/script settings (loft, ball_dz, wr_end, ...). Fixed by storing env_kwargs_full in the results JSON and using it in eval_gate (commit follows); rows below with prefix imit2 are the valid ones. (In-training-env numbers for the retry models were: s52 det carry 114.2, lat 2.29, launch 12.1; s53 114.4/2.22/12.1; s51 51.4/0.61/3.7.)

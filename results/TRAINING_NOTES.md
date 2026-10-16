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

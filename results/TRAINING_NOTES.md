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

# Leaderboard

**Current best model: ppo_resid_v3_r3_s0** (100000 steps) - mean true contact over det+stoch 100%, mean carry 5.479 m. Peak club-head speed (best single swing over det+stoch): 52.11 m/s = 116.6 mph = 97.2% of the 120 mph (53.64 m/s) target. **Best overall (incl. scripted, no-learning baseline): scripted_baseline** - mean contact 100%, mean carry 11.978 m (no trained checkpoint beats it).

Ranking criterion: (1) true club-ball contact rate averaged over deterministic and stochastic modes, higher first; (2) ties broken by mean carry (m, averaged over both modes, mean over all episodes). Distance is not used.

Full ranking (scripted baseline included): scripted_baseline > ppo_resid_v3_r3_s0 > ppo_resid_v3_r2_s0 > ppo_resid_v3_ladder_s0 > ppo_resid_v3_s0 > ppo_scott > ppo_scott_prev_backup > ppo_scott_curr > ppo_scott_final2 > ppo_scott_baseline

Peak club speed = max club_head linear speed over every physics substep of the swing, measured per episode (mean / max over episodes); mph = m/s x 2.23694; % of target = peak / 53.64 m/s (120 mph). Impact club speed = club_head linear speed at first club-ball contact; smash factor = peak ball speed / impact club speed (contact shots with club speed > 0.05 m/s, averaged).

Current env fingerprint `99f124d7b5dd` (env + XML hash). 50 episodes, seeds 4000..4049. +y = left, miss = |final y| > 0.5 m. Distance = final ball x (total); carry = x at landing after flight, 0 if never landed (mean over all episodes). DTW = mean joint-trajectory DTW (rad) to each reference; non-Scott columns are pure reference-style distances.

| Model(s) | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak ball spd (m/s) | Impact club spd (m/s) | Smash | Peak club spd mean/max (m/s) | Peak club mph mean/max | % of 120 mph mean/max | DTW Mason best (11j / upper5) | DTW average | DTW rory | DTW scheffler | DTW scott |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | 30000 | deter | 0% | 0.30 | 0.30 | 0.000 | 0% | 0.000 | 0% | 0% | 0.71 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 7.07e+05 m/s) | 2.975 / 2.532 | 2.777 | 2.797 | 2.832 | 2.733 |
| ppo_scott_baseline | 30000 | stoch | 0% | 0.56 | 7.90 | 0.000 | 0% | 0.395 | 2% | 4% | 0.94 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 1.05e+06 m/s) | 8.183 / 6.582 | 11.003 | 11.026 | 11.398 | 10.701 |
| ppo_scott_curr | 30000 | deter | 100% | 3.01 | 3.01 | 0.000 | 0% | 0.000 | 0% | 0% | 0.77 | 0.58 | 1.32 (n=50) | 6.41 / 6.41 | 14.3 / 14.3 | 12.0% / 12.0% | 3.218 / 2.631 | 2.743 | 2.774 | 2.939 | 2.689 |
| ppo_scott_curr | 30000 | stoch | 34% | 5.04 | 13.90 | 0.062 | 6% | 2.628 | 18% | 18% | 2.83 | 2.65 | 0.96 (n=17) | 23.86 / 37.97 | 53.4 / 84.9 | 44.5% / 70.8% | 3.328 / 2.504 | 2.947 | 2.953 | 2.967 | 2.938 |
| ppo_scott_prev_backup | 30000 | deter | 100% | 2.76 | 2.76 | 0.000 | 0% | 0.000 | 0% | 0% | 0.94 | 0.95 | 0.99 (n=50) | 1.00 / 1.00 | 2.2 / 2.2 | 1.9% / 1.9% | 2.560 / 2.185 | 1.812 | 1.845 | 1.851 | 1.840 |
| ppo_scott_prev_backup | 30000 | stoch | 38% | 4.86 | 13.62 | 0.021 | 2% | 1.804 | 14% | 22% | 2.31 | 3.09 | 0.77 (n=19) | 23.37 / 42.55 | 52.3 / 95.2 | 43.6% / 79.3% | 3.368 / 2.577 | 2.952 | 2.952 | 2.956 | 2.942 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | deter | 48% | 1.80 | 9.80 | 0.091 | 16% | 0.980 | 14% | 10% | 0.69 | 0.17 | 15.91 (n=5) | 3.45 / 12.64 | 7.7 / 28.3 | 6.4% / 23.6% | 3.139 / 2.719 | 2.423 | 2.432 | 2.424 | 2.426 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | stoch | 60% | 1.96 | 10.37 | 0.128 | 26% | 3.842 | 20% | 18% | 2.18 | 1.38 | 1.04 (n=11) | 22.70 / 33.43 | 50.8 / 74.8 | 42.3% / 62.3% | 3.302 / 2.517 | 2.869 | 2.887 | 2.879 | 2.880 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | deter | 98% | 0.47 | 0.59 | 0.102 | 20% | 0.062 | 0% | 0% | 0.50 | 0.10 | 1.51 (n=27) | 0.35 / 0.58 | 0.8 / 1.3 | 0.6% / 1.1% | 2.472 / 2.000 | 1.535 | 1.556 | 1.500 | 1.578 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | stoch | 66% | 0.88 | 5.93 | 0.237 | 26% | 0.313 | 2% | 2% | 2.45 | 1.74 | 1.14 (n=14) | 25.78 / 40.74 | 57.7 / 91.1 | 48.1% / 75.9% | 3.148 / 2.418 | 2.676 | 2.687 | 2.701 | 2.673 |
| ppo_resid_v3_s0 | 60000 | deter | 100% | 50.53 | 64.81 | 0.971 | 2% | 27.418 | 30% | 70% | 29.63 | 44.88 | 0.66 (n=50) | 44.90 / 45.52 | 100.4 / 101.8 | 83.7% / 84.9% | 2.239 / 1.885 | 1.216 | 1.214 | 1.205 | 1.220 |
| ppo_resid_v3_s0 | 60000 | stoch | 66% | 28.73 | 146.42 | 6.222 | 34% | 13.017 | 26% | 18% | 18.43 | 48.93 | 0.57 (n=33) | 49.65 / 64.40 | 111.1 / 144.1 | 92.6% / 120.1% | 2.137 / 1.770 | 1.486 | 1.489 | 1.478 | 1.484 |
| ppo_resid_v3_r2_s0 | 60000 | deter | 100% | 80.25 | 94.48 | 3.265 | 4% | 8.178 | 42% | 56% | 32.47 | 47.95 | 0.68 (n=50) | 47.95 / 48.14 | 107.3 / 107.7 | 89.4% / 89.7% | 2.236 / 1.897 | 1.241 | 1.238 | 1.228 | 1.247 |
| ppo_resid_v3_r2_s0 | 60000 | stoch | 100% | 82.18 | 156.86 | 3.344 | 8% | 15.228 | 44% | 46% | 34.15 | 48.50 | 0.70 (n=50) | 48.50 / 51.50 | 108.5 / 115.2 | 90.4% / 96.0% | 2.230 / 1.891 | 1.256 | 1.254 | 1.243 | 1.262 |
| ppo_resid_v3_r3_s0 | 100000 | deter | 100% | 89.05 | 117.29 | 5.306 | 6% | 7.023 | 46% | 50% | 36.88 | 48.46 | 0.76 (n=50) | 48.46 / 48.75 | 108.4 / 109.0 | 90.3% / 90.9% | 2.246 / 1.907 | 1.236 | 1.233 | 1.224 | 1.241 |
| ppo_resid_v3_r3_s0 | 100000 | stoch | 100% | 88.08 | 156.48 | 5.653 | 12% | 10.818 | 36% | 52% | 36.14 | 48.54 | 0.74 (n=50) | 48.54 / 52.11 | 108.6 / 116.6 | 90.5% / 97.2% | 2.233 / 1.897 | 1.265 | 1.263 | 1.254 | 1.270 |
| ppo_resid_v3_ladder_s0 | 150000 | deter | 100% | 88.56 | 111.93 | 0.000 | 0% | 7.096 | 44% | 52% | 35.92 | 49.65 | 0.72 (n=50) | 49.65 / 49.94 | 111.1 / 111.7 | 92.6% / 93.1% | 2.236 / 1.893 | 1.244 | 1.242 | 1.232 | 1.249 |
| ppo_resid_v3_ladder_s0 | 150000 | stoch | 100% | 78.45 | 155.60 | 2.361 | 16% | 13.502 | 46% | 32% | 37.50 | 49.98 | 0.75 (n=50) | 49.98 / 53.11 | 111.8 / 118.8 | 93.2% / 99.0% | 2.216 / 1.879 | 1.302 | 1.300 | 1.291 | 1.306 |
| scripted_baseline | 0 | deter | 100% | 99.85 | 152.07 | 11.978 | 32% | 2.735 | 8% | 22% | 42.34 | 48.22 | 0.88 (n=50) | 48.22 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 2.197 / 1.870 | 1.335 | 1.334 | 1.321 | 1.338 |
| scripted_baseline | 0 | stoch | 100% | 99.85 | 152.07 | 11.978 | 32% | 2.735 | 8% | 22% | 42.34 | 48.22 | 0.88 (n=50) | 48.22 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 2.197 / 1.870 | 1.335 | 1.334 | 1.321 | 1.338 |

## Configs used (each model evaluated with its own)

- **ppo_scott_baseline** (30000 steps): launch cmd `--timesteps 30000 --tag _baseline` (default env); no train JSON; env = `{}`
- **ppo_scott_curr** (30000 steps): launch cmd `--curriculum --pin_torso --address_pose fixed --torque_scale 3 --tag _curr`; no train JSON; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 3.0}`
- **ppo_scott_prev_backup** (30000 steps): results/train_scott_prev_backup.json; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 3.0}`
- **ppo_scott_final2/ppo_scott_prev2_backup** (60000 steps): results/train_scott_final2.json; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 3.0, "randomize_reset": true, "forward_reward": true}`
- **ppo_scott/ppo_scott_carry1** (100000 steps): results/train_scott.json; env = `{"curriculum": true, "pin_torso": true, "address_pose": "fixed", "torque_scale": 4.0, "randomize_reset": true, "forward_reward": true, "carry_reward": true, "ball_damping": 0.05, "action_smoothing": 0.3, "shoulder_range_deg": 150.0}`
- **ppo_resid_v3_s0** (60000 steps): results/ppo_resid_v3_s0.json args; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.4, 0.4, 0.4, 0.25], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.0, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_r2_s0** (60000 steps): results/ppo_resid_v3_r2_s0.json args; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.0, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_r3_s0** (100000 steps): results/ppo_resid_v3_r3_s0.json args; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.0, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_ladder_s0** (150000 steps): results/ppo_resid_v3_ladder_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **scripted_baseline** (0 steps): zero-residual action with results/ppo_resid_v3_ladder_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`

## DTW vs MIRRORED Mason video references (mirrored=true copies of all 8 refs in docs/REFERENCE_PATHS.md; mean DTW rad: all 11 joints / upper-body 5 joints)

**CAVEAT: Mason references are 2D-proxy joint angles from MediaPipe landmarks of a single phone view (unknown angle), screen-recorded at ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak. Scores are INDICATIVE ONLY and say nothing about swing quality.**

Mapping: `*_mirrored.npz` (mirrored=True, left-handed-consistent per docs) `joints` (degrees, 11 cols = process_video.JOINT_NAMES) -> radians; only `valid_mask` frames kept; policy trajectory = those 11 joints read BY NAME from qpos each env step (works for both the original and v3 models; joint sign conventions between video angles and MuJoCo joints are NOT calibrated; right-handed policies vs left-handed-consistent refs may be penalised); length-normalised DTW (tempo-tolerant). 'upper5' = joint cols 0-4 only (leg cols 5-10 unreliable). q = reference quality_score from the docs.

| Model(s) | Mode | part1_s05_mirrored (q=0.86) | part2_s01_mirrored (q=0.8) | part1_s02_mirrored (q=0.79) | part1_s06_mirrored (q=0.78) | part1_s03_mirrored (q=0.78) | part1_s04_mirrored (q=0.78) | part2_s05_mirrored (q=0.77) | part2_s02_mirrored (q=0.75) |
|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | deter | 2.975 / 2.532 | 3.375 / 2.634 | 3.393 / 2.828 | 3.443 / 2.915 | 3.489 / 2.880 | 3.391 / 2.804 | 3.465 / 2.689 | 3.414 / 2.711 |
| ppo_scott_baseline | stoch | 8.183 / 6.582 | 8.648 / 6.815 | 11.878 / 9.367 | 10.769 / 8.575 | 10.800 / 8.513 | 10.583 / 8.381 | 11.520 / 9.112 | 9.155 / 7.217 |
| ppo_scott_curr | deter | 3.218 / 2.631 | 3.428 / 2.807 | 3.165 / 2.389 | 3.451 / 2.765 | 3.481 / 2.671 | 3.445 / 2.705 | 3.340 / 2.504 | 3.615 / 2.921 |
| ppo_scott_curr | stoch | 3.328 / 2.504 | 3.510 / 2.553 | 3.427 / 2.556 | 3.573 / 2.627 | 3.595 / 2.610 | 3.555 / 2.639 | 3.564 / 2.595 | 3.685 / 2.694 |
| ppo_scott_prev_backup | deter | 2.560 / 2.185 | 2.683 / 2.228 | 2.409 / 1.934 | 2.638 / 2.226 | 2.673 / 2.140 | 2.615 / 2.148 | 2.640 / 2.151 | 2.799 / 2.327 |
| ppo_scott_prev_backup | stoch | 3.368 / 2.577 | 3.586 / 2.609 | 3.528 / 2.667 | 3.689 / 2.805 | 3.687 / 2.760 | 3.648 / 2.762 | 3.751 / 2.829 | 3.758 / 2.769 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | 3.139 / 2.719 | 3.451 / 2.876 | 3.081 / 2.587 | 3.326 / 2.853 | 3.361 / 2.786 | 3.309 / 2.776 | 3.192 / 2.628 | 3.537 / 2.960 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | 3.302 / 2.517 | 3.519 / 2.543 | 3.472 / 2.577 | 3.633 / 2.703 | 3.621 / 2.635 | 3.587 / 2.635 | 3.656 / 2.735 | 3.679 / 2.684 |
| ppo_scott<br>ppo_scott_carry1 | deter | 2.472 / 2.000 | 2.883 / 2.104 | 2.431 / 1.632 | 2.674 / 2.009 | 2.708 / 1.906 | 2.650 / 1.884 | 2.638 / 1.825 | 2.954 / 2.150 |
| ppo_scott<br>ppo_scott_carry1 | stoch | 3.148 / 2.418 | 3.411 / 2.518 | 3.288 / 2.499 | 3.416 / 2.551 | 3.466 / 2.546 | 3.437 / 2.592 | 3.388 / 2.470 | 3.584 / 2.643 |
| ppo_resid_v3_s0 | deter | 2.239 / 1.885 | 2.478 / 1.903 | 1.917 / 1.400 | 2.101 / 1.596 | 2.123 / 1.491 | 2.060 / 1.514 | 2.051 / 1.427 | 2.441 / 1.831 |
| ppo_resid_v3_s0 | stoch | 2.137 / 1.770 | 2.479 / 1.873 | 2.012 / 1.562 | 2.283 / 1.854 | 2.264 / 1.695 | 2.191 / 1.690 | 2.320 / 1.765 | 2.467 / 1.878 |
| ppo_resid_v3_r2_s0 | deter | 2.236 / 1.897 | 2.481 / 1.909 | 1.927 / 1.418 | 2.121 / 1.628 | 2.129 / 1.513 | 2.061 / 1.537 | 2.082 / 1.474 | 2.447 / 1.845 |
| ppo_resid_v3_r2_s0 | stoch | 2.230 / 1.891 | 2.483 / 1.911 | 1.931 / 1.427 | 2.130 / 1.643 | 2.137 / 1.524 | 2.071 / 1.547 | 2.096 / 1.493 | 2.449 / 1.849 |
| ppo_resid_v3_r3_s0 | deter | 2.246 / 1.907 | 2.487 / 1.916 | 1.928 / 1.416 | 2.116 / 1.618 | 2.132 / 1.508 | 2.068 / 1.533 | 2.070 / 1.457 | 2.450 / 1.846 |
| ppo_resid_v3_r3_s0 | stoch | 2.233 / 1.897 | 2.485 / 1.914 | 1.937 / 1.435 | 2.138 / 1.654 | 2.148 / 1.537 | 2.080 / 1.556 | 2.102 / 1.500 | 2.451 / 1.853 |
| ppo_resid_v3_ladder_s0 | deter | 2.236 / 1.893 | 2.482 / 1.910 | 1.923 / 1.412 | 2.111 / 1.613 | 2.124 / 1.501 | 2.064 / 1.529 | 2.067 / 1.452 | 2.447 / 1.843 |
| ppo_resid_v3_ladder_s0 | stoch | 2.216 / 1.879 | 2.487 / 1.917 | 1.944 / 1.451 | 2.154 / 1.682 | 2.160 / 1.555 | 2.100 / 1.575 | 2.126 / 1.532 | 2.456 / 1.863 |
| scripted_baseline | deter | 2.197 / 1.870 | 2.484 / 1.913 | 1.959 / 1.477 | 2.188 / 1.734 | 2.183 / 1.592 | 2.116 / 1.607 | 2.171 / 1.593 | 2.458 / 1.872 |
| scripted_baseline | stoch | 2.197 / 1.870 | 2.484 / 1.913 | 1.959 / 1.477 | 2.188 / 1.734 | 2.183 / 1.592 | 2.116 / 1.607 | 2.171 / 1.593 | 2.458 / 1.872 |

## Contact regressions (vs best earlier-trained checkpoint, same mode)

- ppo_scott_baseline [deterministic]: contact 0% < best previous 100% (ppo_scott(30k, old))
- ppo_scott_baseline [stochastic]: contact 0% < best previous 52% (ppo_scott_final2)
- ppo_scott_curr [stochastic]: contact 34% < best previous 52% (ppo_scott_final2)
- ppo_scott_prev_backup [stochastic]: contact 38% < best previous 52% (ppo_scott_final2)
- ppo_scott_final2/ppo_scott_prev2_backup [deterministic]: contact 48% < best previous 100% (ppo_scott_prev_backup)
- ppo_scott/ppo_scott_carry1 [deterministic]: contact 98% < best previous 100% (ppo_scott_prev_backup)

## History (all evaluated checkpoints)

| Checkpoint(s) | Steps | Env | Det contact | Stoch contact |
|---|---|---|---|---|
| ppo_scott(30k, old), ppo_scott_prev_backup | 30000 | pre-v2-physics | 100% | 18% |
| ppo_scott_final2, ppo_scott(60k) | 60000 | pre-v2-physics | 98% | 52% |
| ppo_scott_baseline | 30000 | f0a3f737fc77 | 0% | 0% |
| ppo_scott_baseline | 30000 | ae180bdc10a3 | 0% | 0% |
| ppo_scott_baseline | 30000 | e9a0050d94b6 | 0% | 0% |
| ppo_scott_baseline | 30000 | 9145629439d4 | 0% | 0% |
| ppo_scott_baseline | 30000 | 25d5c5608c4d | 0% | 0% |
| ppo_scott_baseline | 30000 | 59bc5ea99d60 | 0% | 0% |
| ppo_scott_baseline | 30000 | 99f124d7b5dd | 0% | 0% |
| ppo_scott_curr | 30000 | f0a3f737fc77 | 100% | 34% |
| ppo_scott_curr | 30000 | ae180bdc10a3 | 100% | 34% |
| ppo_scott_curr | 30000 | e9a0050d94b6 | 100% | 34% |
| ppo_scott_curr | 30000 | 9145629439d4 | 100% | 34% |
| ppo_scott_curr | 30000 | 25d5c5608c4d | 100% | 34% |
| ppo_scott_curr | 30000 | 59bc5ea99d60 | 100% | 34% |
| ppo_scott_curr | 30000 | 99f124d7b5dd | 100% | 34% |
| ppo_scott_prev_backup | 30000 | f0a3f737fc77 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | ae180bdc10a3 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | e9a0050d94b6 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 9145629439d4 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 25d5c5608c4d | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 59bc5ea99d60 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 99f124d7b5dd | 100% | 38% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | f0a3f737fc77 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | ae180bdc10a3 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | e9a0050d94b6 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 9145629439d4 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 25d5c5608c4d | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 59bc5ea99d60 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 99f124d7b5dd | 48% | 60% |
| ppo_scott, ppo_scott_carry1 | 100000 | f0a3f737fc77 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | ae180bdc10a3 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | e9a0050d94b6 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 9145629439d4 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 25d5c5608c4d | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 59bc5ea99d60 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 99f124d7b5dd | 98% | 66% |
| ppo_resid_v3_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r2_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r3_s0 | 100000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_ladder_s0 | 150000 | 99f124d7b5dd | n/a | n/a |

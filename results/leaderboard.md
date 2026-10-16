# Leaderboard

**Current best model: ppo_resid_v3_left_an3_s1** (150000 steps) - mean true contact over det+stoch 100%, mean carry 102.905 m. Peak club-head speed (best single swing over det+stoch): 53.09 m/s = 118.7 mph = 99.0% of the 120 mph (53.64 m/s) target. **Best left-handed model: ppo_resid_v3_left_an3_s1** (mean contact 100%, mean carry 102.90 m, physics protocol). Best overall incl. scripted baseline: ppo_resid_v3_left_an3_s1.

Ranking criterion: (1) true club-ball contact rate averaged over deterministic and stochastic modes, higher first; (2) ties broken by mean carry (m, averaged over both modes, mean over all episodes). Distance is not used.

Full ranking (scripted baseline included): ppo_resid_v3_left_an3_s1 > ppo_resid_v3_left_an2_s0 > ppo_resid_v3_left_an1_s0 > ppo_resid_v3_ladder_s0 > ppo_resid_v3_r3_s0 > ppo_resid_v3_r2_s0 > scripted_baseline > ppo_scott > ppo_resid_v3_s0 > ppo_scott_prev_backup > ppo_scott_curr > ppo_scott_final2 > ppo_scott_baseline

Peak club speed = max club_head linear speed over every physics substep of the swing, measured per episode (mean / max over episodes); mph = m/s x 2.23694; % of target = peak / 53.64 m/s (120 mph). Impact club speed = club_head linear speed at first club-ball contact; smash factor = peak ball speed / impact club speed (contact shots with club speed > 0.05 m/s, averaged).

Current env fingerprint `95e60a7e2ccf` (env + XML hash). 50 episodes, seeds 4000..4049. +y = left, miss = |final y| > 0.5 m. Distance = final ball x (total); carry = x at landing after flight, 0 if never landed (mean over all episodes). DTW = mean joint-trajectory DTW (rad) to each reference; non-Scott columns are pure reference-style distances.

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
| ppo_resid_v3_s0 | 60000 | deter | 100% | 56.70 | 69.85 | 56.696 | 100% | 31.443 | 30% | 70% | 29.63 | 44.88 | 0.66 (n=50) | 44.90 / 45.52 | 100.4 / 101.8 | 83.7% / 84.9% | 2.167 / 1.772 | 1.155 | 1.151 | 1.147 | 1.156 |
| ppo_resid_v3_s0 | 60000 | stoch | 60% | 36.30 | 289.55 | 22.604 | 50% | 13.361 | 32% | 12% | 17.14 | 47.04 | 0.60 (n=30) | 48.50 / 70.39 | 108.5 / 157.5 | 90.4% / 131.2% | 2.086 / 1.719 | 1.464 | 1.465 | 1.466 | 1.457 |
| ppo_resid_v3_r2_s0 | 60000 | deter | 100% | 87.78 | 109.95 | 87.783 | 100% | 9.021 | 42% | 56% | 32.47 | 47.95 | 0.68 (n=50) | 47.95 / 48.14 | 107.3 / 107.7 | 89.4% / 89.7% | 2.179 / 1.809 | 1.191 | 1.187 | 1.180 | 1.194 |
| ppo_resid_v3_r2_s0 | 60000 | stoch | 100% | 104.08 | 321.49 | 60.682 | 86% | 17.589 | 44% | 38% | 35.74 | 48.07 | 0.75 (n=50) | 48.07 / 51.04 | 107.5 / 114.2 | 89.6% / 95.2% | 2.119 / 1.737 | 1.219 | 1.215 | 1.209 | 1.220 |
| ppo_resid_v3_r3_s0 | 100000 | deter | 100% | 103.03 | 151.89 | 103.032 | 100% | 8.259 | 46% | 50% | 36.88 | 48.46 | 0.76 (n=50) | 48.46 / 48.75 | 108.4 / 109.0 | 90.3% / 90.9% | 2.155 / 1.764 | 1.160 | 1.155 | 1.151 | 1.161 |
| ppo_resid_v3_r3_s0 | 100000 | stoch | 100% | 143.19 | 343.53 | 66.368 | 76% | 11.246 | 40% | 52% | 36.41 | 48.75 | 0.75 (n=50) | 48.75 / 52.36 | 109.1 / 117.1 | 90.9% / 97.6% | 2.107 / 1.695 | 1.136 | 1.130 | 1.128 | 1.135 |
| ppo_resid_v3_ladder_s0 | 150000 | deter | 100% | 101.91 | 148.16 | 101.908 | 100% | 8.277 | 44% | 50% | 35.92 | 49.65 | 0.72 (n=50) | 49.65 / 49.94 | 111.1 / 111.7 | 92.6% / 93.1% | 2.145 / 1.752 | 1.169 | 1.164 | 1.159 | 1.170 |
| ppo_resid_v3_ladder_s0 | 150000 | stoch | 100% | 108.18 | 342.09 | 69.468 | 88% | 11.577 | 48% | 32% | 37.51 | 49.76 | 0.75 (n=50) | 49.76 / 54.95 | 111.3 / 122.9 | 92.8% / 102.4% | 2.121 / 1.729 | 1.221 | 1.218 | 1.212 | 1.222 |
| scripted_baseline | 0 | deter | 100% | 178.15 | 328.02 | 38.065 | 56% | 2.945 | 8% | 22% | 42.34 | 48.22 | 0.88 (n=50) | 48.22 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 2.035 / 1.612 | 1.188 | 1.182 | 1.180 | 1.184 |
| scripted_baseline | 0 | stoch | 100% | 178.15 | 328.02 | 38.065 | 56% | 2.945 | 8% | 22% | 42.34 | 48.22 | 0.88 (n=50) | 48.22 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 2.035 / 1.612 | 1.188 | 1.182 | 1.180 | 1.184 |
| ppo_resid_v3_left_an1_s0 | 150000 | deter | 100% | 110.28 | 162.27 | 110.280 | 100% | 7.530 | 52% | 46% | 37.90 | 51.20 | 0.74 (n=50) | 51.20 / 51.59 | 114.5 / 115.4 | 95.4% / 96.2% | 2.132 / 1.720 | 1.157 | 1.152 | 1.149 | 1.157 |
| ppo_resid_v3_left_an1_s0 | 150000 | stoch | 100% | 105.46 | 344.17 | 84.943 | 94% | 12.430 | 44% | 46% | 37.65 | 50.65 | 0.74 (n=50) | 50.65 / 53.38 | 113.3 / 119.4 | 94.4% / 99.5% | 2.115 / 1.708 | 1.194 | 1.189 | 1.185 | 1.193 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | 150000 | deter | 100% | 114.29 | 160.27 | 114.289 | 100% | 7.420 | 46% | 46% | 39.00 | 51.25 | 0.76 (n=50) | 51.25 / 51.62 | 114.7 / 115.5 | 95.6% / 96.2% | 2.123 / 1.707 | 1.147 | 1.141 | 1.139 | 1.146 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | 150000 | stoch | 100% | 110.95 | 342.58 | 90.809 | 94% | 7.568 | 40% | 48% | 37.81 | 51.24 | 0.74 (n=50) | 51.24 / 53.09 | 114.6 / 118.8 | 95.5% / 99.0% | 2.125 / 1.724 | 1.188 | 1.184 | 1.179 | 1.187 |
| ppo_resid_v3_left_an3_s1 | 150000 | deter | 100% | 108.60 | 162.26 | 108.602 | 100% | 6.743 | 54% | 36% | 39.23 | 51.24 | 0.77 (n=50) | 51.24 / 51.48 | 114.6 / 115.2 | 95.5% / 96.0% | 2.122 / 1.710 | 1.166 | 1.161 | 1.159 | 1.166 |
| ppo_resid_v3_left_an3_s1 | 150000 | stoch | 100% | 116.68 | 334.78 | 97.208 | 94% | 7.491 | 54% | 36% | 38.29 | 50.96 | 0.75 (n=50) | 50.96 / 53.09 | 114.0 / 118.7 | 95.0% / 99.0% | 2.128 / 1.724 | 1.165 | 1.159 | 1.157 | 1.165 |

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
- **ppo_resid_v3_left_an1_s0** (150000 steps): results/ppo_resid_v3_left_an1_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an2_s0/best_carry_analytic** (150000 steps): results/ppo_resid_v3_left_an2_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an3_s1** (150000 steps): results/ppo_resid_v3_left_an3_s1.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`

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
| ppo_resid_v3_s0 | deter | 2.167 / 1.772 | 2.375 / 1.798 | 1.890 / 1.360 | 2.045 / 1.513 | 2.076 / 1.416 | 2.007 / 1.443 | 2.006 / 1.366 | 2.363 / 1.719 |
| ppo_resid_v3_s0 | stoch | 2.086 / 1.719 | 2.426 / 1.822 | 1.997 / 1.552 | 2.254 / 1.822 | 2.231 / 1.671 | 2.156 / 1.664 | 2.277 / 1.721 | 2.435 / 1.835 |
| ppo_resid_v3_r2_s0 | deter | 2.179 / 1.809 | 2.400 / 1.828 | 1.906 / 1.387 | 2.077 / 1.562 | 2.091 / 1.454 | 2.017 / 1.481 | 2.045 / 1.425 | 2.385 / 1.757 |
| ppo_resid_v3_r2_s0 | stoch | 2.119 / 1.737 | 2.348 / 1.774 | 1.910 / 1.405 | 2.094 / 1.592 | 2.102 / 1.473 | 2.019 / 1.492 | 2.082 / 1.478 | 2.352 / 1.720 |
| ppo_resid_v3_r3_s0 | deter | 2.155 / 1.764 | 2.356 / 1.781 | 1.894 / 1.365 | 2.045 / 1.512 | 2.071 / 1.413 | 2.000 / 1.443 | 2.012 / 1.379 | 2.350 / 1.703 |
| ppo_resid_v3_r3_s0 | stoch | 2.107 / 1.695 | 2.290 / 1.713 | 1.885 / 1.354 | 2.027 / 1.485 | 2.054 / 1.388 | 1.970 / 1.415 | 2.003 / 1.372 | 2.303 / 1.639 |
| ppo_resid_v3_ladder_s0 | deter | 2.145 / 1.752 | 2.354 / 1.779 | 1.889 / 1.362 | 2.041 / 1.507 | 2.065 / 1.407 | 1.997 / 1.439 | 2.009 / 1.374 | 2.349 / 1.702 |
| ppo_resid_v3_ladder_s0 | stoch | 2.121 / 1.729 | 2.349 / 1.774 | 1.907 / 1.396 | 2.082 / 1.573 | 2.097 / 1.458 | 2.025 / 1.481 | 2.067 / 1.455 | 2.351 / 1.713 |
| scripted_baseline | deter | 2.035 / 1.612 | 2.237 / 1.658 | 1.897 / 1.388 | 2.064 / 1.547 | 2.077 / 1.427 | 1.981 / 1.446 | 2.065 / 1.457 | 2.272 / 1.608 |
| scripted_baseline | stoch | 2.035 / 1.612 | 2.237 / 1.658 | 1.897 / 1.388 | 2.064 / 1.547 | 2.077 / 1.427 | 1.981 / 1.446 | 2.065 / 1.457 | 2.272 / 1.608 |
| ppo_resid_v3_left_an1_s0 | deter | 2.132 / 1.720 | 2.329 / 1.755 | 1.888 / 1.354 | 2.024 / 1.478 | 2.055 / 1.383 | 1.999 / 1.421 | 1.989 / 1.344 | 2.331 / 1.672 |
| ppo_resid_v3_left_an1_s0 | stoch | 2.115 / 1.708 | 2.325 / 1.749 | 1.897 / 1.375 | 2.052 / 1.523 | 2.075 / 1.417 | 2.008 / 1.447 | 2.029 / 1.401 | 2.331 / 1.679 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | deter | 2.123 / 1.707 | 2.319 / 1.742 | 1.880 / 1.342 | 2.013 / 1.462 | 2.048 / 1.369 | 1.989 / 1.406 | 1.977 / 1.327 | 2.322 / 1.658 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | stoch | 2.125 / 1.724 | 2.338 / 1.763 | 1.898 / 1.372 | 2.049 / 1.519 | 2.077 / 1.417 | 2.013 / 1.447 | 2.020 / 1.387 | 2.341 / 1.691 |
| ppo_resid_v3_left_an3_s1 | deter | 2.122 / 1.710 | 2.326 / 1.751 | 1.895 / 1.366 | 2.038 / 1.500 | 2.067 / 1.401 | 2.009 / 1.434 | 2.006 / 1.369 | 2.330 / 1.674 |
| ppo_resid_v3_left_an3_s1 | stoch | 2.128 / 1.724 | 2.334 / 1.759 | 1.894 / 1.363 | 2.037 / 1.499 | 2.066 / 1.399 | 2.008 / 1.434 | 2.004 / 1.365 | 2.335 / 1.680 |

## Left-handed models: trainer gate JSON vs verified (this leaderboard, same protocol: MuJoCo physics, flight tracker, 450-step horizon, deterministic, 50 eps, seeds 4000+)

Verified = this run. Trainer gate = `results/gate_<name>.json` (`eval.eval_gate`; gate: carry > 11.98 m AND lateral std < 2.73 m AND contact >= 99%). Trainer 'analytic' = `results/<name>.json` policy block (100 eps, analytic flight from the MuJoCo launch vector with ASSUMED backspin, episode ends 3 steps after contact) - NOT re-verified here, different protocol.

| Model | Source | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club mph mean | Gate pass |
|---|---|---|---|---|---|---|---|
| ppo_resid_v3_left_an1_s0 | verified (this run, det) | 100% | 100% | 110.28 | 7.53 | 114.5 | FAIL |
| ppo_resid_v3_left_an1_s0 | trainer gate JSON (det) | 100% | 100% | 110.28 | 7.53 | 114.5 | FAIL |
| ppo_resid_v3_left_an1_s0 | trainer analytic (100 eps) | 100% | 100% | 93.13 | 6.61 | 114.0 (impact) | n/a |
| ppo_resid_v3_left_an2_s0 | verified (this run, det) | 100% | 100% | 114.29 | 7.42 | 114.7 | FAIL |
| ppo_resid_v3_left_an2_s0 | trainer gate JSON (det) | 100% | 100% | 114.29 | 7.42 | 114.7 | FAIL |
| ppo_resid_v3_left_an2_s0 | trainer analytic (100 eps) | 100% | 100% | 91.79 | 6.53 | 114.7 (impact) | n/a |
| ppo_resid_v3_left_an3_s1 | verified (this run, det) | 100% | 100% | 108.60 | 6.74 | 114.6 | FAIL |
| ppo_resid_v3_left_an3_s1 | trainer gate JSON (det) | 100% | 100% | 108.60 | 6.74 | 114.6 | FAIL |
| ppo_resid_v3_left_an3_s1 | trainer analytic (100 eps) | 100% | 100% | 87.88 | 5.91 | 114.8 (impact) | n/a |

## DTW vs NATIVE Mason v2 references (recommended, non-partial, license self_owned/commercial_ok; mean DTW rad: all 11 joints / upper-body 5)

**CAVEATS: 2D-proxy joint angles from single-view MediaPipe, screen-recorded ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak; native left-handed footage, `right_*` columns = anatomical right = LEAD arm of a left-hander, whereas the env's `right_*` joints are the swinging arm of its own model (mapping/sign conventions NOT calibrated). Indicative only. MultiSense (right-handed, CC0, different protocol) deliberately NOT scored here.**

Refs: `p1_s06` (q=0.76, oblique, mirrored=False), `p1_s11` (q=0.76, face_on, mirrored=False), `p2_s02` (q=0.75, down_the_line, mirrored=False), `p2_s01` (q=0.7, down_the_line, mirrored=False), `p1_s04` (q=0.69, down_the_line, mirrored=False), `p1_s03` (q=0.69, down_the_line, mirrored=False), `p2_s13` (q=0.68, down_the_line, mirrored=False), `p2_s10` (q=0.68, down_the_line, mirrored=False), `p1_s05` (q=0.66, down_the_line, mirrored=False), `p2_s11` (q=0.66, down_the_line, mirrored=False), `p3_s09_unmirrored` (q=0.83, down_the_line, mirrored=True)

| Model(s) | Mode | p1_s06 | p1_s11 | p2_s02 | p2_s01 | p1_s04 | p1_s03 | p2_s13 | p2_s10 | p1_s05 | p2_s11 | p3_s09_unmirrored | mean over refs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | deter | 3.001 / 2.532 | 3.821 / 3.263 | 3.419 / 2.654 | 3.381 / 2.686 | 3.534 / 2.899 | 3.669 / 2.938 | 3.731 / 3.006 | 3.643 / 3.002 | 3.439 / 2.781 | 3.761 / 3.119 | 3.273 / 2.899 | 3.516 / 2.889 |
| ppo_scott_baseline | stoch | 8.929 / 7.164 | 11.079 / 8.837 | 9.298 / 7.373 | 9.286 / 7.402 | 11.823 / 9.305 | 13.741 / 10.878 | 13.040 / 10.352 | 12.408 / 9.895 | 11.164 / 8.884 | 14.835 / 11.673 | 9.584 / 7.664 | 11.381 / 9.039 |
| ppo_scott_curr | deter | 3.694 / 3.210 | 3.922 / 3.198 | 3.862 / 3.289 | 3.792 / 3.290 | 3.746 / 3.053 | 3.554 / 2.900 | 3.586 / 2.913 | 3.648 / 3.031 | 3.698 / 3.117 | 3.573 / 2.888 | 3.307 / 2.433 | 3.671 / 3.029 |
| ppo_scott_curr | stoch | 3.514 / 2.703 | 3.868 / 2.940 | 3.715 / 2.817 | 3.680 / 2.827 | 3.574 / 2.696 | 3.440 / 2.606 | 3.462 / 2.598 | 3.502 / 2.701 | 3.526 / 2.727 | 3.399 / 2.565 | 3.667 / 2.582 | 3.577 / 2.706 |
| ppo_scott_prev_backup | deter | 2.579 / 2.209 | 2.898 / 2.201 | 2.764 / 2.323 | 2.725 / 2.364 | 2.620 / 2.102 | 2.304 / 1.802 | 2.471 / 1.869 | 2.514 / 2.043 | 2.589 / 2.146 | 2.363 / 1.903 | 2.747 / 2.148 | 2.598 / 2.101 |
| ppo_scott_prev_backup | stoch | 3.518 / 2.701 | 3.850 / 2.923 | 3.743 / 2.794 | 3.723 / 2.823 | 3.613 / 2.728 | 3.462 / 2.617 | 3.561 / 2.706 | 3.541 / 2.727 | 3.569 / 2.764 | 3.436 / 2.606 | 3.601 / 2.623 | 3.602 / 2.728 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | 3.289 / 2.887 | 3.637 / 3.090 | 3.545 / 3.007 | 3.529 / 3.053 | 3.249 / 2.747 | 3.030 / 2.558 | 3.123 / 2.622 | 3.146 / 2.716 | 3.242 / 2.795 | 2.984 / 2.525 | 3.461 / 3.025 | 3.294 / 2.820 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | 3.430 / 2.640 | 3.856 / 2.946 | 3.679 / 2.724 | 3.669 / 2.763 | 3.547 / 2.646 | 3.423 / 2.560 | 3.472 / 2.597 | 3.465 / 2.637 | 3.509 / 2.676 | 3.378 / 2.518 | 3.668 / 2.677 | 3.554 / 2.671 |
| ppo_scott<br>ppo_scott_carry1 | deter | 2.427 / 1.988 | 2.872 / 2.116 | 2.794 / 2.128 | 2.809 / 2.200 | 2.466 / 1.819 | 2.134 / 1.510 | 2.402 / 1.736 | 2.345 / 1.801 | 2.416 / 1.867 | 2.188 / 1.576 | 2.695 / 2.070 | 2.504 / 1.892 |
| ppo_scott<br>ppo_scott_carry1 | stoch | 3.265 / 2.430 | 3.608 / 2.659 | 3.544 / 2.657 | 3.524 / 2.699 | 3.358 / 2.532 | 3.191 / 2.403 | 3.215 / 2.399 | 3.265 / 2.511 | 3.333 / 2.557 | 3.149 / 2.386 | 3.565 / 2.615 | 3.365 / 2.532 |
| ppo_resid_v3_s0 | deter | 2.037 / 1.636 | 2.538 / 1.860 | 2.347 / 1.734 | 2.244 / 1.733 | 2.028 / 1.389 | 1.835 / 1.284 | 1.949 / 1.362 | 1.930 / 1.420 | 1.947 / 1.435 | 1.824 / 1.257 | 2.576 / 2.187 | 2.114 / 1.573 |
| ppo_resid_v3_s0 | stoch | 2.045 / 1.715 | 2.859 / 2.322 | 2.430 / 1.871 | 2.364 / 1.858 | 2.262 / 1.755 | 2.013 / 1.599 | 2.271 / 1.786 | 2.181 / 1.807 | 2.147 / 1.720 | 2.135 / 1.700 | 2.436 / 1.874 | 2.286 / 1.819 |
| ppo_resid_v3_r2_s0 | deter | 2.054 / 1.669 | 2.569 / 1.908 | 2.364 / 1.772 | 2.266 / 1.773 | 2.054 / 1.439 | 1.833 / 1.317 | 1.982 / 1.416 | 1.956 / 1.465 | 1.972 / 1.478 | 1.850 / 1.304 | 2.591 / 2.134 | 2.135 / 1.607 |
| ppo_resid_v3_r2_s0 | stoch | 2.024 / 1.638 | 2.587 / 1.940 | 2.345 / 1.743 | 2.247 / 1.747 | 2.082 / 1.488 | 1.859 / 1.365 | 2.035 / 1.491 | 1.991 / 1.521 | 1.989 / 1.508 | 1.904 / 1.382 | 2.487 / 1.871 | 2.141 / 1.609 |
| ppo_resid_v3_r3_s0 | deter | 2.033 / 1.630 | 2.526 / 1.848 | 2.338 / 1.720 | 2.233 / 1.719 | 2.028 / 1.392 | 1.832 / 1.293 | 1.955 / 1.373 | 1.933 / 1.424 | 1.947 / 1.437 | 1.832 / 1.270 | 2.555 / 2.152 | 2.110 / 1.569 |
| ppo_resid_v3_r3_s0 | stoch | 1.999 / 1.581 | 2.489 / 1.804 | 2.299 / 1.661 | 2.189 / 1.658 | 2.015 / 1.376 | 1.824 / 1.293 | 1.954 / 1.370 | 1.923 / 1.412 | 1.929 / 1.416 | 1.835 / 1.277 | 2.477 / 2.061 | 2.085 / 1.537 |
| ppo_resid_v3_ladder_s0 | deter | 2.023 / 1.619 | 2.521 / 1.839 | 2.334 / 1.718 | 2.230 / 1.717 | 2.024 / 1.387 | 1.827 / 1.289 | 1.951 / 1.368 | 1.928 / 1.418 | 1.943 / 1.433 | 1.826 / 1.264 | 2.555 / 2.105 | 2.106 / 1.560 |
| ppo_resid_v3_ladder_s0 | stoch | 2.019 / 1.626 | 2.576 / 1.920 | 2.342 / 1.735 | 2.245 / 1.740 | 2.073 / 1.469 | 1.865 / 1.351 | 2.021 / 1.468 | 1.982 / 1.502 | 1.983 / 1.493 | 1.893 / 1.359 | 2.493 / 2.018 | 2.136 / 1.607 |
| scripted_baseline | deter | 1.963 / 1.546 | 2.531 / 1.873 | 2.281 / 1.639 | 2.174 / 1.642 | 2.066 / 1.465 | 1.863 / 1.368 | 2.039 / 1.491 | 1.983 / 1.505 | 1.965 / 1.473 | 1.921 / 1.400 | 2.345 / 1.859 | 2.103 / 1.569 |
| scripted_baseline | stoch | 1.963 / 1.546 | 2.531 / 1.873 | 2.281 / 1.639 | 2.174 / 1.642 | 2.066 / 1.465 | 1.863 / 1.368 | 2.039 / 1.491 | 1.983 / 1.505 | 1.965 / 1.473 | 1.921 / 1.400 | 2.345 / 1.859 | 2.103 / 1.569 |
| ppo_resid_v3_left_an1_s0 | deter | 2.011 / 1.592 | 2.489 / 1.793 | 2.321 / 1.689 | 2.214 / 1.687 | 2.011 / 1.358 | 1.838 / 1.278 | 1.937 / 1.341 | 1.917 / 1.394 | 1.932 / 1.412 | 1.817 / 1.243 | 2.532 / 2.081 | 2.093 / 1.533 |
| ppo_resid_v3_left_an1_s0 | stoch | 2.007 / 1.600 | 2.532 / 1.857 | 2.324 / 1.701 | 2.221 / 1.701 | 2.043 / 1.415 | 1.854 / 1.320 | 1.985 / 1.412 | 1.951 / 1.452 | 1.956 / 1.452 | 1.862 / 1.311 | 2.496 / 2.005 | 2.112 / 1.566 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | deter | 2.001 / 1.579 | 2.482 / 1.782 | 2.312 / 1.675 | 2.203 / 1.672 | 2.002 / 1.343 | 1.831 / 1.265 | 1.926 / 1.324 | 1.906 / 1.379 | 1.922 / 1.397 | 1.807 / 1.228 | 2.530 / 2.080 | 2.084 / 1.520 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | stoch | 2.015 / 1.608 | 2.530 / 1.851 | 2.332 / 1.711 | 2.230 / 1.712 | 2.039 / 1.407 | 1.855 / 1.310 | 1.975 / 1.396 | 1.947 / 1.442 | 1.956 / 1.447 | 1.851 / 1.292 | 2.519 / 2.066 | 2.114 / 1.567 |
| ppo_resid_v3_left_an3_s1 | deter | 2.008 / 1.593 | 2.514 / 1.831 | 2.323 / 1.693 | 2.218 / 1.693 | 2.028 / 1.387 | 1.855 / 1.301 | 1.962 / 1.377 | 1.935 / 1.424 | 1.945 / 1.432 | 1.842 / 1.279 | 2.510 / 2.055 | 2.104 / 1.551 |
| ppo_resid_v3_left_an3_s1 | stoch | 2.012 / 1.599 | 2.512 / 1.827 | 2.325 / 1.698 | 2.221 / 1.698 | 2.025 / 1.383 | 1.850 / 1.295 | 1.956 / 1.369 | 1.931 / 1.418 | 1.944 / 1.430 | 1.835 / 1.269 | 2.523 / 2.067 | 2.103 / 1.550 |

## Contact regressions (vs best earlier-trained checkpoint, same mode)

- ppo_scott_baseline [deterministic]: contact 0% < best previous 100% (ppo_scott(30k, old))
- ppo_scott_baseline [stochastic]: contact 0% < best previous 52% (ppo_scott_final2)
- ppo_scott_curr [stochastic]: contact 34% < best previous 52% (ppo_scott_final2)
- ppo_scott_prev_backup [stochastic]: contact 38% < best previous 52% (ppo_scott_final2)
- ppo_scott_final2/ppo_scott_prev2_backup [deterministic]: contact 48% < best previous 100% (ppo_scott_prev_backup)
- ppo_scott/ppo_scott_carry1 [deterministic]: contact 98% < best previous 100% (ppo_scott_prev_backup)
- ppo_resid_v3_s0 [stochastic]: contact 60% < best previous 66% (ppo_scott)

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
| ppo_scott_baseline | 30000 | 95e60a7e2ccf | 0% | 0% |
| ppo_scott_curr | 30000 | f0a3f737fc77 | 100% | 34% |
| ppo_scott_curr | 30000 | ae180bdc10a3 | 100% | 34% |
| ppo_scott_curr | 30000 | e9a0050d94b6 | 100% | 34% |
| ppo_scott_curr | 30000 | 9145629439d4 | 100% | 34% |
| ppo_scott_curr | 30000 | 25d5c5608c4d | 100% | 34% |
| ppo_scott_curr | 30000 | 59bc5ea99d60 | 100% | 34% |
| ppo_scott_curr | 30000 | 99f124d7b5dd | 100% | 34% |
| ppo_scott_curr | 30000 | 95e60a7e2ccf | 100% | 34% |
| ppo_scott_prev_backup | 30000 | f0a3f737fc77 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | ae180bdc10a3 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | e9a0050d94b6 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 9145629439d4 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 25d5c5608c4d | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 59bc5ea99d60 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 99f124d7b5dd | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 95e60a7e2ccf | 100% | 38% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | f0a3f737fc77 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | ae180bdc10a3 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | e9a0050d94b6 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 9145629439d4 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 25d5c5608c4d | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 59bc5ea99d60 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 99f124d7b5dd | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 95e60a7e2ccf | 48% | 60% |
| ppo_scott, ppo_scott_carry1 | 100000 | f0a3f737fc77 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | ae180bdc10a3 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | e9a0050d94b6 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 9145629439d4 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 25d5c5608c4d | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 59bc5ea99d60 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 99f124d7b5dd | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 95e60a7e2ccf | 98% | 66% |
| ppo_resid_v3_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_s0 | 60000 | 95e60a7e2ccf | 100% | 60% |
| ppo_resid_v3_r2_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r2_s0 | 60000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r3_s0 | 100000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_ladder_s0 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 95e60a7e2ccf | 100% | 100% |

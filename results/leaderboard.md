# Leaderboard

**Current best model: ppo_v4yaw_s42** (30000 steps) - mean true contact over det+stoch 100%, mean carry 246.621 m. Peak club-head speed (best single swing over det+stoch): 57.52 m/s = 128.7 mph = 107.2% of the 120 mph (53.64 m/s) target. **Best left-handed model: ppo_v4yaw_s42** (mean contact 100%, mean carry 246.62 m, physics protocol). **Best model meeting the showcase criterion (real carry AND tight lateral AND not-flat launch AND 100% contact; see below): ppo_v4yaw_s42.** Best overall incl. scripted baseline: ppo_v4yaw_s42. **HYPOTHETICAL ACTUATORS: ppo_v4yaw_s42 (force_scale 2), ppo_v4yaw_s43 (force_scale 2), ppo_v4yaw_s41 (force_scale 2), imit3_w050_s51 (force_scale 2), ppo_v3flt_yaw_s31 (force_scale 2), ppo_v3flt_yaw_s32 (force_scale 2), imit3_w075_s53 (force_scale 2), imit3_w075_s51 (force_scale 2), imit3_w050_s52 (force_scale 2), imit3_w075_s52 (force_scale 2), imit3_w025_s51 (force_scale 2) run with boosted actuator force caps (force_scale > 1 = more force than the default model); speeds/carries are not evidence of human- or robot-attainable performance.** Rows `imit_w075_s51/52/53` are excluded: INVALID config (eval rebuilt the env from args and dropped v3 settings; see TRAINING_NOTES CORRECTION; superseded by imit2/imit3). Rows with script_weight<1 are BLENDS (executed command = script_weight x scripted + rest learned), shown in the per-row summary.

Ranking criterion: (1) true club-ball contact rate averaged over deterministic and stochastic modes, higher first; (2) ties broken by mean carry (m, averaged over both modes, mean over all episodes). Distance is not used.

Full ranking (scripted baseline included): ppo_v4yaw_s42 > ppo_v4yaw_s43 > ppo_v4yaw_s41 > imit3_w050_s51 > scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] > ppo_v3flt_yaw_s31 > ppo_v3flt_yaw_s32 > imit3_w075_s53 > imit3_w075_s51 > imit2_w075_s52 > imit3_w000_s51 > imit3_w050_s52 > imit3_w075_s52 > ppo_resid_v3_left_an3_s1 > imit2_w075_s53 > imit3_w025_s51 > ppo_resid_v3_left_an2_s0 > ppo_v3tiny_s22 > imit3_w000_s52 > ppo_v3tiny_s23 > ppo_resid_v3_left_an1_s0 > ppo_resid_v3_left_an4_s2 > ppo_v3flt_all_s33 > ppo_v3tiny_s21 > ppo_resid_v3_left_an6_s4 > ppo_resid_v3_left_an9_s7 > imit3_w025_s52 > ppo_resid_v3_r3_s0 > ppo_resid_v3_ladder_s0 > ppo_resid_v3_left_an10_s8 > ppo_resid_v3_r2_s0 > scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] > imit2_w075_s51 > scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] > scripted_baseline[ladder cfg: right, loft 6, default ball_x] > ppo_resid_v3_left_fast1_s10 > ppo_resid_v3_left_fast2_s11 > ppo_resid_v3_left_an8_s6 > ppo_resid_v3_left_an5_s3 > ppo_resid_v3_left_an7_s5 > ppo_scott > ppo_resid_v3_s0 > ppo_scott_prev_backup > ppo_scott_curr > ppo_scott_final2 > ppo_scott_baseline

Peak club speed = max club_head linear speed over every physics substep of the swing, measured per episode (mean / max over episodes); mph = m/s x 2.23694; % of target = peak / 53.64 m/s (120 mph). Impact club speed = club_head linear speed at first club-ball contact; smash factor = peak ball speed / impact club speed (contact shots with club speed > 0.05 m/s, averaged).

Current env fingerprint `30178ef58c6a` (env + XML hash). 50 episodes, seeds 4000..4049. +y = left, miss = |final y| > 0.5 m. Distance = final ball x (total); carry = x at landing after flight, 0 if never landed (mean over all episodes). DTW = mean joint-trajectory DTW (rad) to each reference; non-Scott columns are pure reference-style distances.

| Model(s) | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak ball spd (m/s) | Impact club spd (m/s) | Smash | Peak club spd mean/max (m/s) | Peak club mph mean/max | % of 120 mph mean/max | Launch elev mean deg (std) [flat?] | DTW native Mason v2, mean of 11 refs (11j / upper5) | DTW average | DTW rory | DTW scheffler | DTW scott |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | 30000 | deter | 0% | 0.30 | 0.30 | 0.000 | 0% | 0.000 | 0% | 0% | 0.71 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 7.07e+05 m/s) | nan (nan) | 4.642 / 3.957 | 4.128 | 4.138 | 4.257 | 4.009 |
| ppo_scott_baseline | 30000 | stoch | 0% | 0.94 | 7.90 | 0.000 | 0% | 0.384 | 0% | 8% | 1.04 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 3.55e+05 m/s) | nan (nan) | 8.685 / 7.297 | 8.287 | 8.309 | 8.364 | 8.180 |
| ppo_scott_curr | 30000 | deter | 100% | 3.01 | 3.01 | 0.000 | 0% | 0.000 | 0% | 0% | 0.77 | 0.58 | 1.32 (n=50) | 6.41 / 6.41 | 14.3 / 14.3 | 12.0% / 12.0% | 11.3 (0.0) | 3.494 / 2.771 | 2.768 | 2.778 | 2.757 | 2.792 |
| ppo_scott_curr | 30000 | stoch | 36% | 4.47 | 12.37 | 0.024 | 4% | 2.512 | 24% | 8% | 2.71 | 1.92 | 1.03 (n=18) | 23.27 / 33.50 | 52.1 / 74.9 | 43.4% / 62.5% | 10.1 (12.7) | 3.377 / 2.544 | 2.896 | 2.895 | 2.898 | 2.891 |
| ppo_scott_prev_backup | 30000 | deter | 100% | 2.76 | 2.76 | 0.000 | 0% | 0.000 | 0% | 0% | 0.94 | 0.95 | 0.99 (n=50) | 1.00 / 1.00 | 2.2 / 2.2 | 1.9% / 1.9% | 25.0 (0.0) | 2.359 / 1.786 | 1.755 | 1.812 | 1.844 | 1.781 |
| ppo_scott_prev_backup | 30000 | stoch | 52% | 4.58 | 13.62 | 0.000 | 0% | 1.244 | 20% | 16% | 2.00 | 2.96 | 0.60 (n=26) | 22.77 / 30.50 | 50.9 / 68.2 | 42.5% / 56.9% | 4.7 (6.3) FLAT | 3.414 / 2.566 | 2.963 | 2.963 | 2.974 | 2.956 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | deter | 48% | 1.80 | 9.80 | 0.091 | 16% | 0.980 | 14% | 10% | 0.69 | 0.17 | 15.91 (n=5) | 3.45 / 12.64 | 7.7 / 28.3 | 6.4% / 23.6% | 34.2 (34.5) | 3.019 / 2.521 | 2.292 | 2.300 | 2.303 | 2.297 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | stoch | 46% | 2.69 | 11.55 | 0.142 | 28% | 3.420 | 18% | 16% | 2.52 | 0.74 | 1.66 (n=4) | 23.03 / 35.61 | 51.5 / 79.7 | 42.9% / 66.4% | 36.8 (28.5) | 3.374 / 2.493 | 2.867 | 2.863 | 2.882 | 2.859 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | deter | 98% | 0.47 | 0.59 | 0.102 | 20% | 0.062 | 0% | 0% | 0.50 | 0.10 | 1.51 (n=27) | 0.35 / 0.58 | 0.8 / 1.3 | 0.6% / 1.1% | 48.4 (24.9) | 2.259 / 1.572 | 1.278 | 1.289 | 1.264 | 1.302 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | stoch | 68% | 0.88 | 6.41 | 0.413 | 32% | 0.297 | 2% | 2% | 2.49 | 1.47 | 1.88 (n=15) | 26.48 / 57.32 | 59.2 / 128.2 | 49.4% / 106.9% | 36.4 (28.8) | 3.165 / 2.390 | 2.686 | 2.688 | 2.702 | 2.675 |
| ppo_resid_v3_s0 | 60000 | deter | 100% | 57.12 | 69.85 | 57.123 | 100% | 31.455 | 30% | 70% | 29.55 | 44.91 | 0.66 (n=50) | 44.92 / 45.52 | 100.5 / 101.8 | 83.7% / 84.9% | 49.6 (6.0) | 1.917 / 1.294 | 0.922 | 0.912 | 0.931 | 0.912 |
| ppo_resid_v3_s0 | 60000 | stoch | 64% | 38.16 | 289.76 | 20.830 | 52% | 17.980 | 28% | 22% | 18.17 | 49.58 | 0.57 (n=32) | 49.73 / 63.08 | 111.2 / 141.1 | 92.7% / 117.6% | 16.6 (35.1) | 2.347 / 1.877 | 1.304 | 1.302 | 1.312 | 1.297 |
| ppo_resid_v3_r2_s0 | 60000 | deter | 100% | 86.95 | 105.44 | 86.947 | 100% | 8.446 | 42% | 58% | 32.29 | 47.96 | 0.67 (n=50) | 47.96 / 48.14 | 107.3 / 107.7 | 89.4% / 89.7% | 36.1 (3.6) | 1.925 / 1.334 | 0.954 | 0.945 | 0.961 | 0.946 |
| ppo_resid_v3_r2_s0 | 60000 | stoch | 100% | 110.46 | 332.87 | 60.467 | 84% | 13.191 | 46% | 36% | 35.48 | 47.89 | 0.74 (n=50) | 47.89 / 50.96 | 107.1 / 114.0 | 89.3% / 95.0% | 26.3 (19.6) | 2.005 / 1.434 | 1.004 | 0.995 | 1.009 | 0.997 |
| ppo_resid_v3_r3_s0 | 100000 | deter | 100% | 103.44 | 152.86 | 103.438 | 100% | 8.908 | 46% | 52% | 36.56 | 48.51 | 0.75 (n=50) | 48.51 / 48.89 | 108.5 / 109.4 | 90.4% / 91.1% | 32.8 (5.1) | 1.912 / 1.296 | 0.928 | 0.918 | 0.937 | 0.918 |
| ppo_resid_v3_r3_s0 | 100000 | stoch | 100% | 123.91 | 343.53 | 66.750 | 82% | 10.718 | 38% | 46% | 36.22 | 48.77 | 0.74 (n=50) | 48.77 / 52.36 | 109.1 / 117.1 | 90.9% / 97.6% | 26.7 (17.4) | 1.963 / 1.369 | 0.972 | 0.963 | 0.980 | 0.964 |
| ppo_resid_v3_ladder_s0 | 150000 | deter | 100% | 99.64 | 134.14 | 99.639 | 100% | 8.232 | 46% | 50% | 35.67 | 49.64 | 0.72 (n=50) | 49.64 / 49.88 | 111.0 / 111.6 | 92.5% / 93.0% | 33.1 (4.4) | 1.905 / 1.299 | 0.946 | 0.936 | 0.953 | 0.936 |
| ppo_resid_v3_ladder_s0 | 150000 | stoch | 100% | 94.48 | 339.80 | 69.082 | 92% | 14.276 | 44% | 36% | 36.77 | 49.72 | 0.74 (n=50) | 49.72 / 54.95 | 111.2 / 122.9 | 92.7% / 102.4% | 25.4 (19.2) | 2.044 / 1.475 | 1.049 | 1.041 | 1.055 | 1.041 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | 0 | deter | 100% | 177.22 | 331.62 | 36.672 | 56% | 2.733 | 8% | 20% | 42.31 | 48.23 | 0.88 (n=50) | 48.23 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 9.2 (13.2) FLAT | 2.045 / 1.482 | 1.029 | 1.021 | 1.036 | 1.021 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | 0 | stoch | 100% | 177.22 | 331.62 | 36.672 | 56% | 2.733 | 8% | 20% | 42.31 | 48.23 | 0.88 (n=50) | 48.23 / 48.33 | 107.9 / 108.1 | 89.9% / 90.1% | 9.2 (13.2) FLAT | 2.045 / 1.482 | 1.029 | 1.021 | 1.036 | 1.021 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | 0 | deter | 100% | 118.44 | 326.09 | 53.934 | 80% | 1.985 | 4% | 10% | 43.59 | 48.21 | 0.90 (n=50) | 48.21 / 48.27 | 107.8 / 108.0 | 89.9% / 90.0% | 11.5 (11.6) | 2.177 / 1.659 | 1.196 | 1.195 | 1.203 | 1.193 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | 0 | stoch | 100% | 118.44 | 326.09 | 53.934 | 80% | 1.985 | 4% | 10% | 43.59 | 48.21 | 0.90 (n=50) | 48.21 / 48.27 | 107.8 / 108.0 | 89.9% / 90.0% | 11.5 (11.6) | 2.177 / 1.659 | 1.196 | 1.195 | 1.203 | 1.193 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | 0 | deter | 100% | 80.70 | 289.84 | 69.405 | 96% | 0.013 | 0% | 0% | 53.10 | 53.80 | 0.99 (n=50) | 53.80 / 53.94 | 120.4 / 120.7 | 100.3% / 100.6% | 9.0 (2.9) | 2.242 / 1.778 | 1.308 | 1.309 | 1.306 | 1.315 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | 0 | stoch | 100% | 80.70 | 289.84 | 69.405 | 96% | 0.013 | 0% | 0% | 53.10 | 53.80 | 0.99 (n=50) | 53.80 / 53.94 | 120.4 / 120.7 | 100.3% / 100.6% | 9.0 (2.9) | 2.242 / 1.778 | 1.308 | 1.309 | 1.306 | 1.315 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | 0 | deter | 100% | 115.71 | 186.55 | 115.710 | 100% | 1.699 | 2% | 12% | 54.09 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.060 / 1.524 | 1.106 | 1.101 | 1.110 | 1.105 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | 0 | stoch | 100% | 115.71 | 186.55 | 115.710 | 100% | 1.699 | 2% | 12% | 54.09 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.060 / 1.524 | 1.106 | 1.101 | 1.110 | 1.105 |
| ppo_resid_v3_left_an1_s0 | 150000 | deter | 100% | 108.88 | 144.06 | 108.884 | 100% | 6.905 | 56% | 40% | 38.22 | 51.16 | 0.75 (n=50) | 51.16 / 51.67 | 114.4 / 115.6 | 95.4% / 96.3% | 32.0 (3.8) | 1.900 / 1.283 | 0.950 | 0.940 | 0.958 | 0.940 |
| ppo_resid_v3_left_an1_s0 | 150000 | stoch | 100% | 106.22 | 340.25 | 85.974 | 94% | 15.283 | 46% | 46% | 37.59 | 51.01 | 0.74 (n=50) | 51.01 / 53.93 | 114.1 / 120.6 | 95.1% / 100.5% | 30.4 (14.7) | 1.951 / 1.350 | 0.986 | 0.977 | 0.994 | 0.977 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | 150000 | deter | 100% | 111.87 | 159.77 | 111.875 | 100% | 7.622 | 50% | 46% | 39.17 | 51.27 | 0.76 (n=50) | 51.27 / 51.57 | 114.7 / 115.4 | 95.6% / 96.1% | 31.3 (3.9) | 1.893 / 1.270 | 0.939 | 0.928 | 0.947 | 0.928 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | 150000 | stoch | 100% | 116.37 | 353.00 | 89.888 | 92% | 8.519 | 50% | 38% | 37.56 | 51.08 | 0.74 (n=50) | 51.08 / 52.68 | 114.3 / 117.8 | 95.2% / 98.2% | 28.7 (12.7) | 1.935 / 1.325 | 0.964 | 0.954 | 0.972 | 0.954 |
| ppo_resid_v3_left_an3_s1 | 150000 | deter | 100% | 117.57 | 338.43 | 110.799 | 98% | 7.204 | 58% | 40% | 39.75 | 51.25 | 0.78 (n=50) | 51.25 / 51.58 | 114.7 / 115.4 | 95.6% / 96.2% | 30.0 (6.9) | 1.905 / 1.286 | 0.932 | 0.921 | 0.940 | 0.921 |
| ppo_resid_v3_left_an3_s1 | 150000 | stoch | 100% | 112.11 | 334.78 | 105.412 | 98% | 9.205 | 58% | 36% | 38.83 | 50.69 | 0.77 (n=50) | 50.69 / 52.42 | 113.4 / 117.3 | 94.5% / 97.7% | 30.0 (8.6) | 1.921 / 1.310 | 0.944 | 0.933 | 0.952 | 0.932 |
| ppo_resid_v3_left_an4_s2 | 150000 | deter | 100% | 95.37 | 162.98 | 95.375 | 100% | 6.570 | 52% | 44% | 34.35 | 49.93 | 0.69 (n=50) | 49.93 / 50.31 | 111.7 / 112.5 | 93.1% / 93.8% | 34.4 (3.9) | 1.916 / 1.304 | 0.946 | 0.936 | 0.953 | 0.937 |
| ppo_resid_v3_left_an4_s2 | 150000 | stoch | 100% | 98.84 | 170.36 | 98.835 | 100% | 8.450 | 50% | 44% | 36.04 | 50.11 | 0.72 (n=50) | 50.11 / 51.98 | 112.1 / 116.3 | 93.4% / 96.9% | 33.7 (6.6) | 1.924 / 1.314 | 0.953 | 0.943 | 0.960 | 0.943 |
| ppo_resid_v3_left_an5_s3 | 150000 | deter | 100% | 102.05 | 357.37 | 10.004 | 74% | 0.143 | 0% | 0% | 45.91 | 52.32 | 0.88 (n=50) | 52.32 / 52.60 | 117.0 / 117.7 | 97.5% / 98.1% | -3.8 (2.2) FLAT | 2.418 / 1.942 | 1.326 | 1.327 | 1.326 | 1.324 |
| ppo_resid_v3_left_an5_s3 | 150000 | stoch | 100% | 141.48 | 359.56 | 8.546 | 62% | 0.737 | 20% | 8% | 46.29 | 52.02 | 0.89 (n=50) | 52.02 / 54.06 | 116.4 / 120.9 | 97.0% / 100.8% | -3.3 (2.2) FLAT | 2.316 / 1.811 | 1.243 | 1.241 | 1.246 | 1.239 |
| ppo_resid_v3_left_an6_s4 | 150000 | deter | 100% | 112.18 | 335.10 | 105.479 | 98% | 8.939 | 50% | 38% | 39.38 | 50.52 | 0.78 (n=50) | 50.52 / 51.37 | 113.0 / 114.9 | 94.2% / 95.8% | 28.9 (8.2) | 1.929 / 1.323 | 0.969 | 0.959 | 0.976 | 0.959 |
| ppo_resid_v3_left_an6_s4 | 150000 | stoch | 100% | 145.59 | 354.13 | 78.147 | 80% | 6.739 | 44% | 40% | 39.90 | 50.71 | 0.79 (n=50) | 50.71 / 52.65 | 113.4 / 117.8 | 94.5% / 98.2% | 23.2 (15.0) | 1.941 / 1.336 | 0.961 | 0.950 | 0.968 | 0.950 |
| ppo_resid_v3_left_an7_s5 | 120000 | deter | 100% | 140.08 | 355.77 | 7.866 | 62% | 0.278 | 0% | 38% | 45.66 | 51.51 | 0.89 (n=50) | 51.51 / 52.16 | 115.2 / 116.7 | 96.0% / 97.2% | -3.3 (2.2) FLAT | 2.329 / 1.834 | 1.239 | 1.236 | 1.245 | 1.234 |
| ppo_resid_v3_left_an7_s5 | 120000 | stoch | 100% | 93.30 | 357.35 | 9.553 | 76% | 0.380 | 0% | 14% | 44.59 | 51.65 | 0.86 (n=50) | 51.65 / 53.23 | 115.5 / 119.1 | 96.3% / 99.2% | -4.0 (2.6) FLAT | 2.449 / 1.982 | 1.366 | 1.367 | 1.367 | 1.354 |
| ppo_resid_v3_left_an8_s6 | 120000 | deter | 100% | 89.85 | 359.69 | 11.215 | 78% | 0.087 | 0% | 0% | 45.13 | 52.97 | 0.85 (n=50) | 52.97 / 53.26 | 118.5 / 119.1 | 98.7% / 99.3% | -5.1 (2.8) FLAT | 2.462 / 2.001 | 1.362 | 1.365 | 1.366 | 1.362 |
| ppo_resid_v3_left_an8_s6 | 120000 | stoch | 100% | 88.82 | 361.67 | 10.924 | 78% | 0.610 | 6% | 6% | 44.39 | 52.55 | 0.84 (n=50) | 52.55 / 54.07 | 117.6 / 120.9 | 98.0% / 100.8% | -4.6 (2.8) FLAT | 2.461 / 1.997 | 1.365 | 1.367 | 1.369 | 1.363 |
| ppo_resid_v3_left_an9_s7 | 120000 | deter | 100% | 102.12 | 136.61 | 102.123 | 100% | 7.919 | 60% | 38% | 36.34 | 49.39 | 0.74 (n=50) | 49.39 / 49.97 | 110.5 / 111.8 | 92.1% / 93.2% | 33.2 (4.2) | 1.908 / 1.299 | 0.942 | 0.932 | 0.951 | 0.931 |
| ppo_resid_v3_left_an9_s7 | 120000 | stoch | 100% | 130.89 | 337.38 | 78.302 | 84% | 7.109 | 52% | 32% | 38.52 | 49.63 | 0.78 (n=50) | 49.63 / 52.31 | 111.0 / 117.0 | 92.5% / 97.5% | 26.4 (15.4) | 1.944 / 1.345 | 0.969 | 0.959 | 0.977 | 0.959 |
| ppo_resid_v3_left_an10_s8 | 120000 | deter | 100% | 126.17 | 327.65 | 107.036 | 94% | 5.442 | 54% | 32% | 42.17 | 47.86 | 0.88 (n=50) | 47.86 / 48.45 | 107.1 / 108.4 | 89.2% / 90.3% | 25.2 (9.6) | 1.933 / 1.332 | 0.954 | 0.944 | 0.961 | 0.945 |
| ppo_resid_v3_left_an10_s8 | 120000 | stoch | 100% | 149.68 | 338.04 | 55.494 | 70% | 4.191 | 46% | 22% | 40.12 | 47.87 | 0.84 (n=50) | 47.87 / 50.04 | 107.1 / 111.9 | 89.2% / 93.3% | 15.4 (16.3) FLAT | 2.020 / 1.447 | 1.014 | 1.005 | 1.020 | 1.006 |
| ppo_resid_v3_left_fast1_s10 | 100000 | deter | 100% | 15.85 | 24.02 | 15.854 | 100% | 0.022 | 0% | 0% | 48.74 | 54.65 | 0.89 (n=50) | 54.65 / 54.73 | 122.3 / 122.4 | 101.9% / 102.0% | -5.2 (1.5) FLAT | 2.668 / 2.271 | 1.504 | 1.512 | 1.511 | 1.507 |
| ppo_resid_v3_left_fast1_s10 | 100000 | stoch | 100% | 15.47 | 24.43 | 15.470 | 100% | 0.289 | 2% | 0% | 47.36 | 54.59 | 0.87 (n=50) | 54.59 / 55.10 | 122.1 / 123.3 | 101.8% / 102.7% | -5.0 (1.5) FLAT | 2.669 / 2.271 | 1.504 | 1.508 | 1.507 | 1.506 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | 100000 | deter | 100% | 14.97 | 23.18 | 14.975 | 100% | 0.024 | 0% | 0% | 49.31 | 55.24 | 0.89 (n=50) | 55.24 / 55.32 | 123.6 / 123.8 | 103.0% / 103.1% | -5.2 (1.4) FLAT | 2.666 / 2.267 | 1.506 | 1.510 | 1.505 | 1.509 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | 100000 | stoch | 100% | 15.50 | 23.76 | 15.497 | 100% | 0.033 | 0% | 0% | 48.10 | 55.24 | 0.87 (n=50) | 55.24 / 55.72 | 123.6 / 124.6 | 103.0% / 103.9% | -4.9 (1.3) FLAT | 2.663 / 2.262 | 1.507 | 1.511 | 1.509 | 1.507 |
| ppo_v3tiny_s22 | 60000 | deter | 100% | 109.83 | 265.00 | 99.241 | 96% | 6.323 | 6% | 12% | 51.66 | 52.92 | 0.98 (n=50) | 52.92 / 53.08 | 118.4 / 118.7 | 98.7% / 99.0% | 10.8 (5.3) | 2.090 / 1.565 | 1.125 | 1.121 | 1.128 | 1.125 |
| ppo_v3tiny_s22 | 60000 | stoch | 100% | 118.03 | 272.21 | 101.892 | 94% | 7.339 | 12% | 16% | 52.02 | 52.98 | 0.98 (n=50) | 52.98 / 54.06 | 118.5 / 120.9 | 98.8% / 100.8% | 10.3 (5.2) | 2.078 / 1.545 | 1.113 | 1.108 | 1.117 | 1.111 |
| ppo_v3tiny_s21 | 60000 | deter | 100% | 122.72 | 276.21 | 84.582 | 86% | 4.411 | 6% | 6% | 50.55 | 53.18 | 0.95 (n=50) | 53.18 / 53.31 | 119.0 / 119.3 | 99.1% / 99.4% | 9.0 (6.8) | 2.079 / 1.549 | 1.109 | 1.104 | 1.112 | 1.107 |
| ppo_v3tiny_s21 | 60000 | stoch | 100% | 119.22 | 271.57 | 103.337 | 94% | 8.576 | 14% | 10% | 52.63 | 53.10 | 0.99 (n=50) | 53.10 / 53.96 | 118.8 / 120.7 | 99.0% / 100.6% | 11.0 (4.5) | 2.065 / 1.532 | 1.103 | 1.098 | 1.106 | 1.101 |
| ppo_v3tiny_s23 | 60000 | deter | 100% | 118.90 | 289.05 | 91.004 | 90% | 2.812 | 10% | 10% | 50.33 | 53.18 | 0.95 (n=50) | 53.18 / 53.75 | 119.0 / 120.2 | 99.1% / 100.2% | 8.8 (7.3) | 2.095 / 1.568 | 1.126 | 1.122 | 1.130 | 1.125 |
| ppo_v3tiny_s23 | 60000 | stoch | 100% | 121.64 | 278.66 | 105.232 | 94% | 9.167 | 12% | 10% | 52.55 | 53.20 | 0.99 (n=50) | 53.20 / 54.03 | 119.0 / 120.9 | 99.2% / 100.7% | 10.7 (4.7) | 2.059 / 1.523 | 1.094 | 1.089 | 1.098 | 1.092 |
| ppo_v3flt_all_s33 | 30000 | deter | 100% | 100.70 | 284.74 | 95.003 | 98% | 5.132 | 2% | 0% | 51.66 | 53.78 | 0.96 (n=50) | 53.78 / 53.88 | 120.3 / 120.5 | 100.3% / 100.4% | 10.5 (6.0) | 2.126 / 1.614 | 1.165 | 1.162 | 1.167 | 1.165 |
| ppo_v3flt_all_s33 | 30000 | stoch | 100% | 110.41 | 281.27 | 99.163 | 96% | 9.747 | 8% | 6% | 51.24 | 53.80 | 0.95 (n=50) | 53.80 / 53.92 | 120.3 / 120.6 | 100.3% / 100.5% | 9.2 (7.2) | 2.108 / 1.583 | 1.138 | 1.134 | 1.142 | 1.137 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | 30000 | deter | 100% | 113.90 | 186.22 | 113.904 | 100% | 1.586 | 4% | 12% | 54.07 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.068 / 1.536 | 1.115 | 1.110 | 1.118 | 1.114 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | 30000 | stoch | 100% | 113.98 | 186.20 | 113.978 | 100% | 1.582 | 4% | 12% | 54.06 | 53.80 | 1.00 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.066 / 1.532 | 1.111 | 1.106 | 1.114 | 1.110 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | 30000 | deter | 100% | 114.25 | 186.20 | 114.250 | 100% | 1.614 | 2% | 12% | 54.07 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.066 / 1.533 | 1.112 | 1.107 | 1.115 | 1.110 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | 30000 | stoch | 100% | 114.78 | 186.14 | 114.779 | 100% | 1.935 | 4% | 12% | 54.07 | 53.80 | 1.01 (n=50) | 53.80 / 53.90 | 120.3 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.063 / 1.529 | 1.109 | 1.104 | 1.112 | 1.107 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | 30000 | deter | 100% | 261.71 | 309.87 | 243.591 | 94% | 1.670 | 52% | 36% | 82.60 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.845 / 1.187 | 0.909 | 0.897 | 0.920 | 0.894 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | 30000 | stoch | 100% | 261.52 | 309.88 | 243.409 | 94% | 1.692 | 50% | 36% | 82.49 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.845 / 1.187 | 0.908 | 0.896 | 0.919 | 0.893 |
| ppo_v4yaw_s42 | 30000 | deter | 100% | 261.40 | 309.50 | 243.290 | 94% | 1.660 | 42% | 40% | 82.61 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.846 / 1.189 | 0.909 | 0.897 | 0.920 | 0.895 |
| ppo_v4yaw_s42 | 30000 | stoch | 100% | 262.03 | 309.50 | 249.951 | 96% | 1.654 | 44% | 40% | 82.55 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.843 / 1.184 | 0.906 | 0.894 | 0.917 | 0.892 |
| ppo_v4yaw_s43 | 30000 | deter | 100% | 261.13 | 309.87 | 243.011 | 94% | 1.648 | 42% | 38% | 82.60 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.847 / 1.190 | 0.910 | 0.898 | 0.921 | 0.896 |
| ppo_v4yaw_s43 | 30000 | stoch | 100% | 262.39 | 309.87 | 244.277 | 94% | 1.739 | 44% | 40% | 82.70 | 57.36 | 1.44 (n=50) | 57.36 / 57.52 | 128.3 / 128.7 | 106.9% / 107.2% | 10.9 (2.0) | 1.843 / 1.184 | 0.906 | 0.894 | 0.917 | 0.891 |
| imit2_w075_s53 | 15000 | deter | 100% | 139.24 | 292.69 | 116.877 | 92% | 3.569 | 6% | 24% | 53.84 | 53.98 | 1.00 (n=50) | 53.98 / 54.09 | 120.7 / 121.0 | 100.6% / 100.8% | 11.3 (3.7) | 2.010 / 1.449 | 1.055 | 1.049 | 1.060 | 1.051 |
| imit2_w075_s53 | 15000 | stoch | 100% | 112.71 | 279.75 | 96.121 | 94% | 1.007 | 2% | 10% | 51.41 | 53.99 | 0.95 (n=50) | 53.99 / 54.26 | 120.8 / 121.4 | 100.7% / 101.2% | 8.9 (7.7) | 2.106 / 1.581 | 1.141 | 1.137 | 1.144 | 1.139 |
| imit2_w075_s51 | 15000 | deter | 100% | 126.57 | 286.60 | 49.278 | 72% | 0.582 | 4% | 2% | 46.23 | 53.88 | 0.86 (n=50) | 53.88 / 53.98 | 120.5 / 120.7 | 100.4% / 100.6% | 1.4 (9.5) FLAT | 2.161 / 1.642 | 1.168 | 1.166 | 1.175 | 1.166 |
| imit2_w075_s51 | 15000 | stoch | 100% | 124.70 | 281.63 | 80.579 | 84% | 4.286 | 8% | 6% | 50.01 | 53.87 | 0.93 (n=50) | 53.87 / 54.12 | 120.5 / 121.1 | 100.4% / 100.9% | 6.6 (8.5) | 2.104 / 1.574 | 1.131 | 1.127 | 1.136 | 1.128 |
| imit2_w075_s52 | 15000 | deter | 100% | 139.93 | 283.49 | 117.839 | 92% | 2.963 | 8% | 26% | 53.82 | 53.89 | 1.00 (n=50) | 53.89 / 54.01 | 120.6 / 120.8 | 100.5% / 100.7% | 11.3 (3.7) | 2.007 / 1.446 | 1.051 | 1.045 | 1.056 | 1.047 |
| imit2_w075_s52 | 15000 | stoch | 100% | 131.14 | 290.92 | 103.222 | 90% | 2.728 | 2% | 22% | 52.46 | 53.88 | 0.97 (n=50) | 53.88 / 54.10 | 120.5 / 121.0 | 100.5% / 100.9% | 9.7 (6.2) | 2.047 / 1.498 | 1.086 | 1.081 | 1.091 | 1.083 |
| imit3_w075_s51 | 8000 | deter | 100% | 113.09 | 182.73 | 113.093 | 100% | 0.733 | 2% | 10% | 53.91 | 53.73 | 1.00 (n=50) | 53.73 / 53.83 | 120.2 / 120.4 | 100.2% / 100.3% | 12.2 (1.4) | 2.062 / 1.527 | 1.110 | 1.106 | 1.114 | 1.109 |
| imit3_w075_s51 | 8000 | stoch | 100% | 112.42 | 182.78 | 112.425 | 100% | 0.670 | 2% | 8% | 53.90 | 53.73 | 1.00 (n=50) | 53.73 / 53.82 | 120.2 / 120.4 | 100.2% / 100.3% | 12.2 (1.4) | 2.066 / 1.533 | 1.115 | 1.110 | 1.118 | 1.114 |
| imit3_w075_s52 | 8000 | deter | 100% | 124.97 | 277.56 | 108.424 | 94% | 1.097 | 6% | 12% | 53.63 | 53.76 | 1.00 (n=50) | 53.76 / 53.90 | 120.3 / 120.6 | 100.2% / 100.5% | 11.4 (3.3) | 2.046 / 1.503 | 1.091 | 1.086 | 1.095 | 1.089 |
| imit3_w075_s52 | 8000 | stoch | 100% | 124.70 | 276.34 | 108.181 | 94% | 1.365 | 4% | 10% | 53.64 | 53.76 | 1.00 (n=50) | 53.76 / 53.91 | 120.3 / 120.6 | 100.2% / 100.5% | 11.4 (3.3) | 2.049 / 1.508 | 1.095 | 1.090 | 1.099 | 1.093 |
| imit3_w050_s51 | 8000 | deter | 100% | 119.39 | 190.07 | 119.392 | 100% | 2.203 | 6% | 18% | 54.22 | 53.81 | 1.01 (n=50) | 53.81 / 53.92 | 120.4 / 120.6 | 100.3% / 100.5% | 12.3 (1.4) | 2.052 / 1.512 | 1.100 | 1.095 | 1.104 | 1.099 |
| imit3_w050_s51 | 8000 | stoch | 100% | 120.45 | 186.89 | 120.450 | 100% | 2.154 | 4% | 16% | 54.22 | 53.81 | 1.01 (n=50) | 53.81 / 53.92 | 120.4 / 120.6 | 100.3% / 100.5% | 12.2 (1.4) | 2.045 / 1.501 | 1.090 | 1.085 | 1.094 | 1.088 |
| imit3_w050_s52 | 8000 | deter | 100% | 107.74 | 162.79 | 107.739 | 100% | 0.232 | 0% | 4% | 53.98 | 53.84 | 1.00 (n=50) | 53.84 / 53.94 | 120.4 / 120.7 | 100.4% / 100.6% | 12.3 (1.3) | 2.086 / 1.560 | 1.133 | 1.129 | 1.136 | 1.133 |
| imit3_w050_s52 | 8000 | stoch | 100% | 109.70 | 171.77 | 109.699 | 100% | 0.294 | 0% | 4% | 53.99 | 53.84 | 1.00 (n=50) | 53.84 / 53.95 | 120.4 / 120.7 | 100.4% / 100.6% | 12.3 (1.3) | 2.075 / 1.544 | 1.123 | 1.119 | 1.126 | 1.123 |
| imit3_w075_s53 | 8000 | deter | 100% | 134.13 | 281.13 | 111.950 | 92% | 2.267 | 6% | 16% | 53.60 | 53.80 | 1.00 (n=50) | 53.80 / 53.91 | 120.3 / 120.6 | 100.3% / 100.5% | 11.2 (3.7) | 2.023 / 1.469 | 1.065 | 1.059 | 1.070 | 1.062 |
| imit3_w075_s53 | 8000 | stoch | 100% | 131.49 | 286.87 | 114.637 | 94% | 2.248 | 6% | 16% | 53.77 | 53.80 | 1.00 (n=50) | 53.80 / 53.91 | 120.3 / 120.6 | 100.3% / 100.5% | 11.5 (3.3) | 2.026 / 1.474 | 1.068 | 1.062 | 1.072 | 1.065 |
| imit3_w025_s52 | 8000 | deter | 100% | 117.07 | 286.49 | 88.949 | 90% | 5.314 | 6% | 2% | 50.19 | 55.12 | 0.91 (n=50) | 55.12 / 55.67 | 123.3 / 124.5 | 102.8% / 103.8% | 6.8 (8.8) | 2.119 / 1.588 | 1.140 | 1.136 | 1.146 | 1.137 |
| imit3_w025_s52 | 8000 | stoch | 100% | 125.17 | 284.62 | 91.405 | 88% | 5.708 | 6% | 4% | 51.20 | 55.11 | 0.93 (n=50) | 55.11 / 55.64 | 123.3 / 124.5 | 102.7% / 103.7% | 7.9 (8.0) | 2.086 / 1.548 | 1.113 | 1.108 | 1.118 | 1.110 |
| imit3_w025_s51 | 8000 | deter | 100% | 105.11 | 166.65 | 105.109 | 100% | 0.108 | 0% | 2% | 53.81 | 53.86 | 1.00 (n=50) | 53.86 / 53.99 | 120.5 / 120.8 | 100.4% / 100.7% | 12.2 (1.3) | 2.095 / 1.573 | 1.145 | 1.142 | 1.148 | 1.146 |
| imit3_w025_s51 | 8000 | stoch | 100% | 106.16 | 157.84 | 106.157 | 100% | 0.091 | 0% | 2% | 53.83 | 53.87 | 1.00 (n=50) | 53.87 / 54.00 | 120.5 / 120.8 | 100.4% / 100.7% | 12.2 (1.3) | 2.087 / 1.563 | 1.136 | 1.132 | 1.138 | 1.136 |
| imit3_w000_s52 | 8000 | deter | 100% | 127.37 | 287.04 | 105.147 | 92% | 5.529 | 8% | 10% | 52.85 | 53.24 | 0.99 (n=50) | 53.24 / 55.22 | 119.1 / 123.5 | 99.3% / 102.9% | 11.3 (3.6) | 2.043 / 1.501 | 1.084 | 1.078 | 1.087 | 1.081 |
| imit3_w000_s52 | 8000 | stoch | 100% | 119.80 | 291.44 | 91.859 | 90% | 1.613 | 6% | 10% | 50.95 | 53.37 | 0.95 (n=50) | 53.37 / 55.06 | 119.4 / 123.2 | 99.5% / 102.7% | 8.3 (7.7) | 2.103 / 1.575 | 1.123 | 1.119 | 1.127 | 1.121 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | 8000 | deter | 100% | 125.97 | 277.24 | 109.442 | 94% | 3.969 | 4% | 14% | 53.65 | 53.91 | 1.00 (n=50) | 53.91 / 54.04 | 120.6 / 120.9 | 100.5% / 100.7% | 11.2 (3.6) | 2.049 / 1.506 | 1.090 | 1.084 | 1.094 | 1.087 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | 8000 | stoch | 100% | 127.77 | 275.81 | 111.273 | 94% | 2.569 | 6% | 12% | 53.85 | 53.91 | 1.00 (n=50) | 53.91 / 54.04 | 120.6 / 120.9 | 100.5% / 100.8% | 11.5 (3.2) | 2.040 / 1.494 | 1.085 | 1.079 | 1.089 | 1.082 |

## Per-row summary: learned fraction, style distance, sequencing (proxy)

Learned fraction = what the JSON args record (residual caps / env type), never guessed. DTW = native mason_v2 recommended set, mean over refs (all 11 joints, rad). Sequencing = time of peak |angular velocity| per segment relative to first true contact (ms; negative = before impact), measured every 5 ms of simulated time within [impact-0.30 s, impact+0.05 s]; proximal-to-distal = hips -> chest yaw -> shoulder -> elbow -> wrist -> club-head speed peaks non-decreasing (5 ms ties count as in order). PROXY: single-joint angular speeds, the sim has no pelvis yaw joint, club speed is the head geom speed.

| Model(s) | Mode | Learned fraction (from JSON args) | DTW all11 mean | Peak t rel. impact ms: hips / chest yaw / shoulder / elbow / wrist / club | Prox-to-distal | wrist-shoulder lag s | elbow-shoulder lag s |
|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 4.642 | n/a | nan% (n=0) | nan | nan |
| ppo_scott_baseline | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 8.685 | n/a | nan% (n=0) | nan | nan |
| ppo_scott_curr | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 3.494 | 0 / nan / -20 / -60 / 40 / 20 | 0% (n=50) | 0.060 | -0.040 |
| ppo_scott_curr | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.377 | 38 / nan / 38 / 38 / -42 / 38 | 0% (n=2) | -0.080 | 0.000 |
| ppo_scott_prev_backup | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 2.359 | 18 / nan / -2 / 38 / 38 / 18 | 0% (n=50) | 0.040 | 0.040 |
| ppo_scott_prev_backup | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.414 | 5 / nan / 14 / 25 / -16 / 41 | 0% (n=16) | -0.030 | 0.000 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 3.019 | 10 / nan / -116 / -116 / -52 / 5 | 0% (n=4) | 0.050 | 0.000 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.374 | -6 / nan / 4 / 34 / 4 / 4 | 0% (n=2) | 0.000 | 0.030 |
| ppo_scott<br>ppo_scott_carry1 | deter | direct policy control (HumanoidGolfEnv; no scripted base) | 2.259 | -119 / nan / -151 / 27 / 37 / -51 | 0% (n=30) | 0.130 | 0.180 |
| ppo_scott<br>ppo_scott_carry1 | stoch | direct policy control (HumanoidGolfEnv; no scripted base) | 3.165 | -6 / nan / -6 / 17 / -125 / 1 | 0% (n=10) | -0.040 | 0.030 |
| ppo_resid_v3_s0 | deter | residual on scripted swing: cap +-[0.4, 0.4, 0.4, 0.25] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.917 | 48 / -70 / -3 / -11 / 45 / -1 | 0% (n=50) | 0.050 | -0.010 |
| ppo_resid_v3_s0 | stoch | residual on scripted swing: cap +-[0.4, 0.4, 0.4, 0.25] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.347 | -10 / -124 / -10 / -27 / 30 / -2 | 0% (n=32) | 0.040 | -0.022 |
| ppo_resid_v3_r2_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.925 | -18 / -58 / -13 / 16 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_r2_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.005 | -14 / -151 / -9 / 19 / 45 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_r3_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.912 | -16 / -40 / -11 / 23 / 47 / -2 | 0% (n=50) | 0.060 | 0.035 |
| ppo_resid_v3_r3_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.963 | -13 / -161 / -10 / 21 / 46 / -3 | 0% (n=50) | 0.055 | 0.030 |
| ppo_resid_v3_ladder_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.905 | -12 / -57 / -8 / -3 / 42 / -3 | 0% (n=50) | 0.050 | 0.005 |
| ppo_resid_v3_ladder_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.044 | -14 / -94 / -11 / 7 / 44 / -3 | 0% (n=50) | 0.055 | 0.015 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deter | 0% (scripted, zero residual) | 2.045 | -20 / 4 / -10 / 19 / 44 / -1 | 0% (n=50) | 0.055 | 0.030 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stoch | 0% (scripted, zero residual) | 2.045 | -20 / 4 / -10 / 19 / 44 / -1 | 0% (n=50) | 0.055 | 0.030 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deter | 0% (scripted, zero residual) | 2.177 | -20 / 4 / -10 / 19 / 44 / -0 | 0% (n=50) | 0.055 | 0.030 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stoch | 0% (scripted, zero residual) | 2.177 | -20 / 4 / -10 / 19 / 44 / -0 | 0% (n=50) | 0.055 | 0.030 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deter | 0% (scripted, zero residual) | 2.242 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stoch | 0% (scripted, zero residual) | 2.242 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deter | 0% (scripted, zero residual) | 2.060 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stoch | 0% (scripted, zero residual) | 2.060 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an1_s0 | deter | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.900 | -13 / -87 / -13 / 18 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an1_s0 | stoch | residual on scripted swing: cap +-[0.2, 0.2, 0.2, 0.1] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.951 | -13 / -153 / -10 / 17 / 45 / -3 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | deter | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.893 | -14 / 12 / -9 / 16 / 45 / -4 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | stoch | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.935 | -13 / -138 / -11 / 16 / 44 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an3_s1 | deter | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.905 | -13 / 3 / -10 / 15 / 45 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an3_s1 | stoch | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.921 | -13 / -107 / -11 / 16 / 45 / -2 | 0% (n=50) | 0.055 | 0.030 |
| ppo_resid_v3_left_an4_s2 | deter | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.916 | -14 / 46 / -14 / 16 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an4_s2 | stoch | residual on scripted swing: cap +-[0.1, 0.1, 0.1, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.924 | -12 / -104 / -11 / 15 / 44 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an5_s3 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.418 | -15 / 10 / -14 / 11 / 45 / -3 | 0% (n=50) | 0.060 | 0.025 |
| ppo_resid_v3_left_an5_s3 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.316 | -16 / -116 / -13 / -1 / 44 / -2 | 0% (n=50) | 0.060 | 0.015 |
| ppo_resid_v3_left_an6_s4 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.929 | -17 / -53 / -17 / 16 / 44 / -3 | 0% (n=50) | 0.060 | 0.032 |
| ppo_resid_v3_left_an6_s4 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.03] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.941 | -14 / -123 / -11 / 16 / 45 / -3 | 0% (n=50) | 0.055 | 0.030 |
| ppo_resid_v3_left_an7_s5 | deter | residual on scripted swing: cap +-[0.04, 0.04, 0.03, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.329 | -14 / -58 / -13 / 16 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an7_s5 | stoch | residual on scripted swing: cap +-[0.04, 0.04, 0.03, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.449 | -15 / -113 / -14 / 15 / 45 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an8_s6 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.462 | -14 / -49 / -14 / 16 / 46 / -4 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an8_s6 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.461 | -14 / -174 / -13 / 15 / 45 / -2 | 0% (n=50) | 0.060 | 0.030 |
| ppo_resid_v3_left_an9_s7 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.908 | -12 / -2 / -9 / 18 / 45 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an9_s7 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.944 | -13 / -169 / -9 / 18 / 46 / -3 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an10_s8 | deter | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 1.933 | -12 / 42 / -7 / 18 / 46 / -2 | 0% (n=50) | 0.055 | 0.025 |
| ppo_resid_v3_left_an10_s8 | stoch | residual on scripted swing: cap +-[0.1, 0.08, 0.05, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.020 | -14 / -149 / -11 / 20 / 46 / -3 | 0% (n=50) | 0.057 | 0.030 |
| ppo_resid_v3_left_fast1_s10 | deter | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.668 | -16 / -2 / -16 / -1 / 44 / -1 | 0% (n=50) | 0.060 | 0.015 |
| ppo_resid_v3_left_fast1_s10 | stoch | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.669 | -15 / -156 / -14 / -1 / 45 / -3 | 0% (n=50) | 0.060 | 0.015 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | deter | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.666 | -15 / -51 / -15 / -1 / 44 / -3 | 0% (n=50) | 0.060 | 0.015 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | stoch | residual on scripted swing: cap +-[0.02, 0.02, 0.01, 0.02] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.663 | -16 / -102 / -16 / -2 / 44 / -2 | 0% (n=50) | 0.060 | 0.015 |
| ppo_v3tiny_s22 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.090 | -13 / 1 / -13 / 16 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s22 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.078 | -14 / -92 / -13 / 16 / 45 / -2 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s21 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.079 | -15 / 49 / -15 / 14 / 44 / -1 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s21 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.065 | -14 / -32 / -13 / 14 / 45 / -2 | 0% (n=50) | 0.060 | 0.025 |
| ppo_v3tiny_s23 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.095 | -13 / 0 / -13 / 15 / 46 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3tiny_s23 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.3 (env default); % of control from policy = not defined/unknown | 2.059 | -14 / -72 / -13 / 15 / 45 / -3 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3flt_all_s33 | deter | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.02; % of control from policy = not defined/unknown | 2.126 | -15 / 7 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3flt_all_s33 | stoch | residual on scripted swing: cap +-[0.01, 0.01, 0.01, 0.01] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.02; % of control from policy = not defined/unknown | 2.108 | -15 / -139 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.068 | -15 / 20 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.066 | -15 / -170 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.066 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 2.063 | -15 / -180 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.845 | -15 / -40 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.845 | -15 / -138 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s42 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.846 | -15 / 1 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s42 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.843 | -15 / -165 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s43 | deter | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.847 | -15 / 4 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| ppo_v4yaw_s43 | stoch | residual on scripted swing: cap +-[0.0, 0.0, 0.0, 0.05] rad (shoulder, elbow, wrist, yaw) + tempo_scale 0.0; % of control from policy = not defined/unknown | 1.843 | -15 / -85 / -15 / -5 / 44 / -0 | 0% (n=50) | 0.060 | 0.010 |
| imit2_w075_s53 | deter | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.010 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s53 | stoch | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.106 | -15 / 0 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s51 | deter | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.161 | -15 / 3 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s51 | stoch | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.104 | -15 / 0 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s52 | deter | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.007 | -15 / 10 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit2_w075_s52 | stoch | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.047 | -15 / 10 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s51 | deter | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.062 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s51 | stoch | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.066 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s52 | deter | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.046 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s52 | stoch | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.049 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w050_s51 | deter | BLEND: executed command = 50% scripted + 50% learned (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.052 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w050_s51 | stoch | BLEND: executed command = 50% scripted + 50% learned (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.045 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w050_s52 | deter | BLEND: executed command = 50% scripted + 50% learned (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.086 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w050_s52 | stoch | BLEND: executed command = 50% scripted + 50% learned (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.075 | -15 / 3 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s53 | deter | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.023 | -15 / 3 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w075_s53 | stoch | BLEND: executed command = 75% scripted + 25% learned (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.026 | -15 / 5 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w025_s52 | deter | BLEND: executed command = 25% scripted + 75% learned (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.119 | -16 / 4 / -16 / 14 / 40 / -1 | 0% (n=50) | 0.055 | 0.030 |
| imit3_w025_s52 | stoch | BLEND: executed command = 25% scripted + 75% learned (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.086 | -16 / 3 / -16 / 14 / 42 / -1 | 0% (n=50) | 0.055 | 0.030 |
| imit3_w025_s51 | deter | BLEND: executed command = 25% scripted + 75% learned (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.095 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w025_s51 | stoch | BLEND: executed command = 25% scripted + 75% learned (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.087 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w000_s52 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.043 | -14 / 5 / -14 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w000_s52 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.103 | -15 / 5 / -14 / 15 / 45 / -4 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | deter | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.049 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | stoch | BLEND: executed command = 0% scripted + 100% learned (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); residual cap +-[0.01, 0.01, 0.01, 0.01] rad ; HYPOTHETICAL ACTUATORS force_scale 2 | 2.040 | -15 / 1 / -15 / 15 / 45 / -5 | 0% (n=50) | 0.060 | 0.030 |

**Mason reference (proxy, `data/references/mason_target_features.json`, file mtime 2026-10-16 11:30; schema mason_target_features/v1; self-filmed ~30 fps 2D MediaPipe angles, ?-swing set, events +-1 frame, tempo +-15%):** arm-only sequencing, times in seconds from takeoff within [top, impact+0.15 s]: shoulder_R peak 0.94, elbow_R 1.09, wrist_R 1.04; wrist-minus-shoulder lag median 0.05 s; elbow-minus-shoulder (from medians) 0.15 s. Pelvis/thorax sequencing is UNAVAILABLE for Mason (reported 'unavailable'), so hips/torso rows cannot be compared. The Data Agent's regenerated (0.4 s timing fix) version is used only if the file in this tree is that version (check the mtime above); no sequencing number is taken from anywhere else. Sim lags and Mason lags are different windows/definitions: indicative only.

## Distance in yards (1 m = 1.09361 yd) - det / stoch separate

Total = carry + roll = final ball x minus start x along the target line at episode end (450-step horizon; ball may still be rolling; analytic-ball runs end early). Carry = first-landing distance (0 if never landed). Means over all episodes.

| Model(s) | Mode | Carry m | Carry yd | Total m | Total yd | Roll m (landed shots) | Max total yd |
|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | deter | 0.0 | 0.0 | -0.0 | -0.1 | nan | -0 |
| ppo_scott_baseline | stoch | 0.0 | 0.0 | 0.6 | 0.6 | nan | 8 |
| ppo_scott_curr | deter | 0.0 | 0.0 | 2.6 | 2.8 | nan | 3 |
| ppo_scott_curr | stoch | 0.0 | 0.0 | 4.0 | 4.4 | nan | 13 |
| ppo_scott_prev_backup | deter | 0.0 | 0.0 | 2.3 | 2.5 | nan | 3 |
| ppo_scott_prev_backup | stoch | 0.0 | 0.0 | 4.1 | 4.5 | nan | 14 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | 0.1 | 0.1 | 1.4 | 1.5 | nan | 10 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | 0.1 | 0.2 | 2.3 | 2.5 | nan | 12 |
| ppo_scott<br>ppo_scott_carry1 | deter | 0.1 | 0.1 | 0.0 | 0.0 | nan | 0 |
| ppo_scott<br>ppo_scott_carry1 | stoch | 0.4 | 0.5 | 0.5 | 0.5 | nan | 7 |
| ppo_resid_v3_s0 | deter | 57.1 | 62.5 | 56.7 | 62.0 | 0.0 | 76 |
| ppo_resid_v3_s0 | stoch | 20.8 | 22.8 | 37.7 | 41.3 | nan | 316 |
| ppo_resid_v3_r2_s0 | deter | 86.9 | 95.1 | 86.5 | 94.6 | 0.0 | 115 |
| ppo_resid_v3_r2_s0 | stoch | 60.5 | 66.1 | 110.0 | 120.3 | nan | 364 |
| ppo_resid_v3_r3_s0 | deter | 103.4 | 113.1 | 103.0 | 112.7 | 0.0 | 167 |
| ppo_resid_v3_r3_s0 | stoch | 66.8 | 73.0 | 123.5 | 135.0 | nan | 375 |
| ppo_resid_v3_ladder_s0 | deter | 99.6 | 109.0 | 99.2 | 108.5 | 0.0 | 146 |
| ppo_resid_v3_ladder_s0 | stoch | 69.1 | 75.5 | 94.0 | 102.9 | nan | 371 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deter | 36.7 | 40.1 | 176.8 | 193.3 | nan | 362 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stoch | 36.7 | 40.1 | 176.8 | 193.3 | nan | 362 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deter | 53.9 | 59.0 | 118.0 | 129.1 | nan | 356 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stoch | 53.9 | 59.0 | 118.0 | 129.1 | nan | 356 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deter | 69.4 | 75.9 | 80.3 | 87.8 | nan | 317 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stoch | 69.4 | 75.9 | 80.3 | 87.8 | nan | 317 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deter | 115.7 | 126.5 | 115.3 | 126.1 | 0.0 | 204 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stoch | 115.7 | 126.5 | 115.3 | 126.1 | 0.0 | 204 |
| ppo_resid_v3_left_an1_s0 | deter | 108.9 | 119.1 | 108.5 | 118.6 | 0.0 | 157 |
| ppo_resid_v3_left_an1_s0 | stoch | 86.0 | 94.0 | 105.8 | 115.7 | nan | 372 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | deter | 111.9 | 122.3 | 111.4 | 121.9 | 0.0 | 174 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | stoch | 89.9 | 98.3 | 115.9 | 126.8 | nan | 386 |
| ppo_resid_v3_left_an3_s1 | deter | 110.8 | 121.2 | 117.1 | 128.1 | nan | 370 |
| ppo_resid_v3_left_an3_s1 | stoch | 105.4 | 115.3 | 111.7 | 122.1 | nan | 366 |
| ppo_resid_v3_left_an4_s2 | deter | 95.4 | 104.3 | 94.9 | 103.8 | 0.0 | 178 |
| ppo_resid_v3_left_an4_s2 | stoch | 98.8 | 108.1 | 98.4 | 107.6 | 0.0 | 186 |
| ppo_resid_v3_left_an5_s3 | deter | 10.0 | 10.9 | 101.6 | 111.1 | nan | 390 |
| ppo_resid_v3_left_an5_s3 | stoch | 8.5 | 9.3 | 141.1 | 154.3 | nan | 393 |
| ppo_resid_v3_left_an6_s4 | deter | 105.5 | 115.4 | 111.8 | 122.2 | nan | 366 |
| ppo_resid_v3_left_an6_s4 | stoch | 78.1 | 85.5 | 145.2 | 158.8 | nan | 387 |
| ppo_resid_v3_left_an7_s5 | deter | 7.9 | 8.6 | 139.7 | 152.7 | nan | 389 |
| ppo_resid_v3_left_an7_s5 | stoch | 9.6 | 10.4 | 92.9 | 101.6 | nan | 390 |
| ppo_resid_v3_left_an8_s6 | deter | 11.2 | 12.3 | 89.4 | 97.8 | nan | 393 |
| ppo_resid_v3_left_an8_s6 | stoch | 10.9 | 11.9 | 88.4 | 96.7 | nan | 395 |
| ppo_resid_v3_left_an9_s7 | deter | 102.1 | 111.7 | 101.7 | 111.2 | 0.0 | 149 |
| ppo_resid_v3_left_an9_s7 | stoch | 78.3 | 85.6 | 130.5 | 142.7 | nan | 368 |
| ppo_resid_v3_left_an10_s8 | deter | 107.0 | 117.1 | 125.8 | 137.5 | nan | 358 |
| ppo_resid_v3_left_an10_s8 | stoch | 55.5 | 60.7 | 149.3 | 163.2 | nan | 369 |
| ppo_resid_v3_left_fast1_s10 | deter | 15.9 | 17.3 | 15.5 | 16.9 | 0.0 | 26 |
| ppo_resid_v3_left_fast1_s10 | stoch | 15.5 | 16.9 | 15.1 | 16.5 | 0.0 | 26 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | deter | 15.0 | 16.4 | 14.6 | 16.0 | 0.0 | 25 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | stoch | 15.5 | 16.9 | 15.1 | 16.5 | 0.0 | 26 |
| ppo_v3tiny_s22 | deter | 99.2 | 108.5 | 109.4 | 119.7 | nan | 289 |
| ppo_v3tiny_s22 | stoch | 101.9 | 111.4 | 117.6 | 128.6 | nan | 297 |
| ppo_v3tiny_s21 | deter | 84.6 | 92.5 | 122.3 | 133.8 | nan | 302 |
| ppo_v3tiny_s21 | stoch | 103.3 | 113.0 | 118.8 | 130.0 | nan | 297 |
| ppo_v3tiny_s23 | deter | 91.0 | 99.5 | 118.5 | 129.6 | nan | 316 |
| ppo_v3tiny_s23 | stoch | 105.2 | 115.1 | 121.2 | 132.6 | nan | 304 |
| ppo_v3flt_all_s33 | deter | 95.0 | 103.9 | 100.3 | 109.7 | nan | 311 |
| ppo_v3flt_all_s33 | stoch | 99.2 | 108.4 | 110.0 | 120.3 | nan | 307 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | deter | 113.9 | 124.6 | 113.5 | 124.1 | 0.0 | 203 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | stoch | 114.0 | 124.6 | 113.6 | 124.2 | 0.0 | 203 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | deter | 114.3 | 124.9 | 113.9 | 124.5 | 0.0 | 203 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | stoch | 114.8 | 125.5 | 114.4 | 125.1 | 0.0 | 203 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | deter | 243.6 | 266.4 | 261.3 | 285.8 | nan | 338 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | stoch | 243.4 | 266.2 | 261.1 | 285.6 | nan | 338 |
| ppo_v4yaw_s42 | deter | 243.3 | 266.1 | 261.0 | 285.4 | nan | 338 |
| ppo_v4yaw_s42 | stoch | 250.0 | 273.3 | 261.6 | 286.1 | nan | 338 |
| ppo_v4yaw_s43 | deter | 243.0 | 265.8 | 260.7 | 285.1 | nan | 338 |
| ppo_v4yaw_s43 | stoch | 244.3 | 267.1 | 262.0 | 286.5 | nan | 338 |
| imit2_w075_s53 | deter | 116.9 | 127.8 | 138.8 | 151.8 | nan | 320 |
| imit2_w075_s53 | stoch | 96.1 | 105.1 | 112.3 | 122.8 | nan | 305 |
| imit2_w075_s51 | deter | 49.3 | 53.9 | 126.2 | 138.0 | nan | 313 |
| imit2_w075_s51 | stoch | 80.6 | 88.1 | 124.3 | 135.9 | nan | 308 |
| imit2_w075_s52 | deter | 117.8 | 128.9 | 139.5 | 152.6 | nan | 310 |
| imit2_w075_s52 | stoch | 103.2 | 112.9 | 130.7 | 143.0 | nan | 318 |
| imit3_w075_s51 | deter | 113.1 | 123.7 | 112.7 | 123.2 | 0.0 | 199 |
| imit3_w075_s51 | stoch | 112.4 | 122.9 | 112.0 | 122.5 | 0.0 | 199 |
| imit3_w075_s52 | deter | 108.4 | 118.6 | 124.6 | 136.2 | nan | 303 |
| imit3_w075_s52 | stoch | 108.2 | 118.3 | 124.3 | 135.9 | nan | 302 |
| imit3_w050_s51 | deter | 119.4 | 130.6 | 119.0 | 130.1 | 0.0 | 207 |
| imit3_w050_s51 | stoch | 120.5 | 131.7 | 120.1 | 131.3 | 0.0 | 204 |
| imit3_w050_s52 | deter | 107.7 | 117.8 | 107.3 | 117.4 | 0.0 | 178 |
| imit3_w050_s52 | stoch | 109.7 | 120.0 | 109.3 | 119.5 | 0.0 | 187 |
| imit3_w075_s53 | deter | 112.0 | 122.4 | 133.7 | 146.3 | nan | 307 |
| imit3_w075_s53 | stoch | 114.6 | 125.4 | 131.1 | 143.4 | nan | 313 |
| imit3_w025_s52 | deter | 88.9 | 97.3 | 116.7 | 127.6 | nan | 313 |
| imit3_w025_s52 | stoch | 91.4 | 100.0 | 124.8 | 136.5 | nan | 311 |
| imit3_w025_s51 | deter | 105.1 | 114.9 | 104.7 | 114.5 | 0.0 | 182 |
| imit3_w025_s51 | stoch | 106.2 | 116.1 | 105.8 | 115.7 | 0.0 | 172 |
| imit3_w000_s52 | deter | 105.1 | 115.0 | 127.0 | 138.9 | nan | 313 |
| imit3_w000_s52 | stoch | 91.9 | 100.5 | 119.4 | 130.6 | nan | 318 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | deter | 109.4 | 119.7 | 125.6 | 137.3 | nan | 303 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | stoch | 111.3 | 121.7 | 127.4 | 139.3 | nan | 301 |

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
- **scripted_baseline[ladder cfg: right, loft 6, default ball_x]** (0 steps): zero-residual action with results/ppo_resid_v3_ladder_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 6.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "right", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm]** (0 steps): zero-residual action; trainer config from TRAINING_NOTES / eval/eval_scripted_cfg.py base + ball_x 0.422, ball_x_noise 0.005, loft 7, left; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "ball_x": 0.422, "ball_x_noise": 0.005}`
- **scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01]** (0 steps): zero-residual; configs/fast_scripted_v2_lofted.json (trainer) applied over eval/eval_scripted_cfg.py base (as the trainer's eval_scripted_cfg usage); env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "loft_deg": -26, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.01, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1}`
- **scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01]** (0 steps): zero-residual; configs/fast_scripted_v3.json (trainer) applied over eval/eval_scripted_cfg.py base (as the trainer's eval_scripted_cfg usage); env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "loft_deg": -31, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1}`
- **ppo_resid_v3_left_an1_s0** (150000 steps): results/ppo_resid_v3_left_an1_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.2, 0.2, 0.2, 0.1], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an2_s0/best_carry_analytic** (150000 steps): results/ppo_resid_v3_left_an2_s0.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an3_s1** (150000 steps): results/ppo_resid_v3_left_an3_s1.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 8.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an4_s2** (150000 steps): results/ppo_resid_v3_left_an4_s2.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.1, 0.1, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an5_s3** (150000 steps): results/ppo_resid_v3_left_an5_s3.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an6_s4** (150000 steps): results/ppo_resid_v3_left_an6_s4.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.03], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an7_s5** (120000 steps): results/ppo_resid_v3_left_an7_s5.json args; env = `{"_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.04, 0.04, 0.03, 0.02], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an8_s6** (120000 steps): results/ppo_resid_v3_left_an8_s6.json args; env = `{"ball_x": 0.4, "ball_x_noise": 0.015, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an9_s7** (120000 steps): results/ppo_resid_v3_left_an9_s7.json args; env = `{"ball_x": 0.43, "ball_x_noise": 0.015, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_an10_s8** (120000 steps): results/ppo_resid_v3_left_an10_s8.json args; env = `{"ball_x": 0.422, "ball_x_noise": 0.005, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.12, "t_back": 0.6}, "residual_scale": [0.1, 0.08, 0.05, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 7.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 1.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_fast1_s10** (100000 steps): results/ppo_resid_v3_left_fast1_s10.json args; env = `{"ball_x": 0.39, "ball_x_noise": 0.005, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6}, "residual_scale": [0.02, 0.02, 0.01, 0.02], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 9.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.5, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph** (100000 steps): results/ppo_resid_v3_left_fast2_s11.json args; env = `{"ball_x": 0.39, "ball_x_noise": 0.005, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6}, "residual_scale": [0.02, 0.02, 0.01, 0.02], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": 9.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": 0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.5, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3tiny_s22** (60000 steps): results/ppo_v3tiny_s22.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3tiny_s21** (60000 steps): results/ppo_v3tiny_s21.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3tiny_s23** (60000 steps): results/ppo_v3tiny_s23.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3flt_all_s33** (30000 steps): results/ppo_v3flt_all_s33.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.02, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3flt_yaw_s32/best_learned_yaw_s32** (30000 steps): results/ppo_v3flt_yaw_s32.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v3flt_yaw_s31/best_learned_yaw_s31** (30000 steps): results/ppo_v3flt_yaw_s31.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v4yaw_s41/best_v4yaw_s41** (30000 steps): results/ppo_v4yaw_s41.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": -0.019, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.065, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v4yaw_s42** (30000 steps): results/ppo_v4yaw_s42.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": -0.019, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.065, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **ppo_v4yaw_s43** (30000 steps): results/ppo_v4yaw_s43.json args; env = `{"ball_x": 0.396, "ball_x_noise": 0.003, "sh_noise": 0.05, "el_noise": 0.1, "tempo_scale": 0.0, "contact_damp": 0.3, "impact_model": {"gain": 1.28, "dz0": -0.019, "k_off": 0.4, "spin_k": 130, "k_side": 3500}, "_env": "residual", "script": {"q_back": 2.2, "t_down": 0.065, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.0, 0.0, 0.0, 0.05], "model_xml": "humanoid_golf_v3.xml", "flight_model": true, "tee_height": 0.04, "force_scale": 2.0, "kp": 700.0, "kd": 23.333333333333332, "loft_deg": -31.0, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "ball_dz": -0.008, "handedness": "left", "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05}`
- **imit2_w075_s53** (15000 steps): results/imit2_w075_s53.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit2_w075_s51** (15000 steps): results/imit2_w075_s51.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit2_w075_s52** (15000 steps): results/imit2_w075_s52.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w075_s51** (8000 steps): results/imit3_w075_s51.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w075_s52** (8000 steps): results/imit3_w075_s52.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w050_s51** (8000 steps): results/imit3_w050_s51.json env_kwargs_full (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.5, "learn_scale": [1.2, 0.35, 0.075, 0.075], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w050_s52** (8000 steps): results/imit3_w050_s52.json env_kwargs_full (script_weight=0.5, learn_scale=[1.2, 0.35, 0.075, 0.075]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.5, "learn_scale": [1.2, 0.35, 0.075, 0.075], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w075_s53** (8000 steps): results/imit3_w075_s53.json env_kwargs_full (script_weight=0.75, learn_scale=[0.6, 0.175, 0.0375, 0.0375]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.75, "learn_scale": [0.6, 0.175, 0.0375, 0.0375], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w025_s52** (8000 steps): results/imit3_w025_s52.json env_kwargs_full (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.25, "learn_scale": [1.8, 0.525, 0.1125, 0.1125], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w025_s51** (8000 steps): results/imit3_w025_s51.json env_kwargs_full (script_weight=0.25, learn_scale=[1.8, 0.525, 0.1125, 0.1125]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.25, "learn_scale": [1.8, 0.525, 0.1125, 0.1125], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w000_s52** (8000 steps): results/imit3_w000_s52.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`
- **imit3_w000_s51/best_imit_scriptfree_s51_NOTPASS_lat3.56** (8000 steps): results/imit3_w000_s51.json env_kwargs_full (script_weight=0.0, learn_scale=[2.4, 0.7, 0.15, 0.15]); env = `{"script": {"q_back": 2.2, "t_down": 0.095, "t_back": 0.6, "wr_end": -0.01, "yaw_ff": 0.0}, "residual_scale": [0.01, 0.01, 0.01, 0.01], "flight_model": true, "curriculum": true, "carry_reward": true, "forward_reward": true, "randomize_reset": true, "gate_lo": 15.0, "gate_hi": 35.0, "seq_weight": 0.0, "style_prior": false, "yaw_amp": 0.1, "wrist_amp": 0.0, "style_lead": 0.05, "analytic_ball": false, "lat_weight": 0.0, "elev_weight": 0.0, "carry_cap": 120.0, "tempo_scale": 0.0, "shot_pen": 1.0, "act_l2": 0.0, "script_weight": 0.0, "learn_scale": [2.4, 0.7, 0.15, 0.15], "track_set": null, "track_weight": 0.0, "ball_x": 0.396, "ball_x_noise": 0.003, "loft_deg": -31, "ball_dz": -0.008, "tee_height": 0.04, "force_scale": 2.0, "kp": 700, "kd": 23.33, "handedness": "left", "model_xml": "humanoid_golf_v3.xml", "sh_noise": 0.05, "el_noise": 0.1, "_env": "residual"}`

## Showcase qualification criterion

A model qualifies only if ALL hold (deterministic mode unless stated, physics protocol, 50 eps): true contact 100% in both modes; mean carry >= 30 m (documented threshold; the scripted baseline carries ~38 m on this protocol); lateral std <= 2.73 m (the trainer's gate baseline); mean launch elevation >= 5 deg (ball velocity at the end of club-ball contact; rules out the flat/negative-launch exploit). Among qualifiers: highest mean carry over det+stoch.

| Model | contact==100% (det and stoch) | mean carry >= 30 m (det) | lateral std <= 2.73 m (det) | mean launch elev >= 5 deg, not flat (det) | Qualifies |
|---|---|---|---|---|---|
| ppo_v4yaw_s42 | yes | yes | yes | yes | **YES** |
| ppo_v4yaw_s43 | yes | yes | yes | yes | **YES** |
| ppo_v4yaw_s41/best_v4yaw_s41 | yes | yes | yes | yes | **YES** |
| imit3_w050_s51 | yes | yes | yes | yes | **YES** |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | yes | yes | yes | yes | **YES** |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | yes | yes | yes | yes | **YES** |
| imit3_w075_s53 | yes | yes | yes | yes | **YES** |
| imit3_w075_s51 | yes | yes | yes | yes | **YES** |
| imit2_w075_s52 | yes | yes | NO | yes | no |
| imit3_w000_s51/best_imit_scriptfree_s51_NOTPASS_lat3.56 | yes | yes | NO | yes | no |
| imit3_w050_s52 | yes | yes | yes | yes | **YES** |
| imit3_w075_s52 | yes | yes | yes | yes | **YES** |
| ppo_resid_v3_left_an3_s1 | yes | yes | NO | yes | no |
| imit2_w075_s53 | yes | yes | NO | yes | no |
| imit3_w025_s51 | yes | yes | yes | yes | **YES** |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | yes | yes | NO | yes | no |
| ppo_v3tiny_s22 | yes | yes | NO | yes | no |
| imit3_w000_s52 | yes | yes | NO | yes | no |
| ppo_v3tiny_s23 | yes | yes | NO | yes | no |
| ppo_resid_v3_left_an1_s0 | yes | yes | NO | yes | no |
| ppo_resid_v3_left_an4_s2 | yes | yes | NO | yes | no |
| ppo_v3flt_all_s33 | yes | yes | NO | yes | no |
| ppo_v3tiny_s21 | yes | yes | NO | yes | no |
| ppo_resid_v3_left_an6_s4 | yes | yes | NO | yes | no |
| ppo_resid_v3_left_an9_s7 | yes | yes | NO | yes | no |
| imit3_w025_s52 | yes | yes | NO | yes | no |
| ppo_resid_v3_r3_s0 | yes | yes | NO | yes | no |
| ppo_resid_v3_ladder_s0 | yes | yes | NO | yes | no |
| ppo_resid_v3_left_an10_s8 | yes | yes | NO | yes | no |
| ppo_resid_v3_r2_s0 | yes | yes | NO | yes | no |
| imit2_w075_s51 | yes | yes | yes | NO | no |
| ppo_resid_v3_left_fast1_s10 | yes | NO | yes | NO | no |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an8_s6 | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an5_s3 | yes | NO | yes | NO | no |
| ppo_resid_v3_left_an7_s5 | yes | NO | yes | NO | no |
| ppo_scott/ppo_scott_carry1 | NO | NO | yes | yes | no |
| ppo_resid_v3_s0 | NO | yes | NO | yes | no |
| ppo_scott_prev_backup | NO | NO | yes | yes | no |
| ppo_scott_curr | NO | NO | yes | yes | no |
| ppo_scott_final2/ppo_scott_prev2_backup | NO | NO | yes | yes | no |
| ppo_scott_baseline | NO | NO | yes | yes | no |

Qualifying: ppo_v4yaw_s42, ppo_v4yaw_s43, ppo_v4yaw_s41/best_v4yaw_s41, imit3_w050_s51, ppo_v3flt_yaw_s31/best_learned_yaw_s31, ppo_v3flt_yaw_s32/best_learned_yaw_s32, imit3_w075_s53, imit3_w075_s51, imit3_w050_s52, imit3_w075_s52, imit3_w025_s51

Flat/negative-launch flag (mean elevation < 5 deg or >= 50% of shots below it): ppo_scott_prev_backup [sto 4.7 deg], scripted_baseline[ladder cfg: right, loft 6, default ball_x] [det 9.2 deg, sto 9.2 deg], ppo_resid_v3_left_an5_s3 [det -3.8 deg, sto -3.3 deg], ppo_resid_v3_left_an7_s5 [det -3.3 deg, sto -4.0 deg], ppo_resid_v3_left_an8_s6 [det -5.1 deg, sto -4.6 deg], ppo_resid_v3_left_an10_s8 [sto 15.4 deg], ppo_resid_v3_left_fast1_s10 [det -5.2 deg, sto -5.0 deg], ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph [det -5.2 deg, sto -4.9 deg], imit2_w075_s51 [det 1.4 deg]

## Left-handed models: trainer gate JSON vs verified (this leaderboard, same protocol: MuJoCo physics, flight tracker, 450-step horizon, deterministic, 50 eps, seeds 4000+)

Verified = this run. Trainer gate = `results/gate_<name>.json` (`eval.eval_gate`; gate: carry > 11.98 m AND lateral std < 2.73 m AND contact >= 99%). Trainer 'analytic' = `results/<name>.json` policy block (100 eps, analytic flight from the MuJoCo launch vector with ASSUMED backspin, episode ends 3 steps after contact) - NOT re-verified here, different protocol.

| Model | Source | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club mph mean | Gate pass |
|---|---|---|---|---|---|---|---|
| ppo_resid_v3_left_an1_s0 | verified (this run, det) | 100% | 100% | 108.88 | 6.90 | 114.4 | FAIL |
| ppo_resid_v3_left_an1_s0 | trainer gate JSON (det) | 100% | 100% | 110.28 | 7.53 | 114.5 | FAIL |
| ppo_resid_v3_left_an1_s0 | trainer analytic (100 eps) | 100% | 100% | 93.13 | 6.61 | 114.0 (impact) | n/a |
| ppo_resid_v3_left_an2_s0 | verified (this run, det) | 100% | 100% | 111.87 | 7.62 | 114.7 | FAIL |
| ppo_resid_v3_left_an2_s0 | trainer gate JSON (det) | 100% | 100% | 114.29 | 7.42 | 114.7 | FAIL |
| ppo_resid_v3_left_an2_s0 | trainer analytic (100 eps) | 100% | 100% | 91.79 | 6.53 | 114.7 (impact) | n/a |
| ppo_resid_v3_left_an3_s1 | verified (this run, det) | 100% | 98% | 110.80 | 7.20 | 114.7 | FAIL |
| ppo_resid_v3_left_an3_s1 | trainer gate JSON (det) | 100% | 100% | 108.60 | 6.74 | 114.6 | FAIL |
| ppo_resid_v3_left_an3_s1 | trainer analytic (100 eps) | 100% | 100% | 87.88 | 5.91 | 114.8 (impact) | n/a |
| ppo_resid_v3_left_an4_s2 | verified (this run, det) | 100% | 100% | 95.37 | 6.57 | 111.7 | FAIL |
| ppo_resid_v3_left_an4_s2 | trainer gate JSON (det) | 100% | 100% | 96.13 | 6.68 | 111.7 | FAIL |
| ppo_resid_v3_left_an4_s2 | trainer analytic (100 eps) | 100% | 100% | 78.82 | 5.87 | 111.5 (impact) | n/a |
| ppo_resid_v3_left_an5_s3 | verified (this run, det) | 100% | 74% | 10.00 | 0.14 | 117.0 | FAIL |
| ppo_resid_v3_left_an5_s3 | trainer gate JSON (det) | 100% | 72% | 9.57 | 0.14 | 117.0 | FAIL |
| ppo_resid_v3_left_an5_s3 | trainer analytic (100 eps) | 100% | 100% | 19.44 | 0.01 | 117.2 (impact) | n/a |
| ppo_resid_v3_left_an6_s4 | verified (this run, det) | 100% | 98% | 105.48 | 8.94 | 113.0 | FAIL |
| ppo_resid_v3_left_an6_s4 | trainer gate JSON (det) | 100% | 98% | 99.80 | 6.95 | 113.0 | FAIL |
| ppo_resid_v3_left_an6_s4 | trainer analytic (100 eps) | 100% | 100% | 89.06 | 6.63 | 112.9 (impact) | n/a |
| ppo_resid_v3_left_an7_s5 | verified (this run, det) | 100% | 62% | 7.87 | 0.28 | 115.2 | FAIL |
| ppo_resid_v3_left_an7_s5 | trainer analytic (100 eps) | 100% | 100% | 19.88 | 0.01 | 115.2 (impact) | n/a |
| ppo_resid_v3_left_an8_s6 | verified (this run, det) | 100% | 78% | 11.21 | 0.09 | 118.5 | FAIL |
| ppo_resid_v3_left_an8_s6 | trainer analytic (100 eps) | 100% | 100% | 24.42 | 0.01 | 118.5 (impact) | n/a |
| ppo_resid_v3_left_an9_s7 | verified (this run, det) | 100% | 100% | 102.12 | 7.92 | 110.5 | FAIL |
| ppo_resid_v3_left_an9_s7 | trainer gate JSON (det) | 100% | 100% | 103.33 | 8.17 | 110.4 | FAIL |
| ppo_resid_v3_left_an9_s7 | trainer analytic (100 eps) | 100% | 100% | 85.32 | 6.61 | 110.5 (impact) | n/a |
| ppo_resid_v3_left_an10_s8 | verified (this run, det) | 100% | 94% | 107.04 | 5.44 | 107.1 | FAIL |
| ppo_resid_v3_left_an10_s8 | trainer analytic (100 eps) | 100% | 100% | 92.72 | 5.74 | 107.2 (impact) | n/a |
| ppo_resid_v3_left_fast1_s10 | verified (this run, det) | 100% | 100% | 15.85 | 0.02 | 122.3 | PASS |
| ppo_resid_v3_left_fast1_s10 | trainer analytic (100 eps) | 100% | 100% | 28.57 | 0.02 | 122.2 (impact) | n/a |
| ppo_resid_v3_left_fast2_s11 | verified (this run, det) | 100% | 100% | 14.97 | 0.02 | 123.6 | PASS |
| ppo_resid_v3_left_fast2_s11 | trainer gate JSON (det) | 100% | 100% | 15.24 | 0.02 | 123.6 | PASS |
| ppo_resid_v3_left_fast2_s11 | trainer analytic (100 eps) | 100% | 100% | 31.25 | 0.04 | 123.6 (impact) | n/a |
| ppo_v3tiny_s22 | verified (this run, det) | 100% | 96% | 99.24 | 6.32 | 118.4 | FAIL |
| ppo_v3tiny_s22 | trainer gate JSON (det) | 100% | 94% | 105.08 | 5.23 | 118.4 | FAIL |
| ppo_v3tiny_s22 | trainer analytic (100 eps) | 100% | 100% | 140.62 | 0.14 | 118.4 (impact) | n/a |
| ppo_v3tiny_s21 | verified (this run, det) | 100% | 86% | 84.58 | 4.41 | 119.0 | FAIL |
| ppo_v3tiny_s21 | trainer gate JSON (det) | 100% | 88% | 86.42 | 6.45 | 118.9 | FAIL |
| ppo_v3tiny_s21 | trainer analytic (100 eps) | 100% | 100% | 120.95 | 0.10 | 119.0 (impact) | n/a |
| ppo_v3tiny_s23 | verified (this run, det) | 100% | 90% | 91.00 | 2.81 | 119.0 | FAIL |
| ppo_v3tiny_s23 | trainer gate JSON (det) | 100% | 87% | 93.63 | 4.43 | 118.9 | FAIL |
| ppo_v3tiny_s23 | trainer analytic (100 eps) | 100% | 100% | 131.80 | 0.14 | 118.9 (impact) | n/a |
| ppo_v3flt_all_s33 | verified (this run, det) | 100% | 98% | 95.00 | 5.13 | 120.3 | FAIL |
| ppo_v3flt_all_s33 | trainer gate JSON (det) | 100% | 99% | 104.98 | 10.23 | 120.3 | FAIL |
| ppo_v3flt_all_s33 | trainer analytic (100 eps) | 100% | 97% | 100.59 | 9.35 | 120.3 (impact) | n/a |
| ppo_v3flt_yaw_s32 | verified (this run, det) | 100% | 100% | 113.90 | 1.59 | 120.3 | PASS |
| ppo_v3flt_yaw_s32 | trainer gate JSON (det) | 100% | 100% | 112.56 | 2.09 | 120.3 | PASS |
| ppo_v3flt_yaw_s32 | trainer analytic (100 eps) | 100% | 100% | 109.46 | 1.34 | 120.3 (impact) | n/a |
| ppo_v3flt_yaw_s31 | verified (this run, det) | 100% | 100% | 114.25 | 1.61 | 120.3 | PASS |
| ppo_v3flt_yaw_s31 | trainer gate JSON (det) | 100% | 100% | 112.60 | 1.99 | 120.3 | PASS |
| ppo_v3flt_yaw_s31 | trainer analytic (100 eps) | 100% | 100% | 109.13 | 1.38 | 120.3 (impact) | n/a |
| ppo_v4yaw_s41 | verified (this run, det) | 100% | 94% | 243.59 | 1.67 | 128.3 | PASS |
| ppo_v4yaw_s41 | trainer gate JSON (det) | 100% | 94% | 242.71 | 2.31 | 128.3 | PASS |
| ppo_v4yaw_s41 | trainer analytic (100 eps) | 100% | 94% | 246.59 | 2.15 | 128.3 (impact) | n/a |
| ppo_v4yaw_s42 | verified (this run, det) | 100% | 94% | 243.29 | 1.66 | 128.3 | PASS |
| ppo_v4yaw_s42 | trainer gate JSON (det) | 100% | 94% | 242.96 | 2.37 | 128.3 | PASS |
| ppo_v4yaw_s42 | trainer analytic (100 eps) | 100% | 94% | 246.25 | 2.16 | 128.3 (impact) | n/a |
| ppo_v4yaw_s43 | verified (this run, det) | 100% | 94% | 243.01 | 1.65 | 128.3 | PASS |
| ppo_v4yaw_s43 | trainer gate JSON (det) | 100% | 94% | 242.63 | 2.31 | 128.3 | PASS |
| ppo_v4yaw_s43 | trainer analytic (100 eps) | 100% | 94% | 246.47 | 2.14 | 128.3 (impact) | n/a |
| imit2_w075_s53 | verified (this run, det) | 100% | 92% | 116.88 | 3.57 | 120.7 | FAIL |
| imit2_w075_s53 | trainer gate JSON (det) | 100% | 91% | 109.78 | 3.04 | 120.7 | FAIL |
| imit2_w075_s53 | trainer analytic (100 eps) | 100% | 100% | 114.43 | 2.22 | 120.7 (impact) | n/a |
| imit2_w075_s51 | verified (this run, det) | 100% | 72% | 49.28 | 0.58 | 120.5 | PASS |
| imit2_w075_s51 | trainer gate JSON (det) | 100% | 67% | 45.78 | 2.24 | 120.5 | PASS |
| imit2_w075_s51 | trainer analytic (100 eps) | 100% | 68% | 51.42 | 0.61 | 120.4 (impact) | n/a |
| imit2_w075_s52 | verified (this run, det) | 100% | 92% | 117.84 | 2.96 | 120.6 | FAIL |
| imit2_w075_s52 | trainer gate JSON (det) | 100% | 93% | 112.62 | 2.82 | 120.5 | FAIL |
| imit2_w075_s52 | trainer analytic (100 eps) | 100% | 100% | 114.15 | 2.29 | 120.6 (impact) | n/a |
| imit3_w075_s51 | verified (this run, det) | 100% | 100% | 113.09 | 0.73 | 120.2 | PASS |
| imit3_w075_s51 | trainer gate JSON (det) | 100% | 100% | 113.39 | 1.51 | 120.2 | PASS |
| imit3_w075_s51 | trainer analytic (100 eps) | 100% | 100% | 106.96 | 0.35 | 120.2 (impact) | n/a |
| imit3_w075_s52 | verified (this run, det) | 100% | 94% | 108.42 | 1.10 | 120.3 | PASS |
| imit3_w075_s52 | trainer gate JSON (det) | 100% | 97% | 110.77 | 1.73 | 120.3 | PASS |
| imit3_w075_s52 | trainer analytic (100 eps) | 100% | 100% | 106.09 | 0.36 | 120.4 (impact) | n/a |
| imit3_w050_s51 | verified (this run, det) | 100% | 100% | 119.39 | 2.20 | 120.4 | PASS |
| imit3_w050_s51 | trainer gate JSON (det) | 100% | 100% | 117.43 | 2.39 | 120.4 | PASS |
| imit3_w050_s51 | trainer analytic (100 eps) | 100% | 98% | 111.12 | 1.57 | 120.3 (impact) | n/a |
| imit3_w050_s52 | verified (this run, det) | 100% | 100% | 107.74 | 0.23 | 120.4 | PASS |
| imit3_w050_s52 | trainer gate JSON (det) | 100% | 100% | 107.66 | 1.14 | 120.4 | PASS |
| imit3_w050_s52 | trainer analytic (100 eps) | 100% | 100% | 112.60 | 1.05 | 120.3 (impact) | n/a |
| imit3_w075_s53 | verified (this run, det) | 100% | 92% | 111.95 | 2.27 | 120.3 | PASS |
| imit3_w075_s53 | trainer gate JSON (det) | 100% | 96% | 111.73 | 3.04 | 120.3 | FAIL |
| imit3_w075_s53 | trainer analytic (100 eps) | 100% | 100% | 110.97 | 1.36 | 120.3 (impact) | n/a |
| imit3_w025_s52 | verified (this run, det) | 100% | 90% | 88.95 | 5.31 | 123.3 | FAIL |
| imit3_w025_s52 | trainer gate JSON (det) | 100% | 92% | 94.73 | 6.25 | 122.8 | FAIL |
| imit3_w025_s52 | trainer analytic (100 eps) | 100% | 100% | 107.35 | 0.43 | 120.5 (impact) | n/a |
| imit3_w025_s51 | verified (this run, det) | 100% | 100% | 105.11 | 0.11 | 120.5 | PASS |
| imit3_w025_s51 | trainer gate JSON (det) | 100% | 100% | 108.48 | 2.97 | 120.4 | FAIL |
| imit3_w025_s51 | trainer analytic (100 eps) | 100% | 90% | 85.00 | 1.94 | 116.8 (impact) | n/a |
| imit3_w000_s52 | verified (this run, det) | 100% | 92% | 105.15 | 5.53 | 119.1 | FAIL |
| imit3_w000_s52 | trainer gate JSON (det) | 100% | 91% | 90.02 | 5.04 | 118.3 | FAIL |
| imit3_w000_s52 | trainer analytic (100 eps) | 100% | 100% | 106.79 | 5.02 | 120.6 (impact) | n/a |
| imit3_w000_s51 | verified (this run, det) | 100% | 94% | 109.44 | 3.97 | 120.6 | FAIL |
| imit3_w000_s51 | trainer gate JSON (det) | 100% | 100% | 113.77 | 3.56 | 120.7 | FAIL |
| imit3_w000_s51 | trainer analytic (100 eps) | 100% | 78% | 84.30 | 1.33 | 120.4 (impact) | n/a |

## DTW vs NATIVE Mason v2 references (recommended, non-partial, license self_owned/commercial_ok; mean DTW rad: all 11 joints / upper-body 5)

**DTW provenance:** scored against `data/references/mason_v2_*.npz` (npz mtimes unchanged, 2026-10-16 03:39); these do NOT read `mason_target_features.json` or `mason_impact_geometry_targets.json`, so the Data Agent regeneration (0.4 s timing fix) does not alter any DTW number here, and no DTW value used pre-fix target values. `mason_impact_geometry_targets.json` was not present in this working tree when this was generated.  **CAVEATS: 2D-proxy joint angles from single-view MediaPipe, screen-recorded ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak; native left-handed footage, `right_*` columns = anatomical right = LEAD arm of a left-hander, whereas the env's `right_*` joints are the swinging arm of its own model (mapping/sign conventions NOT calibrated). Indicative only. MultiSense (right-handed, CC0, different protocol) deliberately NOT scored here.**

Refs: `p1_s06` (q=0.76, oblique, mirrored=False), `p1_s11` (q=0.76, face_on, mirrored=False), `p2_s02` (q=0.75, down_the_line, mirrored=False), `p2_s01` (q=0.7, down_the_line, mirrored=False), `p1_s04` (q=0.69, down_the_line, mirrored=False), `p1_s03` (q=0.69, down_the_line, mirrored=False), `p2_s13` (q=0.68, down_the_line, mirrored=False), `p2_s10` (q=0.68, down_the_line, mirrored=False), `p1_s05` (q=0.66, down_the_line, mirrored=False), `p2_s11` (q=0.66, down_the_line, mirrored=False), `p3_s09_unmirrored` (q=0.83, down_the_line, mirrored=True)

| Model(s) | Mode | p1_s06 | p1_s11 | p2_s02 | p2_s01 | p1_s04 | p1_s03 | p2_s13 | p2_s10 | p1_s05 | p2_s11 | p3_s09_unmirrored | mean over refs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | deter | 3.868 / 3.317 | 4.866 / 4.311 | 4.260 / 3.439 | 4.214 / 3.462 | 4.750 / 4.059 | 5.142 / 4.378 | 5.131 / 4.336 | 4.910 / 4.229 | 4.578 / 3.869 | 5.153 / 4.451 | 4.192 / 3.674 | 4.642 / 3.957 |
| ppo_scott_baseline | stoch | 7.809 / 6.680 | 8.766 / 7.368 | 8.035 / 6.772 | 8.029 / 6.803 | 8.932 / 7.472 | 9.335 / 7.777 | 9.262 / 7.696 | 9.085 / 7.636 | 8.705 / 7.330 | 9.393 / 7.857 | 8.183 / 6.874 | 8.685 / 7.297 |
| ppo_scott_curr | deter | 3.551 / 2.982 | 3.615 / 2.808 | 3.752 / 2.980 | 3.661 / 2.986 | 3.586 / 2.806 | 3.485 / 2.790 | 3.423 / 2.736 | 3.500 / 2.797 | 3.516 / 2.867 | 3.459 / 2.720 | 2.886 / 2.009 | 3.494 / 2.771 |
| ppo_scott_curr | stoch | 3.359 / 2.583 | 3.469 / 2.601 | 3.510 / 2.611 | 3.458 / 2.635 | 3.399 / 2.533 | 3.359 / 2.526 | 3.320 / 2.466 | 3.347 / 2.539 | 3.352 / 2.564 | 3.298 / 2.472 | 3.282 / 2.450 | 3.377 / 2.544 |
| ppo_scott_prev_backup | deter | 2.358 / 1.914 | 2.452 / 1.592 | 2.516 / 1.924 | 2.473 / 2.013 | 2.384 / 1.795 | 2.230 / 1.679 | 2.267 / 1.611 | 2.301 / 1.799 | 2.382 / 1.864 | 2.230 / 1.763 | 2.361 / 1.693 | 2.359 / 1.786 |
| ppo_scott_prev_backup | stoch | 3.384 / 2.627 | 3.528 / 2.695 | 3.531 / 2.590 | 3.474 / 2.612 | 3.416 / 2.547 | 3.371 / 2.507 | 3.412 / 2.545 | 3.369 / 2.538 | 3.375 / 2.570 | 3.334 / 2.484 | 3.358 / 2.510 | 3.414 / 2.566 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | 3.025 / 2.608 | 3.215 / 2.665 | 3.209 / 2.629 | 3.168 / 2.679 | 3.006 / 2.465 | 2.901 / 2.405 | 2.905 / 2.373 | 2.917 / 2.447 | 2.962 / 2.482 | 2.842 / 2.363 | 3.056 / 2.616 | 3.019 / 2.521 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | 3.313 / 2.494 | 3.489 / 2.599 | 3.492 / 2.534 | 3.454 / 2.558 | 3.360 / 2.449 | 3.334 / 2.432 | 3.336 / 2.437 | 3.317 / 2.447 | 3.321 / 2.478 | 3.275 / 2.391 | 3.428 / 2.605 | 3.374 / 2.493 |
| ppo_scott<br>ppo_scott_carry1 | deter | 2.214 / 1.657 | 2.492 / 1.609 | 2.422 / 1.669 | 2.360 / 1.705 | 2.261 / 1.531 | 2.075 / 1.387 | 2.242 / 1.491 | 2.168 / 1.551 | 2.166 / 1.560 | 2.085 / 1.440 | 2.364 / 1.694 | 2.259 / 1.572 |
| ppo_scott<br>ppo_scott_carry1 | stoch | 3.096 / 2.353 | 3.237 / 2.380 | 3.323 / 2.481 | 3.275 / 2.512 | 3.150 / 2.340 | 3.114 / 2.335 | 3.050 / 2.250 | 3.091 / 2.346 | 3.114 / 2.383 | 3.041 / 2.290 | 3.322 / 2.624 | 3.165 / 2.390 |
| ppo_resid_v3_s0 | deter | 1.822 / 1.294 | 2.203 / 1.435 | 2.103 / 1.367 | 1.963 / 1.362 | 1.887 / 1.190 | 1.779 / 1.228 | 1.834 / 1.204 | 1.808 / 1.244 | 1.798 / 1.248 | 1.761 / 1.174 | 2.129 / 1.487 | 1.917 / 1.294 |
| ppo_resid_v3_s0 | stoch | 2.065 / 1.712 | 2.887 / 2.302 | 2.473 / 1.873 | 2.426 / 1.958 | 2.411 / 1.928 | 2.141 / 1.747 | 2.343 / 1.862 | 2.304 / 1.903 | 2.297 / 1.845 | 2.167 / 1.725 | 2.301 / 1.788 | 2.347 / 1.877 |
| ppo_resid_v3_r2_s0 | deter | 1.851 / 1.340 | 2.231 / 1.481 | 2.120 / 1.407 | 1.983 / 1.403 | 1.912 / 1.238 | 1.772 / 1.264 | 1.866 / 1.258 | 1.833 / 1.291 | 1.822 / 1.294 | 1.790 / 1.222 | 1.993 / 1.475 | 1.925 / 1.334 |
| ppo_resid_v3_r2_s0 | stoch | 1.885 / 1.396 | 2.353 / 1.640 | 2.177 / 1.473 | 2.054 / 1.488 | 2.010 / 1.365 | 1.857 / 1.373 | 1.980 / 1.400 | 1.935 / 1.410 | 1.913 / 1.391 | 1.873 / 1.326 | 2.025 / 1.514 | 2.005 / 1.434 |
| ppo_resid_v3_r3_s0 | deter | 1.826 / 1.299 | 2.194 / 1.428 | 2.098 / 1.360 | 1.954 / 1.353 | 1.889 / 1.195 | 1.772 / 1.240 | 1.841 / 1.217 | 1.812 / 1.251 | 1.799 / 1.255 | 1.770 / 1.188 | 2.076 / 1.473 | 1.912 / 1.296 |
| ppo_resid_v3_r3_s0 | stoch | 1.858 / 1.352 | 2.278 / 1.541 | 2.144 / 1.421 | 2.015 / 1.430 | 1.948 / 1.282 | 1.818 / 1.306 | 1.910 / 1.307 | 1.873 / 1.327 | 1.856 / 1.327 | 1.821 / 1.258 | 2.068 / 1.504 | 1.963 / 1.369 |
| ppo_resid_v3_ladder_s0 | deter | 1.826 / 1.303 | 2.200 / 1.432 | 2.100 / 1.367 | 1.959 / 1.361 | 1.890 / 1.196 | 1.770 / 1.238 | 1.841 / 1.218 | 1.811 / 1.251 | 1.800 / 1.257 | 1.769 / 1.185 | 1.995 / 1.479 | 1.905 / 1.299 |
| ppo_resid_v3_ladder_s0 | stoch | 1.897 / 1.419 | 2.411 / 1.710 | 2.210 / 1.506 | 2.099 / 1.537 | 2.045 / 1.412 | 1.910 / 1.413 | 2.021 / 1.448 | 1.973 / 1.435 | 1.949 / 1.428 | 1.901 / 1.355 | 2.072 / 1.565 | 2.044 / 1.475 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deter | 1.900 / 1.421 | 2.432 / 1.740 | 2.211 / 1.514 | 2.096 / 1.530 | 2.063 / 1.433 | 1.877 / 1.403 | 2.017 / 1.443 | 1.974 / 1.468 | 1.967 / 1.450 | 1.897 / 1.363 | 2.061 / 1.537 | 2.045 / 1.482 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stoch | 1.900 / 1.421 | 2.432 / 1.740 | 2.211 / 1.514 | 2.096 / 1.530 | 2.063 / 1.433 | 1.877 / 1.403 | 2.017 / 1.443 | 1.974 / 1.468 | 1.967 / 1.450 | 1.897 / 1.363 | 2.061 / 1.537 | 2.045 / 1.482 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deter | 2.010 / 1.597 | 2.666 / 2.042 | 2.376 / 1.748 | 2.307 / 1.792 | 2.186 / 1.607 | 1.941 / 1.490 | 2.109 / 1.597 | 2.081 / 1.631 | 2.098 / 1.624 | 1.968 / 1.469 | 2.205 / 1.655 | 2.177 / 1.659 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stoch | 2.010 / 1.597 | 2.666 / 2.042 | 2.376 / 1.748 | 2.307 / 1.792 | 2.186 / 1.607 | 1.941 / 1.490 | 2.109 / 1.597 | 2.081 / 1.631 | 2.098 / 1.624 | 1.968 / 1.469 | 2.205 / 1.655 | 2.177 / 1.659 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deter | 2.142 / 1.797 | 2.756 / 2.173 | 2.491 / 1.965 | 2.464 / 2.037 | 2.203 / 1.698 | 1.952 / 1.533 | 2.118 / 1.658 | 2.114 / 1.718 | 2.141 / 1.732 | 2.004 / 1.534 | 2.278 / 1.718 | 2.242 / 1.778 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stoch | 2.142 / 1.797 | 2.756 / 2.173 | 2.491 / 1.965 | 2.464 / 2.037 | 2.203 / 1.698 | 1.952 / 1.533 | 2.118 / 1.658 | 2.114 / 1.718 | 2.141 / 1.732 | 2.004 / 1.534 | 2.278 / 1.718 | 2.242 / 1.778 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deter | 1.983 / 1.544 | 2.448 / 1.764 | 2.274 / 1.674 | 2.178 / 1.686 | 2.029 / 1.426 | 1.868 / 1.376 | 1.965 / 1.412 | 1.952 / 1.465 | 1.958 / 1.479 | 1.877 / 1.339 | 2.132 / 1.604 | 2.060 / 1.524 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stoch | 1.983 / 1.544 | 2.448 / 1.764 | 2.274 / 1.674 | 2.178 / 1.686 | 2.029 / 1.426 | 1.868 / 1.376 | 1.965 / 1.412 | 1.952 / 1.465 | 1.958 / 1.479 | 1.877 / 1.339 | 2.132 / 1.604 | 2.060 / 1.524 |
| ppo_resid_v3_left_an1_s0 | deter | 1.818 / 1.286 | 2.187 / 1.410 | 2.096 / 1.352 | 1.955 / 1.345 | 1.881 / 1.175 | 1.785 / 1.227 | 1.831 / 1.196 | 1.804 / 1.232 | 1.794 / 1.241 | 1.759 / 1.165 | 1.994 / 1.488 | 1.900 / 1.283 |
| ppo_resid_v3_left_an1_s0 | stoch | 1.846 / 1.332 | 2.268 / 1.519 | 2.136 / 1.402 | 2.007 / 1.411 | 1.940 / 1.257 | 1.825 / 1.290 | 1.893 / 1.281 | 1.861 / 1.305 | 1.850 / 1.311 | 1.807 / 1.232 | 2.022 / 1.513 | 1.951 / 1.350 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | deter | 1.809 / 1.271 | 2.178 / 1.396 | 2.087 / 1.336 | 1.945 / 1.328 | 1.872 / 1.159 | 1.782 / 1.215 | 1.820 / 1.179 | 1.795 / 1.217 | 1.785 / 1.225 | 1.750 / 1.151 | 2.004 / 1.491 | 1.893 / 1.270 |
| ppo_resid_v3_left_an2_s0<br>best_carry_analytic | stoch | 1.830 / 1.305 | 2.239 / 1.479 | 2.117 / 1.377 | 1.984 / 1.379 | 1.920 / 1.229 | 1.822 / 1.274 | 1.880 / 1.253 | 1.846 / 1.280 | 1.830 / 1.282 | 1.797 / 1.213 | 2.016 / 1.507 | 1.935 / 1.325 |
| ppo_resid_v3_left_an3_s1 | deter | 1.815 / 1.279 | 2.192 / 1.420 | 2.093 / 1.342 | 1.953 / 1.338 | 1.887 / 1.181 | 1.798 / 1.236 | 1.841 / 1.206 | 1.812 / 1.236 | 1.799 / 1.242 | 1.765 / 1.173 | 2.000 / 1.488 | 1.905 / 1.286 |
| ppo_resid_v3_left_an3_s1 | stoch | 1.828 / 1.299 | 2.219 / 1.456 | 2.108 / 1.366 | 1.971 / 1.365 | 1.905 / 1.211 | 1.806 / 1.255 | 1.858 / 1.232 | 1.829 / 1.265 | 1.818 / 1.269 | 1.780 / 1.196 | 2.009 / 1.493 | 1.921 / 1.310 |
| ppo_resid_v3_left_an4_s2 | deter | 1.834 / 1.308 | 2.204 / 1.438 | 2.109 / 1.377 | 1.969 / 1.372 | 1.894 / 1.201 | 1.785 / 1.242 | 1.846 / 1.221 | 1.819 / 1.256 | 1.809 / 1.263 | 1.771 / 1.187 | 2.031 / 1.484 | 1.916 / 1.304 |
| ppo_resid_v3_left_an4_s2 | stoch | 1.836 / 1.312 | 2.219 / 1.457 | 2.115 / 1.381 | 1.977 / 1.380 | 1.905 / 1.214 | 1.795 / 1.250 | 1.855 / 1.232 | 1.828 / 1.267 | 1.819 / 1.274 | 1.777 / 1.194 | 2.033 / 1.491 | 1.924 / 1.314 |
| ppo_resid_v3_left_an5_s3 | deter | 2.061 / 1.706 | 2.964 / 2.440 | 2.489 / 1.846 | 2.461 / 1.992 | 2.464 / 1.999 | 2.323 / 1.920 | 2.519 / 1.958 | 2.409 / 1.938 | 2.340 / 1.907 | 2.287 / 1.848 | 2.278 / 1.810 | 2.418 / 1.942 |
| ppo_resid_v3_left_an5_s3 | stoch | 2.006 / 1.612 | 2.810 / 2.237 | 2.405 / 1.731 | 2.354 / 1.849 | 2.355 / 1.841 | 2.217 / 1.785 | 2.392 / 1.824 | 2.299 / 1.802 | 2.235 / 1.775 | 2.187 / 1.717 | 2.217 / 1.742 | 2.316 / 1.811 |
| ppo_resid_v3_left_an6_s4 | deter | 1.844 / 1.324 | 2.234 / 1.476 | 2.130 / 1.393 | 1.997 / 1.400 | 1.906 / 1.219 | 1.799 / 1.254 | 1.854 / 1.235 | 1.830 / 1.272 | 1.824 / 1.281 | 1.780 / 1.198 | 2.018 / 1.502 | 1.929 / 1.323 |
| ppo_resid_v3_left_an6_s4 | stoch | 1.837 / 1.315 | 2.251 / 1.499 | 2.123 / 1.378 | 1.989 / 1.387 | 1.934 / 1.250 | 1.817 / 1.280 | 1.889 / 1.270 | 1.859 / 1.294 | 1.843 / 1.298 | 1.800 / 1.224 | 2.010 / 1.503 | 1.941 / 1.336 |
| ppo_resid_v3_left_an7_s5 | deter | 2.023 / 1.632 | 2.823 / 2.254 | 2.418 / 1.750 | 2.365 / 1.868 | 2.369 / 1.860 | 2.232 / 1.813 | 2.414 / 1.907 | 2.317 / 1.823 | 2.252 / 1.793 | 2.205 / 1.741 | 2.198 / 1.733 | 2.329 / 1.834 |
| ppo_resid_v3_left_an7_s5 | stoch | 2.089 / 1.737 | 2.997 / 2.481 | 2.519 / 1.883 | 2.494 / 2.027 | 2.498 / 2.036 | 2.355 / 1.954 | 2.562 / 2.067 | 2.448 / 1.975 | 2.376 / 1.936 | 2.315 / 1.879 | 2.285 / 1.824 | 2.449 / 1.982 |
| ppo_resid_v3_left_an8_s6 | deter | 2.095 / 1.754 | 3.028 / 2.523 | 2.532 / 1.903 | 2.512 / 2.057 | 2.516 / 2.072 | 2.345 / 1.954 | 2.574 / 2.032 | 2.469 / 2.007 | 2.393 / 1.973 | 2.314 / 1.885 | 2.300 / 1.848 | 2.462 / 2.001 |
| ppo_resid_v3_left_an8_s6 | stoch | 2.089 / 1.747 | 3.025 / 2.518 | 2.529 / 1.900 | 2.510 / 2.051 | 2.512 / 2.063 | 2.356 / 1.959 | 2.575 / 2.025 | 2.464 / 2.002 | 2.388 / 1.964 | 2.316 / 1.884 | 2.303 / 1.848 | 2.461 / 1.997 |
| ppo_resid_v3_left_an9_s7 | deter | 1.830 / 1.302 | 2.197 / 1.431 | 2.103 / 1.367 | 1.961 / 1.359 | 1.889 / 1.194 | 1.783 / 1.243 | 1.840 / 1.215 | 1.814 / 1.251 | 1.804 / 1.257 | 1.770 / 1.186 | 1.996 / 1.485 | 1.908 / 1.299 |
| ppo_resid_v3_left_an9_s7 | stoch | 1.844 / 1.327 | 2.258 / 1.508 | 2.131 / 1.397 | 1.998 / 1.401 | 1.932 / 1.251 | 1.818 / 1.286 | 1.888 / 1.276 | 1.856 / 1.306 | 1.844 / 1.305 | 1.805 / 1.231 | 2.015 / 1.502 | 1.944 / 1.345 |
| ppo_resid_v3_left_an10_s8 | deter | 1.842 / 1.324 | 2.241 / 1.487 | 2.121 / 1.390 | 1.987 / 1.393 | 1.920 / 1.241 | 1.792 / 1.267 | 1.874 / 1.261 | 1.843 / 1.292 | 1.831 / 1.291 | 1.792 / 1.217 | 2.015 / 1.487 | 1.933 / 1.332 |
| ppo_resid_v3_left_an10_s8 | stoch | 1.884 / 1.395 | 2.379 / 1.670 | 2.189 / 1.480 | 2.069 / 1.498 | 2.026 / 1.383 | 1.867 / 1.379 | 1.990 / 1.413 | 1.945 / 1.423 | 1.932 / 1.411 | 1.878 / 1.333 | 2.055 / 1.528 | 2.020 / 1.447 |
| ppo_resid_v3_left_fast1_s10 | deter | 2.231 / 1.948 | 3.348 / 2.933 | 2.714 / 2.204 | 2.732 / 2.335 | 2.757 / 2.364 | 2.509 / 2.163 | 2.808 / 2.412 | 2.714 / 2.325 | 2.630 / 2.215 | 2.472 / 2.087 | 2.437 / 1.997 | 2.668 / 2.271 |
| ppo_resid_v3_left_fast1_s10 | stoch | 2.230 / 1.948 | 3.346 / 2.932 | 2.713 / 2.190 | 2.731 / 2.335 | 2.756 / 2.363 | 2.520 / 2.175 | 2.811 / 2.409 | 2.714 / 2.325 | 2.629 / 2.215 | 2.479 / 2.095 | 2.436 / 1.995 | 2.669 / 2.271 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | deter | 2.216 / 1.945 | 3.331 / 2.915 | 2.703 / 2.142 | 2.723 / 2.328 | 2.740 / 2.361 | 2.543 / 2.199 | 2.827 / 2.422 | 2.706 / 2.299 | 2.613 / 2.220 | 2.494 / 2.112 | 2.430 / 1.991 | 2.666 / 2.267 |
| ppo_resid_v3_left_fast2_s11<br>best_gate_flat_123mph | stoch | 2.217 / 1.945 | 3.332 / 2.916 | 2.704 / 2.145 | 2.724 / 2.328 | 2.741 / 2.363 | 2.532 / 2.188 | 2.807 / 2.388 | 2.700 / 2.292 | 2.613 / 2.219 | 2.489 / 2.107 | 2.435 / 1.996 | 2.663 / 2.262 |
| ppo_v3tiny_s22 | deter | 2.003 / 1.576 | 2.498 / 1.831 | 2.300 / 1.707 | 2.211 / 1.727 | 2.065 / 1.481 | 1.880 / 1.409 | 1.999 / 1.462 | 1.985 / 1.512 | 1.994 / 1.523 | 1.903 / 1.379 | 2.146 / 1.613 | 2.090 / 1.565 |
| ppo_v3tiny_s22 | stoch | 1.982 / 1.546 | 2.483 / 1.810 | 2.284 / 1.669 | 2.191 / 1.693 | 2.060 / 1.462 | 1.880 / 1.400 | 1.995 / 1.446 | 1.977 / 1.499 | 1.982 / 1.504 | 1.896 / 1.367 | 2.133 / 1.603 | 2.078 / 1.545 |
| ppo_v3tiny_s21 | deter | 1.987 / 1.552 | 2.481 / 1.809 | 2.284 / 1.676 | 2.190 / 1.697 | 2.062 / 1.469 | 1.877 / 1.404 | 1.995 / 1.452 | 1.979 / 1.500 | 1.986 / 1.509 | 1.900 / 1.373 | 2.129 / 1.600 | 2.079 / 1.549 |
| ppo_v3tiny_s21 | stoch | 1.984 / 1.546 | 2.456 / 1.777 | 2.276 / 1.674 | 2.180 / 1.685 | 2.039 / 1.441 | 1.866 / 1.386 | 1.976 / 1.428 | 1.960 / 1.477 | 1.965 / 1.489 | 1.885 / 1.353 | 2.123 / 1.595 | 2.065 / 1.532 |
| ppo_v3tiny_s23 | deter | 1.995 / 1.566 | 2.510 / 1.846 | 2.300 / 1.689 | 2.212 / 1.718 | 2.077 / 1.491 | 1.890 / 1.416 | 2.009 / 1.471 | 1.992 / 1.518 | 2.003 / 1.528 | 1.908 / 1.384 | 2.149 / 1.615 | 2.095 / 1.568 |
| ppo_v3tiny_s23 | stoch | 1.978 / 1.536 | 2.447 / 1.763 | 2.271 / 1.660 | 2.174 / 1.675 | 2.034 / 1.432 | 1.862 / 1.380 | 1.971 / 1.419 | 1.956 / 1.468 | 1.960 / 1.480 | 1.881 / 1.346 | 2.121 / 1.591 | 2.059 / 1.523 |
| ppo_v3flt_all_s33 | deter | 2.031 / 1.619 | 2.556 / 1.906 | 2.338 / 1.764 | 2.260 / 1.787 | 2.101 / 1.534 | 1.909 / 1.441 | 2.029 / 1.504 | 2.019 / 1.560 | 2.031 / 1.571 | 1.929 / 1.414 | 2.180 / 1.648 | 2.126 / 1.614 |
| ppo_v3flt_all_s33 | stoch | 2.006 / 1.581 | 2.528 / 1.868 | 2.317 / 1.708 | 2.231 / 1.743 | 2.089 / 1.505 | 1.898 / 1.426 | 2.018 / 1.483 | 2.004 / 1.533 | 2.017 / 1.546 | 1.915 / 1.395 | 2.162 / 1.629 | 2.108 / 1.583 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | deter | 1.991 / 1.556 | 2.461 / 1.781 | 2.283 / 1.690 | 2.189 / 1.702 | 2.036 / 1.438 | 1.871 / 1.383 | 1.971 / 1.423 | 1.959 / 1.476 | 1.966 / 1.490 | 1.882 / 1.347 | 2.139 / 1.609 | 2.068 / 1.536 |
| ppo_v3flt_yaw_s32<br>best_learned_yaw_s32 | stoch | 1.989 / 1.553 | 2.456 / 1.774 | 2.281 / 1.686 | 2.186 / 1.698 | 2.034 / 1.434 | 1.870 / 1.381 | 1.969 / 1.419 | 1.957 / 1.472 | 1.964 / 1.487 | 1.880 / 1.344 | 2.136 / 1.607 | 2.066 / 1.532 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | deter | 1.989 / 1.553 | 2.457 / 1.776 | 2.281 / 1.686 | 2.186 / 1.698 | 2.035 / 1.435 | 1.870 / 1.381 | 1.969 / 1.420 | 1.958 / 1.473 | 1.964 / 1.488 | 1.881 / 1.345 | 2.137 / 1.608 | 2.066 / 1.533 |
| ppo_v3flt_yaw_s31<br>best_learned_yaw_s31 | stoch | 1.987 / 1.549 | 2.453 / 1.770 | 2.278 / 1.681 | 2.183 / 1.693 | 2.032 / 1.431 | 1.869 / 1.379 | 1.967 / 1.416 | 1.955 / 1.469 | 1.961 / 1.484 | 1.879 / 1.342 | 2.134 / 1.606 | 2.063 / 1.529 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | deter | 1.739 / 1.178 | 2.102 / 1.288 | 2.034 / 1.236 | 1.886 / 1.215 | 1.821 / 1.055 | 1.788 / 1.165 | 1.767 / 1.086 | 1.743 / 1.130 | 1.730 / 1.138 | 1.707 / 1.080 | 1.982 / 1.491 | 1.845 / 1.187 |
| ppo_v4yaw_s41<br>best_v4yaw_s41 | stoch | 1.739 / 1.177 | 2.101 / 1.286 | 2.034 / 1.235 | 1.885 / 1.214 | 1.821 / 1.054 | 1.788 / 1.165 | 1.767 / 1.086 | 1.743 / 1.129 | 1.729 / 1.137 | 1.706 / 1.080 | 1.981 / 1.491 | 1.845 / 1.187 |
| ppo_v4yaw_s42 | deter | 1.740 / 1.179 | 2.103 / 1.289 | 2.035 / 1.237 | 1.887 / 1.217 | 1.822 / 1.056 | 1.788 / 1.166 | 1.768 / 1.087 | 1.744 / 1.131 | 1.730 / 1.139 | 1.707 / 1.081 | 1.983 / 1.492 | 1.846 / 1.189 |
| ppo_v4yaw_s42 | stoch | 1.737 / 1.174 | 2.099 / 1.283 | 2.032 / 1.231 | 1.883 / 1.210 | 1.819 / 1.051 | 1.787 / 1.163 | 1.765 / 1.083 | 1.741 / 1.126 | 1.727 / 1.134 | 1.705 / 1.078 | 1.980 / 1.490 | 1.843 / 1.184 |
| ppo_v4yaw_s43 | deter | 1.741 / 1.180 | 2.105 / 1.291 | 2.036 / 1.239 | 1.888 / 1.218 | 1.823 / 1.058 | 1.789 / 1.167 | 1.768 / 1.088 | 1.745 / 1.132 | 1.731 / 1.140 | 1.708 / 1.082 | 1.984 / 1.492 | 1.847 / 1.190 |
| ppo_v4yaw_s43 | stoch | 1.737 / 1.174 | 2.099 / 1.283 | 2.032 / 1.232 | 1.883 / 1.211 | 1.820 / 1.052 | 1.787 / 1.163 | 1.766 / 1.084 | 1.742 / 1.127 | 1.728 / 1.135 | 1.705 / 1.078 | 1.980 / 1.490 | 1.843 / 1.184 |
| imit2_w075_s53 | deter | 1.930 / 1.464 | 2.369 / 1.657 | 2.216 / 1.570 | 2.107 / 1.575 | 1.983 / 1.347 | 1.844 / 1.330 | 1.922 / 1.345 | 1.904 / 1.392 | 1.905 / 1.403 | 1.840 / 1.286 | 2.087 / 1.566 | 2.010 / 1.449 |
| imit2_w075_s53 | stoch | 2.000 / 1.574 | 2.529 / 1.869 | 2.308 / 1.703 | 2.222 / 1.733 | 2.089 / 1.505 | 1.906 / 1.426 | 2.017 / 1.481 | 2.002 / 1.529 | 2.017 / 1.543 | 1.914 / 1.391 | 2.166 / 1.635 | 2.106 / 1.581 |
| imit2_w075_s51 | deter | 2.007 / 1.592 | 2.630 / 1.999 | 2.345 / 1.699 | 2.268 / 1.770 | 2.169 / 1.602 | 1.944 / 1.486 | 2.090 / 1.570 | 2.063 / 1.606 | 2.096 / 1.623 | 1.956 / 1.456 | 2.199 / 1.654 | 2.161 / 1.642 |
| imit2_w075_s51 | stoch | 1.989 / 1.559 | 2.529 / 1.868 | 2.304 / 1.672 | 2.216 / 1.715 | 2.093 / 1.504 | 1.901 / 1.426 | 2.021 / 1.484 | 2.002 / 1.528 | 2.019 / 1.541 | 1.913 / 1.394 | 2.155 / 1.622 | 2.104 / 1.574 |
| imit2_w075_s52 | deter | 1.928 / 1.460 | 2.364 / 1.652 | 2.213 / 1.565 | 2.103 / 1.570 | 1.981 / 1.344 | 1.841 / 1.329 | 1.921 / 1.343 | 1.903 / 1.390 | 1.903 / 1.401 | 1.840 / 1.285 | 2.082 / 1.563 | 2.007 / 1.446 |
| imit2_w075_s52 | stoch | 1.953 / 1.501 | 2.433 / 1.742 | 2.251 / 1.611 | 2.151 / 1.629 | 2.027 / 1.411 | 1.866 / 1.367 | 1.962 / 1.398 | 1.943 / 1.445 | 1.950 / 1.458 | 1.869 / 1.328 | 2.114 / 1.589 | 2.047 / 1.498 |
| imit3_w075_s51 | deter | 1.984 / 1.546 | 2.453 / 1.770 | 2.276 / 1.677 | 2.181 / 1.689 | 2.031 / 1.428 | 1.870 / 1.376 | 1.966 / 1.414 | 1.952 / 1.466 | 1.959 / 1.481 | 1.877 / 1.340 | 2.135 / 1.606 | 2.062 / 1.527 |
| imit3_w075_s51 | stoch | 1.988 / 1.553 | 2.460 / 1.779 | 2.280 / 1.684 | 2.187 / 1.696 | 2.034 / 1.435 | 1.872 / 1.380 | 1.969 / 1.420 | 1.957 / 1.472 | 1.964 / 1.487 | 1.880 / 1.345 | 2.138 / 1.609 | 2.066 / 1.533 |
| imit3_w075_s52 | deter | 1.968 / 1.521 | 2.426 / 1.734 | 2.257 / 1.643 | 2.157 / 1.653 | 2.016 / 1.404 | 1.860 / 1.363 | 1.953 / 1.394 | 1.938 / 1.444 | 1.943 / 1.458 | 1.867 / 1.325 | 2.117 / 1.591 | 2.046 / 1.503 |
| imit3_w075_s52 | stoch | 1.971 / 1.526 | 2.432 / 1.742 | 2.260 / 1.649 | 2.162 / 1.659 | 2.019 / 1.409 | 1.861 / 1.366 | 1.956 / 1.399 | 1.941 / 1.449 | 1.946 / 1.462 | 1.869 / 1.329 | 2.120 / 1.593 | 2.049 / 1.508 |
| imit3_w050_s51 | deter | 1.974 / 1.530 | 2.437 / 1.748 | 2.264 / 1.655 | 2.166 / 1.665 | 2.022 / 1.412 | 1.865 / 1.368 | 1.957 / 1.401 | 1.944 / 1.452 | 1.949 / 1.466 | 1.870 / 1.330 | 2.126 / 1.599 | 2.052 / 1.512 |
| imit3_w050_s51 | stoch | 1.967 / 1.520 | 2.424 / 1.731 | 2.257 / 1.643 | 2.157 / 1.653 | 2.015 / 1.401 | 1.860 / 1.362 | 1.951 / 1.392 | 1.938 / 1.442 | 1.942 / 1.456 | 1.865 / 1.323 | 2.119 / 1.593 | 2.045 / 1.501 |
| imit3_w050_s52 | deter | 2.008 / 1.582 | 2.488 / 1.815 | 2.304 / 1.723 | 2.215 / 1.738 | 2.051 / 1.462 | 1.883 / 1.396 | 1.983 / 1.442 | 1.974 / 1.497 | 1.984 / 1.514 | 1.892 / 1.361 | 2.161 / 1.626 | 2.086 / 1.560 |
| imit3_w050_s52 | stoch | 1.996 / 1.564 | 2.471 / 1.793 | 2.291 / 1.702 | 2.200 / 1.715 | 2.041 / 1.444 | 1.879 / 1.386 | 1.974 / 1.427 | 1.964 / 1.481 | 1.972 / 1.497 | 1.884 / 1.350 | 2.152 / 1.619 | 2.075 / 1.544 |
| imit3_w075_s53 | deter | 1.945 / 1.485 | 2.388 / 1.684 | 2.231 / 1.598 | 2.125 / 1.605 | 1.995 / 1.369 | 1.848 / 1.342 | 1.934 / 1.364 | 1.917 / 1.412 | 1.919 / 1.424 | 1.850 / 1.301 | 2.098 / 1.573 | 2.023 / 1.469 |
| imit3_w075_s53 | stoch | 1.948 / 1.490 | 2.393 / 1.690 | 2.236 / 1.606 | 2.130 / 1.614 | 1.998 / 1.374 | 1.850 / 1.345 | 1.937 / 1.368 | 1.921 / 1.417 | 1.923 / 1.429 | 1.852 / 1.304 | 2.101 / 1.576 | 2.026 / 1.474 |
| imit3_w025_s52 | deter | 1.993 / 1.563 | 2.546 / 1.887 | 2.313 / 1.684 | 2.228 / 1.728 | 2.110 / 1.523 | 1.929 / 1.440 | 2.033 / 1.493 | 2.018 / 1.543 | 2.036 / 1.552 | 1.925 / 1.401 | 2.176 / 1.649 | 2.119 / 1.588 |
| imit3_w025_s52 | stoch | 1.980 / 1.540 | 2.491 / 1.817 | 2.288 / 1.661 | 2.195 / 1.692 | 2.069 / 1.470 | 1.899 / 1.407 | 1.999 / 1.449 | 1.983 / 1.499 | 1.996 / 1.511 | 1.898 / 1.367 | 2.152 / 1.622 | 2.086 / 1.548 |
| imit3_w025_s51 | deter | 2.016 / 1.596 | 2.505 / 1.839 | 2.312 / 1.738 | 2.228 / 1.755 | 2.059 / 1.477 | 1.887 / 1.405 | 1.991 / 1.455 | 1.982 / 1.511 | 1.992 / 1.527 | 1.899 / 1.373 | 2.168 / 1.632 | 2.095 / 1.573 |
| imit3_w025_s51 | stoch | 2.009 / 1.584 | 2.491 / 1.820 | 2.305 / 1.726 | 2.217 / 1.741 | 2.053 / 1.465 | 1.882 / 1.398 | 1.985 / 1.445 | 1.975 / 1.500 | 1.985 / 1.516 | 1.894 / 1.364 | 2.161 / 1.626 | 2.087 / 1.563 |
| imit3_w000_s52 | deter | 1.969 / 1.519 | 2.419 / 1.727 | 2.252 / 1.637 | 2.151 / 1.646 | 2.014 / 1.404 | 1.856 / 1.366 | 1.952 / 1.396 | 1.939 / 1.445 | 1.942 / 1.458 | 1.868 / 1.328 | 2.108 / 1.584 | 2.043 / 1.501 |
| imit3_w000_s52 | stoch | 1.995 / 1.559 | 2.522 / 1.859 | 2.298 / 1.694 | 2.209 / 1.711 | 2.090 / 1.504 | 1.904 / 1.430 | 2.019 / 1.481 | 2.005 / 1.530 | 2.019 / 1.536 | 1.920 / 1.398 | 2.147 / 1.625 | 2.103 / 1.575 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | deter | 1.967 / 1.518 | 2.431 / 1.740 | 2.258 / 1.640 | 2.158 / 1.651 | 2.023 / 1.411 | 1.866 / 1.369 | 1.959 / 1.400 | 1.944 / 1.449 | 1.950 / 1.462 | 1.871 / 1.329 | 2.120 / 1.594 | 2.049 / 1.506 |
| imit3_w000_s51<br>best_imit_scriptfree_s51_NOTPASS_lat3.56 | stoch | 1.963 / 1.512 | 2.416 / 1.720 | 2.250 / 1.631 | 2.149 / 1.641 | 2.011 / 1.395 | 1.859 / 1.358 | 1.948 / 1.386 | 1.933 / 1.436 | 1.937 / 1.449 | 1.862 / 1.319 | 2.114 / 1.588 | 2.040 / 1.494 |

## Contact regressions (vs best earlier-trained checkpoint, same mode)

- ppo_scott_baseline [deterministic]: contact 0% < best previous 100% (ppo_scott(30k, old))
- ppo_scott_baseline [stochastic]: contact 0% < best previous 52% (ppo_scott_final2)
- ppo_scott_curr [stochastic]: contact 36% < best previous 52% (ppo_scott_final2)
- ppo_scott_final2/ppo_scott_prev2_backup [deterministic]: contact 48% < best previous 100% (ppo_scott_prev_backup)
- ppo_scott/ppo_scott_carry1 [deterministic]: contact 98% < best previous 100% (ppo_scott_prev_backup)
- ppo_resid_v3_s0 [stochastic]: contact 64% < best previous 66% (ppo_scott)

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
| ppo_scott_baseline | 30000 | df95da5d35d6 | 0% | 0% |
| ppo_scott_baseline | 30000 | 7a2ffa104b56 | 0% | 0% |
| ppo_scott_baseline | 30000 | 536694401cb9 | 0% | 0% |
| ppo_scott_curr | 30000 | f0a3f737fc77 | 100% | 34% |
| ppo_scott_curr | 30000 | ae180bdc10a3 | 100% | 34% |
| ppo_scott_curr | 30000 | e9a0050d94b6 | 100% | 34% |
| ppo_scott_curr | 30000 | 9145629439d4 | 100% | 34% |
| ppo_scott_curr | 30000 | 25d5c5608c4d | 100% | 34% |
| ppo_scott_curr | 30000 | 59bc5ea99d60 | 100% | 34% |
| ppo_scott_curr | 30000 | 99f124d7b5dd | 100% | 34% |
| ppo_scott_curr | 30000 | 95e60a7e2ccf | 100% | 34% |
| ppo_scott_curr | 30000 | df95da5d35d6 | 100% | 34% |
| ppo_scott_curr | 30000 | 7a2ffa104b56 | 100% | 34% |
| ppo_scott_curr | 30000 | 536694401cb9 | 100% | 34% |
| ppo_scott_prev_backup | 30000 | f0a3f737fc77 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | ae180bdc10a3 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | e9a0050d94b6 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 9145629439d4 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 25d5c5608c4d | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 59bc5ea99d60 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 99f124d7b5dd | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 95e60a7e2ccf | 100% | 38% |
| ppo_scott_prev_backup | 30000 | df95da5d35d6 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 7a2ffa104b56 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 536694401cb9 | 100% | 38% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | f0a3f737fc77 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | ae180bdc10a3 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | e9a0050d94b6 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 9145629439d4 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 25d5c5608c4d | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 59bc5ea99d60 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 99f124d7b5dd | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 95e60a7e2ccf | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | df95da5d35d6 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 7a2ffa104b56 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 536694401cb9 | 48% | 60% |
| ppo_scott, ppo_scott_carry1 | 100000 | f0a3f737fc77 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | ae180bdc10a3 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | e9a0050d94b6 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 9145629439d4 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 25d5c5608c4d | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 59bc5ea99d60 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 99f124d7b5dd | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 95e60a7e2ccf | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | df95da5d35d6 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 7a2ffa104b56 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 536694401cb9 | 98% | 66% |
| ppo_resid_v3_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_s0 | 60000 | 95e60a7e2ccf | 100% | 60% |
| ppo_resid_v3_s0 | 60000 | df95da5d35d6 | 100% | 60% |
| ppo_resid_v3_s0 | 60000 | 7a2ffa104b56 | 100% | 60% |
| ppo_resid_v3_s0 | 60000 | 536694401cb9 | 100% | 60% |
| ppo_resid_v3_r2_s0 | 60000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r2_s0 | 60000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_r2_s0 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_r3_s0 | 100000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_r3_s0 | 100000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 99f124d7b5dd | n/a | n/a |
| ppo_resid_v3_ladder_s0 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_ladder_s0 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an1_s0 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an2_s0, best_carry_analytic | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 99f124d7b5dd | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 95e60a7e2ccf | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an3_s1 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an4_s2 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | df95da5d35d6 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an5_s3 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an6_s4 | 150000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an7_s5 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an8_s6 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an9_s7 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_an10_s8 | 120000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_fast1_s10 | 100000 | 536694401cb9 | 100% | 100% |
| ppo_resid_v3_left_fast2_s11, best_gate_flat_123mph | 100000 | 7a2ffa104b56 | 100% | 100% |
| ppo_resid_v3_left_fast2_s11, best_gate_flat_123mph | 100000 | 737c4d124c92 | 100% | 100% |
| ppo_resid_v3_left_fast2_s11, best_gate_flat_123mph | 100000 | 536694401cb9 | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 737c4d124c92 | 100% | 100% |
| ppo_v3tiny_s22 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_v3tiny_s21 | 60000 | 737c4d124c92 | 100% | 100% |
| ppo_v3tiny_s21 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 737c4d124c92 | 100% | 100% |
| ppo_v3tiny_s23 | 60000 | 536694401cb9 | 100% | 100% |
| ppo_v3flt_all_s33 | 30000 | 536694401cb9 | 100% | 100% |
| ppo_v3flt_yaw_s32, best_learned_yaw_s32 | 30000 | 536694401cb9 | 100% | 100% |
| ppo_v3flt_yaw_s31, best_learned_yaw_s31 | 30000 | 536694401cb9 | 100% | 100% |
| imit_w075_s53 | 0 | 30178ef58c6a | 100% | 100% |
| imit_w075_s51 | 0 | 30178ef58c6a | 100% | 100% |
| imit_w075_s52 | 0 | 30178ef58c6a | 100% | 100% |
| imit2_w075_s53 | 15000 | 30178ef58c6a | 100% | 100% |
| imit2_w075_s51 | 15000 | 30178ef58c6a | 100% | 100% |
| imit2_w075_s52 | 15000 | 30178ef58c6a | 100% | 100% |
| imit3_w075_s51 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w075_s52 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w050_s51 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w050_s52 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w075_s53 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w025_s52 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w025_s51 | 8000 | 30178ef58c6a | 100% | 100% |
| imit3_w000_s51, best_imit_scriptfree_s51_NOTPASS_lat3.56 | 8000 | 30178ef58c6a | 100% | 100% |

# Dispersion detail: scripted baseline, ladder model and all left-handed models

50 episodes/mode, seeds 4000..4049; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).

| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps | Launch elev mean deg (std) | flat? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 100% | 99.64 | 11.23 | 134.14 | 99.64 | 99.639 | 100% | 8.232 | +0.379 | 46% | 50% | 49.64 / 49.88 | 111.0 / 111.6 | 93.0% | 0 | 33.1 (4.4) | no |
| ppo_resid_v3_ladder_s0 | stochastic | 100% | 94.48 | 75.12 | 339.80 | 94.48 | 69.082 | 92% | 14.276 | -1.328 | 44% | 36% | 49.72 / 54.95 | 111.2 / 122.9 | 102.4% | 0 | 25.4 (19.2) | no |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deterministic | 100% | 177.22 | 130.70 | 331.62 | 177.22 | 36.672 | 56% | 2.733 | -0.487 | 8% | 20% | 48.23 / 48.33 | 107.9 / 108.1 | 90.1% | 0 | 9.2 (13.2) | FLAT |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stochastic | 100% | 177.22 | 130.70 | 331.62 | 177.22 | 36.672 | 56% | 2.733 | -0.487 | 8% | 20% | 48.23 / 48.33 | 107.9 / 108.1 | 90.1% | 0 | 9.2 (13.2) | FLAT |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deterministic | 100% | 118.44 | 110.61 | 326.09 | 118.44 | 53.934 | 80% | 1.985 | -0.180 | 4% | 10% | 48.21 / 48.27 | 107.8 / 108.0 | 90.0% | 0 | 11.5 (11.6) | no |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stochastic | 100% | 118.44 | 110.61 | 326.09 | 118.44 | 53.934 | 80% | 1.985 | -0.180 | 4% | 10% | 48.21 / 48.27 | 107.8 / 108.0 | 90.0% | 0 | 11.5 (11.6) | no |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deterministic | 100% | 80.70 | 43.79 | 289.84 | 80.70 | 69.405 | 96% | 0.013 | -0.001 | 0% | 0% | 53.80 / 53.94 | 120.4 / 120.7 | 100.6% | 0 | 9.0 (2.9) | no |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stochastic | 100% | 80.70 | 43.79 | 289.84 | 80.70 | 69.405 | 96% | 0.013 | -0.001 | 0% | 0% | 53.80 / 53.94 | 120.4 / 120.7 | 100.6% | 0 | 9.0 (2.9) | no |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deterministic | 100% | 115.71 | 27.03 | 186.55 | 115.71 | 115.710 | 100% | 1.699 | -0.341 | 2% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stochastic | 100% | 115.71 | 27.03 | 186.55 | 115.71 | 115.710 | 100% | 1.699 | -0.341 | 2% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_resid_v3_left_an1_s0 | deterministic | 100% | 108.88 | 10.96 | 144.06 | 108.88 | 108.884 | 100% | 6.905 | +0.722 | 56% | 40% | 51.16 / 51.67 | 114.4 / 115.6 | 96.3% | 0 | 32.0 (3.8) | no |
| ppo_resid_v3_left_an1_s0 | stochastic | 100% | 106.22 | 64.78 | 340.25 | 106.22 | 85.974 | 94% | 15.283 | -1.723 | 46% | 46% | 51.01 / 53.93 | 114.1 / 120.6 | 100.5% | 0 | 30.4 (14.7) | no |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | deterministic | 100% | 111.87 | 13.21 | 159.77 | 111.87 | 111.875 | 100% | 7.622 | +0.395 | 50% | 46% | 51.27 / 51.57 | 114.7 / 115.4 | 96.1% | 0 | 31.3 (3.9) | no |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | stochastic | 100% | 116.37 | 68.22 | 353.00 | 116.37 | 89.888 | 92% | 8.519 | +0.515 | 50% | 38% | 51.08 / 52.68 | 114.3 / 117.8 | 98.2% | 0 | 28.7 (12.7) | no |
| ppo_resid_v3_left_an3_s1 | deterministic | 100% | 117.57 | 38.74 | 338.43 | 117.57 | 110.799 | 98% | 7.204 | +1.172 | 58% | 40% | 51.25 / 51.58 | 114.7 / 115.4 | 96.2% | 0 | 30.0 (6.9) | no |
| ppo_resid_v3_left_an3_s1 | stochastic | 100% | 112.11 | 40.52 | 334.78 | 112.11 | 105.412 | 98% | 9.205 | +2.438 | 58% | 36% | 50.69 / 52.42 | 113.4 / 117.3 | 97.7% | 0 | 30.0 (8.6) | no |
| ppo_resid_v3_left_an4_s2 | deterministic | 100% | 95.37 | 11.76 | 162.98 | 95.37 | 95.375 | 100% | 6.570 | +0.060 | 52% | 44% | 49.93 / 50.31 | 111.7 / 112.5 | 93.8% | 0 | 34.4 (3.9) | no |
| ppo_resid_v3_left_an4_s2 | stochastic | 100% | 98.84 | 21.37 | 170.36 | 98.84 | 98.835 | 100% | 8.450 | +0.038 | 50% | 44% | 50.11 / 51.98 | 112.1 / 116.3 | 96.9% | 0 | 33.7 (6.6) | no |
| ppo_resid_v3_left_an5_s3 | deterministic | 100% | 102.05 | 149.39 | 357.37 | 102.05 | 10.004 | 74% | 0.143 | +0.095 | 0% | 0% | 52.32 / 52.60 | 117.0 / 117.7 | 98.1% | 0 | -3.8 (2.2) | FLAT |
| ppo_resid_v3_left_an5_s3 | stochastic | 100% | 141.48 | 163.15 | 359.56 | 141.48 | 8.546 | 62% | 0.737 | +0.166 | 20% | 8% | 52.02 / 54.06 | 116.4 / 120.9 | 100.8% | 0 | -3.3 (2.2) | FLAT |
| ppo_resid_v3_left_an6_s4 | deterministic | 100% | 112.18 | 39.04 | 335.10 | 112.18 | 105.479 | 98% | 8.939 | -0.258 | 50% | 38% | 50.52 / 51.37 | 113.0 / 114.9 | 95.8% | 0 | 28.9 (8.2) | no |
| ppo_resid_v3_left_an6_s4 | stochastic | 100% | 145.59 | 99.74 | 354.13 | 145.59 | 78.147 | 80% | 6.739 | +0.455 | 44% | 40% | 50.71 / 52.65 | 113.4 / 117.8 | 98.2% | 0 | 23.2 (15.0) | no |
| ppo_resid_v3_left_an7_s5 | deterministic | 100% | 140.08 | 162.75 | 355.77 | 140.08 | 7.866 | 62% | 0.278 | -0.241 | 0% | 38% | 51.51 / 52.16 | 115.2 / 116.7 | 97.2% | 0 | -3.3 (2.2) | FLAT |
| ppo_resid_v3_left_an7_s5 | stochastic | 100% | 93.30 | 143.70 | 357.35 | 93.30 | 9.553 | 76% | 0.380 | -0.190 | 0% | 14% | 51.65 / 53.23 | 115.5 / 119.1 | 99.2% | 0 | -4.0 (2.6) | FLAT |
| ppo_resid_v3_left_an8_s6 | deterministic | 100% | 89.85 | 142.12 | 359.69 | 89.85 | 11.215 | 78% | 0.087 | -0.055 | 0% | 0% | 52.97 / 53.26 | 118.5 / 119.1 | 99.3% | 0 | -5.1 (2.8) | FLAT |
| ppo_resid_v3_left_an8_s6 | stochastic | 100% | 88.82 | 140.91 | 361.67 | 88.82 | 10.924 | 78% | 0.610 | -0.050 | 6% | 6% | 52.55 / 54.07 | 117.6 / 120.9 | 100.8% | 0 | -4.6 (2.8) | FLAT |
| ppo_resid_v3_left_an9_s7 | deterministic | 100% | 102.12 | 9.30 | 136.61 | 102.12 | 102.123 | 100% | 7.919 | +1.976 | 60% | 38% | 49.39 / 49.97 | 110.5 / 111.8 | 93.2% | 0 | 33.2 (4.2) | no |
| ppo_resid_v3_left_an9_s7 | stochastic | 100% | 130.89 | 90.27 | 337.38 | 130.89 | 78.302 | 84% | 7.109 | +0.495 | 52% | 32% | 49.63 / 52.31 | 111.0 / 117.0 | 97.5% | 0 | 26.4 (15.4) | no |
| ppo_resid_v3_left_an10_s8 | deterministic | 100% | 126.17 | 56.33 | 327.65 | 126.17 | 107.036 | 94% | 5.442 | +0.827 | 54% | 32% | 47.86 / 48.45 | 107.1 / 108.4 | 90.3% | 0 | 25.2 (9.6) | no |
| ppo_resid_v3_left_an10_s8 | stochastic | 100% | 149.68 | 113.36 | 338.04 | 149.68 | 55.494 | 70% | 4.191 | +1.179 | 46% | 22% | 47.87 / 50.04 | 107.1 / 111.9 | 93.3% | 0 | 15.4 (16.3) | FLAT |
| ppo_resid_v3_left_fast1_s10 | deterministic | 100% | 15.85 | 3.01 | 24.02 | 15.85 | 15.854 | 100% | 0.022 | +0.005 | 0% | 0% | 54.65 / 54.73 | 122.3 / 122.4 | 102.0% | 0 | -5.2 (1.5) | FLAT |
| ppo_resid_v3_left_fast1_s10 | stochastic | 100% | 15.47 | 3.23 | 24.43 | 15.47 | 15.470 | 100% | 0.289 | +0.043 | 2% | 0% | 54.59 / 55.10 | 122.1 / 123.3 | 102.7% | 0 | -5.0 (1.5) | FLAT |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | deterministic | 100% | 14.97 | 2.65 | 23.18 | 14.97 | 14.975 | 100% | 0.024 | -0.007 | 0% | 0% | 55.24 / 55.32 | 123.6 / 123.8 | 103.1% | 0 | -5.2 (1.4) | FLAT |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | stochastic | 100% | 15.50 | 3.33 | 23.76 | 15.50 | 15.497 | 100% | 0.033 | -0.004 | 0% | 0% | 55.24 / 55.72 | 123.6 / 124.6 | 103.9% | 0 | -4.9 (1.3) | FLAT |
| ppo_v3tiny_s22 | deterministic | 100% | 109.83 | 42.20 | 265.00 | 109.83 | 99.241 | 96% | 6.323 | -1.215 | 6% | 12% | 52.92 / 53.08 | 118.4 / 118.7 | 99.0% | 0 | 10.8 (5.3) | no |
| ppo_v3tiny_s22 | stochastic | 100% | 118.03 | 52.52 | 272.21 | 118.03 | 101.892 | 94% | 7.339 | +1.348 | 12% | 16% | 52.98 / 54.06 | 118.5 / 120.9 | 100.8% | 0 | 10.3 (5.2) | no |
| ppo_v3tiny_s21 | deterministic | 100% | 122.72 | 65.94 | 276.21 | 122.72 | 84.582 | 86% | 4.411 | -0.706 | 6% | 6% | 53.18 / 53.31 | 119.0 / 119.3 | 99.4% | 0 | 9.0 (6.8) | no |
| ppo_v3tiny_s21 | stochastic | 100% | 119.22 | 45.49 | 271.57 | 119.22 | 103.337 | 94% | 8.576 | -1.109 | 14% | 10% | 53.10 / 53.96 | 118.8 / 120.7 | 100.6% | 0 | 11.0 (4.5) | no |
| ppo_v3tiny_s23 | deterministic | 100% | 118.90 | 65.59 | 289.05 | 118.90 | 91.004 | 90% | 2.812 | +0.052 | 10% | 10% | 53.18 / 53.75 | 119.0 / 120.2 | 100.2% | 0 | 8.8 (7.3) | no |
| ppo_v3tiny_s23 | stochastic | 100% | 121.64 | 48.77 | 278.66 | 121.64 | 105.232 | 94% | 9.167 | +1.065 | 12% | 10% | 53.20 / 54.03 | 119.0 / 120.9 | 100.7% | 0 | 10.7 (4.7) | no |
| ppo_v3flt_all_s33 | deterministic | 100% | 100.70 | 37.11 | 284.74 | 100.70 | 95.003 | 98% | 5.132 | +0.700 | 2% | 0% | 53.78 / 53.88 | 120.3 / 120.5 | 100.4% | 0 | 10.5 (6.0) | no |
| ppo_v3flt_all_s33 | stochastic | 100% | 110.41 | 50.24 | 281.27 | 110.41 | 99.163 | 96% | 9.747 | +0.988 | 8% | 6% | 53.80 / 53.92 | 120.3 / 120.6 | 100.5% | 0 | 9.2 (7.2) | no |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | deterministic | 100% | 113.90 | 26.32 | 186.22 | 113.90 | 113.904 | 100% | 1.586 | -0.295 | 4% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | stochastic | 100% | 113.98 | 24.77 | 186.20 | 113.98 | 113.978 | 100% | 1.582 | -0.375 | 4% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | deterministic | 100% | 114.25 | 25.92 | 186.20 | 114.25 | 114.250 | 100% | 1.614 | -0.286 | 2% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | stochastic | 100% | 114.78 | 26.40 | 186.14 | 114.78 | 114.779 | 100% | 1.935 | -0.334 | 4% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_v4yaw_s41/best_v4yaw_s41 | deterministic | 100% | 261.71 | 58.62 | 309.87 | 261.71 | 243.591 | 94% | 1.670 | +0.140 | 52% | 36% | 57.36 / 57.52 | 128.3 / 128.7 | 107.2% | 0 | 10.9 (2.0) | no |
| ppo_v4yaw_s41/best_v4yaw_s41 | stochastic | 100% | 261.52 | 58.35 | 309.88 | 261.52 | 243.409 | 94% | 1.692 | +0.125 | 50% | 36% | 57.36 / 57.52 | 128.3 / 128.7 | 107.2% | 0 | 10.9 (2.0) | no |
| ppo_v4yaw_s42 | deterministic | 100% | 261.40 | 58.00 | 309.50 | 261.40 | 243.290 | 94% | 1.660 | -0.260 | 42% | 40% | 57.36 / 57.52 | 128.3 / 128.7 | 107.2% | 0 | 10.9 (2.0) | no |
| ppo_v4yaw_s42 | stochastic | 100% | 262.03 | 56.73 | 309.50 | 262.03 | 249.951 | 96% | 1.654 | -0.321 | 44% | 40% | 57.36 / 57.52 | 128.3 / 128.7 | 107.2% | 0 | 10.9 (2.0) | no |
| ppo_v4yaw_s43 | deterministic | 100% | 261.13 | 58.92 | 309.87 | 261.13 | 243.011 | 94% | 1.648 | -0.082 | 42% | 38% | 57.36 / 57.52 | 128.3 / 128.7 | 107.2% | 0 | 10.9 (2.0) | no |
| ppo_v4yaw_s43 | stochastic | 100% | 262.39 | 57.11 | 309.87 | 262.39 | 244.277 | 94% | 1.739 | -0.058 | 44% | 40% | 57.36 / 57.52 | 128.3 / 128.7 | 107.2% | 0 | 10.9 (2.0) | no |
| imit2_w075_s53 | deterministic | 100% | 139.24 | 53.46 | 292.69 | 139.24 | 116.877 | 92% | 3.569 | -1.140 | 6% | 24% | 53.98 / 54.09 | 120.7 / 121.0 | 100.8% | 0 | 11.3 (3.7) | no |
| imit2_w075_s53 | stochastic | 100% | 112.71 | 55.26 | 279.75 | 112.71 | 96.121 | 94% | 1.007 | -0.173 | 2% | 10% | 53.99 / 54.26 | 120.8 / 121.4 | 101.2% | 0 | 8.9 (7.7) | no |
| imit2_w075_s51 | deterministic | 100% | 126.57 | 99.65 | 286.60 | 126.57 | 49.278 | 72% | 0.582 | +0.074 | 4% | 2% | 53.88 / 53.98 | 120.5 / 120.7 | 100.6% | 0 | 1.4 (9.5) | FLAT |
| imit2_w075_s51 | stochastic | 100% | 124.70 | 76.51 | 281.63 | 124.70 | 80.579 | 84% | 4.286 | -0.091 | 8% | 6% | 53.87 / 54.12 | 120.5 / 121.1 | 100.9% | 0 | 6.6 (8.5) | no |
| imit2_w075_s52 | deterministic | 100% | 139.93 | 52.13 | 283.49 | 139.93 | 117.839 | 92% | 2.963 | -0.944 | 8% | 26% | 53.89 / 54.01 | 120.6 / 120.8 | 100.7% | 0 | 11.3 (3.7) | no |
| imit2_w075_s52 | stochastic | 100% | 131.14 | 61.12 | 290.92 | 131.14 | 103.222 | 90% | 2.728 | -1.093 | 2% | 22% | 53.88 / 54.10 | 120.5 / 121.0 | 100.9% | 0 | 9.7 (6.2) | no |
| imit3_w075_s51 | deterministic | 100% | 113.09 | 23.15 | 182.73 | 113.09 | 113.093 | 100% | 0.733 | -0.110 | 2% | 10% | 53.73 / 53.83 | 120.2 / 120.4 | 100.3% | 0 | 12.2 (1.4) | no |
| imit3_w075_s51 | stochastic | 100% | 112.42 | 24.11 | 182.78 | 112.42 | 112.425 | 100% | 0.670 | -0.065 | 2% | 8% | 53.73 / 53.82 | 120.2 / 120.4 | 100.3% | 0 | 12.2 (1.4) | no |
| imit3_w075_s52 | deterministic | 100% | 124.97 | 46.22 | 277.56 | 124.97 | 108.424 | 94% | 1.097 | -0.167 | 6% | 12% | 53.76 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 11.4 (3.3) | no |
| imit3_w075_s52 | stochastic | 100% | 124.70 | 46.88 | 276.34 | 124.70 | 108.181 | 94% | 1.365 | -0.246 | 4% | 10% | 53.76 / 53.91 | 120.3 / 120.6 | 100.5% | 0 | 11.4 (3.3) | no |
| imit3_w050_s51 | deterministic | 100% | 119.39 | 32.18 | 190.07 | 119.39 | 119.392 | 100% | 2.203 | -0.547 | 6% | 18% | 53.81 / 53.92 | 120.4 / 120.6 | 100.5% | 0 | 12.3 (1.4) | no |
| imit3_w050_s51 | stochastic | 100% | 120.45 | 30.49 | 186.89 | 120.45 | 120.450 | 100% | 2.154 | -0.614 | 4% | 16% | 53.81 / 53.92 | 120.4 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| imit3_w050_s52 | deterministic | 100% | 107.74 | 17.57 | 162.79 | 107.74 | 107.739 | 100% | 0.232 | -0.056 | 0% | 4% | 53.84 / 53.94 | 120.4 / 120.7 | 100.6% | 0 | 12.3 (1.3) | no |
| imit3_w050_s52 | stochastic | 100% | 109.70 | 19.17 | 171.77 | 109.70 | 109.699 | 100% | 0.294 | -0.070 | 0% | 4% | 53.84 / 53.95 | 120.4 / 120.7 | 100.6% | 0 | 12.3 (1.3) | no |
| imit3_w075_s53 | deterministic | 100% | 134.13 | 52.10 | 281.13 | 134.13 | 111.950 | 92% | 2.267 | -0.637 | 6% | 16% | 53.80 / 53.91 | 120.3 / 120.6 | 100.5% | 0 | 11.2 (3.7) | no |
| imit3_w075_s53 | stochastic | 100% | 131.49 | 48.13 | 286.87 | 131.49 | 114.637 | 94% | 2.248 | -0.622 | 6% | 16% | 53.80 / 53.91 | 120.3 / 120.6 | 100.5% | 0 | 11.5 (3.3) | no |
| imit3_w025_s52 | deterministic | 100% | 117.07 | 67.87 | 286.49 | 117.07 | 88.949 | 90% | 5.314 | -0.241 | 6% | 2% | 55.12 / 55.67 | 123.3 / 124.5 | 103.8% | 0 | 6.8 (8.8) | no |
| imit3_w025_s52 | stochastic | 100% | 125.17 | 67.50 | 284.62 | 125.17 | 91.405 | 88% | 5.708 | +0.882 | 6% | 4% | 55.11 / 55.64 | 123.3 / 124.5 | 103.7% | 0 | 7.9 (8.0) | no |
| imit3_w025_s51 | deterministic | 100% | 105.11 | 18.20 | 166.65 | 105.11 | 105.109 | 100% | 0.108 | -0.022 | 0% | 2% | 53.86 / 53.99 | 120.5 / 120.8 | 100.7% | 0 | 12.2 (1.3) | no |
| imit3_w025_s51 | stochastic | 100% | 106.16 | 15.45 | 157.84 | 106.16 | 106.157 | 100% | 0.091 | -0.020 | 0% | 2% | 53.87 / 54.00 | 120.5 / 120.8 | 100.7% | 0 | 12.2 (1.3) | no |
| imit3_w000_s52 | deterministic | 100% | 127.37 | 51.77 | 287.04 | 127.37 | 105.147 | 92% | 5.529 | +0.698 | 8% | 10% | 53.24 / 55.22 | 119.1 / 123.5 | 102.9% | 0 | 11.3 (3.6) | no |
| imit3_w000_s52 | stochastic | 100% | 119.80 | 66.79 | 291.44 | 119.80 | 91.859 | 90% | 1.613 | -0.025 | 6% | 10% | 53.37 / 55.06 | 119.4 / 123.2 | 102.7% | 0 | 8.3 (7.7) | no |
| imit3_w000_s51/best_imit_scriptfree_s51_NOTPASS_lat3.56 | deterministic | 100% | 125.97 | 48.66 | 277.24 | 125.97 | 109.442 | 94% | 3.969 | -0.022 | 4% | 14% | 53.91 / 54.04 | 120.6 / 120.9 | 100.7% | 0 | 11.2 (3.6) | no |
| imit3_w000_s51/best_imit_scriptfree_s51_NOTPASS_lat3.56 | stochastic | 100% | 127.77 | 47.31 | 275.81 | 127.77 | 111.273 | 94% | 2.569 | -0.133 | 6% | 12% | 53.91 / 54.04 | 120.6 / 120.9 | 100.8% | 0 | 11.5 (3.2) | no |

DTW to native Mason v2 recommended refs (mean rad, all11 / upper5; see leaderboard.md for caveats): mean over the 11 refs

| Model | Mode | mean of 11 refs |
|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 1.905 / 1.299 |
| ppo_resid_v3_ladder_s0 | stochastic | 2.044 / 1.475 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deterministic | 2.045 / 1.482 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stochastic | 2.045 / 1.482 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deterministic | 2.177 / 1.659 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stochastic | 2.177 / 1.659 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deterministic | 2.242 / 1.778 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stochastic | 2.242 / 1.778 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deterministic | 2.060 / 1.524 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stochastic | 2.060 / 1.524 |
| ppo_resid_v3_left_an1_s0 | deterministic | 1.900 / 1.283 |
| ppo_resid_v3_left_an1_s0 | stochastic | 1.951 / 1.350 |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | deterministic | 1.893 / 1.270 |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | stochastic | 1.935 / 1.325 |
| ppo_resid_v3_left_an3_s1 | deterministic | 1.905 / 1.286 |
| ppo_resid_v3_left_an3_s1 | stochastic | 1.921 / 1.310 |
| ppo_resid_v3_left_an4_s2 | deterministic | 1.916 / 1.304 |
| ppo_resid_v3_left_an4_s2 | stochastic | 1.924 / 1.314 |
| ppo_resid_v3_left_an5_s3 | deterministic | 2.418 / 1.942 |
| ppo_resid_v3_left_an5_s3 | stochastic | 2.316 / 1.811 |
| ppo_resid_v3_left_an6_s4 | deterministic | 1.929 / 1.323 |
| ppo_resid_v3_left_an6_s4 | stochastic | 1.941 / 1.336 |
| ppo_resid_v3_left_an7_s5 | deterministic | 2.329 / 1.834 |
| ppo_resid_v3_left_an7_s5 | stochastic | 2.449 / 1.982 |
| ppo_resid_v3_left_an8_s6 | deterministic | 2.462 / 2.001 |
| ppo_resid_v3_left_an8_s6 | stochastic | 2.461 / 1.997 |
| ppo_resid_v3_left_an9_s7 | deterministic | 1.908 / 1.299 |
| ppo_resid_v3_left_an9_s7 | stochastic | 1.944 / 1.345 |
| ppo_resid_v3_left_an10_s8 | deterministic | 1.933 / 1.332 |
| ppo_resid_v3_left_an10_s8 | stochastic | 2.020 / 1.447 |
| ppo_resid_v3_left_fast1_s10 | deterministic | 2.668 / 2.271 |
| ppo_resid_v3_left_fast1_s10 | stochastic | 2.669 / 2.271 |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | deterministic | 2.666 / 2.267 |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | stochastic | 2.663 / 2.262 |
| ppo_v3tiny_s22 | deterministic | 2.090 / 1.565 |
| ppo_v3tiny_s22 | stochastic | 2.078 / 1.545 |
| ppo_v3tiny_s21 | deterministic | 2.079 / 1.549 |
| ppo_v3tiny_s21 | stochastic | 2.065 / 1.532 |
| ppo_v3tiny_s23 | deterministic | 2.095 / 1.568 |
| ppo_v3tiny_s23 | stochastic | 2.059 / 1.523 |
| ppo_v3flt_all_s33 | deterministic | 2.126 / 1.614 |
| ppo_v3flt_all_s33 | stochastic | 2.108 / 1.583 |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | deterministic | 2.068 / 1.536 |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | stochastic | 2.066 / 1.532 |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | deterministic | 2.066 / 1.533 |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | stochastic | 2.063 / 1.529 |
| ppo_v4yaw_s41/best_v4yaw_s41 | deterministic | 1.845 / 1.187 |
| ppo_v4yaw_s41/best_v4yaw_s41 | stochastic | 1.845 / 1.187 |
| ppo_v4yaw_s42 | deterministic | 1.846 / 1.189 |
| ppo_v4yaw_s42 | stochastic | 1.843 / 1.184 |
| ppo_v4yaw_s43 | deterministic | 1.847 / 1.190 |
| ppo_v4yaw_s43 | stochastic | 1.843 / 1.184 |
| imit2_w075_s53 | deterministic | 2.010 / 1.449 |
| imit2_w075_s53 | stochastic | 2.106 / 1.581 |
| imit2_w075_s51 | deterministic | 2.161 / 1.642 |
| imit2_w075_s51 | stochastic | 2.104 / 1.574 |
| imit2_w075_s52 | deterministic | 2.007 / 1.446 |
| imit2_w075_s52 | stochastic | 2.047 / 1.498 |
| imit3_w075_s51 | deterministic | 2.062 / 1.527 |
| imit3_w075_s51 | stochastic | 2.066 / 1.533 |
| imit3_w075_s52 | deterministic | 2.046 / 1.503 |
| imit3_w075_s52 | stochastic | 2.049 / 1.508 |
| imit3_w050_s51 | deterministic | 2.052 / 1.512 |
| imit3_w050_s51 | stochastic | 2.045 / 1.501 |
| imit3_w050_s52 | deterministic | 2.086 / 1.560 |
| imit3_w050_s52 | stochastic | 2.075 / 1.544 |
| imit3_w075_s53 | deterministic | 2.023 / 1.469 |
| imit3_w075_s53 | stochastic | 2.026 / 1.474 |
| imit3_w025_s52 | deterministic | 2.119 / 1.588 |
| imit3_w025_s52 | stochastic | 2.086 / 1.548 |
| imit3_w025_s51 | deterministic | 2.095 / 1.573 |
| imit3_w025_s51 | stochastic | 2.087 / 1.563 |
| imit3_w000_s52 | deterministic | 2.043 / 1.501 |
| imit3_w000_s52 | stochastic | 2.103 / 1.575 |
| imit3_w000_s51/best_imit_scriptfree_s51_NOTPASS_lat3.56 | deterministic | 2.049 / 1.506 |
| imit3_w000_s51/best_imit_scriptfree_s51_NOTPASS_lat3.56 | stochastic | 2.040 / 1.494 |

# Dispersion detail: scripted baseline, ladder model and all left-handed models

50 episodes/mode, seeds 4000..4049; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).

| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps | Launch elev mean deg (std) | flat? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 100% | 101.91 | 13.01 | 148.16 | 101.91 | 101.908 | 100% | 8.277 | -0.136 | 44% | 50% | 49.65 / 49.94 | 111.1 / 111.7 | 93.1% | 0 | 32.4 (4.6) | no |
| ppo_resid_v3_ladder_s0 | stochastic | 100% | 108.18 | 86.11 | 342.09 | 108.18 | 69.468 | 88% | 11.577 | +0.242 | 48% | 32% | 49.76 / 54.95 | 111.3 / 122.9 | 102.4% | 0 | 25.3 (18.7) | no |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deterministic | 100% | 178.15 | 128.88 | 328.02 | 178.15 | 38.065 | 56% | 2.945 | -0.635 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 | 9.1 (13.2) | FLAT |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stochastic | 100% | 178.15 | 128.88 | 328.02 | 178.15 | 38.065 | 56% | 2.945 | -0.635 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 | 9.1 (13.2) | FLAT |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deterministic | 100% | 117.44 | 110.71 | 326.09 | 117.44 | 53.056 | 80% | 1.980 | -0.204 | 4% | 12% | 48.21 / 48.27 | 107.8 / 108.0 | 90.0% | 0 | 11.0 (11.3) | no |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stochastic | 100% | 117.44 | 110.71 | 326.09 | 117.44 | 53.056 | 80% | 1.980 | -0.204 | 4% | 12% | 48.21 / 48.27 | 107.8 / 108.0 | 90.0% | 0 | 11.0 (11.3) | no |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deterministic | 100% | 79.89 | 42.31 | 275.96 | 79.89 | 68.872 | 96% | 0.013 | -0.001 | 0% | 0% | 53.80 / 53.93 | 120.3 / 120.6 | 100.5% | 0 | 9.0 (2.9) | no |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stochastic | 100% | 79.89 | 42.31 | 275.96 | 79.89 | 68.872 | 96% | 0.013 | -0.001 | 0% | 0% | 53.80 / 53.93 | 120.3 / 120.6 | 100.5% | 0 | 9.0 (2.9) | no |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deterministic | 100% | 113.83 | 26.54 | 186.42 | 113.83 | 113.827 | 100% | 1.664 | -0.340 | 2% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stochastic | 100% | 113.83 | 26.54 | 186.42 | 113.83 | 113.827 | 100% | 1.664 | -0.340 | 2% | 12% | 53.80 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_resid_v3_left_an1_s0 | deterministic | 100% | 110.28 | 14.50 | 162.27 | 110.28 | 110.280 | 100% | 7.530 | +0.425 | 52% | 46% | 51.20 / 51.59 | 114.5 / 115.4 | 96.2% | 0 | 32.0 (3.6) | no |
| ppo_resid_v3_left_an1_s0 | stochastic | 100% | 105.46 | 66.91 | 344.17 | 105.46 | 84.943 | 94% | 12.430 | -2.190 | 44% | 46% | 50.65 / 53.38 | 113.3 / 119.4 | 99.5% | 0 | 30.3 (15.8) | no |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | deterministic | 100% | 114.29 | 17.54 | 160.27 | 114.29 | 114.289 | 100% | 7.420 | -0.081 | 46% | 46% | 51.25 / 51.62 | 114.7 / 115.5 | 96.2% | 0 | 31.7 (4.1) | no |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | stochastic | 100% | 110.95 | 63.02 | 342.58 | 110.95 | 90.809 | 94% | 7.568 | -0.072 | 40% | 48% | 51.24 / 53.09 | 114.6 / 118.8 | 99.0% | 0 | 28.8 (12.5) | no |
| ppo_resid_v3_left_an3_s1 | deterministic | 100% | 108.60 | 25.87 | 162.26 | 108.60 | 108.602 | 100% | 6.743 | +0.940 | 54% | 36% | 51.24 / 51.48 | 114.6 / 115.2 | 96.0% | 0 | 30.7 (7.5) | no |
| ppo_resid_v3_left_an3_s1 | stochastic | 100% | 116.68 | 56.85 | 334.78 | 116.68 | 97.208 | 94% | 7.491 | +1.741 | 54% | 36% | 50.96 / 53.09 | 114.0 / 118.7 | 99.0% | 0 | 29.8 (10.3) | no |
| ppo_resid_v3_left_an4_s2 | deterministic | 100% | 96.13 | 8.38 | 115.77 | 96.13 | 96.129 | 100% | 6.675 | +0.113 | 48% | 44% | 49.94 / 50.23 | 111.7 / 112.4 | 93.6% | 0 | 33.4 (3.5) | no |
| ppo_resid_v3_left_an4_s2 | stochastic | 100% | 100.02 | 37.15 | 328.06 | 100.02 | 93.456 | 98% | 8.905 | -0.109 | 48% | 48% | 49.82 / 51.99 | 111.4 / 116.3 | 96.9% | 0 | 34.3 (7.7) | no |
| ppo_resid_v3_left_an5_s3 | deterministic | 100% | 108.04 | 152.00 | 357.37 | 108.04 | 9.572 | 72% | 0.143 | +0.098 | 0% | 0% | 52.30 / 52.62 | 117.0 / 117.7 | 98.1% | 0 | -3.4 (2.1) | FLAT |
| ppo_resid_v3_left_an5_s3 | stochastic | 100% | 133.61 | 157.32 | 359.56 | 133.61 | 14.490 | 66% | 1.583 | +0.029 | 22% | 12% | 51.99 / 53.79 | 116.3 / 120.3 | 100.3% | 0 | -1.6 (7.8) | FLAT |
| ppo_resid_v3_left_an6_s4 | deterministic | 100% | 106.50 | 37.70 | 335.10 | 106.50 | 99.802 | 98% | 6.947 | -0.002 | 48% | 40% | 50.50 / 51.41 | 113.0 / 115.0 | 95.8% | 0 | 29.4 (8.4) | no |
| ppo_resid_v3_left_an6_s4 | stochastic | 100% | 131.66 | 87.19 | 346.83 | 131.66 | 84.548 | 86% | 7.703 | +0.731 | 48% | 36% | 50.94 / 52.90 | 114.0 / 118.3 | 98.6% | 0 | 24.2 (13.7) | no |
| ppo_resid_v3_left_an7_s5 | deterministic | 100% | 127.22 | 158.32 | 355.37 | 127.22 | 8.983 | 66% | 0.262 | -0.213 | 0% | 34% | 51.53 / 52.24 | 115.3 / 116.9 | 97.4% | 0 | -3.2 (2.1) | FLAT |
| ppo_resid_v3_left_an7_s5 | stochastic | 100% | 141.36 | 163.01 | 357.35 | 141.36 | 8.538 | 62% | 0.469 | -0.234 | 0% | 20% | 51.73 / 53.23 | 115.7 / 119.1 | 99.2% | 0 | -2.9 (2.1) | FLAT |
| ppo_resid_v3_left_an8_s6 | deterministic | 100% | 75.60 | 131.64 | 359.26 | 75.60 | 11.427 | 82% | 0.096 | -0.050 | 0% | 0% | 52.97 / 53.27 | 118.5 / 119.2 | 99.3% | 0 | -5.2 (2.8) | FLAT |
| ppo_resid_v3_left_an8_s6 | stochastic | 100% | 82.61 | 136.51 | 366.34 | 82.61 | 11.504 | 80% | 0.853 | -0.174 | 6% | 10% | 52.83 / 54.08 | 118.2 / 121.0 | 100.8% | 0 | -4.6 (2.4) | FLAT |
| ppo_resid_v3_left_an9_s7 | deterministic | 100% | 103.03 | 10.64 | 143.64 | 103.03 | 103.032 | 100% | 7.113 | +1.052 | 58% | 42% | 49.39 / 49.97 | 110.5 / 111.8 | 93.2% | 0 | 32.8 (4.0) | no |
| ppo_resid_v3_left_an9_s7 | stochastic | 100% | 126.63 | 83.41 | 345.37 | 126.63 | 81.200 | 86% | 8.189 | +0.147 | 46% | 42% | 49.28 / 52.10 | 110.2 / 116.5 | 97.1% | 0 | 28.3 (14.3) | no |
| ppo_resid_v3_left_an10_s8 | deterministic | 100% | 128.80 | 53.58 | 324.46 | 128.80 | 109.967 | 94% | 5.670 | +0.786 | 50% | 32% | 47.82 / 48.45 | 107.0 / 108.4 | 90.3% | 0 | 24.7 (8.9) | no |
| ppo_resid_v3_left_an10_s8 | stochastic | 100% | 126.19 | 106.94 | 334.03 | 126.19 | 57.133 | 78% | 6.396 | +1.591 | 38% | 24% | 48.00 / 50.41 | 107.4 / 112.8 | 94.0% | 0 | 14.5 (15.7) | no |
| ppo_resid_v3_left_fast1_s10 | deterministic | 100% | 22.54 | 48.37 | 360.36 | 22.54 | 15.337 | 98% | 0.023 | +0.008 | 0% | 0% | 54.65 / 54.72 | 122.2 / 122.4 | 102.0% | 0 | -5.3 (1.5) | FLAT |
| ppo_resid_v3_left_fast1_s10 | stochastic | 100% | 18.58 | 20.13 | 124.50 | 18.58 | 18.577 | 100% | 0.925 | +0.167 | 4% | 0% | 54.56 / 55.14 | 122.0 / 123.3 | 102.8% | 0 | -3.5 (6.8) | FLAT |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | deterministic | 100% | 15.24 | 2.68 | 22.08 | 15.24 | 15.242 | 100% | 0.017 | -0.011 | 0% | 0% | 55.24 / 55.34 | 123.6 / 123.8 | 103.2% | 0 | -5.8 (1.4) | FLAT |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | stochastic | 100% | 15.20 | 2.98 | 24.89 | 15.20 | 15.201 | 100% | 0.027 | -0.011 | 0% | 0% | 55.21 / 55.77 | 123.5 / 124.7 | 104.0% | 0 | -5.4 (1.4) | FLAT |
| ppo_v3tiny_s22 | deterministic | 100% | 117.09 | 33.41 | 190.49 | 117.09 | 117.093 | 100% | 6.099 | -0.270 | 10% | 20% | 52.91 / 53.04 | 118.4 / 118.6 | 98.9% | 0 | 12.1 (2.3) | no |
| ppo_v3tiny_s22 | stochastic | 100% | 121.38 | 55.83 | 272.74 | 121.38 | 99.875 | 92% | 9.212 | +1.538 | 16% | 8% | 53.17 / 54.26 | 118.9 / 121.4 | 101.2% | 0 | 9.7 (6.6) | no |
| ppo_v3tiny_s21 | deterministic | 100% | 121.21 | 70.68 | 283.77 | 121.21 | 82.600 | 86% | 7.886 | -0.433 | 6% | 8% | 53.18 / 53.31 | 119.0 / 119.3 | 99.4% | 0 | 8.0 (7.4) | no |
| ppo_v3tiny_s21 | stochastic | 100% | 110.68 | 51.87 | 276.51 | 110.68 | 94.506 | 94% | 10.305 | -1.068 | 8% | 6% | 53.17 / 54.13 | 118.9 / 121.1 | 100.9% | 0 | 9.5 (7.0) | no |
| ppo_v3tiny_s23 | deterministic | 100% | 125.02 | 58.10 | 280.26 | 125.02 | 97.646 | 90% | 2.936 | +0.032 | 6% | 16% | 53.18 / 53.75 | 119.0 / 120.2 | 100.2% | 0 | 10.0 (5.9) | no |
| ppo_v3tiny_s23 | stochastic | 100% | 123.10 | 56.98 | 276.12 | 123.10 | 95.829 | 90% | 7.460 | +1.869 | 10% | 4% | 53.38 / 54.71 | 119.4 / 122.4 | 102.0% | 0 | 10.2 (5.2) | no |
| ppo_v3flt_all_s33 | deterministic | 100% | 102.28 | 39.06 | 284.74 | 102.28 | 96.587 | 98% | 7.146 | +0.005 | 2% | 2% | 53.78 / 53.87 | 120.3 / 120.5 | 100.4% | 0 | 10.6 (6.0) | no |
| ppo_v3flt_all_s33 | stochastic | 100% | 106.08 | 36.88 | 176.99 | 106.08 | 106.078 | 100% | 11.081 | +0.261 | 6% | 10% | 53.79 / 53.92 | 120.3 / 120.6 | 100.5% | 0 | 10.0 (6.8) | no |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | deterministic | 100% | 113.77 | 26.25 | 185.90 | 113.77 | 113.772 | 100% | 1.555 | -0.287 | 4% | 12% | 53.79 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | stochastic | 100% | 113.71 | 25.48 | 185.82 | 113.71 | 113.713 | 100% | 1.786 | -0.445 | 4% | 12% | 53.79 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | deterministic | 100% | 113.83 | 26.18 | 185.89 | 113.83 | 113.831 | 100% | 1.585 | -0.280 | 2% | 12% | 53.79 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | stochastic | 100% | 114.56 | 25.92 | 185.87 | 114.56 | 114.559 | 100% | 1.610 | -0.177 | 4% | 12% | 53.79 / 53.90 | 120.3 / 120.6 | 100.5% | 0 | 12.2 (1.4) | no |

DTW to native Mason v2 recommended refs (mean rad, all11 / upper5; see leaderboard.md for caveats): mean over the 11 refs

| Model | Mode | mean of 11 refs |
|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 2.106 / 1.560 |
| ppo_resid_v3_ladder_s0 | stochastic | 2.136 / 1.607 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | deterministic | 2.103 / 1.569 |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] | stochastic | 2.103 / 1.569 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | deterministic | 2.222 / 1.738 |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] | stochastic | 2.222 / 1.738 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | deterministic | 2.412 / 1.971 |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] | stochastic | 2.412 / 1.971 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | deterministic | 2.338 / 1.832 |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] | stochastic | 2.338 / 1.832 |
| ppo_resid_v3_left_an1_s0 | deterministic | 2.093 / 1.533 |
| ppo_resid_v3_left_an1_s0 | stochastic | 2.112 / 1.566 |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | deterministic | 2.084 / 1.520 |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | stochastic | 2.114 / 1.567 |
| ppo_resid_v3_left_an3_s1 | deterministic | 2.104 / 1.551 |
| ppo_resid_v3_left_an3_s1 | stochastic | 2.103 / 1.550 |
| ppo_resid_v3_left_an4_s2 | deterministic | 2.126 / 1.584 |
| ppo_resid_v3_left_an4_s2 | stochastic | 2.116 / 1.571 |
| ppo_resid_v3_left_an5_s3 | deterministic | 2.240 / 1.784 |
| ppo_resid_v3_left_an5_s3 | stochastic | 2.194 / 1.715 |
| ppo_resid_v3_left_an6_s4 | deterministic | 2.122 / 1.578 |
| ppo_resid_v3_left_an6_s4 | stochastic | 2.102 / 1.554 |
| ppo_resid_v3_left_an7_s5 | deterministic | 2.217 / 1.749 |
| ppo_resid_v3_left_an7_s5 | stochastic | 2.198 / 1.719 |
| ppo_resid_v3_left_an8_s6 | deterministic | 2.295 / 1.863 |
| ppo_resid_v3_left_an8_s6 | stochastic | 2.285 / 1.847 |
| ppo_resid_v3_left_an9_s7 | deterministic | 2.109 / 1.562 |
| ppo_resid_v3_left_an9_s7 | stochastic | 2.099 / 1.547 |
| ppo_resid_v3_left_an10_s8 | deterministic | 2.095 / 1.544 |
| ppo_resid_v3_left_an10_s8 | stochastic | 2.144 / 1.629 |
| ppo_resid_v3_left_fast1_s10 | deterministic | 2.388 / 1.994 |
| ppo_resid_v3_left_fast1_s10 | stochastic | 2.391 / 1.997 |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | deterministic | 2.390 / 2.001 |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | stochastic | 2.390 / 2.002 |
| ppo_v3tiny_s22 | deterministic | 2.308 / 1.813 |
| ppo_v3tiny_s22 | stochastic | 2.293 / 1.796 |
| ppo_v3tiny_s21 | deterministic | 2.295 / 1.798 |
| ppo_v3tiny_s21 | stochastic | 2.325 / 1.839 |
| ppo_v3tiny_s23 | deterministic | 2.292 / 1.795 |
| ppo_v3tiny_s23 | stochastic | 2.305 / 1.806 |
| ppo_v3flt_all_s33 | deterministic | 2.361 / 1.883 |
| ppo_v3flt_all_s33 | stochastic | 2.336 / 1.852 |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | deterministic | 2.337 / 1.833 |
| ppo_v3flt_yaw_s32/best_learned_yaw_s32 | stochastic | 2.338 / 1.833 |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | deterministic | 2.337 / 1.833 |
| ppo_v3flt_yaw_s31/best_learned_yaw_s31 | stochastic | 2.335 / 1.828 |

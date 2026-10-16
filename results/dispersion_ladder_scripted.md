# Dispersion detail: scripted baseline, ladder model and all left-handed models

50 episodes/mode, seeds 4000..4049; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).

| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps | Launch elev mean deg (std) | flat? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 100% | 101.91 | 13.01 | 148.16 | 101.91 | 101.908 | 100% | 8.277 | -0.136 | 44% | 50% | 49.65 / 49.94 | 111.1 / 111.7 | 93.1% | 0 | 32.4 (4.6) | no |
| ppo_resid_v3_ladder_s0 | stochastic | 100% | 108.18 | 86.11 | 342.09 | 108.18 | 69.468 | 88% | 11.577 | +0.242 | 48% | 32% | 49.76 / 54.95 | 111.3 / 122.9 | 102.4% | 0 | 25.3 (18.7) | no |
| scripted_baseline | deterministic | 100% | 178.15 | 128.88 | 328.02 | 178.15 | 38.065 | 56% | 2.945 | -0.635 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 | 9.1 (13.2) | FLAT |
| scripted_baseline | stochastic | 100% | 178.15 | 128.88 | 328.02 | 178.15 | 38.065 | 56% | 2.945 | -0.635 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 | 9.1 (13.2) | FLAT |
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

DTW to native Mason v2 recommended refs (mean rad, all11 / upper5; see leaderboard.md for caveats): mean over the 11 refs

| Model | Mode | mean of 11 refs |
|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 2.106 / 1.560 |
| ppo_resid_v3_ladder_s0 | stochastic | 2.136 / 1.607 |
| scripted_baseline | deterministic | 2.103 / 1.569 |
| scripted_baseline | stochastic | 2.103 / 1.569 |
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

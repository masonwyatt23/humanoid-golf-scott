# Dispersion detail: ladder model and scripted baseline

50 episodes/mode, seeds 4000..4049; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).

| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 100% | 88.56 | 8.85 | 111.93 | 88.56 | 0.000 | 0% | 7.096 | -0.110 | 44% | 52% | 49.65 / 49.94 | 111.1 / 111.7 | 93.1% | 0 |
| ppo_resid_v3_ladder_s0 | stochastic | 100% | 78.45 | 40.50 | 155.60 | 78.45 | 2.361 | 16% | 13.502 | -0.208 | 46% | 32% | 49.98 / 53.11 | 111.8 / 118.8 | 99.0% | 0 |
| scripted_baseline | deterministic | 100% | 99.85 | 51.34 | 152.07 | 99.85 | 11.978 | 32% | 2.735 | -0.578 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 |
| scripted_baseline | stochastic | 100% | 99.85 | 51.34 | 152.07 | 99.85 | 11.978 | 32% | 2.735 | -0.578 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 |

DTW to mirrored Mason refs (mean rad, all11 / upper5):

| Model | Mode | mason_swing_part1_s05_refined_mirrored | mason_swing_part2_s01_refined_mirrored | mason_swing_part1_s02_refined_mirrored | mason_swing_part1_s06_refined_mirrored | mason_swing_part1_s03_refined_mirrored | mason_swing_part1_s04_refined_mirrored | mason_swing_part2_s05_refined_mirrored | mason_swing_part2_s02_refined_mirrored |
|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 2.236 / 1.893 | 2.482 / 1.910 | 1.923 / 1.412 | 2.111 / 1.613 | 2.124 / 1.501 | 2.064 / 1.529 | 2.067 / 1.452 | 2.447 / 1.843 |
| ppo_resid_v3_ladder_s0 | stochastic | 2.216 / 1.879 | 2.487 / 1.917 | 1.944 / 1.451 | 2.154 / 1.682 | 2.160 / 1.555 | 2.100 / 1.575 | 2.126 / 1.532 | 2.456 / 1.863 |
| scripted_baseline | deterministic | 2.197 / 1.870 | 2.484 / 1.913 | 1.959 / 1.477 | 2.188 / 1.734 | 2.183 / 1.592 | 2.116 / 1.607 | 2.171 / 1.593 | 2.458 / 1.872 |
| scripted_baseline | stochastic | 2.197 / 1.870 | 2.484 / 1.913 | 1.959 / 1.477 | 2.188 / 1.734 | 2.183 / 1.592 | 2.116 / 1.607 | 2.171 / 1.593 | 2.458 / 1.872 |

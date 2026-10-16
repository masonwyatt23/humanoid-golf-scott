# Dispersion detail: ladder model and scripted baseline

50 episodes/mode, seeds 4000..4049; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).

| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 100% | 101.91 | 13.01 | 148.16 | 101.91 | 101.908 | 100% | 8.277 | -0.136 | 44% | 50% | 49.65 / 49.94 | 111.1 / 111.7 | 93.1% | 0 |
| ppo_resid_v3_ladder_s0 | stochastic | 100% | 108.18 | 86.11 | 342.09 | 108.18 | 69.468 | 88% | 11.577 | +0.242 | 48% | 32% | 49.76 / 54.95 | 111.3 / 122.9 | 102.4% | 0 |
| scripted_baseline | deterministic | 100% | 178.15 | 128.88 | 328.02 | 178.15 | 38.065 | 56% | 2.945 | -0.635 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 |
| scripted_baseline | stochastic | 100% | 178.15 | 128.88 | 328.02 | 178.15 | 38.065 | 56% | 2.945 | -0.635 | 8% | 22% | 48.22 / 48.33 | 107.9 / 108.1 | 90.1% | 0 |

DTW to mirrored Mason refs (mean rad, all11 / upper5):

| Model | Mode | mason_swing_part1_s05_refined_mirrored | mason_swing_part2_s01_refined_mirrored | mason_swing_part1_s02_refined_mirrored | mason_swing_part1_s06_refined_mirrored | mason_swing_part1_s03_refined_mirrored | mason_swing_part1_s04_refined_mirrored | mason_swing_part2_s05_refined_mirrored | mason_swing_part2_s02_refined_mirrored |
|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_ladder_s0 | deterministic | 2.145 / 1.752 | 2.354 / 1.779 | 1.889 / 1.362 | 2.041 / 1.507 | 2.065 / 1.407 | 1.997 / 1.439 | 2.009 / 1.374 | 2.349 / 1.702 |
| ppo_resid_v3_ladder_s0 | stochastic | 2.121 / 1.729 | 2.349 / 1.774 | 1.907 / 1.396 | 2.082 / 1.573 | 2.097 / 1.458 | 2.025 / 1.481 | 2.067 / 1.455 | 2.351 / 1.713 |
| scripted_baseline | deterministic | 2.035 / 1.612 | 2.237 / 1.658 | 1.897 / 1.388 | 2.064 / 1.547 | 2.077 / 1.427 | 1.981 / 1.446 | 2.065 / 1.457 | 2.272 / 1.608 |
| scripted_baseline | stochastic | 2.035 / 1.612 | 2.237 / 1.658 | 1.897 / 1.388 | 2.064 / 1.547 | 2.077 / 1.427 | 1.981 / 1.446 | 2.065 / 1.457 | 2.272 / 1.608 |

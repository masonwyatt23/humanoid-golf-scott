# Multi-model comparison (GENERATED from results/leaderboard.json by eval.compare_styles.from_leaderboard - do not edit by hand)

Env fingerprint `737c4d124c92`, 50 episodes/mode, seeds 4000+. Distance = final ball x; carry = first landing (mean over all episodes; 0 if never landed); +y = left, miss = |y| > 0.5 m.
Best trained: **ppo_resid_v3_left_an3_s1**; best left-handed: **ppo_resid_v3_left_an3_s1**; best overall incl. scripted baseline: **scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01]**.

| Model | Steps | Hand | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak club mph (mean/max) | % of 120 mph (max) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | 30000 | right | deter | 0% | 0.30 | 0.30 | 0.00 | 0% | 0.00 | 0% | 0% | n/a / n/a | n/a% |
| ppo_scott_baseline | 30000 | right | stoch | 0% | 0.56 | 7.90 | 0.00 | 0% | 0.39 | 2% | 4% | n/a / n/a | n/a% |
| ppo_scott_curr | 30000 | right | deter | 100% | 3.01 | 3.01 | 0.00 | 0% | 0.00 | 0% | 0% | 14.3 / 14.3 | 12.0% |
| ppo_scott_curr | 30000 | right | stoch | 34% | 5.04 | 13.90 | 0.06 | 6% | 2.63 | 18% | 18% | 53.4 / 84.9 | 70.8% |
| ppo_scott_prev_backup | 30000 | right | deter | 100% | 2.76 | 2.76 | 0.00 | 0% | 0.00 | 0% | 0% | 2.2 / 2.2 | 1.9% |
| ppo_scott_prev_backup | 30000 | right | stoch | 38% | 4.86 | 13.62 | 0.02 | 2% | 1.80 | 14% | 22% | 52.3 / 95.2 | 79.3% |
| ppo_scott_final2/ppo_scott_prev2_backup | 60000 | right | deter | 48% | 1.80 | 9.80 | 0.09 | 16% | 0.98 | 14% | 10% | 7.7 / 28.3 | 23.6% |
| ppo_scott_final2/ppo_scott_prev2_backup | 60000 | right | stoch | 60% | 1.96 | 10.37 | 0.13 | 26% | 3.84 | 20% | 18% | 50.8 / 74.8 | 62.3% |
| ppo_scott/ppo_scott_carry1 | 100000 | right | deter | 98% | 0.47 | 0.59 | 0.10 | 20% | 0.06 | 0% | 0% | 0.8 / 1.3 | 1.1% |
| ppo_scott/ppo_scott_carry1 | 100000 | right | stoch | 66% | 0.88 | 5.93 | 0.24 | 26% | 0.31 | 2% | 2% | 57.7 / 91.1 | 75.9% |
| ppo_resid_v3_s0 | 60000 | right | deter | 100% | 56.70 | 69.85 | 56.70 | 100% | 31.44 | 30% | 70% | 100.4 / 101.8 | 84.9% |
| ppo_resid_v3_s0 | 60000 | right | stoch | 60% | 36.30 | 289.55 | 22.60 | 50% | 13.36 | 32% | 12% | 108.5 / 157.5 | 131.2% |
| ppo_resid_v3_r2_s0 | 60000 | right | deter | 100% | 87.78 | 109.95 | 87.78 | 100% | 9.02 | 42% | 56% | 107.3 / 107.7 | 89.7% |
| ppo_resid_v3_r2_s0 | 60000 | right | stoch | 100% | 104.08 | 321.49 | 60.68 | 86% | 17.59 | 44% | 38% | 107.5 / 114.2 | 95.2% |
| ppo_resid_v3_r3_s0 | 100000 | right | deter | 100% | 103.03 | 151.89 | 103.03 | 100% | 8.26 | 46% | 50% | 108.4 / 109.0 | 90.9% |
| ppo_resid_v3_r3_s0 | 100000 | right | stoch | 100% | 143.19 | 343.53 | 66.37 | 76% | 11.25 | 40% | 52% | 109.1 / 117.1 | 97.6% |
| ppo_resid_v3_ladder_s0 | 150000 | right | deter | 100% | 101.91 | 148.16 | 101.91 | 100% | 8.28 | 44% | 50% | 111.1 / 111.7 | 93.1% |
| ppo_resid_v3_ladder_s0 | 150000 | right | stoch | 100% | 108.18 | 342.09 | 69.47 | 88% | 11.58 | 48% | 32% | 111.3 / 122.9 | 102.4% |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] (scripted) | 0 | right | deter | 100% | 178.15 | 328.02 | 38.07 | 56% | 2.94 | 8% | 22% | 107.9 / 108.1 | 90.1% |
| scripted_baseline[ladder cfg: right, loft 6, default ball_x] (scripted) | 0 | right | stoch | 100% | 178.15 | 328.02 | 38.07 | 56% | 2.94 | 8% | 22% | 107.9 / 108.1 | 90.1% |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] (scripted) | 0 | left | deter | 100% | 117.44 | 326.09 | 53.06 | 80% | 1.98 | 4% | 12% | 107.8 / 108.0 | 90.0% |
| scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm] (scripted) | 0 | left | stoch | 100% | 117.44 | 326.09 | 53.06 | 80% | 1.98 | 4% | 12% | 107.8 / 108.0 | 90.0% |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] (scripted) | 0 | left | deter | 100% | 79.89 | 275.96 | 68.87 | 96% | 0.01 | 0% | 0% | 120.3 / 120.6 | 100.5% |
| scripted (not learned) [fast v2 lofted: left, loft -26, ball_dz -0.01, t_down 0.095, wr_end -0.01] (scripted) | 0 | left | stoch | 100% | 79.89 | 275.96 | 68.87 | 96% | 0.01 | 0% | 0% | 120.3 / 120.6 | 100.5% |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] (scripted) | 0 | left | deter | 100% | 113.83 | 186.42 | 113.83 | 100% | 1.66 | 2% | 12% | 120.3 / 120.6 | 100.5% |
| scripted (not learned) [fast v3 Stage 6: left, loft -31, ball_dz -0.008, t_down 0.095, wr_end -0.01] (scripted) | 0 | left | stoch | 100% | 113.83 | 186.42 | 113.83 | 100% | 1.66 | 2% | 12% | 120.3 / 120.6 | 100.5% |
| ppo_resid_v3_left_an1_s0 | 150000 | left | deter | 100% | 110.28 | 162.27 | 110.28 | 100% | 7.53 | 52% | 46% | 114.5 / 115.4 | 96.2% |
| ppo_resid_v3_left_an1_s0 | 150000 | left | stoch | 100% | 105.46 | 344.17 | 84.94 | 94% | 12.43 | 44% | 46% | 113.3 / 119.4 | 99.5% |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | 150000 | left | deter | 100% | 114.29 | 160.27 | 114.29 | 100% | 7.42 | 46% | 46% | 114.7 / 115.5 | 96.2% |
| ppo_resid_v3_left_an2_s0/best_carry_analytic | 150000 | left | stoch | 100% | 110.95 | 342.58 | 90.81 | 94% | 7.57 | 40% | 48% | 114.6 / 118.8 | 99.0% |
| ppo_resid_v3_left_an3_s1 | 150000 | left | deter | 100% | 108.60 | 162.26 | 108.60 | 100% | 6.74 | 54% | 36% | 114.6 / 115.2 | 96.0% |
| ppo_resid_v3_left_an3_s1 | 150000 | left | stoch | 100% | 116.68 | 334.78 | 97.21 | 94% | 7.49 | 54% | 36% | 114.0 / 118.7 | 99.0% |
| ppo_resid_v3_left_an4_s2 | 150000 | left | deter | 100% | 96.13 | 115.77 | 96.13 | 100% | 6.68 | 48% | 44% | 111.7 / 112.4 | 93.6% |
| ppo_resid_v3_left_an4_s2 | 150000 | left | stoch | 100% | 100.02 | 328.06 | 93.46 | 98% | 8.91 | 48% | 48% | 111.4 / 116.3 | 96.9% |
| ppo_resid_v3_left_an5_s3 | 150000 | left | deter | 100% | 108.04 | 357.37 | 9.57 | 72% | 0.14 | 0% | 0% | 117.0 / 117.7 | 98.1% |
| ppo_resid_v3_left_an5_s3 | 150000 | left | stoch | 100% | 133.61 | 359.56 | 14.49 | 66% | 1.58 | 22% | 12% | 116.3 / 120.3 | 100.3% |
| ppo_resid_v3_left_an6_s4 | 150000 | left | deter | 100% | 106.50 | 335.10 | 99.80 | 98% | 6.95 | 48% | 40% | 113.0 / 115.0 | 95.8% |
| ppo_resid_v3_left_an6_s4 | 150000 | left | stoch | 100% | 131.66 | 346.83 | 84.55 | 86% | 7.70 | 48% | 36% | 114.0 / 118.3 | 98.6% |
| ppo_resid_v3_left_an7_s5 | 120000 | left | deter | 100% | 127.22 | 355.37 | 8.98 | 66% | 0.26 | 0% | 34% | 115.3 / 116.9 | 97.4% |
| ppo_resid_v3_left_an7_s5 | 120000 | left | stoch | 100% | 141.36 | 357.35 | 8.54 | 62% | 0.47 | 0% | 20% | 115.7 / 119.1 | 99.2% |
| ppo_resid_v3_left_an8_s6 | 120000 | left | deter | 100% | 75.60 | 359.26 | 11.43 | 82% | 0.10 | 0% | 0% | 118.5 / 119.2 | 99.3% |
| ppo_resid_v3_left_an8_s6 | 120000 | left | stoch | 100% | 82.61 | 366.34 | 11.50 | 80% | 0.85 | 6% | 10% | 118.2 / 121.0 | 100.8% |
| ppo_resid_v3_left_an9_s7 | 120000 | left | deter | 100% | 103.03 | 143.64 | 103.03 | 100% | 7.11 | 58% | 42% | 110.5 / 111.8 | 93.2% |
| ppo_resid_v3_left_an9_s7 | 120000 | left | stoch | 100% | 126.63 | 345.37 | 81.20 | 86% | 8.19 | 46% | 42% | 110.2 / 116.5 | 97.1% |
| ppo_resid_v3_left_an10_s8 | 120000 | left | deter | 100% | 128.80 | 324.46 | 109.97 | 94% | 5.67 | 50% | 32% | 107.0 / 108.4 | 90.3% |
| ppo_resid_v3_left_an10_s8 | 120000 | left | stoch | 100% | 126.19 | 334.03 | 57.13 | 78% | 6.40 | 38% | 24% | 107.4 / 112.8 | 94.0% |
| ppo_resid_v3_left_fast1_s10 | 100000 | left | deter | 100% | 22.54 | 360.36 | 15.34 | 98% | 0.02 | 0% | 0% | 122.2 / 122.4 | 102.0% |
| ppo_resid_v3_left_fast1_s10 | 100000 | left | stoch | 100% | 18.58 | 124.50 | 18.58 | 100% | 0.92 | 4% | 0% | 122.0 / 123.3 | 102.8% |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | 100000 | left | deter | 100% | 15.24 | 22.08 | 15.24 | 100% | 0.02 | 0% | 0% | 123.6 / 123.8 | 103.2% |
| ppo_resid_v3_left_fast2_s11/best_gate_flat_123mph | 100000 | left | stoch | 100% | 15.20 | 24.89 | 15.20 | 100% | 0.03 | 0% | 0% | 123.5 / 124.7 | 104.0% |

# Dispersion report

50 episodes/run, seeds 3000..3049. Tracker: `eval/flight_tracker.py` (minimal equivalent; no original found).
DTW columns: mean DTW distance (rad, lower=closer) of the Scott-trained policy trajectory to each reference swing; the non-Scott columns are PURE reference-style distances, not evidence the policy imitates that style.
Frame: x forward, +y = LEFT of target line, -y = RIGHT. Miss = final |y| > 0.5 m. Distance = final ball x (total, not carry). Contact = club-head/ball geom contact.

| Model | Mode | Contact | Mean dist (m) | Dist std | Median | Max | Mean y | Lateral std (m) | Left miss | Right miss | In corridor | Carry landed | Peak ball spd mean (m/s) | DTW Scott ref | DTW Rory | DTW Scheffler | DTW Average |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott | deterministic | 98% | 2.71 | 3.18 | 1.31 | 11.20 | -0.169 | 1.791 | 22% | 36% | 42% | 2% | 1.18 | 2.441 | 2.438 | 2.432 | 2.423 |
| ppo_scott | stochastic | 52% | 2.74 | 3.36 | 1.74 | 13.41 | +0.083 | 2.307 | 18% | 24% | 58% | 2% | 1.50 | 2.895 | 2.918 | 2.944 | 2.904 |
| ppo_scott_final2 | deterministic | 98% | 2.71 | 3.18 | 1.31 | 11.20 | -0.169 | 1.791 | 22% | 36% | 42% | 2% | 1.18 | 2.441 | 2.438 | 2.432 | 2.423 |
| ppo_scott_final2 | stochastic | 52% | 2.74 | 3.36 | 1.74 | 13.41 | +0.083 | 2.307 | 18% | 24% | 58% | 2% | 1.50 | 2.895 | 2.918 | 2.944 | 2.904 |
| ppo_scott_prev_backup | deterministic | 100% | 1.92 | 0.00 | 1.92 | 1.92 | +0.149 | 0.000 | 0% | 0% | 100% | 0% | 0.41 | 1.759 | 1.756 | 1.769 | 1.724 |
| ppo_scott_prev_backup | stochastic | 18% | 2.65 | 3.65 | 1.36 | 11.49 | -0.277 | 1.301 | 6% | 10% | 84% | 0% | 1.39 | 2.992 | 3.006 | 3.019 | 2.999 |

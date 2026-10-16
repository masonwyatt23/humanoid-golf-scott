# Dispersion report

50 episodes/run, seeds 2000..2049. Tracker: `eval/flight_tracker.py` (minimal equivalent; no original found).
Frame: x forward, +y = LEFT of target line, -y = RIGHT. Miss = final |y| > 0.5 m. Distance = final ball x (total, not carry). Contact = club-head/ball geom contact.

| Model | Mode | Contact | Mean dist (m) | Dist std | Median | Max | Mean y | Lateral std (m) | Left miss | Right miss | In corridor | Carry landed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott | deterministic | 100% | 1.92 | 0.00 | 1.92 | 1.92 | +0.149 | 0.000 | 0% | 0% | 100% | 0% |
| ppo_scott | stochastic | 18% | 2.65 | 3.65 | 1.36 | 11.49 | -0.277 | 1.301 | 6% | 10% | 84% | 0% |
| ppo_scott_curr | deterministic | 100% | 10.72 | 0.00 | 10.72 | 10.72 | +2.302 | 0.000 | 100% | 0% | 0% | 0% |
| ppo_scott_curr | stochastic | 24% | 3.36 | 3.64 | 2.07 | 15.51 | -0.081 | 1.064 | 6% | 10% | 84% | 0% |
| ppo_scott_baseline | deterministic | 0% | 0.30 | 0.00 | 0.30 | 0.30 | +0.000 | 0.000 | 0% | 0% | 100% | 0% |
| ppo_scott_baseline | stochastic | 0% | 0.56 | 1.66 | 0.30 | 7.90 | -0.011 | 0.395 | 2% | 4% | 94% | 0% |

# Leaderboard

**Current best model: ppo_scott / ppo_scott_carry1** (100000 steps) - mean true contact over det+stoch 82%, mean carry 0.170 m. Peak club-head speed (best single swing over det+stoch): 40.74 m/s = 91.1 mph = 75.9% of the 120 mph (53.64 m/s) target.

Ranking criterion: (1) true club-ball contact rate averaged over deterministic and stochastic modes, higher first; (2) ties broken by mean carry (m, averaged over both modes, mean over all episodes). Distance is not used.

Full ranking: ppo_scott > ppo_scott_prev_backup > ppo_scott_curr > ppo_scott_final2 > ppo_scott_baseline > ppo_resid_v3_s0 > ppo_resid_v3_r2_s0 > ppo_resid_v3_r3_s0

Peak club speed = max club_head linear speed over every physics substep of the swing, measured per episode (mean / max over episodes); mph = m/s x 2.23694; % of target = peak / 53.64 m/s (120 mph). Impact club speed = club_head linear speed at first club-ball contact; smash factor = peak ball speed / impact club speed (contact shots with club speed > 0.05 m/s, averaged).

Current env fingerprint `59bc5ea99d60` (v2 physics). 50 episodes, seeds 4000..4049. +y = left, miss = |final y| > 0.5 m. Distance = final ball x (total); carry = x at landing after flight, 0 if never landed (mean over all episodes). DTW = mean joint-trajectory DTW (rad) to each reference; non-Scott columns are pure reference-style distances.

| Model(s) | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak ball spd (m/s) | Impact club spd (m/s) | Smash | Peak club spd mean/max (m/s) | Peak club mph mean/max | % of 120 mph mean/max | DTW Mason best (11j / upper5) | DTW average | DTW rory | DTW scheffler | DTW scott |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | 30000 | deter | 0% | 0.30 | 0.30 | 0.000 | 0% | 0.000 | 0% | 0% | 0.71 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 7.07e+05 m/s) | 2.913 / 2.468 | 2.777 | 2.797 | 2.832 | 2.733 |
| ppo_scott_baseline | 30000 | stoch | 0% | 0.56 | 7.90 | 0.000 | 0% | 0.395 | 2% | 4% | 0.94 | nan | nan (n=0) | n/a | n/a | n/a (50 sim-unstable eps excluded; raw max 1.05e+06 m/s) | 8.203 / 6.609 | 11.003 | 11.026 | 11.398 | 10.701 |
| ppo_scott_curr | 30000 | deter | 100% | 3.01 | 3.01 | 0.000 | 0% | 0.000 | 0% | 0% | 0.77 | 0.58 | 1.32 (n=50) | 6.41 / 6.41 | 14.3 / 14.3 | 12.0% / 12.0% | 3.514 / 3.023 | 2.743 | 2.774 | 2.939 | 2.689 |
| ppo_scott_curr | 30000 | stoch | 34% | 5.04 | 13.90 | 0.062 | 6% | 2.628 | 18% | 18% | 2.83 | 2.65 | 0.96 (n=17) | 23.86 / 37.97 | 53.4 / 84.9 | 44.5% / 70.8% | 3.313 / 2.572 | 2.947 | 2.953 | 2.967 | 2.938 |
| ppo_scott_prev_backup | 30000 | deter | 100% | 2.76 | 2.76 | 0.000 | 0% | 0.000 | 0% | 0% | 0.94 | 0.95 | 0.99 (n=50) | 1.00 / 1.00 | 2.2 / 2.2 | 1.9% / 1.9% | 2.544 / 2.165 | 1.812 | 1.845 | 1.851 | 1.840 |
| ppo_scott_prev_backup | 30000 | stoch | 38% | 4.86 | 13.62 | 0.021 | 2% | 1.804 | 14% | 22% | 2.31 | 3.09 | 0.77 (n=19) | 23.37 / 42.55 | 52.3 / 95.2 | 43.6% / 79.3% | 3.318 / 2.563 | 2.952 | 2.952 | 2.956 | 2.942 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | deter | 48% | 1.80 | 9.80 | 0.091 | 16% | 0.980 | 14% | 10% | 0.69 | 0.17 | 15.91 (n=5) | 3.45 / 12.64 | 7.7 / 28.3 | 6.4% / 23.6% | 3.162 / 2.763 | 2.423 | 2.432 | 2.424 | 2.426 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | 60000 | stoch | 60% | 1.96 | 10.37 | 0.128 | 26% | 3.842 | 20% | 18% | 2.18 | 1.38 | 1.04 (n=11) | 22.70 / 33.43 | 50.8 / 74.8 | 42.3% / 62.3% | 3.261 / 2.520 | 2.869 | 2.887 | 2.879 | 2.880 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | deter | 98% | 0.47 | 0.59 | 0.102 | 20% | 0.062 | 0% | 0% | 0.50 | 0.10 | 1.51 (n=27) | 0.35 / 0.58 | 0.8 / 1.3 | 0.6% / 1.1% | 2.433 / 1.979 | 1.535 | 1.556 | 1.500 | 1.578 |
| ppo_scott<br>ppo_scott_carry1 | 100000 | stoch | 66% | 0.88 | 5.93 | 0.237 | 26% | 0.313 | 2% | 2% | 2.45 | 1.74 | 1.14 (n=14) | 25.78 / 40.74 | 57.7 / 91.1 | 48.1% / 75.9% | 3.104 / 2.332 | 2.676 | 2.687 | 2.701 | 2.673 |

- ['ppo_resid_v3_s0']: training config UNKNOWN, not evaluated.

- ['ppo_resid_v3_r2_s0']: training config UNKNOWN, not evaluated.

- ['ppo_resid_v3_s0']: training config UNKNOWN, not evaluated.

- ['ppo_resid_v3_r2_s0']: training config UNKNOWN, not evaluated.

- ['ppo_resid_v3_r3_s0']: training config UNKNOWN, not evaluated.

- ['ppo_resid_v3_s0']: training config UNKNOWN, not evaluated.

- ['ppo_resid_v3_r2_s0']: training config UNKNOWN, not evaluated.

- ['ppo_resid_v3_r3_s0']: training config UNKNOWN, not evaluated.

## DTW vs Mason's video references (all refs in docs/REFERENCE_PATHS.md; mean DTW rad: all 11 joints / upper-body 5 joints)

**CAVEAT: Mason references are 2D-proxy joint angles from MediaPipe landmarks of a single phone view (unknown angle), screen-recorded at ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak. Scores are INDICATIVE ONLY and say nothing about swing quality.**

Mapping: reference `joints` (degrees, 11 cols in the same order as env qpos[14:25]) -> radians; only `valid_mask` frames kept; policy trajectory = qpos[14:25] each env step; length-normalised DTW (tempo-tolerant). 'upper5' = joint cols 0-4 only (leg cols 5-10 unreliable). q = reference quality_score from the docs.

| Model(s) | Mode | part1_s05 (q=0.86) | part2_s01 (q=0.8) | part1_s02 (q=0.79) | part1_s06 (q=0.78) | part1_s03 (q=0.78) | part1_s04 (q=0.78) | part2_s05 (q=0.77) | part2_s02 (q=0.75) |
|---|---|---|---|---|---|---|---|---|---|
| ppo_scott_baseline | deter | 2.913 / 2.468 | 3.364 / 2.546 | 3.417 / 2.704 | 3.447 / 2.820 | 3.488 / 2.780 | 3.400 / 2.696 | 3.406 / 2.560 | 3.419 / 2.631 |
| ppo_scott_baseline | stoch | 8.203 / 6.609 | 8.636 / 6.817 | 11.880 / 9.415 | 10.763 / 8.588 | 10.802 / 8.519 | 10.584 / 8.397 | 11.519 / 9.111 | 9.145 / 7.227 |
| ppo_scott_curr | deter | 3.514 / 3.023 | 3.629 / 3.081 | 3.617 / 2.984 | 3.682 / 3.084 | 3.792 / 3.083 | 3.746 / 3.109 | 3.629 / 2.974 | 3.842 / 3.236 |
| ppo_scott_curr | stoch | 3.313 / 2.572 | 3.538 / 2.634 | 3.522 / 2.632 | 3.591 / 2.686 | 3.644 / 2.671 | 3.605 / 2.695 | 3.591 / 2.667 | 3.705 / 2.772 |
| ppo_scott_prev_backup | deter | 2.544 / 2.165 | 2.666 / 2.210 | 2.387 / 1.900 | 2.625 / 2.205 | 2.656 / 2.116 | 2.599 / 2.124 | 2.627 / 2.129 | 2.785 / 2.311 |
| ppo_scott_prev_backup | stoch | 3.318 / 2.563 | 3.561 / 2.596 | 3.557 / 2.652 | 3.685 / 2.786 | 3.692 / 2.721 | 3.647 / 2.746 | 3.739 / 2.841 | 3.736 / 2.755 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | deter | 3.162 / 2.763 | 3.466 / 2.898 | 3.110 / 2.644 | 3.339 / 2.891 | 3.377 / 2.830 | 3.331 / 2.824 | 3.215 / 2.684 | 3.547 / 2.979 |
| ppo_scott_final2<br>ppo_scott_prev2_backup | stoch | 3.261 / 2.520 | 3.508 / 2.538 | 3.491 / 2.582 | 3.610 / 2.696 | 3.629 / 2.644 | 3.587 / 2.638 | 3.655 / 2.680 | 3.666 / 2.696 |
| ppo_scott<br>ppo_scott_carry1 | deter | 2.433 / 1.979 | 2.853 / 2.066 | 2.218 / 1.593 | 2.548 / 1.994 | 2.592 / 1.886 | 2.528 / 1.866 | 2.503 / 1.801 | 2.850 / 2.129 |
| ppo_scott<br>ppo_scott_carry1 | stoch | 3.104 / 2.332 | 3.388 / 2.491 | 3.283 / 2.457 | 3.394 / 2.532 | 3.440 / 2.522 | 3.423 / 2.551 | 3.360 / 2.433 | 3.533 / 2.633 |

## Contact regressions (vs best earlier-trained checkpoint, same mode)

- ppo_scott_baseline [deterministic]: contact 0% < best previous 100% (ppo_scott(30k, old))
- ppo_scott_baseline [stochastic]: contact 0% < best previous 52% (ppo_scott_final2)
- ppo_scott_curr [stochastic]: contact 34% < best previous 52% (ppo_scott_final2)
- ppo_scott_prev_backup [stochastic]: contact 38% < best previous 52% (ppo_scott_final2)
- ppo_scott_final2/ppo_scott_prev2_backup [deterministic]: contact 48% < best previous 100% (ppo_scott_prev_backup)
- ppo_scott/ppo_scott_carry1 [deterministic]: contact 98% < best previous 100% (ppo_scott_prev_backup)

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
| ppo_scott_curr | 30000 | f0a3f737fc77 | 100% | 34% |
| ppo_scott_curr | 30000 | ae180bdc10a3 | 100% | 34% |
| ppo_scott_curr | 30000 | e9a0050d94b6 | 100% | 34% |
| ppo_scott_curr | 30000 | 9145629439d4 | 100% | 34% |
| ppo_scott_curr | 30000 | 25d5c5608c4d | 100% | 34% |
| ppo_scott_curr | 30000 | 59bc5ea99d60 | 100% | 34% |
| ppo_scott_prev_backup | 30000 | f0a3f737fc77 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | ae180bdc10a3 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | e9a0050d94b6 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 9145629439d4 | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 25d5c5608c4d | 100% | 38% |
| ppo_scott_prev_backup | 30000 | 59bc5ea99d60 | 100% | 38% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | f0a3f737fc77 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | ae180bdc10a3 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | e9a0050d94b6 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 9145629439d4 | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 25d5c5608c4d | 48% | 60% |
| ppo_scott_final2, ppo_scott_prev2_backup | 60000 | 59bc5ea99d60 | 48% | 60% |
| ppo_scott, ppo_scott_carry1 | 100000 | f0a3f737fc77 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | ae180bdc10a3 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | e9a0050d94b6 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 9145629439d4 | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 25d5c5608c4d | 98% | 66% |
| ppo_scott, ppo_scott_carry1 | 100000 | 59bc5ea99d60 | 98% | 66% |

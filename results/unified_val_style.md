# Style distance (DTW, rad) to unified_v1 VAL split

Val refs: 3 Mason (native left), 6 MultiSense (mirrored), 2 CMU (mirrored on load). 20 deterministic episodes/model, seeds 4000+. Lower = closer. Cells: all 11 joints / upper-body 5 joints.

**Caveats:** refs resampled 0.01->0.02 s to the sim control step (Data Agent timing audit; unresampled values in json); many ref angles exceed sim joint limits (see json joint_range); tiny val split; reference angles are uncalibrated proxies (Mason 2D MediaPipe; MultiSense amateur IMU; CMU slow recreational) not retargeted to the humanoid; DTW ignores tempo; not comparable with the earlier leaderboard DTW (different ref set); all sim rows use boosted actuators (force_scale 2 = HYPOTHETICAL ACTUATORS). Scripted rows are NOT learned. Magnitudes ~2 rad (mean per-frame distance over 11 joints) mean every row is FAR from every reference in joint space (the leaderboard's native-Mason DTW for ppo_v3flt_yaw_s31 is 2.34 on its own set, same order); learned and scripted v3 rows are within 0.003 rad of each other, i.e. no measurable style learning; an3/loft-7 rows are 'closer' mainly because their trajectories differ, not because they hit better.

| Model | Kind | mason | multisense | cmu |
|---|---|---|---|---|
| best_learned_yaw_s31 | LEARNED | 2.332 / 1.838 | 1.866 / 1.227 | 1.931 / 1.469 |
| ppo_v3flt_yaw_s32 | LEARNED | 2.332 / 1.838 | 1.866 / 1.228 | 1.931 / 1.470 |
| ppo_resid_v3_left_an3_s1 | LEARNED | 2.111 / 1.514 | 1.694 / 0.985 | 1.700 / 1.168 |
| ppo_resid_v3_left_fast2_s11 | LEARNED | 2.700 / 2.337 | 2.265 / 1.839 | 2.146 / 1.811 |
| fast v3 Stage 6 | SCRIPTED (not learned) | 2.338 / 1.846 | 1.870 / 1.232 | 1.935 / 1.475 |
| fast v2 lofted | SCRIPTED (not learned) | 2.534 / 2.112 | 2.051 / 1.485 | 2.104 / 1.698 |
| trainer cfg: left, loft 7 | SCRIPTED (not learned) | 2.351 / 1.847 | 1.929 / 1.317 | 1.900 / 1.434 |

## Per reference (all11)

| Model | mason_v2_p1_s06 | mason_v2_p1_s11 | mason_v2_p2_s01 | multisense_P20_s55_mirrored | multisense_P20_s76_mirrored | multisense_P20_s87_mirrored | multisense_P22_s108_mirrored | multisense_P22_s59_mirrored | multisense_P22_s60_mirrored | cmu_64_02 | cmu_64_06 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| best_learned_yaw_s31 | 2.054 | 2.671 | 2.271 | 2.025 | 1.980 | 1.802 | 1.747 | 1.824 | 1.818 | 1.935 | 1.926 |
| ppo_v3flt_yaw_s32 | 2.054 | 2.672 | 2.271 | 2.025 | 1.980 | 1.803 | 1.748 | 1.824 | 1.818 | 1.935 | 1.927 |
| ppo_resid_v3_left_an3_s1 | 1.876 | 2.411 | 2.047 | 1.836 | 1.787 | 1.659 | 1.586 | 1.654 | 1.644 | 1.675 | 1.725 |
| ppo_resid_v3_left_fast2_s11 | 2.203 | 3.331 | 2.565 | 2.486 | 2.356 | 2.246 | 2.099 | 2.196 | 2.207 | 2.141 | 2.150 |
| fast v3 Stage 6 | 2.059 | 2.678 | 2.276 | 2.028 | 1.983 | 1.805 | 1.751 | 1.828 | 1.822 | 1.940 | 1.930 |
| fast v2 lofted | 2.180 | 2.959 | 2.464 | 2.228 | 2.172 | 1.986 | 1.911 | 2.005 | 2.004 | 2.110 | 2.097 |
| trainer cfg: left, loft 7 | 2.011 | 2.797 | 2.244 | 2.100 | 2.021 | 1.898 | 1.797 | 1.878 | 1.876 | 1.884 | 1.916 |

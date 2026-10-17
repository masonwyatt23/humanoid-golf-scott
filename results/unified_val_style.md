# Style distance (DTW, rad) to unified_v1 VAL split

Val refs: 3 Mason (native left), 6 MultiSense (mirrored), 2 CMU (mirrored on load). 20 deterministic episodes/model, seeds 4000+. Lower = closer. Cells: all 11 joints / upper-body 5 joints.

**Caveats:** tiny val split; reference angles are uncalibrated proxies (Mason 2D MediaPipe; MultiSense amateur IMU; CMU slow recreational) not retargeted to the humanoid; DTW ignores tempo; not comparable with the earlier leaderboard DTW (different ref set); all sim rows use boosted actuators (force_scale 2 = HYPOTHETICAL ACTUATORS). Scripted rows are NOT learned. Magnitudes ~2 rad (mean per-frame distance over 11 joints) mean every row is FAR from every reference in joint space (the leaderboard's native-Mason DTW for ppo_v3flt_yaw_s31 is 2.34 on its own set, same order); learned and scripted v3 rows are within 0.003 rad of each other, i.e. no measurable style learning; an3/loft-7 rows are 'closer' mainly because their trajectories differ, not because they hit better.

| Model | Kind | mason | multisense | cmu |
|---|---|---|---|---|
| best_learned_yaw_s31 | LEARNED | 2.621 / 2.229 | 1.991 / 1.456 | 2.115 / 1.712 |
| ppo_v3flt_yaw_s32 | LEARNED | 2.621 / 2.229 | 1.991 / 1.456 | 2.115 / 1.712 |
| ppo_resid_v3_left_an3_s1 | LEARNED | 2.385 / 1.899 | 1.815 / 1.193 | 2.040 / 1.517 |
| ppo_resid_v3_left_fast2_s11 | LEARNED | 2.498 / 2.120 | 2.006 / 1.573 | 2.051 / 1.713 |
| fast v3 Stage 6 | SCRIPTED (not learned) | 2.622 / 2.232 | 1.990 / 1.455 | 2.113 / 1.710 |
| fast v2 lofted | SCRIPTED (not learned) | 2.606 / 2.227 | 2.003 / 1.476 | 2.083 / 1.705 |
| trainer cfg: left, loft 7 | SCRIPTED (not learned) | 2.429 / 1.979 | 1.899 / 1.331 | 2.044 / 1.591 |

## Per reference (all11)

| Model | mason_v2_p1_s06 | mason_v2_p1_s11 | mason_v2_p2_s01 | multisense_P20_s55_mirrored | multisense_P20_s76_mirrored | multisense_P20_s87_mirrored | multisense_P22_s108_mirrored | multisense_P22_s59_mirrored | multisense_P22_s60_mirrored | cmu_64_02 | cmu_64_06 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| best_learned_yaw_s31 | 2.160 | 3.235 | 2.468 | 2.185 | 2.116 | 1.956 | 1.826 | 1.930 | 1.933 | 2.122 | 2.107 |
| ppo_v3flt_yaw_s32 | 2.160 | 3.235 | 2.468 | 2.185 | 2.116 | 1.956 | 1.826 | 1.930 | 1.932 | 2.122 | 2.107 |
| ppo_resid_v3_left_an3_s1 | 2.084 | 2.759 | 2.312 | 1.992 | 1.940 | 1.788 | 1.668 | 1.754 | 1.749 | 2.058 | 2.021 |
| ppo_resid_v3_left_fast2_s11 | 2.081 | 2.997 | 2.417 | 2.203 | 2.112 | 1.976 | 1.855 | 1.943 | 1.946 | 2.056 | 2.047 |
| fast v3 Stage 6 | 2.159 | 3.243 | 2.466 | 2.183 | 2.115 | 1.954 | 1.825 | 1.929 | 1.932 | 2.120 | 2.105 |
| fast v2 lofted | 2.116 | 3.262 | 2.440 | 2.195 | 2.121 | 1.967 | 1.842 | 1.944 | 1.947 | 2.088 | 2.078 |
| trainer cfg: left, loft 7 | 2.055 | 2.905 | 2.328 | 2.082 | 2.016 | 1.871 | 1.751 | 1.840 | 1.837 | 2.049 | 2.038 |

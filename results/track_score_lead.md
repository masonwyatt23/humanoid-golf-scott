# track_score with track_arm=lead (SEPARATE from legacy; shoulder only, wrist excluded)

Trainer opt-in `track_arm='lead'` (commit 3b60369): Mason shoulder reference mapped to env left_shoulder_pitch. No lead-wrist joint exists, so the wrist part is not remapped and is excluded from `mean(sh,yaw)`. 10 det episodes, seeds 4000+, N small. Legacy columns in leaderboard.md stay VOID/UNVERIFIED.

| model | legacy sh | lead sh | yaw | legacy wr (trail wrist, not remapped) | lead mean(sh,yaw) | legacy mean(sh,yaw,wr) |
|---|---|---|---|---|---|---|
| imit2_w075_s51 | 0.001 | 0.010 | 0.148 | 0.007 | 0.079 | 0.052 |
| imit2_w075_s52 | 0.001 | 0.010 | 0.581 | 0.007 | 0.295 | 0.196 |
| imit2_w075_s53 | 0.001 | 0.010 | 0.169 | 0.005 | 0.089 | 0.058 |
| imit3_w075_s51 | 0.001 | 0.009 | 0.248 | 0.005 | 0.128 | 0.085 |
| imit3_w075_s52 | 0.001 | 0.009 | 0.494 | 0.003 | 0.252 | 0.166 |
| imit3_w075_s53 | 0.001 | 0.009 | 0.176 | 0.003 | 0.093 | 0.060 |
| imit3_w050_s51 | 0.001 | 0.009 | 0.194 | 0.004 | 0.102 | 0.067 |
| imit3_w025_s51 | 0.001 | 0.008 | 0.271 | 0.003 | 0.140 | 0.092 |
| imit3_w025_s52 | 0.001 | 0.008 | 0.042 | 0.001 | 0.025 | 0.015 |
| imit3_w000_s52 | 0.001 | 0.078 | 0.048 | 0.020 | 0.063 | 0.023 |
| imit4_w000_s52 | 0.001 | 0.004 | 0.010 | 0.002 | 0.007 | 0.004 |
| imit4_w000_s51 | 0.001 | 0.006 | 0.004 | 0.000 | 0.005 | 0.002 |
| imit5_w000_s52 | 0.001 | 0.038 | 0.132 | 0.010 | 0.085 | 0.048 |
| imit7_w000_s51 | 0.001 | 0.009 | 0.085 | 0.002 | 0.047 | 0.029 |
| imit8_w000_s51 | 0.001 | 0.004 | 0.028 | 0.000 | 0.016 | 0.010 |
| imit9_w000_s53 | 0.001 | 0.126 | 0.038 | 0.000 | 0.082 | 0.013 |
| imit10_w000_s51_tr | 0.994 | 0.001 | 0.335 | 0.000 | 0.168 | 0.443 |
| imit9_w000_s52 | 0.001 | 0.015 | 0.000 | 0.000 | 0.008 | 0.000 |
| imit13_w000_s51 | 0.002 | 0.003 | 0.080 | 0.001 | 0.042 | 0.028 |
| imit13_w000_s52 | 0.001 | 0.003 | 0.091 | 0.001 | 0.047 | 0.031 |
| imit14_w000_s51 | 0.900 | 0.178 | 0.051 | 0.453 | 0.114 | 0.468 |
| imit15_dart_s51 | 0.001 | 0.003 | 0.079 | 0.001 | 0.041 | 0.027 |
| imit16_fs1_dart_s51 | 0.001 | 0.038 | 0.081 | 0.054 | 0.060 | 0.045 |
| imit15_dart_s52 | 0.001 | 0.003 | 0.053 | 0.023 | 0.028 | 0.026 |
| imit15_dart_s53 | 0.001 | 0.003 | 0.392 | 0.005 | 0.198 | 0.133 |
| imit19_masonmapped_dart_s51 | 0.001 | 0.174 | 0.064 | 0.860 | 0.119 | 0.309 |
| imit18_power_dart_s51 | 0.002 | 0.203 | 0.054 | 0.000 | 0.129 | 0.019 |

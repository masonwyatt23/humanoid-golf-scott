# track_score with track_arm=lead (SEPARATE from legacy; shoulder only, wrist excluded)

Trainer opt-in `track_arm='lead'` (commit 3b60369): Mason shoulder reference mapped to env left_shoulder_pitch. No lead-wrist joint exists, so the wrist part is not remapped and is excluded from `mean(sh,yaw)`. 10 det episodes, seeds 4000+, N small. Legacy columns in leaderboard.md stay VOID/UNVERIFIED.

| model | legacy sh | lead sh | yaw | legacy wr (trail wrist, not remapped) | lead mean(sh,yaw) | legacy mean(sh,yaw,wr) |
|---|---|---|---|---|---|---|
| imit18_power_dart_s52 | 0.002 | 0.203 | 0.006 | 0.000 | 0.104 | 0.002 |
| ppo15_bcreg_s61 | 0.001 | 0.003 | 0.638 | 0.008 | 0.321 | 0.216 |
| ppo15_bcreg_s62 | 0.001 | 0.006 | 0.704 | 0.002 | 0.355 | 0.236 |
| ppo15_stoch_s71 | 0.001 | 0.005 | 0.627 | 0.003 | 0.316 | 0.210 |
| ppo15_anneal_s91 | 0.001 | 0.002 | 0.744 | 0.005 | 0.373 | 0.250 |

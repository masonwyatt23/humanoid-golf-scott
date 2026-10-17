# Strike regime: old vs fixed (verified, this evaluator)

Old vs fixed strike regime (results/strike_regime_rerun.md/.json).  python -m eval.strike_regime_rerun [--episodes 50] [--seed 4000]

What the 'fix' is (git 7da7be9 / ffc6271, results/TRAINING_NOTES.md 'Stage 5'): NOT an env-physics change but a CONFIG sign/offset fix for the v3 XML:
negative loft_deg = lofted face (positive loft closes the face), and ball_dz -0.01 puts the strike mid-face; the old configs (loft +7..+9, ball_dz +0.008)
struck the top/crown edge ('edge-strike', bimodal flat vs ~35 deg launch). Env code since c7ba7dd only added address-noise params (ball_y/sh/el noise, defaults unchanged),
yaw_ff, separation-velocity launch -> env fingerprint changed, leaderboard cache re-evaluated.

OLD  = the model with its own training config (leaderboard.json, same protocol).
NEW  = the SAME checkpoint run under the fixed regime: only loft_deg=-26 and ball_dz=-0.01 overridden (everything else = its training config). These policies were
       NOT trained under this regime -> out-of-distribution; this is a diagnostic, not a retrained model.

Protocol: 50 episodes/mode, seeds 4000+, flight tracker (MuJoCo ball, no spin), flat = launch < 5 deg. Scripted rows are zero-residual (det = stoch).

| Row | Kind | Mode | Contact | Carry m | Landed | Lat std m | Miss L/R | Launch deg (flat frac) | Peak mph mean/max |
|---|---|---|---|---|---|---|---|---|---|
| ppo_resid_v3_left_an3_s1 OLD regime (own config; loft 8.0, ball_dz 0.008) | LEARNED | det | 100% | 108.6 | 100% | 6.743 | 54/36% | 30.7 (2%) | 114.6/115.2 |
| ppo_resid_v3_left_an3_s1 OLD regime (own config; loft 8.0, ball_dz 0.008) | LEARNED | sto | 100% | 97.2 | 94% | 7.491 | 54/36% | 29.8 (10%) | 114.0/118.7 |
| ppo_resid_v3_left_an3_s1 NEW regime (loft -26, ball_dz -0.01; OOD) | LEARNED | det | 100% | 81.1 | 100% | 5.913 | 10/6% | 11.7 (4%) | 114.8/115.6 |
| ppo_resid_v3_left_an3_s1 NEW regime (loft -26, ball_dz -0.01; OOD) | LEARNED | sto | 100% | 87.2 | 100% | 7.656 | 14/24% | 11.1 (8%) | 114.1/117.3 |
| ppo_resid_v3_left_an2_s0 OLD regime (own config; loft 8.0, ball_dz 0.008) | LEARNED | det | 100% | 114.3 | 100% | 7.420 | 46/46% | 31.7 (0%) | 114.7/115.5 |
| ppo_resid_v3_left_an2_s0 OLD regime (own config; loft 8.0, ball_dz 0.008) | LEARNED | sto | 100% | 90.8 | 94% | 7.568 | 40/48% | 28.8 (14%) | 114.6/118.8 |
| ppo_resid_v3_left_an2_s0 NEW regime (loft -26, ball_dz -0.01; OOD) | LEARNED | det | 100% | 78.8 | 100% | 1.275 | 4/6% | 11.9 (2%) | 114.8/115.3 |
| ppo_resid_v3_left_an2_s0 NEW regime (loft -26, ball_dz -0.01; OOD) | LEARNED | sto | 100% | 89.9 | 100% | 4.289 | 24/14% | 11.6 (2%) | 114.8/118.5 |
| ppo_resid_v3_left_fast2_s11 OLD regime (own config; loft 9.0, ball_dz 0.008) | LEARNED | det | 100% | 15.2 | 100% | 0.017 | 0/0% | -5.8 (100%) | 123.6/123.8 |
| ppo_resid_v3_left_fast2_s11 OLD regime (own config; loft 9.0, ball_dz 0.008) | LEARNED | sto | 100% | 15.2 | 100% | 0.027 | 0/0% | -5.4 (100%) | 123.5/124.7 |
| ppo_resid_v3_left_fast2_s11 NEW regime (loft -26, ball_dz -0.01; OOD) | LEARNED | det | 100% | 33.8 | 80% | 0.069 | 0/0% | -0.5 (60%) | 123.5/123.9 |
| ppo_resid_v3_left_fast2_s11 NEW regime (loft -26, ball_dz -0.01; OOD) | LEARNED | sto | 100% | 28.4 | 86% | 0.119 | 0/2% | -3.5 (70%) | 123.4/124.7 |
| scripted fast OLD regime (loft +8, ball_dz +0.008, yaw_ff -3; trainer pre-fix cfg) | SCRIPTED (not learned) | det | 100% | 45.9 | 56% | 6.247 | 38/46% | 10.4 (64%) | 120.4/120.4 |
| scripted fast OLD regime (loft +8, ball_dz +0.008, yaw_ff -3; trainer pre-fix cfg) | SCRIPTED (not learned) | sto | 100% | 45.9 | 56% | 6.247 | 38/46% | 10.4 (64%) | 120.4/120.4 |
| scripted fast NEW regime (configs/fast_scripted_v2_lofted.json) | SCRIPTED (not learned) | det | 100% | 68.9 | 96% | 0.013 | 0/0% | 9.0 (8%) | 120.3/120.6 |
| scripted fast NEW regime (configs/fast_scripted_v2_lofted.json) | SCRIPTED (not learned) | sto | 100% | 68.9 | 96% | 0.013 | 0/0% | 9.0 (8%) | 120.3/120.6 |

| scripted fast v3 Stage 6 (configs/fast_scripted_v3.json; loft -31, ball_dz -0.008) | SCRIPTED (not learned) | det=stoch | 100% | 113.8 | 100% | 1.664 | 2/12% | 12.2 (0%) | 120.3/120.6 |

Scripted NEW trainer-reported (TRAINING_NOTES Stage 5, 100 eps, evaluator protocol): launch 9.3/9.5 deg, carry 70.0/71.9 m, landed 98/99%, lat std 0.013 m, 120.3 mph. Scripted OLD trainer-reported: launch mean 11.5, 62% flat, lat std 6.3 m, landed 58%, 120.4 mph.

Caveat: README numbers for LEARNED models stay valid ONLY for their own (old-regime) training config; the NEW-regime rows show what those frozen policies do under the fixed config, not retrained results.

Stage 6 v3 (row above, from results/leaderboard.json, same protocol): trainer-reported carry 113.0/110.6 m, launch 12.2, lat 2.12/1.60 m, landed 100%, 120.3 mph (100 eps, seeds 4000/8000).

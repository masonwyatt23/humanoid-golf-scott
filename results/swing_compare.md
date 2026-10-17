# Swing comparison: sim features vs Mason refs and published-stats profiles

20 deterministic episodes per model, seeds 4000+, evaluator protocol; medians over contact episodes. Feature definitions + caveats: docstring of `eval/swing_compare.py`. Generated 2026-10-17 01:20 (box time, America/New_York).

**Read this first:** (1) every learned/scripted row here is a boosted-actuator sim (force_scale 2 > 1 => HYPOTHETICAL ACTUATORS) so absolute speeds/tempo are not human-attainable evidence; (2) sim smash ~1.0 is a contact-model artifact; (3) sim X-factor is a chest-yaw proxy (pelvis fixed); (4) Mason features are 2D-video proxies, tempo +-15% at best, and Mason speed/launch/attack/X-factor are unavailable so are never scored; (5) published profiles are summary averages of populations, not any individual's swing; 'within' uses published range, or +-10% around a published point value (my tolerance choice).

## Feature medians (sim)

| Model | learned? | contact | tempo_ratio | backswing_s | downswing_s | takeaway_to_impact_s | wrist_minus_shoulder_s | elbow_minus_shoulder_s | torso_minus_hips_s | seq_proximal_to_distal | chest_yaw_top_deg | peak_club_mph | club_pre_mph | ball_speed_mph | smash | launch_deg | attack_deg | carry_yd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ppo_v3flt_yaw_s31 | LEARNED (PPO residual on scripted base) / hypothetical actuators | 20/20 | 5.17 | 0.62 | 0.12 | 0.74 | 0.06 | 0.03 | 0.01 | 0.00 | 0.05 | 120 | 120 | 122 | 1.01 | 12.68 | 2.65 | 119 |
| ppo_v3flt_yaw_s32 | LEARNED (PPO residual on scripted base) / hypothetical actuators | 20/20 | 5.17 | 0.62 | 0.12 | 0.74 | 0.06 | 0.03 | 0.02 | 0.00 | 0.01 | 120 | 120 | 122 | 1.01 | 12.68 | 2.65 | 119 |
| ppo_resid_v3_left_an3_s1 | LEARNED (PPO residual on scripted base) / hypothetical actuators | 20/20 | 5.18 | 0.65 | 0.12 | 0.77 | 0.05 | 0.02 | 0.02 | 0.00 | 0.30 | 115 | 115 | 82.89 | 0.72 | 29.68 | 4.62 | 117 |
| ppo_resid_v3_left_fast2_s11 | LEARNED (PPO residual on scripted base) / hypothetical actuators | 20/20 | 5.54 | 0.63 | 0.12 | 0.74 | 0.06 | 0.03 | -0.03 | 0.00 | 0.06 | 124 | 123 | 110 | 0.89 | -6.18 | 1.76 | 15.29 |
| fast v3 Stage 6 | SCRIPTED (not learned) / hypothetical actuators | 20/20 | 5.17 | 0.62 | 0.12 | 0.74 | 0.06 | 0.03 | 0.02 | 0.00 | 0.00 | 120 | 120 | 122 | 1.01 | 12.68 | 2.66 | 119 |
| fast v2 lofted | SCRIPTED (not learned) / hypothetical actuators | 20/20 | 5.50 | 0.66 | 0.12 | 0.78 | 0.06 | 0.03 | 0.02 | 0.00 | 0.00 | 120 | 120 | 121 | 1.00 | 10.78 | 2.66 | 80.11 |
| trainer cfg: left, loft 7 | SCRIPTED (not learned) / hypothetical actuators | 20/20 | 5.02 | 0.68 | 0.14 | 0.82 | 0.05 | 0.03 | 0.02 | 0.00 | 0.00 | 108 | 108 | 99.51 | 0.92 | 5.76 | 4.31 | 40.22 |

## vs Mason (target_features.json, v2 real-time clips; IQR of 11 swings)

| Model | feature | sim median | Mason median [IQR] | status |
|---|---|---|---|---|
| ppo_v3flt_yaw_s31 | tempo_ratio | 5.167 | 2.900 [2.875, 3.550] | above (1.78x median) |
| ppo_v3flt_yaw_s31 | backswing_s | 0.620 | 0.483 [0.483, 0.575] | above (1.28x median) |
| ppo_v3flt_yaw_s31 | downswing_s | 0.120 | 0.167 [0.158, 0.167] | below (0.72x median) |
| ppo_v3flt_yaw_s31 | wrist_minus_shoulder_s | 0.060 | 0.050 [0.035, 0.060] | within Mason IQR (1.20x median) |
| ppo_v3flt_yaw_s32 | tempo_ratio | 5.167 | 2.900 [2.875, 3.550] | above (1.78x median) |
| ppo_v3flt_yaw_s32 | backswing_s | 0.620 | 0.483 [0.483, 0.575] | above (1.28x median) |
| ppo_v3flt_yaw_s32 | downswing_s | 0.120 | 0.167 [0.158, 0.167] | below (0.72x median) |
| ppo_v3flt_yaw_s32 | wrist_minus_shoulder_s | 0.060 | 0.050 [0.035, 0.060] | within Mason IQR (1.20x median) |
| ppo_resid_v3_left_an3_s1 | tempo_ratio | 5.179 | 2.900 [2.875, 3.550] | above (1.79x median) |
| ppo_resid_v3_left_an3_s1 | backswing_s | 0.650 | 0.483 [0.483, 0.575] | above (1.34x median) |
| ppo_resid_v3_left_an3_s1 | downswing_s | 0.125 | 0.167 [0.158, 0.167] | below (0.75x median) |
| ppo_resid_v3_left_an3_s1 | wrist_minus_shoulder_s | 0.055 | 0.050 [0.035, 0.060] | within Mason IQR (1.10x median) |
| ppo_resid_v3_left_fast2_s11 | tempo_ratio | 5.545 | 2.900 [2.875, 3.550] | above (1.91x median) |
| ppo_resid_v3_left_fast2_s11 | backswing_s | 0.630 | 0.483 [0.483, 0.575] | above (1.30x median) |
| ppo_resid_v3_left_fast2_s11 | downswing_s | 0.115 | 0.167 [0.158, 0.167] | below (0.69x median) |
| ppo_resid_v3_left_fast2_s11 | wrist_minus_shoulder_s | 0.060 | 0.050 [0.035, 0.060] | within Mason IQR (1.20x median) |
| fast v3 Stage 6 | tempo_ratio | 5.167 | 2.900 [2.875, 3.550] | above (1.78x median) |
| fast v3 Stage 6 | backswing_s | 0.620 | 0.483 [0.483, 0.575] | above (1.28x median) |
| fast v3 Stage 6 | downswing_s | 0.120 | 0.167 [0.158, 0.167] | below (0.72x median) |
| fast v3 Stage 6 | wrist_minus_shoulder_s | 0.060 | 0.050 [0.035, 0.060] | within Mason IQR (1.20x median) |
| fast v2 lofted | tempo_ratio | 5.500 | 2.900 [2.875, 3.550] | above (1.90x median) |
| fast v2 lofted | backswing_s | 0.660 | 0.483 [0.483, 0.575] | above (1.37x median) |
| fast v2 lofted | downswing_s | 0.120 | 0.167 [0.158, 0.167] | below (0.72x median) |
| fast v2 lofted | wrist_minus_shoulder_s | 0.060 | 0.050 [0.035, 0.060] | within Mason IQR (1.20x median) |
| trainer cfg: left, loft 7 | tempo_ratio | 5.018 | 2.900 [2.875, 3.550] | above (1.73x median) |
| trainer cfg: left, loft 7 | backswing_s | 0.680 | 0.483 [0.483, 0.575] | above (1.41x median) |
| trainer cfg: left, loft 7 | downswing_s | 0.135 | 0.167 [0.158, 0.167] | below (0.81x median) |
| trainer cfg: left, loft 7 | wrist_minus_shoulder_s | 0.055 | 0.050 [0.035, 0.060] | within Mason IQR (1.10x median) |

## vs PGA Tour driver averages (TrackMan) + Tour Tempo

Sources (per number):

- `peak_club_mph` = 113: TrackMan PGA Tour driver averages as reproduced by Golf Monthly 'How Far PGA Tour Players Carry Their Drives' (https://www.golfmonthly.com/tour/how-far-pga-tour-players-carry-their-drives; numbers: Trackman) and the TrackMan tour-average table PDF (https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf) -- 'club speed' at impact; our peak substep club speed used as the proxy
- `ball_speed_mph` = 167: TrackMan PGA Tour driver averages as reproduced by Golf Monthly 'How Far PGA Tour Players Carry Their Drives' (https://www.golfmonthly.com/tour/how-far-pga-tour-players-carry-their-drives; numbers: Trackman) and the TrackMan tour-average table PDF (https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf)
- `smash` = 1.48: TrackMan PGA Tour driver averages as reproduced by Golf Monthly 'How Far PGA Tour Players Carry Their Drives' (https://www.golfmonthly.com/tour/how-far-pga-tour-players-carry-their-drives; numbers: Trackman) and the TrackMan tour-average table PDF (https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf) -- sim smash ~1.0 is a known contact-model artifact (smash_anomaly.md)
- `launch_deg` = 10.9: TrackMan PGA Tour driver averages as reproduced by Golf Monthly 'How Far PGA Tour Players Carry Their Drives' (https://www.golfmonthly.com/tour/how-far-pga-tour-players-carry-their-drives; numbers: Trackman) and the TrackMan tour-average table PDF (https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf)
- `attack_deg` = -0.9: TrackMan blog 'What is Attack Angle?' (https://www.trackman.com/blog/attack-angle) tour averages: PGA Tour driver -0.9 deg, LPGA Tour driver +2.8 deg -- older table (S_TM_GM) lists -1.3 deg; both published, we use the newer
- `carry_yd` = 282: TrackMan blog 'What Is Carry in Golf?' (https://www.trackman.com/blog/what-is-carry) tour averages: PGA Tour driver 282 yd, LPGA Tour driver 223 yd -- older table (S_TM_GM) lists 275 yd
- `tempo_ratio` = 3.0: J. Novosel, 'Tour Tempo' (2004) as reported in The Golf Wire press release 2006-05-03 (https://thegolfwire.com/105752-2/) and tourtempo.com/blogs/tips/what-the-numbers-mean: back:down ~3:1 (27/9 frames at 30 fps etc.); takeaway-to-impact 0.93-1.20 s for tour pros. Popular-book video analysis, not peer reviewed -- popular-book 3:1; arXiv single-pro measurement gives 2.8:1 (arXiv)
- `takeaway_to_impact_s` = (0.93, 1.2): J. Novosel, 'Tour Tempo' (2004) as reported in The Golf Wire press release 2006-05-03 (https://thegolfwire.com/105752-2/) and tourtempo.com/blogs/tips/what-the-numbers-mean: back:down ~3:1 (27/9 frames at 30 fps etc.); takeaway-to-impact 0.93-1.20 s for tour pros. Popular-book video analysis, not peer reviewed
- `chest_yaw_top_deg` = 42: Cheetham, Martin, Mottram, St Laurent (2001) 'The importance of stretching the X-Factor in the downswing of golf' (in Optimising Performance in Golf, ISBN 1 875378 37 5; reprinted J. Applied Golf Research 2011) via TPI article https://www.mytpi.com/articles/biomechanics/the-difference-between-x-factor-and-x-factor-stretch : 'TPI Tour average for X-Factor at pelvis transition is about 42 degrees' -- TPI figure is X-factor AT PELVIS TRANSITION (shoulder-minus-pelvis turn); our value is a chest-yaw proxy - NOT the same quantity, shown for context only
- qualitative `sequence_proximal_to_distal`: Cheetham, Rose, Neal, 'Comparison of Kinematic Sequence Parameters between Amateur and Professional Golfers' and Cheetham 'Kinematic Sequence: Transition and Downswing Phases' (http://sgpl.ch/Dokumente/Article-KinematicSequenceTransitionDownswing.pdf): pros peak pelvis -> thorax -> lead arm -> club, club still accelerating at impact; amateurs' mean arm peak occurs before mean thorax peak

| Model | peak_club_mph | ball_speed_mph | smash | launch_deg | attack_deg | carry_yd | tempo_ratio | takeaway_to_impact_s | chest_yaw_top_deg | n within / scored |
|---|---|---|---|---|---|---|---|---|---|---|
| ppo_v3flt_yaw_s31 | 120.43 (within) | 121.63 (below -19.1%) | 1.01 (below -24.1%) | 12.68 (above +0.7deg) | 2.65 (above +3.5deg) | 119.32 (below -53.0%) | 5.17 (above +56.6%) | 0.74 (below -20.4%) | 0.05 (below -99.9%, ctx) | 1/8 |
| ppo_v3flt_yaw_s32 | 120.43 (within) | 121.63 (below -19.1%) | 1.01 (below -24.1%) | 12.68 (above +0.7deg) | 2.65 (above +3.5deg) | 119.32 (below -53.0%) | 5.17 (above +56.6%) | 0.74 (below -20.4%) | 0.01 (below -100.0%, ctx) | 1/8 |
| ppo_resid_v3_left_an3_s1 | 114.83 (within) | 82.89 (below -44.9%) | 0.72 (below -45.7%) | 29.68 (above +17.7deg) | 4.62 (above +5.4deg) | 116.72 (below -54.0%) | 5.18 (above +56.9%) | 0.77 (below -16.7%) | 0.30 (below -99.2%, ctx) | 1/8 |
| ppo_resid_v3_left_fast2_s11 | 123.63 (within) | 109.74 (below -27.0%) | 0.89 (below -33.2%) | -6.18 (below -16.0deg) | 1.76 (above +2.6deg) | 15.29 (below -94.0%) | 5.54 (above +68.0%) | 0.74 (below -20.1%) | 0.06 (below -99.8%, ctx) | 1/8 |
| fast v3 Stage 6 | 120.44 (within) | 121.68 (below -19.0%) | 1.01 (below -24.1%) | 12.68 (above +0.7deg) | 2.66 (above +3.5deg) | 119.06 (below -53.1%) | 5.17 (above +56.6%) | 0.74 (below -20.4%) | 0.00 (below -100.0%, ctx) | 1/8 |
| fast v2 lofted | 120.44 (within) | 120.51 (below -19.8%) | 1.00 (below -24.7%) | 10.78 (within) | 2.66 (above +3.5deg) | 80.11 (below -68.4%) | 5.50 (above +66.7%) | 0.78 (below -16.1%) | 0.00 (below -100.0%, ctx) | 2/8 |
| trainer cfg: left, loft 7 | 107.85 (within) | 99.51 (below -33.8%) | 0.92 (below -30.6%) | 5.76 (below -4.0deg) | 4.31 (above +5.1deg) | 40.22 (below -84.2%) | 5.02 (above +52.1%) | 0.82 (below -12.3%) | 0.00 (below -100.0%, ctx) | 1/8 |

## vs LPGA Tour driver (TrackMan; only the numbers verified)

Sources (per number):

- `attack_deg` = 2.8: TrackMan blog 'What is Attack Angle?' (https://www.trackman.com/blog/attack-angle) tour averages: PGA Tour driver -0.9 deg, LPGA Tour driver +2.8 deg
- `carry_yd` = 223: TrackMan blog 'What Is Carry in Golf?' (https://www.trackman.com/blog/what-is-carry) tour averages: PGA Tour driver 282 yd, LPGA Tour driver 223 yd

| Model | attack_deg | carry_yd | n within / scored |
|---|---|---|---|
| ppo_v3flt_yaw_s31 | 2.65 (within) | 119.32 (below -40.6%) | 1/2 |
| ppo_v3flt_yaw_s32 | 2.65 (within) | 119.32 (below -40.6%) | 1/2 |
| ppo_resid_v3_left_an3_s1 | 4.62 (above +1.5deg) | 116.72 (below -41.8%) | 0/2 |
| ppo_resid_v3_left_fast2_s11 | 1.76 (below -0.8deg) | 15.29 (below -92.4%) | 0/2 |
| fast v3 Stage 6 | 2.66 (within) | 119.06 (below -40.7%) | 1/2 |
| fast v2 lofted | 2.66 (within) | 80.11 (below -60.1%) | 1/2 |
| trainer cfg: left, loft 7 | 4.31 (above +1.2deg) | 40.22 (below -80.0%) | 0/2 |

## vs Data Agent style profiles (data/references/pro_swing_profiles.json, schema pro_swing_profiles/v1, main a5df07b)

STYLE PROFILES = statistical summaries of published numbers (some from single shots / 30 fps video / search snippets), NOT simulations or claims about any person; internal labels only (names are file ids, do not use externally; legal review before any external use - see the file's legal_likeness_cautions).
Scoring: only features with a non-null target, `unverified` == false and confidence != none; weight high 1.0 / medium 0.6 / low 0.3 (my choice). Band = [min,max] if given else target +-10%. 'within' = confidence-weighted fraction of scored features inside the band; 'dev' = weighted mean |x-target|/half-band (0 = on target, 1 = band edge). Not scored: pelvis/thorax/X-factor/peak segment speeds (sim has no pelvis yaw; chest-yaw proxy only), spin (sim spin is ~60% high vs tour data: data/references/impact_physics_calibration.json), driving distance (total vs carry).
Sim rows are boosted actuators (HYPOTHETICAL ACTUATORS) with sim smash ~1.0 (contact artifact) and sim tempo ~5:1, so low scores reflect those, not 'style'. Mason's inputs to the Data Agent's comparison are Instagram screen recordings (~30 fps): tempo is a loose band, durations are unreliable (see docs/MASON_VS_PROFILES.md); Mason is not scored here.
Licensing note: reference MOTION data licences differ (data/references/mocap_dataset_licenses.json); only CMU (and 100STYLE, CC BY) are commercial-clean; Mason/MultiSense refs used for DTW/overlays here are internal diagnostics only.

| Model | adam_scott_style | bryson_dechambeau_style | chris_gotterup_style | rory_mcilroy_style | scottie_scheffler_style | tiger_woods_style | tour_average |
|---|---|---|---|---|---|---|---|
| ppo_v3flt_yaw_s31 | 29% within, dev 9.15 (n=5) | 0% within, dev 2.77 (n=3) | 0% within, dev 7.65 (n=2) | 100% within, dev 0.23 (n=1) | 100% within, dev 0.04 (n=1) | 25% within, dev 10.92 (n=7) | 17% within, dev 6.39 (n=8) |
| ppo_v3flt_yaw_s32 | 29% within, dev 9.15 (n=5) | 0% within, dev 2.77 (n=3) | 0% within, dev 7.65 (n=2) | 100% within, dev 0.23 (n=1) | 100% within, dev 0.04 (n=1) | 25% within, dev 10.92 (n=7) | 17% within, dev 6.39 (n=8) |
| ppo_resid_v3_left_an3_s1 | 0% within, dev 13.11 (n=5) | 40% within, dev 2.36 (n=3) | 0% within, dev 16.70 (n=2) | 100% within, dev 0.69 (n=1) | 100% within, dev 0.43 (n=1) | 0% within, dev 14.57 (n=7) | 17% within, dev 9.98 (n=8) |
| ppo_resid_v3_left_fast2_s11 | 0% within, dev 9.45 (n=5) | 0% within, dev 3.52 (n=3) | 0% within, dev 3.41 (n=2) | 100% within, dev 0.03 (n=1) | 100% within, dev 0.30 (n=1) | 12% within, dev 13.75 (n=7) | 17% within, dev 7.51 (n=8) |
| fast v3 Stage 6 | 29% within, dev 9.16 (n=5) | 0% within, dev 2.76 (n=3) | 0% within, dev 7.64 (n=2) | 100% within, dev 0.23 (n=1) | 100% within, dev 0.04 (n=1) | 25% within, dev 10.91 (n=7) | 17% within, dev 6.39 (n=8) |
| fast v2 lofted | 29% within, dev 9.57 (n=5) | 0% within, dev 2.78 (n=3) | 0% within, dev 7.67 (n=2) | 100% within, dev 0.23 (n=1) | 100% within, dev 0.04 (n=1) | 12% within, dev 11.72 (n=7) | 27% within, dev 6.25 (n=8) |
| trainer cfg: left, loft 7 | 0% within, dev 14.36 (n=5) | 40% within, dev 2.50 (n=3) | 0% within, dev 26.22 (n=2) | 0% within, dev 1.25 (n=1) | 0% within, dev 1.01 (n=1) | 0% within, dev 12.08 (n=7) | 17% within, dev 7.95 (n=8) |

Skipped per profile (reason): adam_scott_style: ball_speed_mph (null target), launch_angle_deg (null target), smash_factor (null target); bryson_dechambeau_style: launch_angle_deg (null target), smash_factor (null target), tempo_ratio (null target); chris_gotterup_style: attack_angle_deg (null target), launch_angle_deg (null target), smash_factor (unverified), tempo_ratio (null target); rory_mcilroy_style: tempo_ratio (unverified); scottie_scheffler_style: tempo_ratio (unverified); tiger_woods_style: attack_angle_deg (null target); tour_average: 

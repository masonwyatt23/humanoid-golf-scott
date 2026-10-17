# Course-mode score estimates: model-based estimate, not a real round (synthetic example course; assumed short game)

Synthetic example course (invented): par 72, 7380 yd. Monte Carlo, 2000 rounds per profile, seed 0.

| profile | mean score | vs par | sd | p10-p90 | fairways | GIR |
|---|---|---|---|---|---|---|
| A: sim as measured - ppo_v3flt_yaw_s31/best_learned_yaw_s31 | 106.7 | +34.7 | 4.8 | 101-113 | 100% | 1% |
| B: HYPOTHETICAL - ppo_v3flt_yaw_s31/best_learned_yaw_s31 spread scaled to 275 yd tour-avg carry | 93.7 | +21.7 | 10.9 | 80-109 | 98% | 31% |

Profile notes:
- A: sim as measured - ppo_v3flt_yaw_s31/best_learned_yaw_s31: ppo_v3flt_yaw_s31/best_learned_yaw_s31 (learned); force_scale=2.0; MuJoCo ball, smash~1.0 artifact; HYPOTHETICAL ACTUATORS
- B: HYPOTHETICAL - ppo_v3flt_yaw_s31/best_learned_yaw_s31 spread scaled to 275 yd tour-avg carry: carry CV 0.23 and lateral/carry 0.014 from ppo_v3flt_yaw_s31/best_learned_yaw_s31; roll from analytic model at TrackMan avg launch; not something the sim achieves

Assumptions (invented constants, see sim/course.py DEFAULTS): {"bag_fractions": [1.0, 0.92, 0.84, 0.77, 0.71, 0.65, 0.59, 0.53, 0.47, 0.4, 0.3], "rough_carry_mult": 0.85, "rough_disp_mult": 1.3, "bunker_carry_mult": 0.6, "bunker_disp_mult": 1.6, "green_radius_yd": 14.0, "chip_max_yd": 45.0, "ob_halfwidth_yd": 45.0, "max_strokes": 12, "chip_leave_sd_frac": 0.1, "chip_leave_min_ft": 4.0, "putt_scale_ft": 8.0, "putt_exp": 2.5}

Caveats: Gaussian dispersion (real/sim tails are heavier: the sim's lateral max was ~12 m), straight holes, fixed bag ratios, no wind, assumed putting/chipping. Profile A reflects the simulator as it is today (a ~120 yd driver); profile B is a what-if and is NOT achieved by any model.

# Course-mode score estimates: model-based estimate, not a real round (synthetic example course; assumed short game)

Synthetic example course (invented): par 72, 7380 yd. Monte Carlo, 2000 rounds per profile, seed 0.

| profile | mean score | vs par | sd | p10-p90 | fairways | GIR |
|---|---|---|---|---|---|---|
| A: sim as measured - best_imit_scriptfree_elbow48_s51/imit9_w000_s51 | 98.8 | +26.8 | 2.9 | 95-102 | 100% | 0% |
| B: HYPOTHETICAL - best_imit_scriptfree_elbow48_s51/imit9_w000_s51 spread scaled to 275 yd tour-avg carry | 76.6 | +4.6 | 6.0 | 70-85 | 100% | 54% |
| A: sim as measured - imit3_w050_s51 | 107.9 | +35.9 | 6.3 | 101-117 | 100% | 2% |
| B: HYPOTHETICAL - imit3_w050_s51 spread scaled to 275 yd tour-avg carry | 100.5 | +28.5 | 12.4 | 85-117 | 96% | 26% |
| C: STOCK motors (force_scale 1) gate-pooled 3 seeds - imit16_fs1_dart_s51 | 130.3 | +58.3 | 2.9 | 127-134 | 100% | 0% |
| C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - imit15_dart_s52 | 106.7 | +34.7 | 4.2 | 102-112 | 100% | 0% |
| C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - imit15_dart_s53 | 106.0 | +34.0 | 3.9 | 101-111 | 100% | 0% |
| C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - imit9_w000_s51 | 99.9 | +27.9 | 3.1 | 96-104 | 100% | 0% |
| C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - ppo_v4power_s61 | 93.4 | +21.4 | 10.2 | 80-108 | 82% | 23% |

Profile notes:
- A: sim as measured - best_imit_scriptfree_elbow48_s51/imit9_w000_s51: best_imit_scriptfree_elbow48_s51/imit9_w000_s51 (script-free imitation of the scripted v3 swing); force_scale=2.0; MuJoCo ball, smash~1.0 artifact; force_scale 2 (hypothetical-strength actuators)
- B: HYPOTHETICAL - best_imit_scriptfree_elbow48_s51/imit9_w000_s51 spread scaled to 275 yd tour-avg carry: carry CV 0.12 and lateral/carry 0.008 from best_imit_scriptfree_elbow48_s51/imit9_w000_s51; roll from analytic model at TrackMan avg launch; not something the sim achieves
- A: sim as measured - imit3_w050_s51: imit3_w050_s51 (blend 50% learned / 50% scripted); force_scale=2.0; MuJoCo ball, smash~1.0 artifact; force_scale 2 (hypothetical-strength actuators)
- B: HYPOTHETICAL - imit3_w050_s51 spread scaled to 275 yd tour-avg carry: carry CV 0.27 and lateral/carry 0.018 from imit3_w050_s51; roll from analytic model at TrackMan avg launch; not something the sim achieves
- C: STOCK motors (force_scale 1) gate-pooled 3 seeds - imit16_fs1_dart_s51: imit16_fs1_dart_s51 pooled over seeds [4000, 8000, 9000] x100 eps (det); force_scale=1.0 (stock motors); landed 100%; Gaussian approx of a heavy-tailed lateral distribution; MuJoCo ball (+analytic model for the power tier impact), roll 0
- C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - imit15_dart_s52: imit15_dart_s52 pooled over seeds [4000, 8000, 9000] x100 eps (det); force_scale=2.0 (hypothetical-strength actuators); landed 100%; Gaussian approx of a heavy-tailed lateral distribution; MuJoCo ball (+analytic model for the power tier impact), roll 0
- C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - imit15_dart_s53: imit15_dart_s53 pooled over seeds [4000, 8000, 9000] x100 eps (det); force_scale=2.0 (hypothetical-strength actuators); landed 100%; Gaussian approx of a heavy-tailed lateral distribution; MuJoCo ball (+analytic model for the power tier impact), roll 0
- C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - imit9_w000_s51: imit9_w000_s51 pooled over seeds [4000, 8000, 9000] x100 eps (det); force_scale=2.0 (hypothetical-strength actuators); landed 100%; Gaussian approx of a heavy-tailed lateral distribution; MuJoCo ball (+analytic model for the power tier impact), roll 0
- C: HYPOTHETICAL (force_scale 2, hypothetical-strength actuators) gate-pooled 3 seeds - ppo_v4power_s61: ppo_v4power_s61 pooled over seeds [4000, 8000, 9000] x100 eps (det); force_scale=2.0 (hypothetical-strength actuators); landed 100%; Gaussian approx of a heavy-tailed lateral distribution; MuJoCo ball (+analytic model for the power tier impact), roll 0

Assumptions (invented constants, see sim/course.py DEFAULTS): {"bag_fractions": [1.0, 0.92, 0.84, 0.77, 0.71, 0.65, 0.59, 0.53, 0.47, 0.4, 0.3], "rough_carry_mult": 0.85, "rough_disp_mult": 1.3, "bunker_carry_mult": 0.6, "bunker_disp_mult": 1.6, "green_radius_yd": 14.0, "chip_max_yd": 45.0, "ob_halfwidth_yd": 45.0, "max_strokes": 12, "chip_leave_sd_frac": 0.1, "chip_leave_min_ft": 4.0, "putt_scale_ft": 8.0, "putt_exp": 2.5}

Caveats: Gaussian dispersion (real/sim tails are heavier: the sim's lateral max was ~12 m), straight holes, fixed bag ratios, no wind, assumed putting/chipping. Profile A reflects the simulator as it is today (a ~120 yd driver); profile B is a what-if and is NOT achieved by any model.

# Speed-gap reward / target spec: stock ~100 mph -> ~120 mph club speed

Status: **model-only, published-biomechanics-only.** No Mason / Instagram-derived number appears here.
Data: `data/references/speed_gap_100_120_published.json`; code: `data/speed_gap_100_120.py`; test: `tests/test_speed_gap_100_120.py`.

## 1. Sources (tag = what was actually read)
| Source | Content | Tag |
|---|---|---|
| Cheetham et al., *Comparison of Kinematic Sequence Parameters between Amateur and Professional Golfers*, Science & Golf V ch.4. http://www.waddengolfacademy.com/biomechanics/Cheetham%20Rose%20Neal%20Comparison_of_Kinematic_Sequence.pdf | 19 amateurs (88 mph) vs 19 Tour pros (109 mph), Table 1 | **fetched, full text** |
| Chu, Sell, Lephart 2010, J Sports Sci. https://doi.org/10.1080/02640414.2010.507249 | 308 golfers; X-factor, delayed release, trunk tilt, weight shift predict ball speed | fetched abstract/snippets (qualitative) |
| Hume, Keogh, Reid 2005, Sports Med 35(5). http://www.waddengolfacademy.com/biomechanics/Hume%20Keogh%20Role%20of%20golf_biomechanics.pdf | pro peaks pelvis 498 / shoulder 723 / arm 1165 / club 2090 deg/s | **snippet only, unverified** |
| TPI linear kinematic sequence article; TPI Brennan article (mytpi.com) | qualitative sequence; one-player trunk anecdote | snippet only, unverified |
| Long-drive (120+ mph) per-segment studies | none found | **unsourced; no numbers given** |

## 2. Published peaks (deg/s) and derived 100/120 mph targets
| Segment | Amateur 88 mph | Pro 109 mph | k | ~100 mph (interpolated) | ~120 mph (**extrapolated**) | ratio 120/100 |
|---|---|---|---|---|---|---|
| Pelvis (yaw) | 395 | 477 | 0.88 | 442 | 519 | 1.174 |
| Thorax (yaw) | 583 | 727 | 1.03 | 665 | 803 | 1.207 |
| Lead arm (swing plane) | 763 | 980 | 1.17 | 886 | 1097 | 1.238 |
| Club (swing plane) | 1790 | 2254 | 1.08 | 2054 | 2500 | 1.217 |

Fit: `peak = peak_pro * (CHS/109)^k`, `k = ln(pro/amateur)/ln(109/88)`, from two group means with large SDs. 100 mph is interpolated and 120 mph is extrapolated, so all derived values are **unverified**.
Honest read: all segments scale roughly with club speed (k 0.9-1.2, differences within noise). The usual claim that proximal segments scale much less is not strongly supported by this data, so the spec uses ratios of about 1.17-1.24 for all segments. Treat 1.17 (pelvis) as a soft lower bound. The Hume 2005 pro values are within about 5-20% of Cheetham's pros (different segment definitions) and are not pooled.

Timing (pros, before impact; Cheetham): pelvis peak 87 ms (SD 19), thorax 68 ms (SD 14), lead arm 65 ms (SD 8); club peaks at impact. Order pelvis, thorax, arm, club. Every pro's pelvis decelerates before impact. Amateurs' mean order was pelvis, arm, thorax, with at least 2x the timing SD. Whether offsets change at 120 mph is not published here; keep them fixed.
X-factor (Chu 2010): more upper-torso/pelvis separation predicts ball speed; no numeric target is given (unsourced).

## 3. Mapping to env joints (read-only look at `env/g1_golf_env.py` actuator names)
`right_*` = trail arm, `left_*` = lead arm for both handednesses (`docs/HANDEDNESS.md`).
| Target | Env joint(s) | Note |
|---|---|---|
| Pelvis yaw speed | `pelvis_yaw` | direct |
| Thorax yaw speed | `pelvis_yaw` + `waist_yaw_joint` rates | waist joint rate is thorax relative to pelvis |
| Lead-arm speed | `left_shoulder_pitch_joint`, `left_shoulder_roll_joint`, `left_shoulder_yaw_joint` | use the norm of the three rates; pitch alone under-reads |
| Club speed | club angular speed from clubhead speed at impact; driven by `left/right_wrist_pitch_joint` | an outcome, not a joint |
`env/humanoid_golf_env.py` uses names without the `_joint` suffix (`right_shoulder_pitch`, `right_elbow`, `right_wrist`, `left_shoulder_pitch`, ...). Targets are deg/s; `qvel` is rad/s, so convert.

## 4. Reward-shaping terms (suggested; weights are untuned guesses)
With `T_seg(CHS) = pro_peak * (CHS/109)^k_seg` (`target_deg_s` in the module):
1. **Peak-speed term** (once per swing, end of downswing): `R_peak = w_peak * sum_seg -(e_seg^2) * (1 if e<0 else 0.25)`, `e = (peak - T)/(0.15*T)`, clipped to [-4, 0], `w_peak = 0.5`. The scale of 15% is conservative against the Cheetham pro SD/mean of 7-13%. Overshoot is penalised at 0.25x so the policy isn't pushed into unsafe speeds.
2. **Sequence bonus**: `+w_seq/3` for each adjacent pair (pelvis<thorax<arm<club) whose peak times are ordered with a gap of at least 5 ms, `w_seq = 1.0`; +0.5 if pelvis speed at impact < 0.8x its peak (all pros decelerated). Pros' gaps: pelvis to thorax about 19 ms, thorax to arm about 3 ms, so 5 ms is relaxed for thorax-arm.
3. **Speed-gap penalty**: `R_gap = -0.1 * max(0, CHS_target - CHS_now)/CHS_target` per downswing step. Curriculum: ramp `CHS_target` 100, 110, 120 mph.
4. Keep the existing joint-limit and torque penalties; do not raise tier limits just to hit the targets.

## 5. Not sourced
* Absolute segment speeds at 120 mph (extrapolated; the fastest published group is 109 mph).
* Long-drive per-segment data, X-factor degrees, and whether timing changes with speed.
* Cheetham's publication year, and Hume's table values (snippet only).

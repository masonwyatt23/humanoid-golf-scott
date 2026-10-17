# Is Mason's median address elbow over-flexed by camera angle?

Provenance: the Mason clips are derived from Mason's own screen-recorded social-media feed video; use of that data in a release needs Mason's consent (not yet given).

Data: `data/references/mason_elbow_camera_bias.json` (script `data/mason_elbow_camera_bias.py`, tests `tests/test_mason_elbow_camera_bias.py`). Everything here is **UNVERIFIED**: no ground-truth elbow angle, no camera calibration, n is tiny.

## Short answer
Probably **modestly over-flexed, but camera yaw is not the main reason**. The raw median is 29.1 deg (0.509 rad, 8 clips, IQR 23.0-30.4). My bias-corrected estimate is a centre of about **23.4 deg (0.41 rad), range 18.4-28.4 deg (0.32-0.50 rad)**, confidence **low**. The +/-5 deg half-width is an assumption, not a measurement.

## What the pipeline actually measures
`joints[:,2]` is `180 - angle(shoulder 12, elbow 14, wrist 16)` on MediaPipe **3-D world landmarks** (`data/process_video.py:167`), not a 2-D image angle. Recomputing it from the stored landmarks reproduces it (mason_v2_p1_s03: 31.2 vs 31.5 deg). World landmarks are metric but monocular, so the depth axis is model-prior driven. So three things could bias it: projection (only partly relevant), noise folding, and takeaway timing.

## 1. Camera view (heuristic labels, small n)
View labels come from the stored `view` field (shoulder/stance-width ratios; docs/MASON_VIDEO_REPORT.md; thresholds set by eye, not ground truth).

| View | Clips (unflagged native left) | Address elbow median (IQR) deg | xy-only (no depth) median deg |
|---|---|---|---|
| Down-the-line | 15 (7 in keyframe stats) | 28.9 (25.5-30.8); keyframe subset 29.4 | 24.6 |
| Oblique | 1 (mason_v2_p1_s06) | 22.3 | 18.5 |
| Face-on | 0 clean. Every face-on clip is flagged (right-handed detected or handedness unverified) and reads 2.7-12 deg | not usable | not usable |

The pool is essentially one view, so I **cannot test a view effect**. The one oblique clip is lower, but n=1. The face-on clips are near-straight, but their handedness is unresolved, so the 'right' arm in them may not be the lead arm.

## 2. 2-D projection bias, by simulation
Assumptions: orthographic camera; upper arm 0.29 m, forearm 0.25 m (measured on one clip's landmarks); upper arm hangs 0/10/20 deg forward of vertical; bend in one plane; yaw 0 = optical axis along the hinge axis (best view); a roll table varies elbow flare. Example (fwd 10 deg, true flexion 25 deg), projected 2-D flexion:

| camera yaw | 0 | 15 | 30 | 45 | 60 |
|---|---|---|---|---|---|
| 2-D flexion (deg) | 25.0 | 24.4 | 22.6 | 19.2 | 14.3 |

A pure 2-D read of an elbow hinge **under-states** flexion as the view turns away; the loss is 0.6 deg at 15 deg yaw, 2.5 at 30, 6 at 45 and 11 at 60. The sign is not guaranteed with flared elbows (roll table: 20 deg of roll gives 23.7 at yaw 0 and 24.9 at yaw 30). So **projection does not explain an over-read**. In the real data, dropping the depth axis lowers the reading by a median of 4.2 deg (IQR 3.7-5.9, n=16), so the model's depth axis adds flexion relative to the image plane. That is consistent with the 3-D landmarks being noisy and with the next effect.

## 3. Folding bias from landmark noise
An unsigned angle is biased upward when the true bend is small. With iid landmark noise (sigma is **assumed**; there is no ground-truth noise level), the simulated median bias at 25 deg true flexion is about +0.7 deg at 1 cm, +2.4 at 2 cm, +5.1 at 3 cm and +9.1 at 4 cm; it is larger at smaller true angles. Matching the raw 29.1 deg median to a true angle gives corrections of -0.6 / -2.1 / -5.1 deg for sigma 1 / 2 / 3 cm. I used the 2 cm value (-2.1 deg).

## 4. Takeaway before the time axis starts
`address_in_motion` is true for 6 of the 8 keyframe clips: the stored time axis starts after takeaway, so the first frame is not true address. The early-window mean exceeds the address value by a median 4.7 deg. Extrapolating the first-0.25 s elbow slope backward over the unobserved lead time gives per-clip corrections of -0.8 to -22 deg (median -3.6, heavily assumption-driven, linear). I clipped the correction to [-6, 0] and applied the median -3.6 deg.

## 5. Comparison with 3-D mocap
CMU address elbow (mirrored, 3-D) has a median 22.5 deg (IQR 21.6-23.8, n=10). Most MultiSense clips read 1-18 deg (22 below 18 deg). These are different golfers, joint-centre definitions and capture methods, so this is only a plausibility check. It says real address elbows are near-straight, in line with a corrected value below the raw 29 deg. MultiSense stays `needs_counsel`; only statistics are used.

## Recommendation
- **Bias-corrected address elbow:** centre about 23.4 deg (0.41 rad), range 18.4-28.4 deg (0.32-0.50 rad). Confidence **low**. This is raw 29.1, minus 2.1 (noise folding), minus 3.6 (takeaway in motion), and plus 0 for projection.
- The range's lower end sits just above the 0.31 rad failure floor from the seed-9000 report (not reproduced here).
- The earlier recommendation of a reset base near 27.5 deg is not contradicted but sits at the high end. Treat it as an upper-leaning choice.
- The decision is the Trainer's, and I touched nothing in `env/`, `eval/` or `train/`. The next real fix is a 240 fps face-on and DTL session with a launch monitor (docs/FILMING_PROTOCOL.md). A calibrated 3-D pose estimator (not monocular world landmarks) would settle the elbow.

## Not verified
Landmark noise level, true segment lengths, view labels, linear back-extrapolation, whether 3-D landmark flexion equals the humanoid's `right_elbow` hinge, and anything about face-on clips. Instagram-derived footage; third-party content unreviewed (docs/RELEASE_QUESTIONS_FOR_COUNSEL.md).

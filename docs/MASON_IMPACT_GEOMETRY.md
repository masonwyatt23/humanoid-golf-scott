# Mason impact-geometry diagnostics

Reproduce: `python -m data.mason_impact_geometry [--cmu-bvh data/raw_mocap/cmu]` -> `data/references/mason_impact_geometry_targets.json` (deterministic: no timestamps, bootstrap seed 0; tests `tests/test_mason_impact_geometry.py`). Without raw BVH the CMU comparison block is `"unavailable"`; the committed JSON was built with the BVH present.

## What this is, and what it is not
- **Hand path**, a **hand-forward / lead-arm-line lean proxy**, and a **hand low-point timing proxy** around the impact event, from single-view MediaPipe world landmarks of Mason's feed clips (~30 unique fps).
- **No club data exists.** Shaft lean is **unavailable**; only hand-forward and lead-shoulder->wrist line lean exist, and they are proxies for lag/lean, not shaft lean.
- **Launch angle is not derived and is not claimed.** It needs a launch monitor or club tracking. Dynamic loft, attack angle, club path, face angle, club/ball speed are all `"unavailable"` in the JSON.
- Everything is view-dependent (9 of 11 clips down-the-line, 1 oblique, 1 face-on). Use only `commercial_ok` data (Mason = self_owned, CMU = cmu_permissive with acknowledgment, synthetic).

## Method (short)
1. Selection = same as `mason_target_features.py` (11 recommended, commercial_ok, native-left v2 swings; mirrored copies excluded) plus the recommended native-left v3 slow-mo clip (`p2_s03`), reported per swing but kept out of the aggregate.
2. **Time alignment.** Stored landmarks are trimmed at the start, so frame 0 is not at `t_start_in_video`. The offset is recovered per file by cross-correlating wrist height with the stored `hands_px` track (all 12 clips: r >= 0.99; files with r < 0.9 would be rejected). Offsets: 0 s for p1_s06, p1_s11, p3_s09_unmirrored; ~0.40-0.47 s for most others (p2_s13: 0.15 s; slow-mo: 1.12 s).
3. Frame per swing: origin mid-hip, up = -y, `tgt` = address hip line (trail->lead hip) in the image-x/depth-z plane, `oth` perpendicular (sign arbitrary). Lengths in torso lengths (|mid-shoulder - mid-hip|). Hand = wrist midpoint (not the grip, not the club).
4. Features: hand height at address/top/impact; `low_point_t_minus_impact_s` = time of minimum hand height in [top, impact+0.20 s] minus the impact event; hand speed peak and its timing; 21-sample hand path takeaway->impact relative to the address hand position; hand-forward and arm-line lean vs address (only when >= 4 address frames exist, otherwise `"unavailable"`).
5. **Weights** (normalised): vertical/timing = quality_score x landmark coverage (views weigh 1.0); forward/lean = quality x coverage x view weight (face-on 1.0, oblique 0.6, DTL 0.4) x 1/(1+axis_std/20 deg) x *view-axis agreement* (does the inferred target axis match the labelled view?) and 0 when the address window is < 4 frames. quality_score is a ranking heuristic, not accuracy.
6. Uncertainty: timing +-~0.05 s (1 source frame on the impact event + 1 sample at 60 Hz; /slowdown for slow-mo); aggregates carry IQR, min/max, n_eff and a 90% bootstrap CI of the weighted median (sampling spread only, not bias).

## Key numbers (Mason v2, n=11; median [IQR]; CMU subject 64 n=10 true 3-D for comparison)
| quantity (torso units unless noted) | Mason | CMU | reliability |
|---|---|---|---|
| hand height at top (above mid-hip) | 1.25 [1.23, 1.37] (CI 1.22-1.42) | 1.51 [1.46, 1.54] | good (vertical) |
| hand height at impact event | 0.39 [0.34, 0.43] (CI 0.37-0.41) | -0.02 [-0.02, 0.00] | see "impact-event offset" |
| hand height at hand low point | -0.08 [-0.12, 0.09] | -0.02 [-0.02, -0.01] | good |
| low point minus impact (s; + = after) | +0.067 [0.067, 0.083] | +0.008 [0.008, 0.017] | +-0.05 s |
| low point as fraction of downswing | 1.40 [1.40, 1.53] | 1.02 | +-~0.3 (5-frame downswing) |
| peak hand speed (torso/s) | 12.9 [12.0, 15.2] | 8.9 [8.6, 9.4] | monocular, 30 fps: lower bound-ish |
| time of peak hand speed vs impact (s) | -0.017 [-0.017, 0.0] | -0.046 | +-0.05 s |
| hand-forward vs address at impact | -0.25 [-0.43, -0.15], **n=3** | -0.12 | low confidence |
| lead-arm line lean at impact (deg) | -58 [-61, -54] (11) | -8 | **do not use** (see below) |

Slow-mo `p2_s03` (oblique): low point +0.198 video-s (window edge) = ~+0.04 s real (slowdown 4.8x, uncertain 2x); not used in the aggregate. Synthetic references have no hand data (hand path/shaft proxy `"unavailable"`); their club-head vertical minimum sits ~0.19-0.20 s after impact by construction (planar model with no ground/ball), so it is only a sanity reference.

## Reading the numbers (honest)
- **Reward-ready (soft bands only):** hand height at top and at low point, low-point timing (about 0-0.1 s after the detected impact event), hand-height path (`hand_path.up_*`), peak hand speed. The JSON's `recommended_use` lists these.
- **Impact-event offset:** Mason's hands are still ~0.4 torso above hip level at the detected impact event, and only reach hip level ~0.07 s later; CMU's hands are at hip level at its impact event. Together with the peak hand speed occurring ~1 frame before the event, this suggests Mason's `t_impact` is ~1-3 frames (0.03-0.1 s) early (a 30 fps-detector heuristic), so prefer low-point-relative targets over absolute hand height at the event. This is a hypothesis, not a measurement.
- **Diagnostic only:** hand-forward/lean and `tgt`/`oth` path components. The inferred target axis disagrees with the labelled view for most DTL clips (monocular depth is model-prior-driven): only p1_s06 (oblique), p1_s11 (face-on) and p3_s09_unmirrored pass the view-axis agreement weighting, and only those three have an address window of >= 4 frames (others start after takeaway). The -58 deg lean is mostly depth/axis smear, not a measured lean; CMU's -8 deg is the true-3-D comparison.
- **Hand-forward is a lag/lean proxy, not shaft lean** and not an attack-angle or launch statement.

## Caveats
Single monocular view per clip (view-dependent everything); wrist midpoint, not grip; hands' low point is not the club's low point/divot; events are detector heuristics at ~30 fps; n is small; upright-camera assumption for "up"; CMU is a slow recreational volunteer (tempo ~1.7, acknowledgment text required, no standalone redistribution); no raw video in the JSON.

## Side finding: landmark/joint time offset in `mason_target_features`
`mason_v2_*` `time`/`joints` start at the first valid landmark frame, not at `t_start_in_video` (offset 0.40-0.47 s in most files). `data/mason_target_features.py` subtracts `t_start_in_video` from the events and then samples `joints` at those times, so the joint angles at top/impact (`joints_deg_at_top/impact`) and the sequencing peak times for files with a non-zero offset are read ~0.4 s too early. Tempo, backswing and downswing durations (event differences) are unaffected. Not changed here; fix = add the per-file offset (as in this script's `_align_offset`) before sampling.

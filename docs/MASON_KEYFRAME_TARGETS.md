# Mason keyframe tracking targets

Files: `data/mason_keyframe_targets.py` (builder, deterministic), `data/references/mason_keyframe_targets.json`, `tests/test_mason_keyframe_targets.py`.
Run: `python -m data.mason_keyframe_targets`. Read-only use of `env/` (code reading, nothing run, nothing edited). Everything below is **unverified**: joint angles are 2-D MediaPipe proxies from ~30 fps Instagram feed screen recordings, view-dependent, n = 8 clips.

## Clips used
Left-handed native footage, `unified_v2`, train/val, handedness-verified, not slow-mo: `p1_s03 p1_s04 p1_s05 p1_s06 p2_s01 p2_s02 p2_s11 p2_s13`.
Excluded: `mason_v2_p1_s11` (detected right-handed), `mason_v2_p2_s10` (unverified), `mason_v3_p2_s03_slowmo` (stretched time axis), all mirrored copies (not needed). The caption-flagged flip-edit `p3_s09_unmirrored` is stored per-clip in the JSON but kept out of every statistic. Views: 7 down-the-line, 1 oblique (p1_s06); no unflagged face-on clip exists.

## Keyframes (medians, suggested sigma = max(MAD-sigma, 8 deg floor); lead-arm/anatomical "right_*" columns)
| joint | address* | top | impact | finish |
|---|---|---|---|---|
| right_shoulder_pitch | 20.8 ± 8.0 | -64.7 ± 8.0 | -0.1 ± 8.0 | -83.8 ± 8.0 |
| right_elbow | 28.8 ± 8.0 | 47.8 ± 8.0 | 59.2 ± 8.3 | 94.1 ± 16.9 |
| right_wrist | 59.1 ± 8.0 | 13.9 ± 8.0 | 45.8 ± 8.0 | 24.5 ± 8.0 |
| left_shoulder_pitch | 27.0 ± 8.4 | -70.7 ± 8.7 | -12.1 ± 8.0 | 0.0 (zero-filled, do not use) |

Full 11-joint tables, IQR, min/max, tolerance bands (median ± 2 sigma), per-clip values, confidence and `unverified` flags are in the JSON. Notes:
- **Sigma is mostly the floor.** Across-clip MAD is under 8 deg for nearly every joint, so the 8 deg floor (pose noise and 30 fps quantisation) sets sigma. That says the clips are consistent, not that the angles are accurate.
- **Address is not a clean address.** The stored joint axis starts at the first landmark frame, ~0.4 s after `t_start_in_video`; in 6 of 8 clips the takeaway precedes the axis start (`address_in_motion`). Use address only as an initial-state prior, not a reward target.
- **Legs are low confidence**: `leg_valid_frame_ratio` is 0.2 to 0.6 and invalid rows are zero-filled/interpolated (note the 0.0 address values for right hip/knee). Give legs ~0 weight. Only 1 of 44 keyframe medians exceeds the env joint limits (left ankle at finish); the audit's 47/50 limit overrun comes from whole trajectories, mostly other sources.
- Shoulder roll is monocular-depth-driven: low confidence.
- Finish is a heuristic (arm-speed settle after impact).

## Timing
- Ratio band (backswing/downswing, video time): median 3.06, IQR 2.88 to 3.53, range 2.21 to 3.78 (n = 8). Per-swing relative uncertainty ~0.27 (downswing is 4 to 6 source frames). Absolute seconds (backswing ~0.45 s) are from edited or possibly sped-up clips and are not trustworthy; the JSON stores them but marks them so.
- Impact is landmark-inferred and **early** vs the hand low point by ~0.067 s (+-0.05). In sim, detect impact at the hand/club low point and subtract 0.067 s when matching these keyframes.
- Reference dt 0.01 s vs env control dt 0.02 s: index by simulated time/phase, never by env step (2x playback otherwise; `docs/REFSET_TIMING_AUDIT.md`).

## X-factor / pelvis-thorax proxy at top (low confidence, not a target)
Shoulder-line yaw change minus hip-line yaw change (address to top) from monocular world landmarks: median 7.8 deg (IQR 3.7 to 8.8, range 1.7 to 16.3, n = 8); shoulder turn 30 to 55 deg, hip turn 29 to 46 deg. These are far below real golf values (shoulder turn ~90 deg is commonly cited; unverified here), so the proxy is compressed by model-driven depth and view. Do not use it to set a reward; a real X-factor needs two-view 240 fps capture (`docs/FILMING_PROTOCOL.md`).

## Recommended reward form
Sparse keyframes (K = top, impact, finish; address excluded):
`r_key = (1/K) sum_k exp( - mean_j [ (q_j(t_k) - mu_jk) / (s sigma_jk) ]^2 )`, joints = arm columns 0, 2, 3, 4 first (shoulder roll and legs at weight ~0), `sigma_jk` from the JSON (8 to 17 deg), curriculum `s` from 2.0 down to 1.0 (below 1.0 the data does not support it).
Windowed dense tracking: `r_dense = exp( - mean_{t in event +-0.06 s, j} [ (q_j(t) - template_j(phi(t))) / (s sigma_j(phi)) ]^2 )` with the phase-normalised templates in the JSON (address-top 21 pts, top-impact 11, impact-finish 11). Total: `0.6 r_key + 0.4 r_dense`, scaled so its spread across policies is comparable to the carry/dispersion term. Events detected from the policy itself (top = lead-arm shoulder extreme, impact = hand low point minus 0.067 s, finish = arm settle), so the reward does not depend on the script timeline.

## Why track_score is ~0.07 to 0.09 (inferred from reading `env/residual_golf_env.py`, not run)
1. **Mason time offset ignored (confirmed numerically in the test).** `_load_track_shapes` computes Mason event indices as `t_top - t_start_in_video`, but the stored `time` axis starts ~0.4 s later. In 7 of 8 clips its "top" and "impact" land ~0.4 s late; at the env's "top" the lead-arm shoulder is at ~0 deg instead of the true -61 to -77 deg top. The Mason shoulder shape is therefore normalised against the wrong anchor. `data.mason_target_features.events_of` already applies the offset.
2. **Score scale.** `exp(-MSE/0.15)` on amplitude-normalised shapes: 0.08 means RMS shape error ~0.62 of the address-to-top amplitude, i.e. the shapes barely correlate; normalising by a small top excursion also inflates noise.
3. **Averaged heterogeneous shapes.** `yaw` and `wr` shapes come from MultiSense/CMU (different tempi, mirrored), averaged with weights, which blurs the reference; Mason contributes only the shoulder shape.
4. **Script-bound windows**: the policy window comes from script `t_hold/t_back/t_pause/t_down`, so the term mostly measures script vs mean shape, and the policy residual (4 dims, small `res_scale`) barely changes it.
5. Possible column mismatch: the shape uses `q[:, 1..3]` for sh/yaw/wr against reference columns from different conventions [unverified, not checked against the env's joint order].
6. Joint-limit mismatch (hip pitch +-60, ankle +-40 in `humanoid_golf.xml`) and 2x reference playback (dt 0.01 vs 0.02) per the timing audit make whole-trajectory tracking unreachable; keyframe-at-events avoids both.

## Not in this data
No club head, ball, force, face/path, true X-factor or sequencing; speeds are not derivable (120+ mph is self-reported). Re-capture per `docs/FILMING_PROTOCOL.md` before treating any of these as more than a prior.

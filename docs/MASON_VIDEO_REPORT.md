# Mason feed screen-recordings: swing extraction report

Generated 2026-10-16 from `data/mason_swings/mason_swing_part{1,2,3}.mov` (Mason's own Instagram feed,
phone screen recordings, HEVC 1180x2556 portrait, 60 fps nominal). Raw videos are git-ignored.

## What the recordings actually are
Not one-swing-per-file: each is a scroll through ~10-15 posts (part1 10 clips, part2 15, part3 13), each
a different short clip (2-14 s, many autoplay-looped) wrapped in Instagram UI (status bar, header, like/boost
rows). Different scenes, range/mat/backyard, different camera angles and subject sizes. Duplicate frames:
46% / 61% / 75% of frames (source clips are ~30 / 23 / 15 fps unique, recorded at 60). Timestamps are read
per frame from the container (variable-fps safe; max gap 18 ms, 33 ms once in part3).

## Pipeline (code)
- `data/swing_segmentation.py` - numeric core + tests (`tests/test_swing_segmentation.py`, 14 tests):
  video-tile finder for the dark UI, scroll/cut/duplicate-frame detection, stable spans, pose-jump (loop restart)
  detector, hand-speed swing detector (takeaway/top/impact/finish, tempo), loop de-duplication.
- `data/ingest_feed_recordings.py` - CLI: layout pass -> per-clip tight person crop -> MediaPipe PoseLandmarker
  (heavy `.task`, IMAGE mode) -> swing windows -> `process_video.process_landmarks` -> `<stem>_sNN.npz`.
  `--from-cache` re-segments saved tracks without re-running pose.
- `data/refine_swings.py` - second pass for chosen swings (best-of-3 detections per frame: tight crop, upscaled
  crop, whole tile; torso-consistency check; rolling-median outlier rejection; cut at pose jumps) ->
  `<stem>_sNN_refined.npz`; `--rejoint` recomputes joints from stored landmarks.
- `data/process_video.py` fixes: `key=` validity set (upper body is enough; legs flagged separately) and shoulder
  angle unwrap (smoothing across the +-180 wrap produced +-200 deg artefacts; 0 now = arm hanging).
- Environment: system lacked `libEGL.so.1` (MediaPipe tasks needs it, no root). I extracted `libegl1/libglvnd0/
  libgles2` debs into `/workspace/golf_scratch/libroot` and set `LD_LIBRARY_PATH`. Model:
  `pose_landmarker_heavy.task` (official storage.googleapis.com/mediapipe-models), in `/workspace/golf_scratch/`.
  HEVC decoded natively by OpenCV (no transcode needed).

## Swing counts (first pass, `data/references/mason_swing_partN_sNN.npz`, untracked)
| Video | Duration | Clips (spans) | Clips with swings | Swings kept | Rejected candidates |
|---|---|---|---|---|---|
| mason_swing_part1.mov | 70.97 s | 10 | 7 | 7 | 2 |
| mason_swing_part2.mov | 88.4 s | 15 | 5 | 5 | 6 |
| mason_swing_part3.mov | 111.96 s | 13 | 4 | 3 | 5 |
| **Total** | | | | **15** | |

## Per-swing quality (first pass)
`vfr` = frames with all 8 key landmarks >=0.5 vis; `legs` = knees+ankles visible; tempo = backswing:downswing (hand-speed peak as impact proxy).

| File | t in video (s) | tempo | mean vis | upper valid | legs | score | flags |
|---|---|---|---|---|---|---|---|
| mason_swing_part1_s05.npz | 37.29-39.97 | 3.5 | 0.784 | 0.795 | 0.575 | 0.79 | - |
| mason_swing_part2_s02.npz | 19.75-22.47 | 3.22 | 0.8 | 0.779 | 0.543 | 0.78 | - |
| mason_swing_part2_s05.npz | 81.52-83.48 | 2.9 | 0.774 | 0.619 | 0.538 | 0.74 | - |
| mason_swing_part1_s02.npz | 12.89-14.79 | 3.22 | 0.727 | 0.617 | 0.561 | 0.74 | - |
| mason_swing_part2_s01.npz | 14.8-17.67 | 3.0 | 0.767 | 0.74 | 0.188 | 0.73 | - |
| mason_swing_part1_s03.npz | 18.82-20.9 | 2.21 | 0.739 | 0.696 | 0.368 | 0.73 | - |
| mason_swing_part1_s04.npz | 26.32-28.44 | 2.55 | 0.72 | 0.622 | 0.298 | 0.69 | - |
| mason_swing_part1_s06.npz | 56.24-58.08 | 2.9 | 0.719 | 0.709 | 0.323 | 0.67 | little_address_before_takeaway |
| mason_swing_part2_s04.npz | 45.21-47.33 | None | 0.922 | 0.969 | 0.667 | 0.66 | tempo_out_of_range(0.09), little_address_before_takeaway, clipped_follow_through |
| mason_swing_part1_s01.npz | 2.67-4.2 | 1.4 | 0.854 | 0.87 | 0.717 | 0.65 | little_address_before_takeaway |
| mason_swing_part1_s07.npz | 61.72-64.18 | None | 0.829 | 0.905 | 0.405 | 0.60 | tempo_out_of_range(0.73), clipped_follow_through |
| mason_swing_part3_s03.npz | 55.31-56.68 | None | 0.72 | 0.817 | 0.088 | 0.52 | phase_too_short_for_tempo, clipped_follow_through |
| mason_swing_part3_s02.npz | 43.34-44.76 | None | 0.662 | 0.635 | 0.2 | 0.47 | tempo_out_of_range(0.47), clipped_follow_through |
| mason_swing_part3_s01.npz | 23.94-24.99 | None | 0.713 | 0.73 | 0.259 | 0.46 | phase_too_short_for_tempo, little_address_before_takeaway, clipped_follow_through |
| mason_swing_part2_s03.npz | 23.74-24.89 | 5.0 | 0.689 | 0.623 | 0.447 | 0.45 | little_address_before_takeaway, tracking_gaps_in_window |

## Refined swings (`*_refined.npz`, tracked in git)
| File | Frames | Score | Tempo | Mean vis | Upper valid | Legs | Outlier frac | Flags |
|---|---|---|---|---|---|---|---|---|
| mason_swing_part1_s02_refined.npz | 169 | 0.79 | 2.7 | 0.81 | 0.84 | 0.65 | 0.004 | - |
| mason_swing_part1_s03_refined.npz | 187 | 0.78 | 2.21 | 0.79 | 0.88 | 0.62 | 0.005 | - |
| mason_swing_part1_s04_refined.npz | 194 | 0.78 | 3.0 | 0.79 | 0.87 | 0.64 | 0.000 | - |
| mason_swing_part1_s05_refined.npz | 266 | 0.86 | 3.18 | 0.85 | 0.93 | 0.83 | 0.000 | - |
| mason_swing_part1_s06_refined.npz | 187 | 0.78 | 2.55 | 0.81 | 0.89 | 0.70 | 0.003 | little_address_before_takeaway |
| mason_swing_part2_s01_refined.npz | 261 | 0.80 | 3.1 | 0.81 | 0.92 | 0.57 | 0.002 | - |
| mason_swing_part2_s02_refined.npz | 232 | 0.75 | 3.33 | 0.83 | 0.94 | 0.68 | 0.004 | trimmed_at_pose_jump(19.55-22.47s) |
| mason_swing_part2_s05_refined.npz | 177 | 0.77 | 3.1 | 0.80 | 0.86 | 0.62 | 0.001 | - |
| mason_swing_part3_s02_refined.npz | 132 | 0.51 | - | 0.66 | 1.00 | 0.18 | 0.004 | tempo_out_of_range(0.47), clipped_follow_through |
| mason_swing_part3_s03_refined.npz | 154 | 0.61 | - | 0.75 | 1.00 | 0.34 | 0.006 | phase_too_short_for_tempo, clipped_follow_through |
(`Upper valid` in the refined table is measured after the stored landmarks were gap-filled, so it reads a little
higher than the first-pass column. `Legs` = fraction of frames with both knees and ankles visible >= 0.3.)

## Video ranking
| Rank | Video | Why |
|---|---|---|
| 1 | **part1** | Every post is a landscape tile with the full body visible (torso ~15-21% of tile height), tile found in 100% of frames, 7 swings kept (mean score 0.70, best 0.79 first pass / 0.86 refined), highest unique frame rate (~33 fps), no night scenes. Best single swing: `part1_s05` (refined 0.86). |
| 2 | **part2** | Same style of posts but a carousel swipe and several short/odd clips; tile found in 81% of frames, 5 swings kept (mean 0.67), 2 clips had no person detected / person intermittent, one "1/2" carousel overlay. `part2_s01` refined (0.80) is the second-best swing overall. |
| 3 | **part3** | Closest framing (torso 19-29% of tile; legs often cut off -> legs 0.1-0.3), mostly 1-2 s clips, ~15 fps unique frames (75% duplicates), a night/silhouette section where the dark-UI tile finder fails (tile found in only 46% of frames), 3 swings kept, none with a measurable tempo (mean score 0.48). |

## Issues found (be sceptical of the numbers)
- **UI overlays:** status bar, header, like/boost rows are cropped out by the tile finder; remaining overlays inside
  the tile (mute icon, `0:05` timer, `1/2` carousel badge) never overlapped a landmark in the sheets I viewed.
  Carousel swipes show a sliver of the next slide at the tile edge (visible in `part2_s04` end frames).
- **Tile finder is dark-UI based:** night/very dark footage (end of part3, ~92-111 s) is not recognised as a tile, so
  those swings were not processed. Fixing needs a layout model that does not rely on brightness.
- **Loops and edits:** many posts autoplay-loop or are edited; the swing window is cut at pose jumps so some
  windows start mid-backswing (`little_address_before_takeaway`) and the same swing seen twice is de-duplicated by
  trajectory similarity (threshold uncalibrated). Some clips look slow-motion; tempo *ratio* survives that, absolute
  durations do not.
- **Tempo reliability:** from ~30 fps (or 15 fps in part3) screen-recorded source frames, one frame = ~12-25% of a
  downswing, so tempo is +-15% at best; impact is approximated by peak hand speed. Tempo 1.4 (`part1_s01`) and 5.0
  (`part2_s03`) are implausible and should be ignored; `tempo_ratio` is NaN when out of 1-6 or phases < 0.1 s.
  Refined swings with tempo 2.2-3.3 are plausible for an amateur but not measured against ground truth.
- **View angle:** every clip is a single hand-held/tripod view of unknown angle (some look face-on, some DTL,
  some oblique); `view` is `unknown`. Joint angles are 2D-image-plane proxies built from MediaPipe world
  landmarks, so shoulder/wrist angles depend on the camera angle.
- **Handedness:** assumed right-handed (Mason); not verified per clip.
- **Small subject:** torso is 15-21% of tile height; tight-crop/upscale re-detection never beat whole-tile
  detection in the refinement stage (frames chosen: native crop 13-35, upscaled 0, whole tile 16-84 per swing),
  i.e. MediaPipe heavy already handles this size; the refinement gain came from outlier rejection, gap handling and
  choosing the best of three detections, not from upscaling.
- **Rejected candidates:** `no_backswing_before_peak` (loop jumps / partial motion), `hands_not_above_shoulder`
  (chips/waggles/short clips), `low_valid_frames` (< 60% upper-body tracked), and duplicates; see the JSON report.
- **Not verified:** I viewed skeleton overlays for 11 swings (first-pass sheets for 4, refined sheets for 5, none for
  part3); they tracked the golfer well. Hand-speed "impact" is not independently confirmed. No ground truth.

## Retargeting limits (honest)
These are Mason's swings (not Adam Scott), single view, 2D-proxy angles (0 = arm hanging along torso for shoulder
pitch; other joints are interior-angle proxies), no club/ball, no pelvis/thorax rotation, no roll/yaw. They are
suitable for sanity-checking tempo and gross joint ranges (compare against `joint_min/max`), not for direct
imitation of the MuJoCo humanoid without retargeting (WHAM/GVHMR + IK, see docs/WHAM_GVHMR.md). Frames-per-second
of the stored `joints` is 100 Hz after resampling from ~30 fps unique source frames.

## Output paths
- Refined (tracked): `data/references/mason_swing_part{1,2,3}_sNN_refined.npz` (10 files; see docs/REFERENCE_PATHS.md)
- First pass, all 15 swings (untracked): `data/references/mason_swing_partN_sNN.npz`
- Report JSON: `data/references/mason_feed_report.json`
- Scratch (not in git): `/workspace/golf_scratch/{cache,out2,refined,refined_debug,debug,dbg}` (pose tracks, skeleton sheets)

## Reproduce
```
export LD_LIBRARY_PATH=/workspace/golf_scratch/libroot/usr/lib/x86_64-linux-gnu   # if libEGL.so.1 is missing
source /workspace/golfvenv/bin/activate
python -m data.ingest_feed_recordings --model /workspace/golf_scratch/pose_landmarker_heavy.task \
    --cache-dir /workspace/golf_scratch/cache --debug-dir /workspace/golf_scratch/debug      # ~7 min
python -m data.refine_swings --report data/references/mason_feed_report.json \
    --video data/mason_swings/mason_swing_part1.mov --model /workspace/golf_scratch/pose_landmarker_heavy.task \
    --cache-dir /workspace/golf_scratch/cache --top 5
```
## Next
Film 20-50 two-view 240 fps swings (docs/MASON_SWINGS.md) or export original files from the phone (not feed
recordings): that fixes fps, view, tempo accuracy, and lets WHAM/GVHMR run properly.

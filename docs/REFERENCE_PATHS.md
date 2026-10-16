# Mason self-filmed reference paths

All files: `source=mason_self_filmed`, `is_synthetic=False`, `capture=screen_recording_of_social_feed`.
Layout = `ReferenceDataset` compatible: `joints (n,11) deg`, `dt=0.01`, `time`, `valid_mask`, plus
`landmarks (m,33,4)` (60 Hz world landmarks), tempo/timing fields and `quality_score` (0-1 heuristic).
Joints: col 0/4 shoulder "pitch" = 0 when the arm hangs along the torso (angle wrap fixed 2026-10-16).

**Caveats (all files):** single phone view of unknown angle (DTL vs face-on not labelled), screen-recorded
Instagram playback (re-encoded, ~30 fps unique frames), so tempo is +-15%; joint angles are 2D-proxy angles from
MediaPipe world landmarks, NOT retargeted/IK-solved to the MuJoCo humanoid; no club data; leg joints (cols 5-10)
are unreliable when `leg_valid_frame_ratio` < 0.6. Not Adam Scott style data: this is Mason's swing.

| Rank | Path | Frames (0.01 s) | Quality | Tempo (back:down) | Notes |
|---|---|---|---|---|---|
| 1 (best) | `data/references/mason_swing_part1_s05_refined.npz` | 266 | 0.86 | 3.2 | part1 @37-40 s, full address->finish, legs 0.83 tracked, no flags |
| 2 | `data/references/mason_swing_part2_s01_refined.npz` | 261 | 0.80 | 3.1 | part2 @14.6-17.9 s, legs only 0.57 tracked (leg joints weak) |
| 3 | `data/references/mason_swing_part1_s02_refined.npz` | 169 | 0.79 | 2.7 | part1 @12.7-15.0 s |
| 4 | `data/references/mason_swing_part1_s06_refined.npz` | 187 | 0.78 | 2.5 | part1 @56-58 s, little address before takeaway |
| 5 | `data/references/mason_swing_part1_s03_refined.npz` | 187 | 0.78 | 2.2 | part1 @18.6-21 s |
| 6 | `data/references/mason_swing_part1_s04_refined.npz` | 194 | 0.78 | 3.0 | part1 @26-28.6 s |
| 7 | `data/references/mason_swing_part2_s05_refined.npz` | 177 | 0.77 | 3.1 | part2 @81-84 s |
| 8 | `data/references/mason_swing_part2_s02_refined.npz` | 232 | 0.75 | 3.3 | part2 @19.6-22.5 s, trimmed at a loop jump |
| low | `mason_swing_part3_s02/s03_refined.npz` | 132/154 | 0.51/0.61 | none | close-up, legs cut off, no tempo - not recommended |

Quality score = 0.35 mean landmark visibility + 0.25 upper-body valid fraction + 0.15 leg-valid ratio
+ 0.15 plausible tempo (2-4.5) + 0.10 subject size - 0.05/flag. It ranks swings; it is not accuracy.
Rebuild: see docs/MASON_VIDEO_REPORT.md. Full per-swing table, issues and ranking: docs/MASON_VIDEO_REPORT.md. First-pass (unrefined) swings and the JSON report
are in the same folder (`mason_swing_partN_sNN.npz`, `mason_feed_report.json`); first-pass files are untracked.

# `mason_v2_p1_s11` handedness re-check

Result: **inconclusive; tag left unchanged (`handedness: left`, `handedness_verified: False`). Needs Mason's confirmation.** Not legal or identity proof; all of this is pose-landmark evidence.

## What could and could not be done
- The raw video (`mason_swing_part1.mov`, 68.0-70.4 s) is **not on this box** (`data/mason_swings/` holds only a README and a metadata example; no `.mov/.mp4` anywhere under `/workspace` for this project). No frames could be re-run. The check used the stored `landmarks` (115 x 33 x 4), `hands_px`, and the cue fields in the `.npz`.

## Evidence
| Cue | Value for p1_s11 | Points to |
|---|---|---|
| Lead-arm (straighter elbow at top) | L elbow 161 deg, R elbow 127 deg | right-handed (L = lead) |
| Finish (hands nearer which shoulder), ratio -0.13 (weak; threshold 0.08) | hands near anatomical-right shoulder | left-handed |
| Hands side at top (recorded, not voted) | left | unreliable face-on when torso turns |
| Earlier by-eye check (docs/MASON_VIDEO_REPORT.md) | rear foot heel-up on image right, target image-left | left-handed |
| Detector result | right, confidence 0.12 | essentially a coin flip |

Landmark-label sanity checks (new here): the anatomical R/L labels do **not** swap during the clip. The shoulder and ankle x-ordering is stable (right ankle stays image-left, shoulder dx is -0.27 at address and turns positive only through the finish as the torso rotates). So this is not a mid-clip left/right label flip. A person facing the camera with anatomical right on image-left is the normal non-mirrored view; a mirrored selfie view would not be detectable from pose (as the detector docstring says) and cannot be excluded.

## Reading
- A mid-clip label swap is ruled out by the landmark ordering.
- The lead-arm cue is the lone dissent. In face-on view the elbow angle comes from monocular depth-prone world landmarks (the straight/bent arm is judged along the camera axis), so it is plausibly a depth artifact. The other face-on or oblique clips (`p2_s05`, `p2_s08`, `p3_s08`) also read right on this cue and are either other golfers or flipped edits, so a systematic face-on bias in the lead-arm cue is possible but **[unverified]**.
- A mirrored-selfie or flipped-edit source cannot be ruled in or out without the video.
- Genuinely a different (right-handed) golfer cannot be ruled out; the finish cue is weak.

## Status of the tag
- Handedness stays `left`, `handedness_verified=False`. The manifest now carries `handedness_verified: false` and `needs_mason_confirmation: true` for this entry (and for `mason_v2_p2_s10`).
- It is in the **validation** split with training weight 0, so it cannot affect training; it only enters `eval/unified_style.py`. If Mason cannot confirm it is him and left-handed in that clip, remove it from the val split (note: `min_val_per_source` for Mason is 2; the other val swings are `p1_s06` and `p2_s01`).
- Ask Mason: watch part 1 at 68-70 s; is this you, is the target to the left of the frame, and was the clip flipped by the app?

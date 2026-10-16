# Mason target features

Reproduce: `python -m data.mason_target_features` -> `data/references/mason_target_features.json` (deterministic; tests: `tests/test_mason_target_features.py`).

**Selection (n=11):** `mason_v2_*.npz` with recommended, commercial_ok (self_owned), not partial, handedness left, native footage — 10 native files plus `mason_v2_p3_s09_unmirrored` (the un-mirrored copy of a flipped-edit clip, i.e. native left). All other mirrored copies excluded. Handedness is footage-verified for 9/11 (p1_s11 and p2_s10 rely on stated handedness).

## Key numbers (Mason, median [IQR])
| feature | value |
|---|---|
| tempo ratio (back/down) | 2.90 [2.88, 3.55], range 2.2–3.8 |
| backswing | 0.48 s [0.48, 0.58] |
| downswing | 0.17 s [0.16, 0.17] (4–6 source frames) |
| top as fraction of takeaway→impact | 0.74 [0.74, 0.78] |
| wrist peak speed, fraction of downswing | 0.94 [0.40, 1.15] (noisy) |
| wrist-minus-shoulder peak lag | +0.05 s [0.035, 0.06] (arm proxy only) |
| elbow_R at top / impact | 90° / 90° (IQR ±~18°, very view-dependent) |

Comparison (same script): CMU subject 64 (n=10): tempo 1.73 [1.64, 1.80], back 0.88 s, down 0.53 s, X-factor at top 34°, pelvis→thorax peak lag 0.15 s. Synthetic Scott (n=1, by construction): tempo 3.0, back 0.80 s, down 0.27 s, X-factor 55°, pelvis→thorax lag 0.03 s. MultiSense (right-handed, CC0) and all synthetic styles are also in the JSON.

## Unavailable for Mason (marked `"unavailable"`)
Pelvis turn, thorax turn, X-factor (top/max), pelvis/thorax peak-velocity timing, club head/speed, sway, wrist hinge. Mason sequencing uses arm joint angular-velocity peaks only (within top → impact+0.15 s).

## Quality weights
`weight = quality_score / (1 + tempo_rel_uncertainty)`, normalised to sum 1. quality_score is a heuristic ranking, not accuracy.

## Caveats (read before using as reward)
- Sources are ~30 fps feed screen-recordings; events ±1 frame (~33 ms). Mason's downswing is only ~5 frames, so per-swing tempo uncertainty is ~14–32% (median 27%) — the detected downswing may be too short; the aggregate is better but treat as ±15% at best. Use tempo as a loose band (about 2.5–3.5), not a sharp target.
- Joint angles are 2D image proxies from MediaPipe, view-dependent (mostly down-the-line; one oblique, one face-on), not humanoid-fitted. `right_*` = anatomical right = lead arm for a lefty.
- Cannot support speed targets: 120+ mph / 300+ yd is not derivable from this data.
- n=11, IQR is descriptive only. CMU is a slow recreational volunteer (acknowledgment text required; no standalone redistribution); Scott is synthetic (tempo 3.0 by construction); MultiSense legal sign-off pending.
- Provenance: Mason = self_owned, commercial_ok; no raw video in the JSON.

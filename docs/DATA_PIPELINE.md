# Data pipeline, provenance tags and licensing notes

Moved verbatim from the previous README. See also [REFERENCE_PATHS.md](REFERENCE_PATHS.md).

## Licensing & data provenance

- **GolfDB:** videos and annotations are research / non-commercial only. Not used in any recorded training run (`docs/GOLFDB_PLAN.md` is a plan). Do not use GolfDB-derived data commercially.
- **CMU Graphics Lab Motion Capture Database:** data from mocap.cs.cmu.edu; acknowledgment is required and the data may not be resold as a standalone dataset (`docs/CMU_MOCAP_GOLF.md`). It is reachable only through `--style_prior`, which is off in every recorded run.
- **MultiSenseGolf:** CC0 (`docs/research_open_data_v2.md`). Mirrored references exist; no recorded run uses them for training.
- **CaddieSet:** MIT licence on the data repo, but dataset consent and commercial terms are unvetted. Counsel is needed before any use. Only a summary JSON (`data/references/caddieset_driver_event_features.json`) is committed; no policy uses it.
- **Mason's own swings:** references in `data/references/mason_*` are derived from Mason's self-filmed / self-posted swings (`self_owned`). Raw videos are never committed. They are 2D-proxy angles from single-view video.
- **Synthetic references:** Scott/Scheffler/Rory styles are generated (`data/generate_synthetic_scott.py`); they are not Adam Scott's real data.
- Per-file tags and a table are in `docs/REFERENCE_PATHS.md`. This repository has no `LICENSE` file yet. Details of what trained each model: `docs/CHECKPOINT_RELEASE.md`.

## Data pipeline

Everything under `data/` turns raw sources into small `.npz` **reference swings** (and JSON summaries of them) that the imitation/reward code reads. Raw videos, raw mocap and trained models are never committed (see `.gitignore`).

```
 video (Mason feed screen-recordings)              mocap / open data                  procedural
   data/ingest_feed_recordings.py  (pass 1)          data/convert_cmu_mocap.py         data/generate_synthetic_scott.py
   data/refine_swings.py           (refined)         data/convert_multisense_golf.py   -> scott/scheffler/rory/average_swing.npz
   data/remine_feed_v2.py          (mason_v2_*)      data/convert_caddieset.py (JSON only)
   data/remine_slowmo_v3.py        (mason_v3_*)      data/download_puregolf_proxy.py (catalog + opt-in downloader)
   data/audit_feed_cadence.py      (fps audit)                    |
              \                                                  |
               +--> data/references/*.npz  <----------------------+
                       |  data/provenance.py + data/tag_provenance.py  (license tags)
                       |  data/mirror_references.py                    (left/right mirrored copies)
                       v
        data/mason_target_features.py     -> data/references/mason_target_features.json    (tempo, durations, sequencing, ranges)
        data/mason_impact_geometry.py     -> data/references/mason_impact_geometry_targets.json (hand path, hand-forward/lag proxy, low-point timing)
                       |
                       v
        imitation/reference_dataset.py  ReferenceDataset(dir, commercial_only=...)  -> env / train / eval
```

## What each script does

| Script | Purpose |
|---|---|
| `data/process_video.py` | Core pose pipeline (MediaPipe Pose): landmarks -> gap-fill -> smoothing -> 11 joint angles (deg) at `dt=0.01` + `landmarks (n,33,4)` world landmarks. Used by all video ingesters. |
| `data/ingest_feed_recordings.py` | Mason's phone screen-recordings of a social feed (several posts per file): finds the video tile, splits into swings, writes `mason_swing_partN_sNN.npz` (first pass, **untracked/ignored**) + `mason_feed_report.json`. |
| `data/refine_swings.py` | Second, higher-quality pose pass (tight crop, outlier rejection) on the best swings -> `*_refined.npz` (tracked). |
| `data/remine_feed_v2.py` | Layout-agnostic re-mining of the same recordings -> `mason_v2_*.npz` with `view` (down_the_line / oblique / face_on), footage-checked handedness, `recommended`, `quality_score`. |
| `data/remine_slowmo_v3.py`, `data/audit_feed_cadence.py` | Frame-rate audit (every window is ~30 unique fps; no 60 fps) and the few verified slow-motion swings -> `mason_v3_*_slowmo.npz`. |
| `data/convert_cmu_mocap.py` | CMU subject 64 BVH -> 10 reference swings (`cmu_64_NN.npz`) incl. pelvis/thorax rotation, X-factor, sway; **no club data**. Raw BVH is gitignored (`data/raw_mocap/cmu/`; see `docs/CMU_MOCAP_GOLF.md`). |
| `data/convert_multisense_golf.py` | MultiSenseGolf (Harvard Dataverse, CC0) -> `multisense_P??_s??.npz` (right-handed, ~89-103 mph club speed; legal sign-off on commercial use still pending). |
| `data/convert_caddieset.py` | CaddieSet event features -> `caddieset_driver_event_features.json` (a diagnostic prior, not a swing reference). |
| `data/generate_synthetic_scott.py` | Parametric Scott / Scheffler / Rory / average caricatures with analytic `club_head` (not measured data). |
| `data/mirror_references.py` | Adds `*_mirrored.npz` copies (`mirrored=True`, original handedness recorded). Mirroring twice returns the original. |
| `data/provenance.py`, `data/tag_provenance.py` | Define and retro-apply the license tags below (idempotent). |
| `data/mason_target_features.py` | Per-swing + aggregate tempo, durations, sequencing, joint ranges from Mason's 11 recommended native-left v2 swings, with CMU/synthetic comparison -> `mason_target_features.json` (`docs/MASON_TARGET_FEATURES.md`). |
| `data/mason_impact_geometry.py` | Impact-geometry **diagnostics**: hand path in a body-relative frame, hand-forward / lead-arm-lean proxies (shaft lean is NOT measured), hand low-point timing; view- and quality-weighted with uncertainty -> `mason_impact_geometry_targets.json` (`docs/MASON_IMPACT_GEOMETRY.md`). Never a launch angle. |
| `data/download_puregolf_proxy.py`, `data/process_mason_swings.py`, `data/real_swing_dataset.py`, `data/ingest_mason_swings.py` | Earlier/auxiliary tools: source catalog + opt-in downloader (needs `--i-have-reviewed-tos`), the original Mason video processor, GolfDB scaffolding, and a single-video Mason ingester. |

The two target-feature scripts are deterministic (no timestamps, fixed bootstrap seed) and re-run with `python -m data.mason_target_features` / `python -m data.mason_impact_geometry`.

## Reference file format

`time (n,)`, `dt` (0.01 s), `joints (n,11)` in degrees (layout in `data/process_video.py`; `right_*` = anatomical right limbs), optionally `joints_rad`, `club_head` (synthetic only), `pelvis_rot_deg`, `thorax_rot_deg`, `x_factor_deg`, `lateral_sway_m`, `landmarks (m,33,4)` (Mason; 60 Hz, hip-centred world coordinates), events (`events` or `t_takeaway/t_top/t_impact`), plus metadata. **Mason files have no club data, no pelvis/thorax rotation and no sway**; joint angles are 2D image proxies from a single view and are not retargeted to the MuJoCo humanoid.

## License / provenance tags and `commercial_only`

Every reference `.npz` carries `license_class` (`synthetic`, `self_owned`, `cmu_permissive`, `cc0`, `noncommercial`, `unknown`), `commercial_ok`, `provenance_source`, `provenance_note`, `acknowledgment_required`, `acknowledgment_text`. Unidentified data is tagged not-commercial. Per-file table: `docs/REFERENCE_PATHS.md`. Only CMU (acknowledgment required, no standalone redistribution), synthetic, Mason's own footage and CC0 MultiSenseGolf are commercial-eligible; GolfDB and AMASS are excluded.

`ReferenceDataset(dir, commercial_only=True)` skips any file whose `commercial_ok` is false. It is **opt-in and defaults to `False`**: `env/`, `train/` and `eval/` do not currently pass it, and the default `*.npz` glob also picks up the `_mirrored` copies and the Mason first-pass/v2/v3 variants (duplicates of the same swings), so select by field (`recommended`, `mirrored`, `native_footage`, `partial`) rather than a filename pattern.

## Handedness and mirroring

Mason is left-handed. Files record `handedness` (and for v2/v3 `handedness_stated`, `handedness_detected`, `handedness_verified`): 18 clips read left-handed from the footage itself, a few right-handed clips are other golfers on the feed (flagged not commercial-safe), and one clip is a flipped edit that also has an `_unmirrored` copy. `data/mirror_references.py` writes `*_mirrored.npz` (joints with left/right columns and roll sign swapped, landmark x negated and left/right indices swapped, `mirrored=True`, original handedness recorded, tags copied) so right-handed sources (CMU, MultiSenseGolf, synthetic) can drive the left humanoid. Conventions in `docs/HANDEDNESS.md`. The target-feature scripts use only native left clips and compute lead/trail-defined (handedness-invariant) quantities.

## Known limits

- Mason data are ~30 unique fps screen-recordings of Instagram playback: events are good to about +-1 frame (33 ms), a normal-speed downswing is only ~5 frames, per-swing tempo is uncertain by roughly 14-32%. Use tempo as a loose band (about 2.5-3.5).
- One camera view per clip (mostly down-the-line), so joint angles and all geometry are view-dependent; depth is the weakest axis.
- No club, ball, launch or force data for Mason. 120+ mph / 300+ yd cannot be derived from these files; launch angle needs a launch monitor or club tracking.
- CMU subject 64 is a slow recreational volunteer (tempo ~1.7); MultiSenseGolf swings are right-handed, ~90-103 mph; synthetic swings are caricatures.
- Landmarks are trimmed at the start of each file, so their time axis is offset from `t_start_in_video` (the impact-geometry script realigns it per file by cross-correlation; see `docs/MASON_IMPACT_GEOMETRY.md`).
- The biggest data upgrade is 20-50 swings filmed at 240 fps from face-on and down-the-line, original phone files (no re-encoding).

## Adding new data

1. Put raw videos/mocap in the gitignored raw folders (`data/mason_swings/`, `data/raw_videos/`, `data/raw_mocap/`); check the license first (`docs/NEXT_DATA_SOURCES.md`, `data/download_puregolf_proxy.py`).
2. Convert with the matching script (or `data.process_video` for generic video; WHAM/GVHMR for production quality, `docs/WHAM_GVHMR.md`) and write the `.npz` to `data/references/`.
3. Tag it: new converters call `data/provenance.py` automatically; otherwise run `python -m data.tag_provenance` (unknown stays `commercial_ok=False`). Record `handedness`, `view` and quality fields for real footage.
4. For a left-handed golfer from right-handed data run `python -m data.mirror_references`; never edit originals.
5. Regenerate the summaries (`python -m data.mason_target_features`, `python -m data.mason_impact_geometry`), update `docs/REFERENCE_PATHS.md`, run `pytest tests`.
6. Commit the small `.npz`/JSON files only (no raw video, BVH, logs or checkpoints).

## Extending with Real PureGolf Content

1. See `python -m data.download_puregolf_proxy` (lists sources + licensing notes; downloads need `--download --i-have-reviewed-tos`; most footage is copyrighted).
2. Place permitted videos in `data/raw_videos/` (gitignored).
3. Run `python -m data.process_video [--capture-fps 250]` (resumable, gap-filling, smoothing).
4. For production quality use WHAM or GVHMR, see `docs/WHAM_GVHMR.md`; save `.npz` to `data/references/`.

5. The ReferenceDataset automatically loads them.

See `docs/NEXT_DATA_SOURCES.md` for the ranked list of real data sources. Tests: `pytest tests`.

## Data licensing notes

- **GolfDB videos are not licensed for commercial use** (research/non-commercial only). Use GolfDB-derived data only for non-commercial research; see `docs/GOLFDB_PLAN.md`.
- **CMU mocap-derived files** (`data/references/cmu_*.npz`) require acknowledgment of the CMU Graphics Lab Motion Capture Database, and may not be resold as a standalone dataset. See `docs/CMU_MOCAP_GOLF.md`.
- Every reference `.npz` carries `license_class` / `commercial_ok` tags; the per-file license column is in `docs/REFERENCE_PATHS.md`.
- Raw videos and footage (including Mason's self-filmed swings) are never committed: `*.mp4`, `*.mov`, `*.avi`, `*.mkv`, `*.webm` and `data/raw_videos/` are gitignored.

## Mason target features

(Impact-geometry diagnostics: `data/references/mason_impact_geometry_targets.json`, `docs/MASON_IMPACT_GEOMETRY.md`.)

`data/references/mason_target_features.json` (see `docs/MASON_TARGET_FEATURES.md`) summarizes Mason's own swings: n=11 left-handed native clips, median tempo ratio (back/down) 2.90, IQR 2.88-3.55 (range 2.2-3.8). The downswing is only ~5 frames at ~30 fps, so per-swing tempo uncertainty is ~14-32%. **Treat tempo as a loose band (about 2.5-3.5), not a sharp target.** These features are 2D image proxies and cannot support speed targets (120+ mph is not derivable from this data).

The JSON also has a `mason_slowmo_v3` block: 4 verified slow-motion swings (`mason_v3_*_slowmo.npz`), median tempo ratio 3.75 (range 2.50-4.58); its single recommended swing has tempo 3.17. The slow-motion factor (~4.7x median) is only an order-of-magnitude estimate, and its event detector differs from the v2 one, so these tempo values are not directly comparable with the n=11 set above.


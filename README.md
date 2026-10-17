# PureGolf / Adam Scott Humanoid Training System

Autonomous pipeline for training a simulated humanoid to swing a golf club in the style of Adam Scott and other pure/textbook swings.

## Status (simulation only; all numbers from committed files)

| Area | State | Verified number / source |
|---|---|---|
| Club-ball contact | Works | 100% true contact in deterministic mode for every left-handed residual-PPO run (`results/gate_*.json`, `results/leaderboard.md`); stochastic mode is lower for some earlier runs |
| Club speed | Works (scripted + residual) | Trained left-handed runs 107-118.5 mph mean peak (123.6 for the flat-launch `left_fast2_s11`) (gate/leaderboard); scripted lofted base 120.3-120.4 mph (`results/TRAINING_NOTES.md` Stage 5). Target 120 mph |
| Deep carry (deterministic) | Works, with a caveat | 96-114 m mean carry (an2: 114.3 m, `results/gate_ppo_resid_v3_left_an2_s0.json`). These runs were trained in the pre-fix strike regime (see Known limits) |
| Lateral gate (carry > 11.98 m, lateral std < 2.73 m, contact >= 99%) | **Fails for every deep-carry trained model** | Lateral std 5.7-8.2 m. Runs that pass the literal gate are flat-launch exploits (e.g. `left_fast2_s11`: 15.2 m carry, -5.8 deg launch) |
| Leaderboard headline (`results/leaderboard.md`) | Best model `ppo_resid_v3_left_an3_s1` | Ranked by contact then mean carry averaged over deterministic + stochastic: 102.9 m (deterministic alone is 108.6 m, stochastic 97.2 m). **No model meets the showcase criterion** |
| Scripted baseline, lofted fix (`configs/fast_scripted_v2_lofted.json`) | Passes in the notes only | Evaluator protocol, 100 eps, seeds 4000/8000: contact 100%, launch 9.3/9.5 deg, carry 70.0/71.9 m, lateral std 0.013 m, 120.3 mph. **No committed gate JSON**; lateral std is tiny because the model has no sidespin |
| Trained policy beating scripted | No | Notes: trained policies never beat their scripted baseline; PPO was not re-run on the fixed base |
| Model checkpoints | Not published | See `docs/CHECKPOINT_RELEASE.md` for what blocks a Release |
| Real robot / real ball validation | None | Simulation only |

## How to run

Install: `pip install -r requirements.txt` (MuJoCo 3, SB3, torch). Commands below match the scripts in this repo; the leaderboard, gate and showcase need trained `models/*.zip` locally, which are not in git.

```bash
# Train a residual-PPO policy (flags as in results/TRAINING_NOTES.md section D; --name sets models/<name>.zip and results/<name>.json)
python -m train.train_residual --timesteps 150000 --flight_model --n_envs 6 --seq_weight 1.0 --name ppo_resid_v3_left_an3_s1 --seed 1 \
  --loft 8 --analytic_ball --elev_target 12.5 --handedness left \
  --style_ref data/references/mason_swing_part1_s05_refined_mirrored.npz --style_weight 1.0
# (exact flags per run are in results/TRAINING_NOTES.md and the "args" block of each results/<name>.json)

# Legacy (non-residual) PPO
python -m train.train_ppo --style scott --timesteps 50000

# Evaluator-protocol gate for one model: 50 episodes, seed 4000 -> results/gate_<name>.json
python -m eval.eval_gate ppo_resid_v3_left_an3_s1 50 4000

# Scripted (no learning) config: per-shot distribution, 100 episodes from seed 5000
python -m eval.shot_dist configs/fast_scripted_v2_lofted.json 100 5000

# Leaderboard (regenerates results/leaderboard.md/.json; --episodes default 50, --seed default 4000, --force ignores cache)
python -m eval.leaderboard

# Showcase video comparing learned an3_s1 with the scripted swing (output is gitignored under results/videos/)
python -m eval.render_showcase --compare

# Tests
pytest tests
```

## Licensing & data provenance

- **GolfDB:** videos and annotations are research / non-commercial only. Not used in any recorded training run (`docs/GOLFDB_PLAN.md` is a plan). Do not use GolfDB-derived data commercially.
- **CMU Graphics Lab Motion Capture Database:** data from mocap.cs.cmu.edu; acknowledgment is required and the data may not be resold as a standalone dataset (`docs/CMU_MOCAP_GOLF.md`). It is reachable only through `--style_prior`, which is off in every recorded run.
- **MultiSenseGolf:** CC0 (`docs/research_open_data_v2.md`). Mirrored references exist; no recorded run uses them for training.
- **CaddieSet:** MIT licence on the data repo, but dataset consent and commercial terms are unvetted. Counsel is needed before any use. Only a summary JSON (`data/references/caddieset_driver_event_features.json`) is committed; no policy uses it.
- **Mason's own swings:** references in `data/references/mason_*` are derived from Mason's self-filmed / self-posted swings (`self_owned`). Raw videos are never committed. They are 2D-proxy angles from single-view video.
- **Synthetic references:** Scott/Scheffler/Rory styles are generated (`data/generate_synthetic_scott.py`); they are not Adam Scott's real data.
- Per-file tags and a table are in `docs/REFERENCE_PATHS.md`. This repository has no `LICENSE` file yet. Details of what trained each model: `docs/CHECKPOINT_RELEASE.md`.

## Known limits

- **Lateral gate fails for deep-carry models.** All trained left-handed runs with 96-114 m carry have lateral std 5.7-8.2 m against a < 2.73 m gate. Runs with tiny lateral spread (an5, an7, an8, fast2) get it from flat or negative launch and carry only 9-15 m.
- **Strike-regime artefact.** Stage 5 notes show negative `loft_deg` means more loft in the v3 model, and that older runs with positive loft or `ball_dz >= 0` struck the club's top edge. Treat all earlier carry/launch numbers (including the table below) as results from that regime, not as physical drives.
- **Scripted vs trained.** The default scripted swing fails the lateral gate (4.22 m / 3.97 m in the gate files). A tuned scripted config passes in the notes, and the lofted v2 config looks better still, but neither has a committed gate JSON. Trained policies have not beaten their scripted baselines.
- **Checkpoints are unpublished,** so the leaderboard and gate cannot be reproduced from this repo alone; `results/` holds the recorded outputs.
- **Deterministic vs stochastic.** The tables below are deterministic unless marked. The leaderboard headline averages both modes (102.9 m for an3_s1), and the carry definition changed between runs (analytic training carry vs MuJoCo physics gate). Compare only within one file.
- Tempo targets from Mason's swings are a loose band (n=11); no speed target is derivable from them.
- Simulation only; no real-robot or real-ball validation.

## Current Performance

Numbers below are copied from the committed `results/leaderboard.md` / `results/leaderboard.json` (50 episodes, seeds 4000-4049, env fingerprint `59bc5ea99d60`, v2 physics; the same rows are unchanged in the current `results/leaderboard.md` (fingerprint `7a2ffa104b56`)). Contact = true club-ball contact. Distance = final ball x in metres (total, including roll); carry = x at landing (0 if the ball never landed).

| Model | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) |
|---|---|---|---|---|---|---|
| ppo_scott_baseline | 30000 | deterministic | 0% | 0.30 | 0.30 | 0.000 |
| ppo_scott_baseline | 30000 | stochastic | 0% | 0.56 | 7.90 | 0.000 |
| ppo_scott_curr | 30000 | deterministic | 100% | 3.01 | 3.01 | 0.000 |
| ppo_scott_curr | 30000 | stochastic | 34% | 5.04 | 13.90 | 0.062 |
| ppo_scott_prev_backup | 30000 | deterministic | 100% | 2.76 | 2.76 | 0.000 |
| ppo_scott_prev_backup | 30000 | stochastic | 38% | 4.86 | 13.62 | 0.021 |
| ppo_scott_final2 | 60000 | deterministic | 48% | 1.80 | 9.80 | 0.091 |
| ppo_scott_final2 | 60000 | stochastic | 60% | 1.96 | 10.37 | 0.128 |
| ppo_scott / ppo_scott_carry1 (best legacy model) | 100000 | deterministic | 98% | 0.47 | 0.59 | 0.102 |
| ppo_scott / ppo_scott_carry1 (best legacy model) | 100000 | stochastic | 66% | 0.88 | 5.93 | 0.237 |

Takeaways for the legacy models above: 100% contact appears only in deterministic mode and carry stays tiny (best mean 0.24 m, stochastic). The residual-PPO runs below are far better. The current `results/leaderboard.md` headline best model is `ppo_resid_v3_left_an3_s1` (ranked by contact averaged over deterministic and stochastic modes, then mean carry; it is not the best on lateral spread or on the gate), not the legacy `ppo_scott_carry1`.

Club speed (from `results/leaderboard.md`, peak club-head linear speed over all physics substeps; 120 mph = 53.64 m/s target): the best legacy model `ppo_scott_carry1` reaches a mean peak of 25.78 m/s and a max of 40.74 m/s (91.1 mph, 75.9% of target) in stochastic mode, with a mean peak ball speed of only 2.45 m/s. In deterministic mode its peak club speed is 0.35 m/s mean / 0.58 m/s max. Single-swing peaks in stochastic mode are not a sustained, controlled swing.

**Early-model club speeds:** the 706,966 m/s peak seen for `ppo_scott_baseline` was real output from an unstable legacy-config simulation (torque_scale 10, out-of-range legacy address pose) that diverged within ~0.05 s (MuJoCo "Nan, Inf or huge value in QACC"), not a metric bug. `eval/flight_tracker.py` now flags episodes with any substep above 100 m/s or non-finite and excludes them from peak stats (raw max is reported, never clipped); the leaderboard shows `ppo_scott_baseline` as n/a (50 sim-unstable episodes excluded).

**Best verified result so far — residual PPO, left-handed, analytic ball flight (`results/gate_ppo_resid_v3_left_an2_s0.json`, `results/gate_ppo_resid_v3_left_an1_s0.json`, `results/leaderboard.md`):** evaluator-protocol gate (`python -m eval.eval_gate <name> 50 4000`: 50 episodes, seeds 4000+, MuJoCo physics with the flight tracker, 450-step flight horizon, **deterministic** policy, v3 env, loft 8 deg). Training notes: `results/TRAINING_NOTES.md` section D.

| Model | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club speed mean (mph) | Peak club max (mph) |
|---|---|---|---|---|---|---|
| scripted zero-residual (no learning) | 100% | 72% | 57.8 | 4.22 | 107.9 | 108.1 |
| ppo_resid_v3_left_an1_s0 | 100% | 100% | 110.3 | 7.53 | 114.5 | 115.4 |
| ppo_resid_v3_left_an2_s0 | 100% | 100% | 114.3 | 7.42 | 114.7 | 115.5 |
| ppo_resid_v3_left_an3_s1 | 100% | 100% | 108.6 | 6.74 | 114.6 | 115.2 |
| ppo_resid_v3_left_an4_s2 (loft 7, native-left Mason style) | 100% | 100% | 96.1 | 6.68 | 111.7 | 112.4 |
| ppo_resid_v3_left_an5_s3 (flat-launch exploit) | 100% | 72% | 9.6 | 0.14 | 117.0 | 117.7 |
| ppo_resid_v3_left_an6_s4 | 100% | 98% | 99.8 | 6.95 | 113.0 | 115.0 |
| ppo_resid_v3_left_an9_s7 | 100% | 100% | 103.3 | 8.17 | 110.4 | 111.7 |
| ppo_resid_v3_left_an7_s5 (flat-launch, leaderboard) | 100% | 66% | 9.0 | 0.26 | 115.3 | 116.9 |
| ppo_resid_v3_left_an8_s6 (flat-launch, leaderboard) | 100% | 82% | 11.4 | 0.10 | 118.5 | 119.2 |
| ppo_resid_v3_left_an10_s8 (leaderboard) | 100% | 94% | 110.0 | 5.67 | 107.0 | 108.4 |
| ppo_resid_v3_left_fast2_s11 (flat-launch, gate JSON) | 100% | 100% | 15.2 | 0.017 | 123.6 | 123.8 |

(All from `results/gate_*.json`, `policy_det` block; same 50 episodes, seeds 4000+. Note the scripted row is the default scripted swing; the an4/an5/an6/an9 gate files use loft 7 and have their own scripted block with 48.1 m carry, 54% landed, 3.97 m lateral std. `gate_pass` is false for every model above.)

an7, an8 and an10 rows come from the committed `results/leaderboard.md`/`.json` (deterministic, 50 episodes, seeds 4000-4049, no gate JSON exists for them). an7 and an8 are flat-launch exploits (mean launch elevation -3.2 and -5.2 degrees) with near-zero lateral spread but only 9-11 m carry, so they fail the carry gate. an10 reaches 110.0 m mean carry (94% landed) with the lowest lateral std of the deep-carry runs, 5.67 m, but it still fails the lateral gate (< 2.73 m); its stochastic carry is 57.1 m with 6.40 m lateral std. Every trained left-handed run in this table fails the gate. Checkpoints are still unpublished.

`left_fast2_s11` (`results/gate_ppo_resid_v3_left_fast2_s11.json`, deterministic, 50 episodes, seed 4000) reaches 123.6 mph mean peak club speed and a 0.017 m lateral std, so it passes the literal gate (carry > 11.98 m, lateral std < 2.73 m, contact >= 99%). But its launch elevation is about -5.8 degrees (100% flat flag), so it is a flat-launch exploit and not a good drive (15.2 m carry). The scripted base in the same protocol carries 30.0 m with 2.92 m lateral std (119.8 mph), i.e. it fails the lateral gate.

**Honest summary (verified against the committed files above):** the best deterministic carry is about 96-114 m at about 111-115 mph peak club speed (an2: 114.3 m / 114.7 mph), but every trained left-handed model **fails** the lateral gate (< 2.73 m): lateral std is 6.7-8.2 m. an5 has lateral std 0.14 m only because it learned a flat, negative-launch strike (carry 9.6 m, 72% landed, so it fails the carry gate too). The default scripted swing also fails the lateral gate (4.22 m / 3.97 m in the gate JSONs). A tuned scripted configuration (`ball_x=0.422`, 5 mm ball-position noise, loft 7, no learning) is reported in `results/TRAINING_NOTES.md` (Address-geometry finding) as passing carry > 11.98 m and lateral std < 2.73 m: 53.1 m carry, 1.98 m lateral std, 107.8 mph, launch about 11 degrees. That result is from the notes only (no committed gate JSON), uses 5 mm noise instead of the default 3 cm, and in the same notes the trained policies do not beat their scripted baseline (an10: lateral 5.74 m vs 2.18 m scripted). Launch is bimodal and set mainly by ball position along the swing arc. Details and an7-an10 numbers (analytic evaluation, not gate protocol) are in `results/TRAINING_NOTES.md`.

Caveats:
- All rows above are **deterministic** (an1/an2 from the committed gate JSONs; an3_s1 from the committed `results/leaderboard.md`/`.json`, same protocol, 50 episodes, seeds 4000+). In stochastic mode an3_s1 has 100% contact, 97.2 m mean carry, 94% landed and 7.49 m lateral std (leaderboard). The leaderboard ranks an3_s1 > an2 > an1 among left-handed models (it has the lowest lateral std, 6.74 m, but an2 has the highest deterministic carry, 114.3 m). The earlier stochastic ladder run (`results/ppo_resid_v3_ladder_s0.json`, v3 env, MuJoCo landing) had 100% contact and a peak club speed max of 50.46 m/s (112.9 mph) but only 0.24 m mean carry and 20% landed, with the scripted swing at 6.6 m. Do not mix these protocols.
- The an1/an2 policies are trained with an **analytic** ball-flight model (drag + Magnus, assumed backspin = clip(1500 + 70 x launch elevation deg, 1000, 5000) rpm, no sidespin). Their training-time carry (about 92-93 m) is analytic. The gate numbers above come from the MuJoCo physics gate. The carry definition changed between runs, so compare only within a single JSON.
- Launch elevation stays near 33 degrees (target 10-15), and smash factor drops from 0.90 (scripted) to about 0.73-0.76 as the policy trades smash for loft. The Mason-style match score is slightly lower than scripted (0.62 vs 0.53-0.55).
- Lateral std is 6.7-7.5 m for an1-an3, so those runs **fail** the teammate gate (carry > 11.98 m AND lateral std < 2.73 m): `gate_pass` is false in every gate JSON and the leaderboard marks an3_s1 FAIL too. Relative to carry, lateral dispersion is about 0.066 (an2) vs 0.073 (scripted).
- Club speed of about 115 mph is the peak head speed in a scripted-swing-plus-residual setup; it is not a human-like or sustained controlled swing and is below the 120 mph target (about 95.5%).
- Everything is simulation only; no real-robot or real-ball validation.
- Details for the older (non-residual) models are in the table above; those carry numbers are not comparable with the gate protocol.

> **Reproducibility caveat:** the v2/v3 environment code (`env/`), `eval/flight_tracker.py`, `eval/leaderboard.py` and training scripts are pushed, but the model checkpoints are not (trained models are not committed; they will be shared via a GitHub Releases note). **Trained model checkpoints are not published yet.** A GitHub Release will be considered only once it is confirmed the models contain no non-commercial data (GolfDB / CMU mocap licensing). The leaderboard therefore can't be re-run end to end from this repo yet; the `results/` files are the recorded outputs.

See [ROADMAP.md](ROADMAP.md) for next steps.

## Features

- MuJoCo humanoid + club + ball with proper address initialization
- Synthetic Adam Scott / Scheffler / Rory / average style references
- Multi-swing reference dataset loader
- Curriculum scaffolding (Address → Contact → Style → Ball flight)
- Dense approach + contact + imitation + ball-flight rewards
- PPO training (Stable-Baselines3)
- Style comparison script (`eval/compare_styles.py`)
- Public video proxy for Adam Scott pure swing footage

## Quick Start

```bash
pip install -r requirements.txt
python -m data.generate_synthetic_scott
python -m train.train_ppo --style scott --timesteps 50000
# train_ppo writes models/ppo_scott.zip (models/ is created by training; trained models are gitignored and go to a releases note)
python -m eval.evaluate --model models/ppo_scott --episodes 5
python -m eval.compare_styles
# showcase video comparing the learned left_an3_s1 policy with the scripted swing (needs trained models/ locally; output goes to results/videos/, which is gitignored)
python -m eval.render_showcase --compare   # add --reuse to reuse swing seeds from an earlier showcase_compare.json
```

## Project Structure

- `data/` — synthetic generators and video processing
- `env/` — MuJoCo environment and model
- `imitation/` — reference dataset and curriculum
- `train/` — PPO training
- `eval/` — evaluation, rendering, style comparison

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

### What each script does

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

### Reference file format

`time (n,)`, `dt` (0.01 s), `joints (n,11)` in degrees (layout in `data/process_video.py`; `right_*` = anatomical right limbs), optionally `joints_rad`, `club_head` (synthetic only), `pelvis_rot_deg`, `thorax_rot_deg`, `x_factor_deg`, `lateral_sway_m`, `landmarks (m,33,4)` (Mason; 60 Hz, hip-centred world coordinates), events (`events` or `t_takeaway/t_top/t_impact`), plus metadata. **Mason files have no club data, no pelvis/thorax rotation and no sway**; joint angles are 2D image proxies from a single view and are not retargeted to the MuJoCo humanoid.

### License / provenance tags and `commercial_only`

Every reference `.npz` carries `license_class` (`synthetic`, `self_owned`, `cmu_permissive`, `cc0`, `noncommercial`, `unknown`), `commercial_ok`, `provenance_source`, `provenance_note`, `acknowledgment_required`, `acknowledgment_text`. Unidentified data is tagged not-commercial. Per-file table: `docs/REFERENCE_PATHS.md`. Only CMU (acknowledgment required, no standalone redistribution), synthetic, Mason's own footage and CC0 MultiSenseGolf are commercial-eligible; GolfDB and AMASS are excluded.

`ReferenceDataset(dir, commercial_only=True)` skips any file whose `commercial_ok` is false. It is **opt-in and defaults to `False`**: `env/`, `train/` and `eval/` do not currently pass it, and the default `*.npz` glob also picks up the `_mirrored` copies and the Mason first-pass/v2/v3 variants (duplicates of the same swings), so select by field (`recommended`, `mirrored`, `native_footage`, `partial`) rather than a filename pattern.

### Handedness and mirroring

Mason is left-handed. Files record `handedness` (and for v2/v3 `handedness_stated`, `handedness_detected`, `handedness_verified`): 18 clips read left-handed from the footage itself, a few right-handed clips are other golfers on the feed (flagged not commercial-safe), and one clip is a flipped edit that also has an `_unmirrored` copy. `data/mirror_references.py` writes `*_mirrored.npz` (joints with left/right columns and roll sign swapped, landmark x negated and left/right indices swapped, `mirrored=True`, original handedness recorded, tags copied) so right-handed sources (CMU, MultiSenseGolf, synthetic) can drive the left humanoid. Conventions in `docs/HANDEDNESS.md`. The target-feature scripts use only native left clips and compute lead/trail-defined (handedness-invariant) quantities.

### Known limits

- Mason data are ~30 unique fps screen-recordings of Instagram playback: events are good to about +-1 frame (33 ms), a normal-speed downswing is only ~5 frames, per-swing tempo is uncertain by roughly 14-32%. Use tempo as a loose band (about 2.5-3.5).
- One camera view per clip (mostly down-the-line), so joint angles and all geometry are view-dependent; depth is the weakest axis.
- No club, ball, launch or force data for Mason. 120+ mph / 300+ yd cannot be derived from these files; launch angle needs a launch monitor or club tracking.
- CMU subject 64 is a slow recreational volunteer (tempo ~1.7); MultiSenseGolf swings are right-handed, ~90-103 mph; synthetic swings are caricatures.
- Landmarks are trimmed at the start of each file, so their time axis is offset from `t_start_in_video` (the impact-geometry script realigns it per file by cross-correlation; see `docs/MASON_IMPACT_GEOMETRY.md`).
- The biggest data upgrade is 20-50 swings filmed at 240 fps from face-on and down-the-line, original phone files (no re-encoding).

### Adding new data

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

### Data licensing notes

- **GolfDB videos are not licensed for commercial use** (research/non-commercial only). Use GolfDB-derived data only for non-commercial research; see `docs/GOLFDB_PLAN.md`.
- **CMU mocap-derived files** (`data/references/cmu_*.npz`) require acknowledgment of the CMU Graphics Lab Motion Capture Database, and may not be resold as a standalone dataset. See `docs/CMU_MOCAP_GOLF.md`.
- Every reference `.npz` carries `license_class` / `commercial_ok` tags; the per-file license column is in `docs/REFERENCE_PATHS.md`.
- Raw videos and footage (including Mason's self-filmed swings) are never committed: `*.mp4`, `*.mov`, `*.avi`, `*.mkv`, `*.webm` and `data/raw_videos/` are gitignored.

### Mason target features

(Impact-geometry diagnostics: `data/references/mason_impact_geometry_targets.json`, `docs/MASON_IMPACT_GEOMETRY.md`.)

`data/references/mason_target_features.json` (see `docs/MASON_TARGET_FEATURES.md`) summarizes Mason's own swings: n=11 left-handed native clips, median tempo ratio (back/down) 2.90, IQR 2.88-3.55 (range 2.2-3.8). The downswing is only ~5 frames at ~30 fps, so per-swing tempo uncertainty is ~14-32%. **Treat tempo as a loose band (about 2.5-3.5), not a sharp target.** These features are 2D image proxies and cannot support speed targets (120+ mph is not derivable from this data).

The JSON also has a `mason_slowmo_v3` block: 4 verified slow-motion swings (`mason_v3_*_slowmo.npz`), median tempo ratio 3.75 (range 2.50-4.58); its single recommended swing has tempo 3.17. The slow-motion factor (~4.7x median) is only an order-of-magnitude estimate, and its event detector differs from the v2 one, so these tempo values are not directly comparable with the n=11 set above.

Created as part of AshlrAI agentic engineering experiments.

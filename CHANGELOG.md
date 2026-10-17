# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Licence items are engineering diligence, not legal advice.

## [Unreleased]

### Added
- Trainer reconciliation: `train_residual.py --flight_steps` (and `flight_steps` in `eval/env_factory.py` arg replay), `configs/fast_scripted_v4_power_hypothetical.json` now sets `flight_steps` 900, opt-in `track_time_fix` / `key_weight` / `key_s` in `ResidualGolfEnv` (all default off), `eval/export_scripted.py`, `eval/diag_reset.py`, `eval/diag_shots.py`, `results/gate_ppo_v4power_s{61,62}.json` (seed 4000; s61 recorded with min_carry 30), `results/trajectories/v4power_scripted_seed4000*`, and TRAINING_NOTES Stage 13/14/14b.
- `data/reference_sets/unified_v2.json` and `unified_v2_sampling.json`: unified_v1 plus the sampler honoring `handedness_unverified` / `exclude_pending_verification` (`mason_v2_p1_s11`, `mason_v2_p2_s10` excluded from train and val; weights renormalised). `data/unified_refset.py` takes a version (`build --version unified_v2`, `load_manifest(version=...)`, `load_sampling_config(version=...)`); `ResidualGolfEnv(track_set="unified_v2")` selects it. See `docs/REFERENCE_PATHS.md`.
- `scripts/retag_multisense.py` (idempotent; changes only licence fields, asserts array equality).
- Licence annotations in the unified manifest (`counsel_required`, `license_url`, CMU resale/acknowledgment fields, Mason handedness-verification fields) and `commercial_cleared()` in `data/provenance.py`.
- Docs: `docs/P1_S11_HANDEDNESS_CHECK.md`, `docs/IMPACT_FACE_PATH_AVAILABILITY.md`, `docs/TRACKING_REWARD_REFERENCE_GAPS.md`, `data/references/mason_impact_face_path_proxies.json` (unverified stub).
- Tests: unified_v1 manifest and sampling hash freeze, unified_v2 behaviour, retag script.

### Changed
- **MultiSenseGolf retag:** all 56 `data/references/multisense_*.npz` files changed from `license_class=cc0`, `commercial_ok=True` to `license_class=needs_counsel`, `commercial_ok=False`, with `license_class_as_published=cc0`, `counsel_required=True` (published as CC0, participants identifiable). `data/provenance.py` gains the `needs_counsel` class and preset `multisensegolf_needs_counsel` (`multisensegolf_cc0` kept as an alias for the same tag); the converter and `infer_kind` use it.
- **Behaviour change:** `ReferenceDataset(commercial_only=True)` and `include_commercial_only()` now exclude MultiSense. Recorded Stage 10 runs do not use that filter; `unified_v1` sampling ignores `commercial_ok`, so recorded runs are not affected and were not re-evaluated.
- `data/mason_target_features.py` comparison stats still read MultiSense files (comparison only, not training) via the `counsel_required` flag, so `mason_target_features.json` is byte-identical. `data/references/mocap_dataset_licenses.json` lists `needs_counsel` under existing tag classes.
- Tests asserting `cc0` for MultiSense now assert `needs_counsel`.

### Unchanged (deliberately)
- `unified_v1.json` sampling, splits and weights, and `unified_v1_sampling.json`, so `imit2`/`imit3` stay reproducible. v1 still samples the two unverified Mason clips.

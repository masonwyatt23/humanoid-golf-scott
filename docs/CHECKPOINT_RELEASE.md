# Checkpoint release checklist (no Release has been created)

Status: **BLOCKED. Do not publish a GitHub Release yet.** Trained checkpoints (`models/*.zip`) are gitignored and live only on the training machine. Everything below was derived from the committed `results/*.json` `args` blocks, `results/TRAINING_NOTES.md` and `docs/`. Nothing here is legal advice.

## What data trained each model (from committed args/notes)

| Model(s) | Real-motion data used in training | Evidence |
|---|---|---|
| `ppo_scott_baseline`, `_curr`, `_prev_backup`, `_final2`, `_carry1` (legacy PPO, `train/train_ppo.py`) | One **synthetic** reference per `--style` (`data/generate_synthetic_scott.py`); no real mocap or video | `train_ppo.py` loads/generates `data/references/<style>_swing.npz`; per-model args are not stored in `results/`, so confirm from the original run commands |
| `ppo_resid_v3_s0`, `_r2_s0`, `_r3_s0` | None (no `style_ref`, no `style_prior` recorded) | `results/ppo_resid_v3_*.json` args have no style keys (older runs); TRAINING_NOTES sec. A commands |
| `ppo_resid_v3_ladder_s0` | None (`style_prior=false`, `style_ref=null`) | `results/ppo_resid_v3_ladder_s0.json` |
| `left_an1`, `left_an2`, `left_an3_s1` | Style term from `mason_swing_part1_s05_refined_mirrored.npz` (**Mason's own** swing, mirrored; `self_owned`) | args in `results/ppo_resid_v3_left_an{1,2,3}_*.json` |
| `ppo_v3tiny_s21`, `_s22`, `_s23` (Stage 7, fixed regime) | None (`style_ref: null`, `style_weight: 0.0` in `results/ppo_v3tiny_s22.json`; check s21/s23 args too) | `results/TRAINING_NOTES.md` Stage 7, `results/ppo_v3tiny_s2*.json` |
| `left_an4`..`an10`, `left_fast1_s10`, `left_fast2_s11` | Style term from `mason_v2_p1_s06.npz` (**Mason's own**, `self_owned`) | args in the matching results JSON |

Not used in any recorded training run: **GolfDB** (plan/research only, `docs/GOLFDB_PLAN.md`), **CMU mocap** (only reachable through `--style_prior`, which is `false`/unset in every recorded run), **MultiSenseGolf** (mirrored references exist, never passed as `style_ref`), **CaddieSet** (only a feature summary JSON exists; no policy uses it).

## Blockers (all must be cleared)

1. [ ] **Models predate the loft/edge-strike fix.** `results/TRAINING_NOTES.md` Stage 5 says results with positive loft / `ball_dz >= 0` are edge-strike artefacts. Every trained checkpoint was trained or evaluated in that regime, so publishing them as "golf swing policies" would mislead. `results/strike_regime_rerun.md` shows their numbers change materially under the fixed config (e.g. `an3_s1` 108.6 m -> 81.1 m carry), so earlier numbers hold only under their original configs. Only the Stage 7 `ppo_v3tiny_s21-23` were trained on the fixed regime (`configs/fast_scripted_v3.json`), and they are a negative result. Retrain on the fixed regime, or label every checkpoint clearly as a research artefact.
2. [ ] **No trained model passes the showcase/gate criteria** (carry >= 30 m, lateral std < 2.73 m, launch >= 5 deg, contact 100%; see `results/leaderboard.md`). The only passing configuration is the Stage 6 scripted swing (`configs/fast_scripted_v3.json`: 113.8 m, 12.2 deg, lateral std 1.66 m, 120.3 mph), which is **not learned** and has no checkpoint. A release should wait for a qualifying trained model, or be explicitly labelled "negative results". Smash factor is unverified and must not be quoted in release text.
3. [ ] **Provenance proof per checkpoint.** Old runs (`r2`, `r3`, `s0`, legacy PPO) do not record style/data args. Re-derive from run commands/logs, or retrain with args stored. Record `git_head`, md5 of each zip and the env fingerprint in a model card.
4. [ ] **Mason's sign-off** on publishing models trained with a style term from his own swings (derived from screen recordings of his own Instagram posts). Confirm he is fine with derived motion being public and that no third-party people or content are encoded.
5. [ ] **Counsel review of CMU mocap terms.** CMU requires acknowledgment and forbids standalone resale of the data. Recorded runs did not use it, but legacy runs lack args, so confirm that no `cmu_*` reference or `--style_prior` was used. Add the CMU acknowledgment to the model card regardless.
6. [ ] **GolfDB: confirm nothing GolfDB-derived** (frames, pose estimates, weights) touched any model. GolfDB is research/non-commercial only, so any use blocks a commercial-friendly release.
7. [ ] **CaddieSet: counsel needed** before any use. Repo is MIT, but its docs flag dataset consent/commercial terms as unvetted (`docs/CADDIESET_INTEGRATION.md`, `docs/research_open_data_v3.md`). Currently unused for training, so keep it that way or clear it first.
8. [ ] **Add a repository `LICENSE`.** The repo has none, so nobody has any right to use released weights.
9. [ ] **Security note in release text:** SB3 `.zip` checkpoints contain pickled objects; tell users to load only from the trusted release and pin versions (`requirements.pinned.txt` is committed with `mujoco 3.16.0`, `torch 2.14.1+cpu`, `stable-baselines3 2.9.0`, `gymnasium 1.4.0`; `requirements.txt` stays unpinned).
10. [ ] **Model card** covering: intended use (simulation research only), metrics (deterministic vs stochastic, gate file names), known limits (README "Known limits"), data table above, and reproduction commands.
11. [ ] **Size/format check:** no videos, no raw CSV/HDF5, no logs in the release assets; attach only the chosen checkpoint zips plus checksums.

When 1-11 are done, create the Release manually (tag, notes from the model card, checksums). This document does not authorise creating it.

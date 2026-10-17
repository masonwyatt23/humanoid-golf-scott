# Blockers before going public

Status as of branch `oss-ready` (prepared locally; nothing published, visibility unchanged). **Not legal advice.** Mason (and counsel where noted) decides each item.

| # | Blocker | Status | Needed |
|---|---|---|---|
| 1 | **Code license** | No `LICENSE` on main. Options (A all rights reserved, B MIT, C Apache-2.0) are in `LICENSE.draft` on branch `drafts/license-modelcard` (draft only; do not rename until chosen). Weights may need separate terms. | Mason/counsel pick one; set copyright holder (Mason and/or AshlrAI). Then add SPDX to `CITATION.cff`. |
| 2 | **CMU mocap** (`data/references/cmu_64_*.npz`) | Acknowledgement required; not resalable as a standalone dataset (`docs/CMU_MOCAP_GOLF.md`). Raw BVH is gitignored, but `data/raw_mocap/cmu/READMEFIRST.txt` and the index text are tracked. | Add the acknowledgement text to the README/NOTICE; confirm derived `.npz` redistribution is acceptable. |
| 3 | **MultiSenseGolf (CC0)** | CC0 per `docs/research_open_data_v2.md`; legal sign-off on commercial use still pending (`docs/DATA_PIPELINE.md`). | Mason/counsel sign-off. |
| 4 | **Instagram-derived data (Mason's own references)** | `mason_*` files are tagged `self_owned`, derived from screen recordings of Instagram playback. The feed recordings also contain other golfers (a few right-handed clips are flagged not commercial-safe). `docs/REFERENCE_PATHS.md` says to "confirm no third-party content/music". | **Mason's explicit sign-off** on the `self_owned` term and publishing models/data derived from it; confirm each published clip is his own and no third party is identifiable; confirm platform terms. |
| 5 | **GolfDB** | Research / non-commercial only. Plan only; nothing downloaded; no recorded run used it (`docs/GOLFDB_PLAN.md`). | Keep it out; any future use must stay non-commercial and be labelled. |
| 6 | **CaddieSet** | MIT on the repo, but MIT-on-data and participant consent are unvetted. Only a summary JSON is committed (`data/references/caddieset_driver_event_features.json`). | Counsel review, or remove the JSON before going public. |
| 7 | **Raw videos / zips / logs in history** | See "History check" below. | Decide whether to accept history as is. |
| 8 | **Third-party player likeness / naming** | See "Naming" below. | Rename or de-emphasise before going public. |
| 9 | **Pickle / checkpoint risk** | See "Pickle risk" below. | Document; no checkpoints published. |
| 10 | **Model card** | `docs/MODEL_CARD.draft.md` exists only on `drafts/license-modelcard`. Checkpoint Release is on hold (`docs/CHECKPOINT_RELEASE.md`). | Finish after items 1-6; then decide on a Release. |
| 11 | **No hero media / CI** | No hero GIF exists; `.github/workflows/smoke.yml` on this branch runs the smoke test only. | Optional; host media outside git. |

## History check (main, checked 2026-10-17)

- **Videos, GIFs, zips, `.pt`/`.pth`/`.h5`, MUJOCO_LOG: none ever added on `main`** (checked with `git log --diff-filter=A` over all of main's history).
- **Three stray logs were committed and later deleted** (still in history, about 3 KB each, no personal paths or secrets found by grep): `logs/resid_v3_left_an1_s0.log` (added b88d9e2, removed db1d629), `logs/resid_v3_left_an2_s0.log` (added 4fa9f0b, removed db1d629), `logs/resid_v3_left_fast2_s11.log` (added edce378, removed 44010bd). `logs/` and `*.log` are now gitignored. (The request mentioned two; there are three.)
- **Model zips and many more logs exist only on other local branches/remotes** (e.g. the artifacts clone: `models/ppo_scott*.zip`, `logs/*.log`), not on `main`. **Never push those branches.**
- `results/leaderboard_cache.json` is tracked (about 1.7 MB) although its path is in `.gitignore`; it was committed before the ignore rule. Consider `git rm --cached`.
- Largest blobs in main's history are `results/leaderboard_cache.json` revisions (about 1.3 to 1.7 MB each); pack size about 17.7 MiB.
- 11 commits use a personal Gmail author address (`masonwyatt2003@gmail.com`). Decide whether that is acceptable to expose; a history rewrite would be needed otherwise (not done).
- Absolute `/workspace/...` paths appear in a few script docstrings/defaults (harmless but untidy).

## Naming and likeness (flag)

- The repository name `humanoid-golf-scott`, the old README title ("PureGolf / Adam Scott Humanoid Training System"), `data/generate_synthetic_scott.py`, `data/references/scott_swing.npz`, `results/*scott*`, models named `ppo_scott*`, `--style scott`, and docs such as `docs/NEXT_DATA_SOURCES.md` ("PureGolf / Adam Scott data sources") and `ROADMAP.md` ("PureGolf and Adam Scott videos") refer to **Adam Scott** by name. The "scott" style is a **procedurally generated caricature, not Adam Scott's data**, and no Adam Scott footage is used in any recorded run.
- Using a real player's name for the repo/style may imply association or endorsement. The new README avoids the name outside this disclaimer. Recommended: rename the repo and the `scott` style identifiers (or at least add a disclaimer), and drop the "Adam Scott pure swing footage" feature wording. Not done on this branch because renames would break committed results paths.

## Pickle risk

- Reference `.npz` files are loaded with `np.load(..., allow_pickle=True)` in `env/residual_golf_env.py`, `env/style_prior.py`, `eval/style_match.py`, `eval/dispersion_report.py` and several `data/` scripts. A malicious `.npz` could execute code on load.
- Trained checkpoints are SB3 `.zip` files that contain pickled objects; loading an untrusted checkpoint is unsafe. None are published. Any future Release should ship checksums and a safe-loading note (or a non-pickle format).




# Quickstart

## One command (light check: no simulator needed)

```bash
make setup && make check
```

`make setup` creates `.venv` with numpy, scipy and pytest. `make check` runs
`scripts/smoke_test.py`, the unit tests, and verifies `docs/RESULTS_DASHBOARD.md`
is up to date. Individual targets: `make smoke`, `make test`, `make dashboard`.

Verified on the dev box with a plain venv (numpy, scipy, pytest): the smoke test
passes and the unit tests give 102 passed, 5 skipped (the skips need `cv2`/`h5py`
or raw CMU data that is not in the repo).

## Full simulation environment

```bash
make setup-full     # installs requirements.pinned.txt (MuJoCo, CPU torch, stable-baselines3)
```

Headless rendering: set `MUJOCO_GL=osmesa` on CPU-only machines or `MUJOCO_GL=egl`
where a GPU/EGL driver exists. Evaluation and training entry points are in `eval/` and `train/`;
see the README for the commands and for what is scripted versus learned.

## Docker

```bash
make docker-build
docker run --rm -v "$PWD":/app humanoid-golf python scripts/smoke_test.py
docker run --rm humanoid-golf          # unit tests
```

The image sets `MUJOCO_GL=osmesa`. The smoke test needs a git checkout, so mount the repo as shown.

## Not verified

- The Dockerfile has not been built (Docker is not available on the dev box).
- `make setup-full` and the pinned torch install, plus MuJoCo rendering under osmesa/egl, were not run.
- The GitHub Actions workflow has not yet run on GitHub.
- Tests that need MuJoCo or torch do not exist in `tests/`; the suite is dependency-light.

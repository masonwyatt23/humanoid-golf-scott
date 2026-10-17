# Headless CPU image for running the smoke test, unit tests and MuJoCo evals.
# NOTE: not build-tested by the author (no Docker on the dev box); see docs/QUICKSTART.md.
FROM python:3.12-slim

# MuJoCo offscreen rendering: osmesa works on CPU-only hosts. Switch to
# MUJOCO_GL=egl if the host exposes a GPU/EGL driver.
ENV MUJOCO_GL=osmesa \
    PYOPENGL_PLATFORM=osmesa \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends git libosmesa6 libgl1 libglfw3 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.pinned.txt ./
# The pin file contains a CPU torch build (+cpu local version); use the PyTorch CPU index for it.
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.pinned.txt

COPY . .
# scripts/smoke_test.py uses `git ls-files`; the .git dir is excluded from the build context,
# so run it from a git checkout (make smoke) or mount the repo: docker run -v "$PWD":/app ...
CMD ["python", "-m", "pytest", "tests", "-q"]

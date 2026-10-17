VENV ?= .venv
PY   := $(VENV)/bin/python

.PHONY: setup setup-full smoke test dashboard check docker-build

# Light install: enough for smoke + tests (numpy, scipy, pytest). No mujoco/torch.
setup:
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install numpy scipy pytest

# Full pinned environment for simulation/training (needs mujoco, torch CPU).
setup-full:
	python3 -m venv $(VENV)
	$(PY) -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.pinned.txt

smoke:
	$(PY) scripts/smoke_test.py

test:
	$(PY) -m pytest tests -q

dashboard:
	$(PY) scripts/gen_results_dashboard.py

check: smoke test
	$(PY) scripts/gen_results_dashboard.py --check

docker-build:
	docker build -t humanoid-golf .

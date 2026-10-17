VENV ?= .venv
PY   := $(VENV)/bin/python

.PHONY: setup setup-full smoke test dashboard check docker-build dev-setup lint lint-strict format format-write typecheck

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

# --- Tooling (see pyproject.toml, .pre-commit-config.yaml) ---------------------------------
dev-setup:
	$(PY) -m pip install ruff mypy pre-commit

# Blocking lint: real errors only (E9,F63,F7,F82). Passes on current code.
lint:
	$(VENV)/bin/ruff check .

# Advisory wider rule set (many existing findings; never fails).
lint-strict:
	-$(VENV)/bin/ruff check . --select E,F,W --ignore E501,E701,E702,E731,E741 --statistics

# Preview formatting changes without touching files.
format:
	$(VENV)/bin/ruff format --diff . | head -200

# Actually reformat (opt-in; touches many existing files).
format-write:
	$(VENV)/bin/ruff format .

# Advisory type check (lenient config; never fails until the src layout lands).
typecheck:
	-$(VENV)/bin/mypy env eval train imitation data scripts

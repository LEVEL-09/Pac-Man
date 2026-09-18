CONFIG ?= config.json
PYTHON := uv run python3
MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test

install:
	uv sync --upgrade

run:
	$(PYTHON) pac-man.py $(CONFIG)

test:
	$(PYTHON) -m pytest

debug:
	$(PYTHON) -m pdb pac-man.py $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache .ruff_cache .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

lint:
	flake8 . --exclude=.venv
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 . --exclude=.venv
	mypy . --strict

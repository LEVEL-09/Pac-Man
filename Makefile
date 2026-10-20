CONFIG ?= config.json
PYTHON := uv run python3
MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug build clean lint lint-strict test re

install:
	uv sync --upgrade

run:
	$(PYTHON) pac-man.py $(CONFIG)

test:
	$(PYTHON) -m pytest

debug:
	$(PYTHON) -m pdb pac-man.py $(CONFIG)

build:
	uv run pyinstaller pac-man.spec pac-man.py

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	find . -type d -name pac_man.egg-info -prune -exec rm -rf {} +
	rm -rf build dist

lint:
	flake8 . --exclude=.venv
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 . --exclude=.venv
	mypy . --strict

re: clean build

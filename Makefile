VENV_PYTHON ?= .venv/bin/python

.PHONY: test

test:
	$(VENV_PYTHON) -m pytest -q

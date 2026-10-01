VENV := .venv
PY := $(VENV)/bin/python
export PATH := $(CURDIR)/$(VENV)/bin:$(PATH)

.PHONY: install test lint format dev migrate

install:
	test -d $(VENV) || python3.12 -m venv $(VENV)
	$(PY) -m pip install -r requirements.txt -r requirements-dev.txt
	SECRET_KEY=$${SECRET_KEY:-install-only-not-secret} $(PY) manage.py tailwind install

test:
	$(PY) -m pytest $(ARGS)

lint:
	$(VENV)/bin/ruff check .

format:
	$(VENV)/bin/ruff format

dev:
	$(PY) manage.py tailwind dev

migrate:
	$(PY) manage.py migrate

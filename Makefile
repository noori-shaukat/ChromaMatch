.PHONY: dev test docker lint docker-run build install

# Detect OS (Windows_NT = Windows, otherwise assume Linux/mac)
ifeq ($(OS),Windows_NT)
    PYTHON := python
else
    PYTHON := python3
endif

dev:
	$(PYTHON) -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/test_basic_app.py --maxfail=1 -q

docker:
	docker build -t chromamatch:latest .

lint:
	ruff check .
	black --check .

docker-run:
	docker run --rm -p 8000:8000 chromamatch:latest

build:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install:
	$(PYTHON) -m venv venv && . venv/bin/activate && pip install -r requirements.txt

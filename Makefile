.PHONY: dev test docker lint docker-run build install

dev:
	python3 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest --maxfail=1 -q

docker:
	docker build -t chromamatch:latest .

lint:
	ruff check .
	black --check .

docker-run:
	docker run --rm -p 8000:8000 chromamatch:latest

build:
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt

install:
	python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

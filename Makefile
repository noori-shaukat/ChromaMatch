dev:
	python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest --maxfail=1 -q

docker:
	docker build -t colormatch:latest .

lint:
	ruff check .
	black --check .

docker-run:
	docker run --rm -p 8000:8000 chromamatch:latest

build:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

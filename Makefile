dev:
	python -m uvicorn src.api.main:app --reload

test:
	pytest --cov=src --cov-fail-under=80

docker:
	docker build -t colormatch:latest .

lint:
	ruff check .
	black --check .

.PHONY: dev test docker lint docker-run build install

# Platform-compatible Python
ifeq ($(OS),Windows_NT)
    PYTHON := py -3.10
    ACTIVATE := venv/Scripts/activate
    PIP := venv/Scripts/pip
else
    PYTHON := python3.10
    ACTIVATE := source venv/bin/activate
    PIP := venv/bin/pip
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

venv:
	$(PYTHON) -m venv venv

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

build-index: install
	$(PYTHON) -m src.rag.indexer

rag: install build-index
	$(PYTHON) - <<EOF
from src.rag.rag_pipeline import ChromaRAGPipeline
pipe = ChromaRAGPipeline()
result = pipe.run("sample.jpg")
print(result)
EOF

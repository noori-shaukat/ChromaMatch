# ChromaMatch
MLOps and LLMops course project


## Quickstart
```bash
git clone https://github.com/<your>/ChromaMatch.git
cd ChromaMatch
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
make dev

# Architecture
flowchart LR
A[User selfie] --> B(Data ingestion)
B --> C(Model training)
C --> D[Model registry (MLflow)]
D --> E[Inference API (FastAPI)]
E --> F[Monitoring (Evidently, Prometheus/Grafana)]

# Make targets
make dev - run dev server
make test - run tests
make docker - build docker

# Monitoring
MLflow server: http://localhost:5000
Evidently: http://localhost:7000
Grafana: http://localhost:3000

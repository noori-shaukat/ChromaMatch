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
```

### MLflow Model Registry

The ChromaMatch v1 model is tracked and versioned using MLflow.

- **Experiment name:** ChromaMatch
- **Model name:** ChromaMatch_Model
- **Version:** v1
- **MLflow UI:**

Here is the MLFlow screenshot to show the experiment for v1 model
![MLFlow](monitoring/screenshots/mlflow.png)
### Evidently Data Drift Report
Here is the data drift dashboard created on Evidently using dummy data

![Data Drift Report](monitoring/screenshots/data_drift_report.png)

### Prometheus Metrics tracking

Prometheus was set up to monitor key metrics including CPU usage, memory consumption, disk I/O, and simulated GPU utilization

Here is the snapshot to show the metric tracking

![Prometheus Monitoring](monitoring/screenshots/prometheus.png)

### Grafana Monitoring Dashboard
Grafana is set up to visualize real-time system metrics (CPU, memory, disk, etc.) collected by Prometheus through the Windows Exporter.

- **Data Source:** Prometheus (`http://localhost:9090`)
- **Dashboard:** Official Windows Exporter Dashboard (ID: 14694)
- **Access URL:** [http://localhost:3000](http://localhost:3000)

Here is the screenshot of the Grafana dashboard displaying live system metrics.

![Grafana Dashboard](monitoring/screenshots/grafana.png)

### Pre-commit Hooks Setup
To maintain clean, consistent, and secure code, pre-commit hooks were configured and verified.

**Active hooks:**
- `trailing-whitespace`
- `end-of-file-fixer`
- `detect-secrets`
- `black`
- `ruff`

All hooks pass successfully when running:
```bash
pre-commit run --all-files
```

## API Documentation

The **ChromaMatch API** is built using **FastAPI**, which automatically generates interactive documentation for developers to explore and test endpoints.

### Access the Auto-Generated Docs

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
  → Interactive interface for sending requests and viewing responses.
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
  → Clean, reference-style API documentation view.

---

### Health Check
**Endpoint:** `GET /health`
**Description:** Confirms that the API is running and reachable.

**Example Response:**
```json
{
  "status": "ok"
}
```
### Analyze Image

**Endpoint:** `POST /analyze`
**Description:** Upload an image to receive AI-generated insights such as skin tone, undertone, and personalized style recommendations.

**Example Response:**

```bash
curl.exe -X POST "http://127.0.0.1:8000/analyze"
     -F "file=@C:\Users\dell\Downloads\MLOPS\ChromaMatch\monitoring\test_images\person1.jpg" `
     -H "accept: application/json"
```

```json
{
  "skin_tone": "warm",
  "undertone": "neutral",
  "face_shape": "oval",
  "recommendation": "Gold jewelry and earth tones suit you best."
}
```
Example:
![Swagger UI](monitoring/screenshots/swagger.png)

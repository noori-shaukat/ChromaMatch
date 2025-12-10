# 🎨 ChromaMatch

**AI-powered color analysis & personalized fashion recommendations using Computer Vision + RAG + MLOps + Cloud.**

ChromaMatch detects **skin tone**, **undertone**, **eye color**, **hair color**, and generates highly personalized recommendations using a **Retrieval-Augmented Generation (RAG)** pipeline.
The project integrates **MLOps**, **LLMOps**, **Prompt Engineering**, **Cloud Deployment**, **Monitoring**, and **Guardrails**.

---

# 🚀 Quickstart

```bash
git clone https://github.com/noori-shaukat/ChromaMatch.git
cd ChromaMatch
make install
make dev
```

### Common Make Targets

| Command            | Description                  |
| ------------------ | ---------------------------- |
| `make dev`         | Run FastAPI server           |
| `make test`        | Run tests                    |
| `make docker`      | Build Docker image           |
| `make docker-run`  | Run container                |
| `make build-index` | Build FAISS RAG index        |
| `make rag`         | Full RAG pipeline end-to-end |

---

# 🧱 System Architecture

![Architecture Diagram](monitoring/screenshots/archdiagram.png)

---

# 🧪 MLflow Model Registry

* **Experiment:** `ChromaMatch`
* **Model Name:** `ChromaMatch_Model`
* **Version:** v1

![MLFlow](monitoring/screenshots/mlflow.png)

---

# 🧾 Evidently Data Drift Dashboard

![Data Drift Report](monitoring/screenshots/data_drift_report.png)

---

# 📈 Prometheus Metrics Tracking

![Prometheus Monitoring](monitoring/screenshots/prometheus.png)

---

# 📉 Grafana Real-Time Dashboard

![Grafana Dashboard](monitoring/screenshots/grafana.png)

---

# 🧹 Pre-commit Hooks

Configured to maintain code quality:

* `trailing-whitespace`
* `end-of-file-fixer`
* `detect-secrets`
* `black`
* `ruff`

Run:

```bash
pre-commit run --all-files
```

---

# 📡 API Documentation

FastAPI auto-generates live documentation.

### Swagger UI

👉 [http://13.60.180.47:8000/docs](http://13.60.180.47:8000/docs)

### ReDoc

👉 [http://13.60.180.47:8000/redoc](http://13.60.180.47:8000/redoc)

---

## `/health`

Check server status.

```json
{"status": "ok"}
```

---

## `/analyze` – (POST)

Upload an image → receive:

* Skin Tone
* Tone Group
* Descriptor
* Undertone
* Eye Color
* Hair Color

Example:

```json
{
  "skin_tone": "MST 4",
  "tone_group": "Medium",
  "descriptor": "Sand / Light Medium",
  "undertone": "Warm",
  "eye_color": ["Brown"],
  "hair_color": "Dark Brown"
}
```

![Swagger UI](monitoring/screenshots/swagger.png)

---

# 🧠 D1 — Prompt Engineering Workflow

This project includes a full experimental pipeline for **prompt robustness testing**.

### 📁 Directory Structure

```
experiments/
 ├── prompts/
 │    ├── baseline_zeroshot.txt
 │    ├── few_shot.txt
 │    └── advanced_cot.txt
 ├── results/
 ├── eval_prompts.py
 └── qualitative_score.py
 data/
 └── eval.jsonl
```

### Required Prompt Strategies (Implemented)

| Strategy                 | Description                        |
| ------------------------ | ---------------------------------- |
| **Baseline Zero-shot**   | Minimal prompt → direct generation |
| **Few-shot (k=3 & k=5)** | Example-driven recommendations     |
| **Advanced**             | Chain-of-Thought (CoT) reasoning   |

### Evaluation Includes:

#### ✔ Quantitative Metrics

* **Cosine Similarity (SentenceTransformers)**
* Optional BLEU / ROUGE via `sacrebleu`

#### ✔ Qualitative Metrics (Human-in-the-loop)

Users manually score:

* **Factuality (1–5)**
* **Helpfulness (1–5)**

#### ✔ MLflow Logging

All experiment runs logged automatically:

👉 [http://13.60.180.47:5000/](http://13.60.180.47:5000/)

### Final Deliverable

A full **prompt_report.md** summarizing:

* Each prompt strategy
* Strengths & weaknesses
* Quantitative results
* Qualitative scores
* Failure cases
* Best performing prompt

---

# 🔍 D2 — RAG (Retrieval-Augmented Generation) Pipeline

### 📁 Code Structure

```
src/rag/
 ├── ingest.py        # Web scraping + document cleaning
 ├── vector_store.py  # FAISS index builder + persistence
 ├── retriever.py     # Query to vector search
 ├── rag_pipeline.py  # Core pipeline
 └── recommend.py     # Endpoint logic
```

### RAG Flow

1. Scrape color/fashion websites
2. Clean + chunk documents
3. Encode using SentenceTransformers
4. Store vectors in **FAISS**
5. Retrieve top-k matches
6. Feed retrieved chunks + user skin profile → LLM
7. Generate personalized recommendations

### Reproducibility

```bash
make rag
```

### RAG Architecture Diagram

Included in repo.

---

# 🛡️ D3 — Guardrails & Safety Mechanisms

Guardrails applied at **input**, **retrieval**, and **output** stages.

### Implemented Policies

### 1️⃣ Input Validation

* PII detection
* Prompt injection filtering
* Image safety validation

### 2️⃣ Output Moderation

* Toxicity thresholding
* Hallucination suppression
* Confidence scoring

All guardrail violations logged to:

* **Prometheus**
* **MLflow**

---

# 📉 D4 — LLM Evaluation & Monitoring

Monitored in real time:

* Latency
* Token usage
* Cost
* Guardrail violations
* Retrieval scores
* System resource usage

### Dashboards

| Service    | URL                                                    |
| ---------- | ------------------------------------------------------ |
| MLflow     | [http://13.60.180.47:5000/](http://13.60.180.47:5000/) |
| Grafana    | [http://13.60.180.47:3000/](http://13.60.180.47:3000/) |
| Prometheus | [http://13.60.180.47:9090/](http://13.60.180.47:9090/) |
| Evidently  | [http://13.60.180.47:7000/](http://13.60.180.47:7000/) |

---

# ☁️ D7 — Cloud Integration (Required)

ChromaMatch uses **AWS** cloud services:

| Cloud Service         | Purpose                                                 |
| --------------------- | ------------------------------------------------------- |
| **S3**                | Store FAISS index + documents + MLflow artifacts        |
| **EC2**               | Host FastAPI, RAG pipeline, MLflow, Grafana, Prometheus |
| **Lambda (Optional)** | Periodic evaluation of RAG pipeline                     |

### Deployment Includes

* Full EC2 setup
* S3 integration
* Open ports for monitoring stack
* Configuration screenshots in repo

---

# 🔐 D8 — Security & Compliance

### SECURITY.md covers:

* Prompt injection defenses
* Safe LLM output handling
* Privacy rules
* PII filtering (image & text)

### Dependency Scanning

```bash
pip-audit
```

CI fails if critical CVEs found.

### Responsible AI

* No personal data stored
* All logs anonymized
* Guardrails enforce safe content

---

# 🌩️ Cloud Deployment (Step-by-Step)

### 1. Launch EC2

```bash
ssh -i chromamatch-key.pem ubuntu@13.60.180.47
```

### 2. Clone repo

```bash
git clone https://github.com/noori-shaukat/ChromaMatch.git
cd ChromaMatch
```

### 3. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run MLflow

```bash
mlflow server --host 0.0.0.0 --port 5000 \
 --backend-store-uri sqlite:///mlflow.db \
 --default-artifact-root s3://chromamatch-artifacts/
```

### 5. Start FastAPI

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 6. Start Monitoring Stack

* **Prometheus:** [http://13.60.180.47:9090](http://13.60.180.47:9090)
* **Grafana:** [http://13.60.180.47:3000](http://13.60.180.47:3000)
* **Evidently:** [http://13.60.180.47:7000](http://13.60.180.47:7000)

---

# 📁 Useful Links

| Service      | URL                                                            |
| ------------ | -------------------------------------------------------------- |
| MLflow       | [http://13.60.180.47:5000/](http://13.60.180.47:5000/)         |
| Grafana      | [http://13.60.180.47:3000/](http://13.60.180.47:3000/)         |
| Prometheus   | [http://13.60.180.47:9090/](http://13.60.180.47:9090/)         |
| Evidently    | [http://13.60.180.47:7000/](http://13.60.180.47:7000/)         |
| Backend API  | [http://13.60.180.47:8000/](http://13.60.180.47:8000/)         |
| Swagger Docs | [http://13.60.180.47:8000/docs](http://13.60.180.47:8000/docs) |

---